"""
voice.py
---------
POST /submit-audio-answer

Mirrors the /submit endpoint exactly, but accepts audio instead of text.
Uses session_id to pull role, topic, difficulty, question, reference_answer
from the existing session store — no duplicate state.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models.schemas import AudioSubmissionResponse, FeedbackScore
from services.transcription_service import transcribe_audio
from services.evaluation_service import evaluate_transcribed_answer, advance_session

# ── Import the shared session store from interview router ─────────────────────
# Both /submit and /submit-audio-answer operate on the same sessions dict.
from routers.interview import sessions

router = APIRouter(tags=["Voice Answers"])

MAX_FILE_SIZE_MB = 25


@router.post("/submit-audio-answer", response_model=AudioSubmissionResponse)
async def submit_audio_answer(
    file: UploadFile = File(..., description="Audio file: WAV, MP3, WebM, OGG"),
    session_id: str = Form(..., description="Active session ID from /interview/start"),
):
    """
    Voice-based answer submission. Works as a drop-in replacement for /submit.

    1. Validates the uploaded audio file
    2. Transcribes speech → text using local Whisper model
    3. Evaluates transcribed text using the same LangChain pipeline as /submit
    4. Updates the session state (scores, answers, next question)
    5. Returns transcription + full evaluation feedback
    """

    # ── 1. Validate session ───────────────────────────────────────────────────
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Start a session via /interview/start first.")

    # ── 2. Validate audio file ────────────────────────────────────────────────
    audio_bytes = await file.read()

    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    size_mb = len(audio_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {size_mb:.1f}MB. Maximum is {MAX_FILE_SIZE_MB}MB."
        )

    # ── 3. Transcribe audio → text ────────────────────────────────────────────
    try:
        transcription = transcribe_audio(audio_bytes, file.content_type)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    transcribed_text = transcription["text"]

    # ── 4. Evaluate using existing LangChain pipeline ─────────────────────────
    try:
        result = evaluate_transcribed_answer(transcribed_text, session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

    # ── 5. Update session state (mirrors /submit logic) ───────────────────────
    session["student_answers"].append(transcribed_text)
    session["scores"].append(result["score"]["overall"])
    session["feedback"].append(result["feedback"])
    session["ideal_answer"].append(result["ideal_answer"])

    session_complete = session["current_question_number"] >= session["max_questions"]

    # Advance to next question if session not complete
    next_question = None
    if not session_complete:
        next_doc = advance_session(session)
        next_question = next_doc["question"] if next_doc else None

    # ── 6. Return combined result ─────────────────────────────────────────────
    return AudioSubmissionResponse(
        transcribed_text=transcribed_text,
        feedback=result["feedback"],
        ideal_answer=result["ideal_answer"],
        missing_concepts=result.get("missing_concepts", []),
        score=FeedbackScore(**result["score"]),
        next_question=next_question,
        session_complete=session_complete,
        audio_duration_seconds=transcription["duration"],
        transcription_confidence=transcription["confidence"],
    )