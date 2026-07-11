"""LangGraph agent state schema (BRD Section 9.1)."""
from __future__ import annotations

from typing import Annotated, Any, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    # Full conversation history (HumanMessage + AIMessage + ToolMessage).
    messages: Annotated[list[BaseMessage], add_messages]
    # Current form field values extracted so far.
    interaction_data: dict
    # Name of the last tool invoked.
    tool_called: Optional[str]
    # Output from the last tool execution.
    tool_result: Optional[dict]
    # Router decision: 'tool' | 'respond' | 'end'.
    next_action: str
    # Accumulated field updates to return to the frontend Redux store.
    fields_to_update: dict[str, Any]
    # True once a tool has run this turn — forces a final text response next.
    tools_done: bool
    # Non-serialized runtime handle to the DB session (injected per request).
    _db: Any
