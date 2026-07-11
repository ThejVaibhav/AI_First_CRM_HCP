"""LangGraph agent graph (BRD Section 9.2).

Structure:
  llm_node  --(tool_calls?)-->  tool_executor_node  -->  llm_node
  llm_node  --(no tool_calls)-->  END

The LLM (gemma2-9b-it) decides which of the 5 tools to call and produces
their arguments. All extraction/inference lives in the LLM (BRD C2).
"""
from __future__ import annotations

import json
import logging
from datetime import date

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langgraph.graph import END, StateGraph

from app.agent.llm import get_primary_llm
from app.agent.state import AgentState
from app.agent.tools import HANDLERS, TOOL_NAME_MAP, TOOL_SCHEMAS

logger = logging.getLogger(__name__)

_MAX_TOOL_LOOPS = 6


def _system_prompt(interaction_data: dict) -> SystemMessage:
    today = date.today()
    return SystemMessage(
        content=(
            "You are the AI assistant of an AI-First pharmaceutical CRM. Field reps "
            "describe their interactions with Healthcare Professionals (HCPs) in natural "
            "language (typed or transcribed from voice). You control a read-only form by "
            "calling tools — the user NEVER fills the form manually.\n\n"
            f"Today's date is {today.isoformat()} ({today.strftime('%A')}). Resolve all "
            "relative dates (today, yesterday, last Monday, next Monday) to real ISO dates.\n\n"
            "Call EXACTLY ONE tool that best matches the user's intent. Never call more "
            "than one tool for a single message. Trigger mapping:\n"
            "- Describing a NEW visit/meeting/call → log_interaction (infer sentiment from "
            "tone; do not keyword-match).\n"
            "- Correcting/changing a field ('change the sentiment', 'the date was actually "
            "…') → edit_interaction. Include ONLY the field(s) being changed; never touch "
            "others. Do NOT also call log_interaction.\n"
            "- 'Schedule a follow-up…', 'set up a follow-up' → schedule_followup. This must "
            "ONLY affect follow_up_actions — do NOT change date, interaction_type, outcomes, "
            "or any other field, and do NOT call log_interaction.\n"
            "- 'What should I do next?', 'what's the next best action', 'any recommendation' "
            "→ suggest_next_action.\n"
            "- 'What did I discuss with…', 'how many times have I met…', questions about past "
            "visits → search_hcp_history.\n\n"
            "If (and only if) the message has no interaction intent, reply helpfully in plain "
            "text with no tool call.\n\n"
            f"Current form state: {json.dumps(interaction_data)}"
        )
    )


def llm_node(state: AgentState) -> dict:
    """Call the primary Groq model. Binds tools on the first pass; on the pass
    after a tool has run, produces a concise final confirmation with no tools."""
    messages = [_system_prompt(state.get("interaction_data", {}))] + state["messages"]

    if state.get("tools_done"):
        # Second pass: force a short natural-language confirmation, no more tools.
        messages.append(
            SystemMessage(
                content=(
                    "A tool has just run (see the tool result above). Write a brief, "
                    "friendly 1–2 sentence confirmation for the user and offer a natural "
                    "next step. Do NOT output raw JSON or the form state, and do NOT call "
                    "any more tools."
                )
            )
        )
        llm = get_primary_llm()
    else:
        llm = get_primary_llm().bind_tools(TOOL_SCHEMAS)

    try:
        response: AIMessage = llm.invoke(messages)
    except Exception as exc:  # Groq rate limit / timeout / network
        logger.exception("LLM invocation failed")
        raise RuntimeError("LLM_UNAVAILABLE") from exc

    next_action = (
        "tool"
        if getattr(response, "tool_calls", None) and not state.get("tools_done")
        else "end"
    )
    return {"messages": [response], "next_action": next_action}


def tool_executor_node(state: AgentState) -> dict:
    """Execute each tool call emitted by the LLM and feed results back."""
    last: AIMessage = state["messages"][-1]
    db = state.get("_db")
    interaction_data = dict(state.get("interaction_data", {}))
    fields_to_update = dict(state.get("fields_to_update", {}))
    tool_messages = []
    last_tool_name = None

    # Execute ONLY the first tool call. One user message maps to one action;
    # this prevents the model from chaining a second tool that would corrupt
    # unrelated fields (e.g. schedule_followup + an extra log_interaction).
    calls = last.tool_calls[:1]
    for call in calls:
        schema_name = call["name"]
        tool_name = TOOL_NAME_MAP.get(schema_name, schema_name)
        handler = HANDLERS.get(tool_name)
        last_tool_name = tool_name
        if handler is None:
            note = f"Unknown tool: {tool_name}"
            tool_messages.append(ToolMessage(content=note, tool_call_id=call["id"]))
            continue
        try:
            fields, note = handler(call.get("args", {}), {"interaction_data": interaction_data}, db)
        except Exception as exc:
            logger.exception("Tool %s failed", tool_name)
            note = f"The {tool_name} action could not be completed: {exc}"
            fields = {}
        interaction_data.update(fields)
        fields_to_update.update(fields)
        tool_messages.append(ToolMessage(content=note, tool_call_id=call["id"]))

    # Satisfy the API contract: every tool_call in the AIMessage needs a
    # matching ToolMessage. Acknowledge any skipped (extra) calls.
    for skipped in last.tool_calls[1:]:
        tool_messages.append(
            ToolMessage(
                content="Skipped — only one action is handled per message.",
                tool_call_id=skipped["id"],
            )
        )

    return {
        "messages": tool_messages,
        "interaction_data": interaction_data,
        "fields_to_update": fields_to_update,
        "tool_called": last_tool_name,
        "tool_result": fields_to_update,
        "tools_done": True,
    }


def _route(state: AgentState) -> str:
    return state.get("next_action", "end")


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("llm_node", llm_node)
    graph.add_node("tool_executor_node", tool_executor_node)
    graph.set_entry_point("llm_node")
    graph.add_conditional_edges(
        "llm_node", _route, {"tool": "tool_executor_node", "end": END}
    )
    graph.add_edge("tool_executor_node", "llm_node")
    return graph.compile()


# Compiled once at import; stateless per-request execution.
agent_graph = build_graph()
