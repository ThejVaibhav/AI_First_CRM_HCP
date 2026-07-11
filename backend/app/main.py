"""FastAPI application entry point.

Wires together CORS, the LangGraph agent endpoint, interaction CRUD,
voice transcription, and the HCP list. See BRD Sections 11 & 13.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import agent, health, hcps, interactions, voice

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI-First CRM – HCP Module",
    description="Log Interaction Screen backend: FastAPI + LangGraph agent (Groq).",
    version="2.0",
)

# CORS: allow the React dev servers (localhost:3000 and Vite's 5173) per BRD C13.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers.
app.include_router(health.router)
app.include_router(agent.router)
app.include_router(voice.router)
app.include_router(interactions.router)
app.include_router(hcps.router)


@app.on_event("startup")
def on_startup() -> None:
    """Create tables if they don't yet exist (dev convenience; Alembic is source of truth)."""
    Base.metadata.create_all(bind=engine)
