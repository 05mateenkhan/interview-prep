from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.interview import router as interview_router
from routers.resume import router as resume_router
from routers.voice import router as voice_router
from services.vector_store import get_vector_store
from services.transcription_service import get_whisper_model

app = FastAPI(title="PrepIQ - Interview Engine", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview_router)
app.include_router(resume_router)
app.include_router(voice_router)

@app.on_event("startup")
async def startup():
    """Pre-build FAISS index on startup so first request isn't slow."""
    get_vector_store()
    get_whisper_model()

@app.get("/")
def root():
    return {"message": "Running..."}