from pydantic import BaseModel
from typing import Optional


class StartSessionRequest(BaseModel):
    role: str        # e.g. "Data Scientist", "Software Engineer"
    topic: str       # e.g. "Statistics", "OOPS"
    difficulty: str  # "Easy" | "Medium" | "Hard"
    max_questions: int


class StartSessionResponse(BaseModel):
    session_id: str
    role: str
    topic: str
    difficulty: str
    question: str
    question_number: int


class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: str      # Student's answer (question is stored in session)


class FeedbackScore(BaseModel):
    accuracy: int
    clarity: int
    completeness: int
    overall: int


class SubmitAnswerResponse(BaseModel):
    feedback: str
    ideal_answer: str
    missing_concepts: list[str]
    score: FeedbackScore
    next_question: Optional[str] = None
    session_complete: bool = False

class ResumeAnalysisResponse(BaseModel):
    detected_role: str
    confidence: str        # "High" | "Medium" | "Low"
    role_reasoning: str
    extracted_skills: list[str]


class AudioSubmissionResponse(BaseModel):
    """
    Returned by POST /submit-audio-answer.
    Identical shape to SubmitAnswerResponse + transcription fields.
    """
    # ── Transcription info ────────────────────────────────────────────────────
    transcribed_text: str
    audio_duration_seconds: float
    transcription_confidence: str          # "high" | "medium" | "low"
 
    # ── Evaluation (same as /submit response) ─────────────────────────────────
    feedback: str
    ideal_answer: str
    missing_concepts: list[str]
    score: FeedbackScore
    next_question: Optional[str] = None
    session_complete: bool = False