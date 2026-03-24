"""
evaluation_service.py
----------------------
Bridges the voice pipeline to your existing evaluate_answer()
from langchain_service.py.

The voice endpoint passes transcribed text here along with session context,
and this function calls your real evaluation chain — exactly like /submit does.
"""

from services.langchain_service import evaluate_answer as _evaluate_answer
from services.vector_store import retrieve_question


def evaluate_transcribed_answer(
    transcribed_text: str,
    session: dict,
) -> dict:
    """
    Evaluate a voice-transcribed answer using the existing LangChain pipeline.

    Args:
        transcribed_text: Text output from Whisper transcription
        session:          The session dict from sessions[session_id] in interview.py
                          Must contain: role, topic, difficulty, asked, reference_answers,
                          current_question_number

    Returns:
        dict with keys: feedback, ideal_answer, missing_concepts, score
        (same shape as your existing /submit endpoint returns)
    """
    current_q_index = session["current_question_number"] - 1
    current_question = session["asked"][current_q_index]
    reference_answer = session["reference_answers"][current_q_index]

    return _evaluate_answer(
        role=session["role"],
        topic=session["topic"],
        difficulty=session["difficulty"],
        question=current_question,
        reference_answer=reference_answer,
        student_answer=transcribed_text,
    )


def advance_session(session: dict) -> dict | None:
    """
    After a voice answer is evaluated, advance the session to the next question
    exactly like /submit does.

    Returns:
        Next question doc (with 'question' key) if session continues, else None.
    """
    session_complete = session["current_question_number"] >= session["max_questions"]

    if session_complete:
        return None

    next_doc = retrieve_question(
        k=5,
        role=session["role"],
        topic=session["topic"],
        difficulty=session["difficulty"],
        exclude_questions=session["asked"],
    )

    session["asked"].append(next_doc["question"])
    session["reference_answers"].append(next_doc["answer"])
    session["current_question_number"] += 1

    return next_doc