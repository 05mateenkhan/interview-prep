import os
import json
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
load_dotenv()

# ── LLM Setup ────────────────────────────────────────────────────────────────
llm = ChatOllama(model="llama3.2")
llm2 = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3,
)

# ── Prompt Template ──────────────────────────────────────────────────────────
EVALUATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert technical interviewer evaluating a student's answer.
You have access to a reference answer from a curated question bank.
Use the reference answer as the ground truth to evaluate the student.
Be honest, constructive, and encouraging."""),

    ("human", """
Domain/Role: {role}
Topic: {topic}
Difficulty: {difficulty}

Interview Question:
{question}

Reference Answer (Ground Truth):
{reference_answer}

Student's Answer:
{student_answer}

Evaluate the student's answer against the reference and respond ONLY with a valid JSON object:
{{
  "feedback": "2-3 sentences: what the student got right, what was missing compared to the reference",
  "ideal_answer": "A polished version of the reference answer in simple language",
  "missing_concepts": ["concept1", "concept2"],
  "score": {{
    "accuracy": <integer 0-10>,
    "clarity": <integer 0-10>,
    "completeness": <integer 0-10>,
    "overall": <integer 0-10>
  }}
}}

Do not include markdown, backticks, or any text outside the JSON.
""")
])

FEEDBACK_PROMPT = ChatPromptTemplate.from_messages([

    ("system", """You are an expert technical interviewer analyzing the overall performance
of a candidate after a mock interview.

Review the interview summary and provide constructive evaluation."""),

    ("human", """
Interview Summary:
{summary_json}

Analyze the interview and generate:

1. overall_feedback → Summary of the candidate's performance
2. areas_to_improve → Key areas the candidate should improve
3. overall_score → Final score out of 10

Respond ONLY with JSON in this format:

{{
  "overall_feedback": "2-3 sentence summary of the performance",
  "areas_to_improve": ["area1", "area2", "area3"],
  "overall_score": 0
}}

Do not include markdown or any text outside the JSON.
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
    return json.loads(raw)

def overall_feedback(summary_output : dict) -> dict:
    raw = feedback_chain.invoke({
        "summary_json": json.dumps(summary_output, indent=2)
    })

    # Strip markdown fences if model adds them
    raw = re.sub(r"^```json|^```|```$", "", raw.strip(), flags=re.MULTILINE).strip()

    return json.loads(raw)