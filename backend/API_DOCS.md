# API Reference — Backend

This document lists the backend endpoints available in the `backend` FastAPI service.

Base URL (local dev): `http://localhost:8000`

## Endpoints

- **GET /**
  - Description: Health check
  - Response: `{ "message": "Running..." }`

---

- **Interview: Start session**
  - Method: `POST`
  - Path: `/interview/start`
  - Request JSON (StartSessionRequest):

```json
{
  "role": "Data Scientist",
  "topic": "Statistics",
  "difficulty": "Medium",
  "max_questions": 5
}
```

  - Success response: `StartSessionResponse`

```json
{
  "session_id": "<uuid>",
  "role": "Data Scientist",
  "topic": "Statistics",
  "difficulty": "Medium",
  "question": "First question text...",
  "question_number": 1
}
```

---

- **Interview: Submit answer**
  - Method: `POST`
  - Path: `/interview/submit`
  - Request JSON (SubmitAnswerRequest):

```json
{
  "session_id": "<session_id>",
  "answer": "My answer text..."
}
```

  - Success response: `SubmitAnswerResponse` — contains `feedback`, `ideal_answer`, `missing_concepts`, `score`, `next_question` (or `null`) and `session_complete` flag.

Example response shape:

```json
{
  "feedback": "Good explanation but missing X",
  "ideal_answer": "Concise model answer...",
  "missing_concepts": ["Bias-Variance Tradeoff"],
  "score": {"accuracy": 8, "clarity": 7, "completeness": 6, "overall": 7},
  "next_question": "Next question text...",
  "session_complete": false
}
```

---

- **Interview: Summary**
  - Method: `GET`
  - Path: `/interview/summary/{session_id}`
  - Description: Returns full session summary including all questions, student answers and scores.

---

- **Interview: Options**
  - Method: `GET`
  - Path: `/interview/options`
  - Description: Returns dropdown options used by client (roles, topics, difficulties).

---

- **Interview: Overall feedback**
  - Method: `GET`
  - Path: `/interview/feedback/{session_id}`
  - Description: Returns aggregated feedback for a session (calls `overall_feedback`).

---

- **Resume Analyzer: Upload and analyze**
  - Method: `POST`
  - Path: `/resume/analyze`
  - Content type: `multipart/form-data` with file field `file` (PDF only)
  - Limits: maximum file size ~5 MB, content-type must be `application/pdf`.
  - Response model: `ResumeAnalysisResponse`

Example curl (Linux / macOS):

```bash
curl -X POST "http://localhost:8000/resume/analyze" \
  -F "file=@/path/to/resume.pdf;type=application/pdf"
```

Example response shape:

```json
{
  "detected_role": "Software Engineer",
  "confidence": "High",
  "role_reasoning": "Resume contains experience with API design, distributed systems...",
  "extracted_skills": ["Python", "FastAPI", "Docker"]
}
```

## Models (compact)

- `StartSessionRequest`: `role` (str), `topic` (str), `difficulty` (str), `max_questions` (int)
- `StartSessionResponse`: `session_id`, `role`, `topic`, `difficulty`, `question`, `question_number`
- `SubmitAnswerRequest`: `session_id`, `answer`
- `SubmitAnswerResponse`: `feedback`, `ideal_answer`, `missing_concepts` (list), `score` (accuracy/clarity/completeness/overall), `next_question`, `session_complete`
- `ResumeAnalysisResponse`: `detected_role`, `confidence`, `role_reasoning`, `extracted_skills`

## Notes & troubleshooting

- If the LLM services or FAISS index are not configured, some endpoints may raise errors — check environment variables in `.env`.
- Use the interactive API docs at `http://localhost:8000/docs` to try requests from Swagger UI.
