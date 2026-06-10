from fastapi import APIRouter, HTTPException
from models.schemas import (
    StartSessionRequest, StartSessionResponse,
    SubmitAnswerRequest, SubmitAnswerResponse, FeedbackScore,
    BatchEvaluationResponse, QuestionEvaluation, SummaryResponse
)
from services.vector_store import retrieve_question
from services.langchain_service import evaluate_answer, overall_feedback, evaluate_batch_answers
import uuid

router = APIRouter(prefix="/interview", tags=["Interview"])

# In-memory session store (replace with DB later)
sessions: dict = {}



@router.post("/start", response_model=StartSessionResponse)
def start_session(req: StartSessionRequest):
    """Start a new interview session — retrieves first question from FAISS."""
    session_id = str(uuid.uuid4())

    # Retrieve first question from vector store
    doc = retrieve_question(req.max_questions, req.role, req.topic, req.difficulty)

    sessions[session_id] = {
        "max_questions": req.max_questions,
        "role": req.role,
        "topic": req.topic,
        "difficulty": req.difficulty,
        "asked": [doc["question"]],           # track asked questions
        "reference_answers": [doc["answer"]], # store reference answers
        "student_answers": [],
        "scores": [],
        "current_question_number": 1,
        "ideal_answer": [],
        "feedback": [],
    }

    return StartSessionResponse(
        session_id=session_id,
        role=req.role,
        topic=req.topic,
        difficulty=req.difficulty,
        question=doc["question"],
        question_number=1,
    )


@router.post("/submit", response_model=SubmitAnswerResponse)
def submit_answer(req: SubmitAnswerRequest):
    """Submit answer → store Q&A → return next question (NO LLM CALL - saved for batch evaluation)."""
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    current_q_index = session["current_question_number"] - 1
    current_question = session["asked"][current_q_index]

    # ✅ BATCH EVALUATION v2: Just store the answer, NO LLM CALL
    session["student_answers"].append(req.answer)
    
    # Store placeholder values (will be filled by batch evaluation later)
    session["scores"].append(None)
    session["feedback"].append(None)
    session["ideal_answer"].append(None)
    
    current_q_num = session["current_question_number"]
    session_complete = current_q_num >= session["max_questions"]

    next_question = None
    if not session_complete:
        # Retrieve next unique question from FAISS
        next_doc = retrieve_question(
            k=session["max_questions"],
            role=session["role"],
            topic=session["topic"],
            difficulty=session["difficulty"],
            exclude_questions=session["asked"],
        )
        session["asked"].append(next_doc["question"])
        session["reference_answers"].append(next_doc["answer"])
        session["current_question_number"] += 1
        next_question = next_doc["question"]

    # Return empty feedback (will be generated at end via feedback_v2 endpoint)
    return SubmitAnswerResponse(
        feedback="",
        ideal_answer="",
        missing_concepts=[],
        score=FeedbackScore(accuracy=0, clarity=0, completeness=0, overall=0),
        next_question=next_question,
        session_complete=session_complete,
    )


@router.get("/summary/{session_id}")
def get_summary(session_id: str):
    """Full session summary with all Q&A and scores."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    scores = session["scores"]
    avg = round(sum(scores) / len(scores), 1) if scores else 0

    return {
        "session_id": session_id,
        "role": session["role"],
        "topic": session["topic"],
        "difficulty": session["difficulty"],
        "total_questions": len(session["asked"]),
        "average_score": avg,
        "breakdown": [
            {
                "question_number": i + 1,
                "question": session["asked"][i],
                "student_answer": session["student_answers"][i] if i < len(session["student_answers"]) else "",
                "score": scores[i] if i < len(scores) else None,
            }
            for i in range(len(session["asked"]))
        ],
    }


@router.get("/options")
def get_options():
    """Return available roles, topics, difficulties for the frontend dropdowns."""
    return {
        "roles": [
            "Data Scientist",
            "Full Stack Engineer",
            "HR / Behavioural",
            "Machine Learning Engineer",
            "Software Engineer",
        ],
        "topics": {
            "Data Scientist": ["Statistics", "EDA", "Feature Engineering", "Feature Selection",
                               "Hypothesis Testing", "Business Interpretation"],
            "Machine Learning Engineer": ["Supervised Learning", "Unsupervised Learning",
                                          "Model Evaluation", "Overfitting / Regularization"],
            "Software Engineer": ["OOPS", "OS", "DBMS", "Networking", "Clean Code Principles",
                                  "System Design Basics", "Performance Optimization"],
            "Full Stack Engineer": ["Frontend Fundamentals", "Backend Development",
                                    "API Design & Integration", "Database Design",
                                    "DevOps Basics", "Deployment Basics", "Web Security"],
            "HR / Behavioural": ["Conflict Resolution", "Leadership", "Failure Handling",
                                 "Strength/Weakness", "Project Explanation"],
        },
        "difficulties": ["Easy", "Medium", "Hard"],
    } 

@router.get("/feedback/{session_id}")
def get_feedback(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    summary = get_summary(session_id)
    result = overall_feedback(summary)
    return result


# ── Phase 2 Batch Evaluation Endpoints ───────────────────────────────────────

@router.post("/feedback_v2/{session_id}", response_model=BatchEvaluationResponse)
def evaluate_batch_feedback(session_id: str):
    """
    Evaluate entire interview session in one LLM call.
    Sends all questions and answers together for comprehensive evaluation.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Build Q&A pairs from session data
    questions_with_answers = [
        {
            "question_id": i + 1,
            "question": session["asked"][i],
            "user_answer": session["student_answers"][i] if i < len(session["student_answers"]) else "",
        }
        for i in range(len(session["asked"]))
    ]
    
    # Call batch evaluation service
    batch_result = evaluate_batch_answers(
        questions_with_answers=questions_with_answers,
        role=session["role"],
        topic=session["topic"],
        difficulty=session["difficulty"],
        resume_text=None,  # Can be added if resume is stored in session
    )
    
    # Transform batch result into BatchEvaluationResponse format
    question_evaluations = [
        QuestionEvaluation(
            question_id=q_eval["question_id"],
            question=session["asked"][q_eval["question_id"] - 1],
            user_answer=questions_with_answers[q_eval["question_id"] - 1]["user_answer"],
            score=q_eval["score"],
            feedback=q_eval["feedback"],
        )
        for q_eval in batch_result.get("question_evaluations", [])
    ]
    
    return BatchEvaluationResponse(
        session_id=session_id,
        overall_score=batch_result.get("overall_score", 0),
        feedback=batch_result.get("overall_feedback", ""),
        question_evaluations=question_evaluations,
        strengths=batch_result.get("strengths", []),
        weaknesses=batch_result.get("weaknesses", []),
        recommendations=batch_result.get("recommendations", []),
    )


@router.post("/summary_v2/{session_id}", response_model=SummaryResponse)
def generate_batch_summary(session_id: str):
    """
    Generate comprehensive interview summary from batch evaluation.
    Combines all Q&A data with LLM evaluation for detailed insights.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # First, get batch evaluation if not already done
    batch_result = evaluate_batch_feedback(session_id)
    
    # Build comprehensive summary
    summary_text = f"""
Interview Summary:
Role: {session['role']}
Topic: {session['topic']}
Difficulty: {session['difficulty']}
Total Questions: {len(session['asked'])}
Overall Score: {batch_result.overall_score}/100

Feedback: {batch_result.feedback}

Strengths:
- {chr(10).join(f"- {s}" for s in batch_result.strengths)}

Weaknesses:
- {chr(10).join(f"- {w}" for w in batch_result.weaknesses)}

Recommendations:
- {chr(10).join(f"- {r}" for r in batch_result.recommendations)}
""".strip()
    
    # Generate next steps based on scores
    next_steps = []
    if batch_result.overall_score < 50:
        next_steps.append("Focus on fundamental concepts")
    if batch_result.overall_score < 70:
        next_steps.append("Practice with more examples")
    next_steps.append("Review areas of weakness highlighted above")
    next_steps.append("Attempt similar difficulty interview again to track progress")

    # Transform batch result into QuestionEvaluation format for frontend
    question_evaluations = [
        QuestionEvaluation(
            question_id=q_eval.question_id,
            question=session["asked"][q_eval.question_id - 1],
            user_answer=session["student_answers"][q_eval.question_id - 1],
            score=q_eval.score,
            feedback=q_eval.feedback,
        )
        for q_eval in batch_result.question_evaluations
    ]

    return SummaryResponse(
        session_id=session_id,
        role=session["role"],
        topic=session["topic"],
        difficulty=session["difficulty"],
        summary=summary_text,
        overall_score=batch_result.overall_score,
        strengths=batch_result.strengths,
        weaknesses=batch_result.weaknesses,
        recommendations=batch_result.recommendations,
        next_steps=next_steps,
        question_evaluations=question_evaluations,
    )
