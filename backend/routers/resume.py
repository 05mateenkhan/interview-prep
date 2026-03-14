from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import ResumeAnalysisResponse
from services.pdf_service import extract_text_from_pdf
from services.resume_service import analyze_resume

router = APIRouter(prefix="/resume", tags=["Resume Analyzer"])

ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_FILE_SIZE_MB = 5


@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    """
    Upload a PDF resume and receive:
    - Detected role
    - Confidence level
    - Role reasoning
    - Extracted skills
    """
    # Validate file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Read and validate file size
    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {MAX_FILE_SIZE_MB}MB.")

    # Extract text from PDF
    try:
        resume_text = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Analyze with LangChain + Gemini
    try:
        result = analyze_resume(resume_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    return ResumeAnalysisResponse(**result)