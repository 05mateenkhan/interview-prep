from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.interview import router as interview_router
from routers.resume import router as resume_router
from services.vector_store import get_vector_store

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

@app.on_event("startup")
async def startup():
    """Pre-build FAISS index on startup so first request isn't slow."""
    get_vector_store()

@app.get("/")
def root():
    return {"message": "Running..."}