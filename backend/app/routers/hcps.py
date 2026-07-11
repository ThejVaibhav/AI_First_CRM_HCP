"""HCP master list for typeahead (BRD Section 13: GET /api/hcps).

Mock/seed data is acceptable per BRD Section 7.2. Also merges any HCP names
already present in logged interactions.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HCPInteraction

router = APIRouter(tags=["hcps"])

SEED_HCPS = [
    "Dr. Smith",
    "Dr. Patel",
    "Dr. Johnson",
    "Dr. Nguyen",
    "Dr. Garcia",
    "Dr. Chen",
    "Dr. Williams",
    "Dr. Anderson",
]


@router.get("/api/hcps")
def list_hcps(db: Session = Depends(get_db)) -> list[str]:
    logged = {
        row[0]
        for row in db.query(HCPInteraction.hcp_name).distinct().all()
        if row[0]
    }
    return sorted(set(SEED_HCPS) | logged)
