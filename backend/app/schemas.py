"""Pydantic request/response schemas."""
from datetime import date, time
from typing import Any, Optional

from pydantic import BaseModel, Field


class InteractionData(BaseModel):
    """The mutable form state carried between frontend and agent."""

    interaction_id: Optional[str] = None
    hcp_name: str = ""
    interaction_type: str = ""
    date: str = ""
    time: str = ""
    attendees: str = ""
    topics_discussed: str = ""
    materials_shared: list[str] = Field(default_factory=list)
    samples_distributed: list[str] = Field(default_factory=list)
    sentiment: str = ""
    outcomes: str = ""
    follow_up_actions: str = ""


class AgentRequest(BaseModel):
    message: str
    interaction_data: InteractionData = Field(default_factory=InteractionData)
    interaction_id: Optional[str] = None


class AgentResponse(BaseModel):
    fields_to_update: dict[str, Any]
    ai_message: str
    interaction_id: Optional[str] = None
    tool_called: Optional[str] = None


class InteractionCreate(BaseModel):
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    interaction_date: Optional[date] = None
    interaction_time: Optional[time] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: list[str] = Field(default_factory=list)
    samples_distributed: list[str] = Field(default_factory=list)
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None


class InteractionUpdate(BaseModel):
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    interaction_date: Optional[date] = None
    interaction_time: Optional[time] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[list[str]] = None
    samples_distributed: Optional[list[str]] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None


class TranscriptionResponse(BaseModel):
    text: str
