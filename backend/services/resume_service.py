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
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)

# ── Available Roles ─────────────────────────────────────────────────────────
AVAILABLE_ROLES = [
    "Data Scientist",
    "Full Stack Engineer",
    "HR / Behavioural",
    "Machine Learning Engineer",
    "Software Engineer",
]

# ── Prompt ───────────────────────────────────────────────────────────────────
RESUME_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert technical recruiter with 10+ years of experience.
Your job is to analyze a candidate's resume and identify their most suitable role
from the available options, and the technical/non-technical skills they possess.
Be precise, objective, and base your analysis strictly on what is written in the resume."""),

    ("human", """
Analyze the following resume and respond ONLY with a valid JSON object in this exact format:

{{
  "detected_role": "<most suitable job role for this candidate>",
  "confidence": "<High | Medium | Low>",
  "role_reasoning": "<2-3 sentences explaining why this role was detected based on the resume content>",
  "extracted_skills": ["<skill1>", "<skill2>", "<skill3>", "..."]
}}

IMPORTANT - Available Roles (choose ONE only):
- Data Scientist
- Full Stack Engineer
- HR / Behavioural
- Machine Learning Engineer
- Software Engineer

Rules:
- detected_role MUST be exactly one of the available roles above
- If the resume doesn't clearly match any role, choose the closest match and set confidence to "Low"
- confidence reflects how clearly the resume points to that role
- extracted_skills should list only skills explicitly mentioned in the resume (tools, languages, frameworks, soft skills)
- Do NOT include markdown, backticks, or any text outside the JSON

Resume:
-----------
{resume_text}
-----------
""")
])

# ── Chain ─────────────────────────────────────────────────────────────────────
analysis_chain = RESUME_ANALYSIS_PROMPT | llm | StrOutputParser()


def analyze_resume(resume_text: str) -> dict:
    """
    Send resume text to Gemini via LangChain and return structured analysis.
    """
    raw = analysis_chain.invoke({"resume_text": resume_text})

    # Strip markdown fences if Gemini adds them
    raw = re.sub(r"^```json|^```|```$", "", raw.strip(), flags=re.MULTILINE).strip()

    result = json.loads(raw)

    # Normalize detected_role to match available roles
    detected = result.get("detected_role", "").strip()
    result["detected_role"] = normalize_role(detected)

    return result


def normalize_role(role: str) -> str:
    """
    Normalize the detected role to match one of the available roles.
    """
    role_lower = role.lower().strip()

    for available_role in AVAILABLE_ROLES:
        if role_lower == available_role.lower():
            return available_role

        # Check for partial matches
        available_lower = available_role.lower()
        if role_lower in available_lower or available_lower in role_lower:
            return available_role

        # Handle special cases
        if "data scientist" in role_lower and "data scientist" in available_lower:
            return "Data Scientist"
        if "full stack" in role_lower and "full stack" in available_lower:
            return "Full Stack Engineer"
        if "hr" in role_lower or "behavioural" in role_lower or "behavioral" in role_lower:
            return "HR / Behavioural"
        if "machine learning" in role_lower or "ml engineer" in role_lower:
            return "Machine Learning Engineer"
        if "software engineer" in role_lower or "software developer" in role_lower:
            return "Software Engineer"

    # Default to Software Engineer if no match
    return "Software Engineer"