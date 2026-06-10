import os
import json
import re
from dotenv import load_dotenv
from typing import Optional
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openrouter import ChatOpenRouter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
import os
load_dotenv()

# ── Helper: Convert word numbers to integers ───────────────────────────────────
WORD_TO_NUM = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "hundred": 100,
}

def parse_number(value) -> int:
    """Convert a numeric or word-based number to an integer."""
    if isinstance(value, (int, float)):
        return int(round(value))
    if isinstance(value, str):
        value = value.lower().strip()
        # Try direct number conversion first
        try:
            return int(value)
        except ValueError:
            pass
        # Try word to number conversion
        if value in WORD_TO_NUM:
            return WORD_TO_NUM[value]
        # Try extracting number from string like "thirty" or "45%"
        match = re.search(r'(\d+)', value)
        if match:
            return int(match.group(1))
    return 0

# ── LLM Setup ────────────────────────────────────────────────────────────────
# Using 3B model for better JSON compliance while still being fast
# llm = ChatOllama(model="llama3.2:3b")

# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

llm = ChatOpenRouter(model="openai/gpt-oss-120b:free")

# ── Prompt Template ──────────────────────────────────────────────────────────
EVALUATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a technical interviewer. Evaluate the answer against the reference. Respond JSON only."),

    ("human", """
Role: {role}, Topic: {topic}, Difficulty: {difficulty}
Q: {question}
Reference: {reference_answer}
Answer: {student_answer}

JSON: {{"feedback": "short feedback", "ideal_answer": "simplified answer", "missing_concepts": ["concept"], "score": {{"accuracy": 0-10, "clarity": 0-10, "completeness": 0-10, "overall": 0-10}}}}
""")
])

FEEDBACK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a technical interviewer. Provide overall feedback. Respond JSON only."),

    ("human", """
Summary: {summary_json}

JSON: {{"overall_feedback": "summary", "areas_to_improve": ["area"], "overall_score": 0-10}}
""")
])

# ── Batch Evaluation Prompt ──────────────────────────────────────────────────
BATCH_EVALUATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a senior technical interviewer. Evaluate all answers comprehensively in one batch. Respond with valid JSON only. No markdown code fences."),

    ("human", """
Interview Details:
Role: {role}
Topic: {topic}
Difficulty: {difficulty}
Resume: {resume_text}

Questions and Answers:
{questions_and_answers}

Provide a comprehensive JSON evaluation with:
1. Overall score (0-100)
2. Per-question scores and feedback
3. Top 3 strengths
4. Top 3 weaknesses
5. Top 3 recommendations

JSON FORMAT (IMPORTANT - no markdown fences, valid JSON only):
{{
  "overall_score": <0-100>,
  "overall_feedback": "comprehensive summary",
  "question_evaluations": [
    {{
      "question_id": <int>,
      "score": <0-100>,
      "feedback": "specific feedback"
    }}
  ],
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2", "weakness3"],
  "recommendations": ["rec1", "rec2", "rec3"]
}}
""")
])

batch_evaluation_chain = BATCH_EVALUATION_PROMPT | llm | StrOutputParser()

# ── Chain ─────────────────────────────────────────────────────────────────────
evaluation_chain = EVALUATION_PROMPT | llm | StrOutputParser()
feedback_chain = FEEDBACK_PROMPT | llm | StrOutputParser()

def evaluate_answer(
    role: str,
    topic: str,
    difficulty: str,
    question: str,
    reference_answer: str,
    student_answer: str,
) -> dict:

    raw = evaluation_chain.invoke({
        "role": role,
        "topic": topic,
        "difficulty": difficulty,
        "question": question,
        "reference_answer": reference_answer,
        "student_answer": student_answer,
    })

    # Strip markdown fences if Gemini adds them
    raw = re.sub(r"^```json|^```|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    result = json.loads(raw)

    # Ensure scores are integers (handle word numbers like "thirty" -> 30)
    if "score" in result:
        for key in result["score"]:
            result["score"][key] = parse_number(result["score"][key])

    return result

def overall_feedback(summary_output : dict) -> dict:
    raw = feedback_chain.invoke({
        "summary_json": json.dumps(summary_output, indent=2)
    })

    # Strip markdown fences if model adds them
    raw = re.sub(r"^```json|^```|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    result = json.loads(raw)

    # Ensure overall_score is an integer (handle word numbers like "thirty" -> 30)
    if "overall_score" in result:
        result["overall_score"] = parse_number(result["overall_score"])

    return result


def evaluate_batch_answers(
    questions_with_answers: list[dict],
    role: str,
    topic: str,
    difficulty: str,
    resume_text: Optional[str] = None,
) -> dict:
    """
    Evaluate all interview questions and answers in one batch LLM call.
    
    Args:
        questions_with_answers: List of dicts with keys: question_id, question, user_answer
        role: Interview role (e.g., "Data Scientist")
        topic: Interview topic (e.g., "Statistics")
        difficulty: Difficulty level (e.g., "Medium")
        resume_text: Optional resume content for context
    
    Returns:
        Dictionary with batch evaluation results
    """
    # Format Q&A pairs for the prompt
    qa_text = "\n".join([
        f"Q{item['question_id']}: {item['question']}\nAnswer: {item['user_answer']}"
        for item in questions_with_answers
    ])
    
    resume_context = resume_text if resume_text else "No resume provided"
    
    # Call the LLM with batch prompt
    raw = batch_evaluation_chain.invoke({
        "role": role,
        "topic": topic,
        "difficulty": difficulty,
        "resume_text": resume_context,
        "questions_and_answers": qa_text,
    })
    
    # Clean response - remove markdown fences
    raw = re.sub(r"^```json|^```|```$", "", raw.strip(), flags=re.MULTILINE).strip()

    # Pre-process: fix common LLM JSON issues (unquoted strings like "thirty" -> 30)
    # Only target score-related keys: "overall_score": thirty -> "overall_score": 30
    raw = re.sub(r'"(overall_score|score)"\s*:\s*([a-zA-Z]+)', lambda m: f'"{m.group(1)}": {parse_number(m.group(2))}', raw)

    # Parse JSON
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Raw response: {raw}")
        raise
    
    # Ensure scores are integers (handle word numbers like "thirty" -> 30)
    if "overall_score" in result:
        result["overall_score"] = parse_number(result["overall_score"])

    if "question_evaluations" in result:
        for q_eval in result["question_evaluations"]:
            if "score" in q_eval:
                q_eval["score"] = parse_number(q_eval["score"])
    
    return result