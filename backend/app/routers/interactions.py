"""Interaction persistence endpoints (BRD Section 13)."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HCPInteraction
from app.schemas import InteractionCreate, InteractionUpdate

router = APIRouter(tags=["interactions"])


def _get_or_404(db: Session, interaction_id: str) -> HCPInteraction:
    try:
        record = db.get(HCPInteraction, uuid.UUID(interaction_id))
    except (ValueError, TypeError):
        record = None
    if record is None:
        raise HTTPException(status_code=404, detail="Interaction not found.")
    return record


@router.post("/api/interactions")
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db)) -> dict:
    record = HCPInteraction(id=uuid.uuid4(), **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record.as_dict()


@router.get("/api/interactions/{interaction_id}")
def get_interaction(interaction_id: str, db: Session = Depends(get_db)) -> dict:
    return _get_or_404(db, interaction_id).as_dict()


@router.put("/api/interactions/{interaction_id}")
def update_interaction(
    interaction_id: str, payload: InteractionUpdate, db: Session = Depends(get_db)
) -> dict:
    record = _get_or_404(db, interaction_id)
    # Only overwrite fields explicitly provided (BRD C4 — preserve others).
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record.as_dict()


@router.get("/api/interactions/hcp/{hcp_name}")
def get_by_hcp(hcp_name: str, db: Session = Depends(get_db)) -> list[dict]:
    rows = (
        db.query(HCPInteraction)
        .filter(func.lower(HCPInteraction.hcp_name) == hcp_name.lower())
        .order_by(HCPInteraction.created_at.desc())
        .all()
    )
    return [r.as_dict() for r in rows]
