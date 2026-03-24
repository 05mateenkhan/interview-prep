"""
transcription_service.py
-------------------------
Handles speech-to-text conversion using OpenAI Whisper (runs locally).
No API key required — model downloads once and runs on your machine.

Whisper model sizes and tradeoffs:
  tiny   → fastest, least accurate  (~39M params)
  base   → good balance             (~74M params)  ← recommended for dev
  small  → better accuracy          (~244M params)
  medium → high accuracy            (~769M params)
  large  → best accuracy, slowest   (~1.5B params)
"""

import whisper
import tempfile
import os
import time
# from pydub import AudioSegment
# from pydub.utils import which

# ── Load Whisper model once at import time ────────────────────────────────────
# Change "base" to "small" or "medium" for better accuracy in production
_MODEL_SIZE = "base"
_whisper_model = None


def get_whisper_model():
    """Lazy-load Whisper model singleton — downloads on first use."""
    global _whisper_model
    if _whisper_model is None:
        print(f"🔄 Loading Whisper '{_MODEL_SIZE}' model...")
        _whisper_model = whisper.load_model(_MODEL_SIZE)
        print(f"✅ Whisper model loaded.")
    return _whisper_model


# ── Supported audio formats ───────────────────────────────────────────────────
SUPPORTED_FORMATS = {
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/mp4": "mp4",
    "audio/webm": "webm",
    "audio/ogg": "ogg",
}

MAX_DURATION_SECONDS = 120  # 2 minutes max per answer


def _get_audio_duration(audio_bytes: bytes, fmt: str) -> float:
    """Return duration of audio in seconds using pydub."""
    with tempfile.NamedTemporaryFile(suffix=f".{fmt}", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        audio = AudioSegment.from_file(tmp_path, format=fmt)
        return len(audio) / 1000.0  # milliseconds → seconds
    finally:
        os.unlink(tmp_path)


def _estimate_confidence(result: dict) -> str:
    """
    Estimate transcription confidence from Whisper segment data.
    Whisper doesn't return a single confidence score, so we derive it
    from average log-probability of segments.
    """
    segments = result.get("segments", [])
    if not segments:
        return "low"

    avg_logprob = sum(s.get("avg_logprob", -1.0) for s in segments) / len(segments)

    if avg_logprob > -0.3:
        return "high"
    elif avg_logprob > -0.6:
        return "medium"
    else:
        return "low"


def transcribe_audio(audio_bytes: bytes, content_type: str) -> dict:
    """
    Transcribe audio bytes to text using local Whisper model.

    Args:
        audio_bytes:  Raw audio file bytes
        content_type: MIME type of the audio (e.g. "audio/wav")

    Returns:
        dict with keys:
          - text: str               → transcribed text
          - duration: float         → audio duration in seconds
          - confidence: str         → "high" | "medium" | "low"
          - language: str           → detected language code (e.g. "en")

    Raises:
        ValueError: if format unsupported, audio too long, or speech is empty
    """
    # Validate format
    fmt = SUPPORTED_FORMATS.get(content_type)
    if not fmt:
        raise ValueError(
            f"Unsupported audio format: '{content_type}'. "
            f"Supported: {', '.join(SUPPORTED_FORMATS.keys())}"
        )

    # Check duration
    # duration = _get_audio_duration(audio_bytes, fmt)
    # duration = len(audio_bytes) * 1000
    # if duration > MAX_DURATION_SECONDS:
    #     raise ValueError(
    #         f"Audio too long: {duration:.1f}s. Maximum allowed is {MAX_DURATION_SECONDS}s."
    #     )
    # if duration < 0.5:
    #     raise ValueError("Audio is too short. Please record a meaningful answer.")

    # Write to temp file for Whisper
    with tempfile.NamedTemporaryFile(suffix=f".{fmt}", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        model = get_whisper_model()
        result = model.transcribe(
            tmp_path,
            language="en",          # Force English; remove for auto-detect
            fp16=False,             # Set True if you have a GPU
            verbose=False,
        )
    finally:
        os.unlink(tmp_path)
    
    # ✅ Extract segments
    segments = result.get("segments", [])

    # ✅ Method 1: duration from last segment
    if segments:
        duration = segments[-1]["end"]
    else: 
        duration = 0

    if duration > MAX_DURATION_SECONDS:
        raise ValueError(
            f"Audio too long: {duration:.1f}s. Maximum allowed is {MAX_DURATION_SECONDS}s."
        )

    if duration < 0.5:
        raise ValueError("Audio is too short. Please record a meaningful answer.")
    text = result.get("text", "").strip()

    if not text:
        raise ValueError(
            "No speech detected in the audio. "
            "Please ensure you spoke clearly and the microphone was working."
        )

    return {
        "text": text,
        "duration": round(duration, 2),
        "confidence": _estimate_confidence(result),
        "language": result.get("language", "unknown"),
    }