"""Groq LLM client factory.

Primary model: gemma2-9b-it (tool routing + extraction).
Secondary model: llama-3.3-70b-versatile (extended-context summaries).
All NLP/extraction is performed by the LLM — no hardcoded parsing (BRD C2).
"""
from langchain_groq import ChatGroq

from app.config import settings


def get_primary_llm(**kwargs) -> ChatGroq:
    """gemma2-9b-it — used for tool routing and field extraction."""
    return ChatGroq(
        model=settings.PRIMARY_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=kwargs.pop("temperature", 0.1),
        **kwargs,
    )


def get_secondary_llm(**kwargs) -> ChatGroq:
    """llama-3.3-70b-versatile — used for longer-context reasoning tasks."""
    return ChatGroq(
        model=settings.SECONDARY_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=kwargs.pop("temperature", 0.3),
        **kwargs,
    )
