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

See the API reference for endpoints and example requests: [backend/API_DOCS.md](backend/API_DOCS.md)
