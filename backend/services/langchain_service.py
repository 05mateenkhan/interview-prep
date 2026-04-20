import os
import json
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
import os
load_dotenv()

# ── LLM Setup ────────────────────────────────────────────────────────────────
# Using 3B model for better JSON compliance while still being fast
llm = ChatOllama(model="llama3.2:3b")
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

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

    # Ensure scores are integers (round floats to int)
    if "score" in result:
        for key in result["score"]:
            result["score"][key] = int(round(result["score"][key]))

    return result

def overall_feedback(summary_output : dict) -> dict:
    raw = feedback_chain.invoke({
        "summary_json": json.dumps(summary_output, indent=2)
    })

    # Strip markdown fences if model adds them
    raw = re.sub(r"^```json|^```|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    result = json.loads(raw)

    # Ensure overall_score is an integer
    if "overall_score" in result:
        result["overall_score"] = int(round(result["overall_score"]))

    return result