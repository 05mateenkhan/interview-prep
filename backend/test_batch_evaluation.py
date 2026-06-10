"""
Test suite for batch evaluation endpoints (Phase 5).
Tests for feedback_v2 and summary_v2 endpoints.
"""
import pytest
import json
import uuid
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from routers.interview import sessions
from services.langchain_service import evaluate_batch_answers


client = TestClient(app)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_session_id():
    """Create a sample session with Q&A data."""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "max_questions": 3,
        "role": "Data Scientist",
        "topic": "Statistics",
        "difficulty": "Medium",
        "asked": [
            "What is the difference between correlation and causation?",
            "Explain the central limit theorem.",
            "What is a p-value and how do you interpret it?"
        ],
        "reference_answers": [
            "Correlation shows relationship, causation shows cause-effect.",
            "The CLT states that the distribution of sample means approaches normal.",
            "P-value is the probability of observing data given null hypothesis is true."
        ],
        "student_answers": [
            "Correlation is when two things move together, causation is when one causes the other.",
            "When you take many samples, their means form a normal distribution.",
            "It's the probability that our result happened by chance."
        ],
        "scores": [85, 78, 82],
        "current_question_number": 3,
        "ideal_answer": [
            "Correlation: statistical relationship. Causation: X causes Y.",
            "Distribution of sample means approaches normal distribution regardless of original distribution.",
            "Probability of observing test statistic at least as extreme under null hypothesis."
        ],
        "feedback": [
            "Good basic understanding, but missing formal definition.",
            "Correct intuition, could add mathematical formulation.",
            "Good practical explanation, needs more statistical rigor."
        ],
    }
    return session_id


@pytest.fixture
def invalid_session_id():
    """Return a non-existent session ID."""
    return str(uuid.uuid4())


# ── Test: Batch Evaluation Endpoint ───────────────────────────────────────────

@patch('routers.interview.evaluate_batch_answers')
def test_feedback_v2_endpoint_success(mock_batch_eval, sample_session_id):
    """Test feedback_v2 endpoint with valid session."""
    # Mock the batch evaluation response
    mock_batch_eval.return_value = {
        "overall_score": 81.67,
        "overall_feedback": "Strong fundamentals with room for mathematical depth.",
        "question_evaluations": [
            {"question_id": 1, "score": 85, "feedback": "Good understanding of distinction."},
            {"question_id": 2, "score": 78, "feedback": "Correct concept, needs formalization."},
            {"question_id": 3, "score": 82, "feedback": "Practical but needs theory."}
        ],
        "strengths": [
            "Clear communication",
            "Practical examples",
            "Logical reasoning"
        ],
        "weaknesses": [
            "Lacks mathematical formulation",
            "Missing edge cases",
            "Could cite research"
        ],
        "recommendations": [
            "Study more statistical theory",
            "Review mathematical notation",
            "Practice with research papers"
        ]
    }
    
    # Call endpoint
    response = client.post(f"/interview/feedback_v2/{sample_session_id}")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == sample_session_id
    assert data["overall_score"] == 81.67
    assert data["feedback"] == "Strong fundamentals with room for mathematical depth."
    assert len(data["question_evaluations"]) == 3
    assert len(data["strengths"]) == 3
    assert len(data["weaknesses"]) == 3
    assert len(data["recommendations"]) == 3


def test_feedback_v2_endpoint_invalid_session(invalid_session_id):
    """Test feedback_v2 endpoint with invalid session ID."""
    response = client.post(f"/interview/feedback_v2/{invalid_session_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert "Session not found" in data["detail"]


@patch('routers.interview.evaluate_batch_answers')
def test_summary_v2_endpoint_success(mock_batch_eval, sample_session_id):
    """Test summary_v2 endpoint with valid session."""
    # Mock the batch evaluation response
    mock_batch_eval.return_value = {
        "overall_score": 81.67,
        "overall_feedback": "Strong fundamentals with room for mathematical depth.",
        "question_evaluations": [
            {"question_id": 1, "score": 85, "feedback": "Good understanding."},
            {"question_id": 2, "score": 78, "feedback": "Correct concept."},
            {"question_id": 3, "score": 82, "feedback": "Practical approach."}
        ],
        "strengths": ["Clear communication", "Practical examples", "Logical reasoning"],
        "weaknesses": ["Lacks mathematical formulation", "Missing edge cases", "Could cite research"],
        "recommendations": ["Study more statistical theory", "Review mathematical notation", "Practice with research papers"]
    }
    
    # Call endpoint
    response = client.post(f"/interview/summary_v2/{sample_session_id}")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == sample_session_id
    assert data["overall_score"] == 81.67
    assert "Interview Summary:" in data["summary"]
    assert "Data Scientist" in data["summary"]
    assert "Statistics" in data["summary"]
    assert len(data["strengths"]) == 3
    assert len(data["weaknesses"]) == 3
    assert len(data["recommendations"]) == 3
    assert len(data["next_steps"]) > 0


def test_summary_v2_endpoint_invalid_session(invalid_session_id):
    """Test summary_v2 endpoint with invalid session ID."""
    response = client.post(f"/interview/summary_v2/{invalid_session_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert "Session not found" in data["detail"]


# ── Test: Batch Evaluation Service ────────────────────────────────────────────

@patch('services.langchain_service.batch_evaluation_chain')
def test_evaluate_batch_answers_success(mock_chain):
    """Test evaluate_batch_answers function with mock LLM."""
    # Mock LLM response
    mock_response = json.dumps({
        "overall_score": 85.0,
        "overall_feedback": "Excellent performance across all topics.",
        "question_evaluations": [
            {"question_id": 1, "score": 85.5, "feedback": "Very good answer."},
            {"question_id": 2, "score": 84.2, "feedback": "Good understanding."}
        ],
        "strengths": ["Clarity", "Logic", "Examples"],
        "weaknesses": ["Formalism", "Edge cases"],
        "recommendations": ["More practice", "Study theory"]
    })
    mock_chain.invoke.return_value = mock_response
    
    # Test data
    questions_with_answers = [
        {"question_id": 1, "question": "Q1?", "user_answer": "A1"},
        {"question_id": 2, "question": "Q2?", "user_answer": "A2"}
    ]
    
    # Call function
    result = evaluate_batch_answers(
        questions_with_answers=questions_with_answers,
        role="Data Scientist",
        topic="Statistics",
        difficulty="Medium",
        resume_text="Resume content"
    )
    
    # Assertions
    assert result["overall_score"] == 85  # Should be rounded to int
    assert result["overall_feedback"] == "Excellent performance across all topics."
    assert len(result["question_evaluations"]) == 2
    assert result["question_evaluations"][0]["score"] == 86  # 85.5 rounded
    assert result["question_evaluations"][1]["score"] == 84  # 84.2 rounded
    assert len(result["strengths"]) == 3
    assert len(result["weaknesses"]) == 2
    assert len(result["recommendations"]) == 2


@patch('services.langchain_service.batch_evaluation_chain')
def test_evaluate_batch_answers_malformed_json(mock_chain):
    """Test evaluate_batch_answers with malformed JSON response."""
    # Mock malformed JSON response
    mock_chain.invoke.return_value = "Not valid JSON"
    
    questions_with_answers = [
        {"question_id": 1, "question": "Q1?", "user_answer": "A1"}
    ]
    
    # Should raise JSONDecodeError
    with pytest.raises(json.JSONDecodeError):
        evaluate_batch_answers(
            questions_with_answers=questions_with_answers,
            role="Data Scientist",
            topic="Statistics",
            difficulty="Medium"
        )


@patch('services.langchain_service.batch_evaluation_chain')
def test_evaluate_batch_answers_markdown_removal(mock_chain):
    """Test that markdown code fences are properly removed."""
    # Mock response with markdown code fences
    mock_response = """```json
{
  "overall_score": 90.0,
  "overall_feedback": "Great job!",
  "question_evaluations": [],
  "strengths": [],
  "weaknesses": [],
  "recommendations": []
}
```"""
    mock_chain.invoke.return_value = mock_response
    
    questions_with_answers = [
        {"question_id": 1, "question": "Q1?", "user_answer": "A1"}
    ]
    
    # Call function
    result = evaluate_batch_answers(
        questions_with_answers=questions_with_answers,
        role="Test",
        topic="Test",
        difficulty="Easy"
    )
    
    # Assertions - should successfully parse despite markdown
    assert result["overall_score"] == 90
    assert result["overall_feedback"] == "Great job!"


# ── Test: Data Models ─────────────────────────────────────────────────────────

def test_batch_evaluation_response_model():
    """Test BatchEvaluationResponse Pydantic model."""
    from models.schemas import BatchEvaluationResponse, QuestionEvaluation
    
    response = BatchEvaluationResponse(
        session_id="test-session-123",
        overall_score=85.5,
        feedback="Good performance",
        question_evaluations=[
            QuestionEvaluation(
                question_id=1,
                question="What is X?",
                user_answer="X is...",
                score=85,
                feedback="Good"
            )
        ],
        strengths=["Clarity"],
        weaknesses=["Depth"],
        recommendations=["Study more"]
    )
    
    assert response.session_id == "test-session-123"
    assert response.overall_score == 85.5
    assert response.feedback == "Good performance"
    assert len(response.question_evaluations) == 1
    assert response.question_evaluations[0].question_id == 1


def test_summary_response_model():
    """Test SummaryResponse Pydantic model."""
    from models.schemas import SummaryResponse
    
    response = SummaryResponse(
        session_id="test-session-456",
        summary="Interview summary text",
        overall_score=88.0,
        strengths=["A", "B"],
        weaknesses=["C"],
        recommendations=["D"],
        next_steps=["Step 1", "Step 2"]
    )
    
    assert response.session_id == "test-session-456"
    assert response.overall_score == 88.0
    assert len(response.next_steps) == 2


# ── Integration Tests ─────────────────────────────────────────────────────────

@patch('services.langchain_service.evaluate_batch_answers')
def test_end_to_end_interview_flow(mock_batch_eval, sample_session_id):
    """End-to-end test: create session → answer questions → batch evaluate → summary."""
    # Mock batch evaluation
    mock_batch_eval.return_value = {
        "overall_score": 82.0,
        "overall_feedback": "Good overall performance.",
        "question_evaluations": [
            {"question_id": 1, "score": 85, "feedback": "Q1 feedback"},
            {"question_id": 2, "score": 80, "feedback": "Q2 feedback"},
            {"question_id": 3, "score": 81, "feedback": "Q3 feedback"}
        ],
        "strengths": ["Communication", "Logic"],
        "weaknesses": ["Theory", "Formalism"],
        "recommendations": ["Study", "Practice"]
    }
    
    # Step 1: Verify session exists
    assert sample_session_id in sessions
    
    # Step 2: Call feedback_v2 endpoint
    feedback_response = client.post(f"/interview/feedback_v2/{sample_session_id}")
    assert feedback_response.status_code == 200
    feedback_data = feedback_response.json()
    assert feedback_data["overall_score"] == 82.0
    
    # Step 3: Call summary_v2 endpoint
    summary_response = client.post(f"/interview/summary_v2/{sample_session_id}")
    assert summary_response.status_code == 200
    summary_data = summary_response.json()
    assert summary_data["overall_score"] == 82.0
    assert len(summary_data["next_steps"]) > 0


# ── Test Cleanup ──────────────────────────────────────────────────────────────

def test_session_isolation():
    """Test that different sessions don't interfere with each other."""
    session_id_1 = str(uuid.uuid4())
    session_id_2 = str(uuid.uuid4())
    
    sessions[session_id_1] = {
        "role": "Data Scientist",
        "topic": "Statistics",
        "difficulty": "Medium",
        "asked": ["Q1"],
        "student_answers": ["A1"],
        "reference_answers": ["Ref1"],
        "scores": [80],
        "current_question_number": 1,
        "ideal_answer": ["Ideal1"],
        "feedback": ["Feedback1"],
        "max_questions": 1
    }
    
    sessions[session_id_2] = {
        "role": "Software Engineer",
        "topic": "OOPS",
        "difficulty": "Hard",
        "asked": ["Q2"],
        "student_answers": ["A2"],
        "reference_answers": ["Ref2"],
        "scores": [90],
        "current_question_number": 1,
        "ideal_answer": ["Ideal2"],
        "feedback": ["Feedback2"],
        "max_questions": 1
    }
    
    # Verify isolation
    assert sessions[session_id_1]["role"] == "Data Scientist"
    assert sessions[session_id_2]["role"] == "Software Engineer"
    assert sessions[session_id_1]["scores"] != sessions[session_id_2]["scores"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
