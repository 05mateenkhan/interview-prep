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


# ── Phase 2 Batch Evaluation Models ───────────────────────────────────────────

class QuestionAnswerPair(BaseModel):
    question_id: int
    question: str
    user_answer: str


class BatchEvaluationRequest(BaseModel):
    """
    Request model for batch evaluation endpoint.
    Accepts a list of questions with answers for a session.
    """
    questions_with_answers: list[QuestionAnswerPair]
    resume_text: Optional[str] = None
    interview_metadata: Optional[dict] = None  # role, topic, difficulty, etc.


class QuestionEvaluation(BaseModel):
    question_id: int
    question: str
    user_answer: str
    score: float  # 0-100
    feedback: str


class BatchEvaluationResponse(BaseModel):
    """
    Response model for batch evaluation endpoint.
    Contains overall score and per-question evaluations.
    """
    session_id: str
    overall_score: float  # 0-100
    feedback: str  # Comprehensive evaluation
    question_evaluations: list[QuestionEvaluation]
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]


class SummaryResponse(BaseModel):
    """
    Response model for summary endpoint.
    Contains formatted interview summary and recommendations.
    """
    session_id: str
    role: str
    topic: str
    difficulty: str
    summary: str
    overall_score: float
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    next_steps: list[str]
    question_evaluations: list[QuestionEvaluation] = []  # Per-question breakdown