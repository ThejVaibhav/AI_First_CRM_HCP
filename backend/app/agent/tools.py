"""The exactly-5 LangGraph tools (BRD Section 9 & Constraint C8).

Each tool is a Pydantic schema (bound to the LLM so it emits structured
arguments) plus a handler executed by the tool_executor node. The LLM is
responsible for ALL extraction/inference — these handlers only merge the
LLM-produced arguments into state and persist to PostgreSQL. No regex,
keyword matching, or rule-based parsing is used anywhere (BRD C2).

Voice Note is deliberately NOT a tool — it is an input path that produces
text which flows into `log_interaction` (BRD C9).
"""
from __future__ import annotations

import uuid
from datetime import date, time
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.agent.llm import get_secondary_llm
from app.models import HCPInteraction

# --------------------------------------------------------------------------
# Tool argument schemas (bound to the LLM via .bind_tools)
# --------------------------------------------------------------------------


class LogInteractionArgs(BaseModel):
    """Extract every interaction field you can from the rep's message.

    Resolve relative dates (today, yesterday, last Monday) to a real
    calendar date using the provided current date. Infer sentiment from
    the overall tone. Leave a field empty only if it is genuinely absent.
    """

    hcp_name: Optional[str] = Field(None, description="Full name of the HCP / doctor")
    interaction_type: Optional[str] = Field(
        None, description="One of: Meeting, Call, Email, Conference"
    )
    date: Optional[str] = Field(None, description="ISO date YYYY-MM-DD, resolved from NL")
    time: Optional[str] = Field(None, description="Time HH:MM (24h) if mentioned")
    attendees: Optional[str] = Field(None, description="Comma-separated attendee names")
    topics_discussed: Optional[str] = Field(None, description="Topics/products discussed")
    materials_shared: Optional[list[str]] = Field(
        None, description="Brochures/materials shared"
    )
    samples_distributed: Optional[list[str]] = Field(
        None, description="Drug samples handed out"
    )
    sentiment: Optional[str] = Field(
        None, description="Inferred tone: Positive, Neutral, or Negative"
    )
    outcomes: Optional[str] = Field(None, description="Key outcomes/agreements")
    follow_up_actions: Optional[str] = Field(None, description="Any follow-up mentioned")


class EditInteractionArgs(BaseModel):
    """Update ONLY the field(s) the user is correcting.

    Include a key ONLY for fields being changed. Never include a field the
    user did not mention — omitted fields must remain untouched.
    """

    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[list[str]] = None
    samples_distributed: Optional[list[str]] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None


class ScheduleFollowupArgs(BaseModel):
    """Schedule a follow-up with an HCP. Resolve relative dates to real dates."""

    hcp_name: Optional[str] = Field(None, description="HCP the follow-up is with")
    followup_date: Optional[str] = Field(None, description="ISO date YYYY-MM-DD")
    followup_time: Optional[str] = Field(None, description="Time HH:MM if given")
    purpose: Optional[str] = Field(None, description="Reason/purpose of the follow-up")


class SuggestNextActionArgs(BaseModel):
    """Request an LLM-generated next-best-action recommendation for the current HCP."""

    hcp_name: Optional[str] = Field(
        None, description="HCP to base the recommendation on (defaults to current)"
    )


class SearchHcpHistoryArgs(BaseModel):
    """Search past interaction history for a specific HCP."""

    hcp_name: str = Field(..., description="HCP name extracted from the user's question")


# Ordered list bound to the LLM. Exactly five (BRD C8).
TOOL_SCHEMAS = [
    LogInteractionArgs,
    EditInteractionArgs,
    ScheduleFollowupArgs,
    SuggestNextActionArgs,
    SearchHcpHistoryArgs,
]

TOOL_NAME_MAP = {
    "LogInteractionArgs": "log_interaction",
    "EditInteractionArgs": "edit_interaction",
    "ScheduleFollowupArgs": "schedule_followup",
    "SuggestNextActionArgs": "suggest_next_action",
    "SearchHcpHistoryArgs": "search_hcp_history",
}


# --------------------------------------------------------------------------
# Persistence helpers
# --------------------------------------------------------------------------


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _parse_time(value: Optional[str]) -> Optional[time]:
    if not value:
        return None
    try:
        return time.fromisoformat(value if len(value) > 5 else value + ":00")
    except (ValueError, TypeError):
        return None


def _persist(db: Session, data: dict) -> str:
    """Insert or update the interaction record; return its id."""
    record: Optional[HCPInteraction] = None
    iid = data.get("interaction_id")
    if iid:
        try:
            record = db.get(HCPInteraction, uuid.UUID(iid))
        except (ValueError, TypeError):
            record = None
    if record is None:
        record = HCPInteraction(id=uuid.uuid4())
        db.add(record)

    record.hcp_name = data.get("hcp_name") or record.hcp_name
    record.interaction_type = data.get("interaction_type") or record.interaction_type
    if _parse_date(data.get("date")):
        record.interaction_date = _parse_date(data.get("date"))
    if _parse_time(data.get("time")):
        record.interaction_time = _parse_time(data.get("time"))
    record.attendees = data.get("attendees") or record.attendees
    record.topics_discussed = data.get("topics_discussed") or record.topics_discussed
    if data.get("materials_shared"):
        record.materials_shared = data.get("materials_shared")
    if data.get("samples_distributed"):
        record.samples_distributed = data.get("samples_distributed")
    record.sentiment = data.get("sentiment") or record.sentiment
    record.outcomes = data.get("outcomes") or record.outcomes
    record.follow_up_actions = data.get("follow_up_actions") or record.follow_up_actions

    db.commit()
    db.refresh(record)
    return str(record.id)


# --------------------------------------------------------------------------
# Tool handlers — each returns (fields_to_update: dict, result_note: str)
# --------------------------------------------------------------------------


def handle_log_interaction(args: dict, state: dict, db: Session):
    """Tool 1 — merge LLM-extracted fields into state and persist."""
    fields = {k: v for k, v in args.items() if v not in (None, "", [])}
    merged = {**state.get("interaction_data", {}), **fields}
    interaction_id = _persist(db, merged)
    fields["interaction_id"] = interaction_id
    populated = ", ".join(k for k in fields if k != "interaction_id")
    return fields, (
        f"Logged interaction and saved to the database. "
        f"Populated fields: {populated}."
    )


def handle_edit_interaction(args: dict, state: dict, db: Session):
    """Tool 2 — update ONLY the provided fields; leave others untouched (BRD C4)."""
    fields = {k: v for k, v in args.items() if v is not None}
    if not fields:
        return {}, "No specific field to update was identified."
    current = dict(state.get("interaction_data", {}))
    current.update(fields)
    if current.get("interaction_id"):
        _persist(db, current)
        fields["interaction_id"] = current["interaction_id"]
    changed = ", ".join(f"{k} to {v}" for k, v in fields.items() if k != "interaction_id")
    return fields, f"Updated {changed}. All other details remain unchanged."


def handle_schedule_followup(args: dict, state: dict, db: Session):
    """Tool 3 — append a follow-up entry to follow_up_actions and persist."""
    hcp = args.get("hcp_name") or state.get("interaction_data", {}).get("hcp_name", "the HCP")
    when = args.get("followup_date") or "the requested date"
    if args.get("followup_time"):
        when += f" at {args['followup_time']}"
    purpose = args.get("purpose") or "follow-up"
    entry = f"Follow-up with {hcp} on {when} — {purpose}."
    existing = state.get("interaction_data", {}).get("follow_up_actions", "")
    combined = f"{existing}\n{entry}".strip() if existing else entry
    fields = {"follow_up_actions": combined}
    current = {**state.get("interaction_data", {}), **fields}
    if current.get("interaction_id"):
        _persist(db, current)
        fields["interaction_id"] = current["interaction_id"]
    return fields, f"Follow-up scheduled with {hcp} on {when}."


def handle_suggest_next_action(args: dict, state: dict, db: Session):
    """Tool 4 — LLM-generated, context-specific recommendation (no templates)."""
    data = state.get("interaction_data", {})
    hcp = args.get("hcp_name") or data.get("hcp_name", "")
    history = []
    if hcp:
        rows = (
            db.query(HCPInteraction)
            .filter(func.lower(HCPInteraction.hcp_name) == hcp.lower())
            .order_by(HCPInteraction.created_at.desc())
            .limit(5)
            .all()
        )
        history = [r.as_dict() for r in rows]
    llm = get_secondary_llm()
    prompt = (
        "You are a pharma sales strategist. Based on the current interaction and "
        "past history, recommend ONE specific, sales-relevant next best action "
        "(e.g. send literature, invite to CME event, escalate to medical affairs, "
        "schedule a follow-up call with clinical data). Be concrete and tailored.\n\n"
        f"Current interaction: {data}\n\nPast interactions with {hcp or 'this HCP'}: {history}"
    )
    recommendation = llm.invoke(prompt).content
    return {}, recommendation


def handle_search_hcp_history(args: dict, state: dict, db: Session):
    """Tool 5 — fetch records for the HCP and have the LLM summarize them."""
    hcp = args.get("hcp_name", "")
    rows = (
        db.query(HCPInteraction)
        .filter(func.lower(HCPInteraction.hcp_name) == hcp.lower())
        .order_by(HCPInteraction.created_at.desc())
        .all()
    )
    if not rows:
        return {}, f"I found no past interactions logged for {hcp}."
    records = [r.as_dict() for r in rows]
    llm = get_secondary_llm()
    prompt = (
        "Summarize this HCP interaction history for a field rep preparing for a "
        "visit. Mention how many times they met, the most recent visit's date, "
        "topics, sentiment, and any outstanding follow-ups. Be concise and natural.\n\n"
        f"HCP: {hcp}\nRecords: {records}"
    )
    summary = llm.invoke(prompt).content
    return {}, summary


HANDLERS = {
    "log_interaction": handle_log_interaction,
    "edit_interaction": handle_edit_interaction,
    "schedule_followup": handle_schedule_followup,
    "suggest_next_action": handle_suggest_next_action,
    "search_hcp_history": handle_search_hcp_history,
}
