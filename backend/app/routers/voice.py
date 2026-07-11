"""Voice Note transcription endpoint (BRD Section 8.4 & 13).

Voice Note is an INPUT PATH, not a tool (BRD C9). This endpoint accepts a
recorded audio blob, transcribes it with Groq Whisper, and returns text.
The frontend then injects that text into the chat -> log_interaction tool.
"""
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from groq import Groq

from app.config import settings
from app.schemas import TranscriptionResponse

router = APIRouter(tags=["voice"])
logger = logging.getLogger(__name__)


@router.post("/api/voice/transcribe", response_model=TranscriptionResponse)
async def transcribe(audio: UploadFile = File(...)) -> TranscriptionResponse:
    try:
        content = await audio.read()
        client = Groq(api_key=settings.GROQ_API_KEY)
        result = client.audio.transcriptions.create(
            file=(audio.filename or "voice.webm", content),
            model=settings.WHISPER_MODEL,
        )
        text = (result.text or "").strip()
        if not text:
            raise ValueError("empty transcription")
        return TranscriptionResponse(text=text)
    except Exception:
        logger.exception("Transcription failed")
        # BRD Section 14: transcription fails -> graceful message.
        raise HTTPException(
            status_code=500,
            detail="I couldn't transcribe the audio clearly. "
            "Please try again or type your interaction details.",
        )
