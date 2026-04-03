from fastapi import APIRouter, HTTPException
from models.schemas import (
    StartSessionRequest, StartSessionResponse,
    SubmitAnswerRequest, SubmitAnswerResponse, FeedbackScore
)
from services.vector_store import retrieve_question
from services.langchain_service import evaluate_answer, overall_feedback
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
    """Submit answer → evaluate against CSV reference → return feedback + next question."""
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    current_q_index = session["current_question_number"] - 1
    current_question = session["asked"][current_q_index]
    reference_answer = session["reference_answers"][current_q_index]

    # Evaluate using LangChain + Gemini/ Ollama with reference answer as ground truth
    result = evaluate_answer(
        role=session["role"],
        topic=session["topic"],
        difficulty=session["difficulty"],
        question=current_question,
        reference_answer=reference_answer,
        student_answer=req.answer,
    )

    session["student_answers"].append(req.answer)
    session["scores"].append(result["score"]["overall"])
    session["feedback"].append(result["feedback"])
    session["ideal_answer"].append(result["ideal_answer"])
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

    return SubmitAnswerResponse(
        feedback=result["feedback"],
        ideal_answer=result["ideal_answer"],
        missing_concepts=result.get("missing_concepts", []),
        score=FeedbackScore(**result["score"]),
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
