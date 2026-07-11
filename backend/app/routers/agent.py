"""Main LangGraph agent endpoint (BRD Section 13: POST /api/agent)."""
import logging

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.orm import Session

from app.agent.graph import agent_graph
from app.database import get_db
from app.schemas import AgentRequest, AgentResponse

router = APIRouter(tags=["agent"])
logger = logging.getLogger(__name__)


@router.post("/api/agent", response_model=AgentResponse)
def run_agent(req: AgentRequest, db: Session = Depends(get_db)) -> AgentResponse:
    interaction_data = req.interaction_data.model_dump()
    if req.interaction_id and not interaction_data.get("interaction_id"):
        interaction_data["interaction_id"] = req.interaction_id

    initial_state = {
        "messages": [HumanMessage(content=req.message)],
        "interaction_data": interaction_data,
        "fields_to_update": {},
        "_db": db,
    }

    try:
        result = agent_graph.invoke(initial_state, config={"recursion_limit": 12})
    except RuntimeError as exc:
        if str(exc) == "LLM_UNAVAILABLE":
            # Groq API rate limit / timeout (BRD Section 14).
            raise HTTPException(
                status_code=503,
                detail="I'm having trouble connecting to the AI right now. "
                "Please try again in a moment.",
            )
        logger.exception("Agent run failed")
        raise HTTPException(status_code=500, detail="Agent execution failed.")
    except Exception:
        logger.exception("Unexpected agent error")
        raise HTTPException(
            status_code=500,
            detail="The interaction was processed but could not be saved. "
            "Please try submitting again.",
        )

    # Final AI text message = last AIMessage with no tool calls.
    ai_message = ""
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and not getattr(msg, "tool_calls", None):
            ai_message = msg.content
            break

    fields = result.get("fields_to_update", {})
    interaction_id = fields.get("interaction_id") or interaction_data.get("interaction_id")

    return AgentResponse(
        fields_to_update=fields,
        ai_message=ai_message or "Done.",
        interaction_id=interaction_id,
        tool_called=result.get("tool_called"),
    )
