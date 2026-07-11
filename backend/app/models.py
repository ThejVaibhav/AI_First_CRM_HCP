"""SQLAlchemy ORM models. See BRD Section 12 (Data Model)."""
import uuid
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, String, Text, Time
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.database import Base


class HCPInteraction(Base):
    """A single logged interaction between a field rep and an HCP."""

    __tablename__ = "hcp_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hcp_name = Column(String(255), nullable=True)
    interaction_type = Column(String(100), nullable=True)
    interaction_date = Column(Date, nullable=True)
    interaction_time = Column(Time, nullable=True)
    attendees = Column(Text, nullable=True)
    topics_discussed = Column(Text, nullable=True)
    # JSONB on PostgreSQL; arrays of strings.
    materials_shared = Column(JSONB, nullable=True, default=list)
    samples_distributed = Column(JSONB, nullable=True, default=list)
    sentiment = Column(String(20), nullable=True)
    outcomes = Column(Text, nullable=True)
    follow_up_actions = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def as_dict(self) -> dict:
        """Serialize to a plain dict matching the frontend Redux shape."""
        return {
            "interaction_id": str(self.id),
            "hcp_name": self.hcp_name or "",
            "interaction_type": self.interaction_type or "",
            "date": self.interaction_date.isoformat() if self.interaction_date else "",
            "time": self.interaction_time.isoformat() if self.interaction_time else "",
            "attendees": self.attendees or "",
            "topics_discussed": self.topics_discussed or "",
            "materials_shared": self.materials_shared or [],
            "samples_distributed": self.samples_distributed or [],
            "sentiment": self.sentiment or "",
            "outcomes": self.outcomes or "",
            "follow_up_actions": self.follow_up_actions or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
