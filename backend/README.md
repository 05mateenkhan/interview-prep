# Backend — (Interview Engine)

This folder contains the FastAPI backend that powers the PrepIQ interview and resume analysis services.

## Requirements
- Python 3.10+ recommended
- A virtual environment (venv)
- Any LLM / vector-store API keys required by services (place in `.env`)
- Currently add your GEMINI_API_KEY in .env

## Quick setup (Windows)

1. Open a terminal and change into the backend folder:

```powershell
cd backend
```

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # PowerShell
# or .\.venv\Scripts\activate  # cmd
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Provide environment variables:

- There is an `.env` in the folder (if present). Add any LLM keys(GEMINI_API_KEY), third-party endpoints or other secrets required by `services/*`.

5. Run the development server:

```powershell
uvicorn main:app --reload --port 8000
```

The app exposes a health root at `/` and documentation at `/docs` (Swagger UI).

Notes:
- On startup the app pre-builds the FAISS vector store (see `services/vector_store.py`) — the first startup may take a few seconds.
 
## Voice-Based Answer Submission (Audio)

This backend now supports voice-based answer submission using a local OpenAI Whisper model. The voice endpoint mirrors the textual `/submit` flow but accepts an audio file and returns both the transcription and the same evaluation feedback you get from text submissions.

- **Endpoint:** `POST /submit-audio-answer`
- **Description:** Upload a short audio answer for the current session. The server transcribes audio → text using a local Whisper model, evaluates the transcribed text with the existing LangChain evaluation pipeline, updates the session state, and returns transcription + evaluation.

- **Request:** multipart/form-data with:
	- `file` (file) — audio file. Supported MIME types: `audio/wav`, `audio/x-wav`, `audio/mpeg`, `audio/mp3`, `audio/mp4`, `audio/webm`, `audio/ogg`.
	- `session_id` (string) — active session ID obtained from `/interview/start`.

- **Limits & validation:**
	- Max file size: **25 MB** (enforced).
	- Max duration: **120 seconds** (2 minutes) per answer (enforced by the transcription service).
	- Common errors: `404` (session not found), `413` (file too large), `422` (invalid/unsupported audio or too short/long), `500` (transcription or evaluation failure).

- **Response:** Same shape as text submit responses plus transcription fields. Example keys:
	- `transcribed_text` — the transcribed audio string
	- `audio_duration_seconds` — duration in seconds
	- `transcription_confidence` — `high`/`medium`/`low`
	- `feedback`, `ideal_answer`, `missing_concepts`, `score`, `next_question`, `session_complete` (same as `/submit`)

- **Example curl**

```bash
curl -X POST "http://localhost:8000/submit-audio-answer" \
	-H "accept: application/json" \
	-H "Content-Type: multipart/form-data" \
	-F "session_id=YOUR_SESSION_ID" \
	-F "file=@./answer.wav;type=audio/wav"
```

- **Implementation notes:**
	- The transcription logic lives in `services/transcription_service.py` and uses OpenAI Whisper locally. The model is lazy-loaded; on startup `main.py` preloads it via `get_whisper_model()` so the first request is faster.
	- To change model size (faster/slower, tradeoff accuracy), edit the `_MODEL_SIZE` constant in `services/transcription_service.py` (e.g., `base`, `small`, `medium`).
	- The evaluation path reuses the existing LangChain evaluation flow via `services/evaluation_service.py`.

See the API reference for endpoints and example requests: [backend/API_DOCS.md](backend/API_DOCS.md)
