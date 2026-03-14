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

# ── Prompt ───────────────────────────────────────────────────────────────────
RESUME_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert technical recruiter with 10+ years of experience.
Your job is to analyze a candidate's resume and identify their most suitable role
and the technical/non-technical skills they possess.
Be precise, objective, and base your analysis strictly on what is written in the resume."""),

    ("human", """
Analyze the following resume and respond ONLY with a valid JSON object in this exact format:

{{
  "detected_role": "<most suitable job role for this candidate>",
  "confidence": "<High | Medium | Low>",
  "role_reasoning": "<2-3 sentences explaining why this role was detected based on the resume content>",
  "extracted_skills": ["<skill1>", "<skill2>", "<skill3>", "..."]
}}

Rules:
- detected_role must be a specific job title (e.g. "Data Scientist", "Backend Engineer", "ML Engineer")
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

    return json.loads(raw)