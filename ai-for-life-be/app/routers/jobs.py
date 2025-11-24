from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.schemas.job import JobCreate, JobSearchRequest
from app.crud.job import create_job, list_jobs, search_jobs_ai
from app.services.pdf_processor import process_resume_pdf

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=Dict[str, Any])
def create(payload: JobCreate):
    print("payload",payload)
    return create_job(payload)

@router.get("", response_model=List[Dict[str, Any]])
def get_all():
    return list_jobs()

@router.post("/search", response_model=List[Dict[str, Any]])
async def search_jobs(
    search_request: JobSearchRequest,
) -> List[Dict[str, Any]]:
    """
    Search for jobs using AI-powered matching
    
    - **title**: Job title to search for (optional)
    - **skills**: List of skills to match (optional)
    - **experience**: Years of experience (optional)
    - **location**: Job location (optional)
    """
    try:
        return search_jobs_ai(search_request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching for jobs: {str(e)}"
        )

@router.post("/upload-resume", response_model=List[Dict[str, Any]])
async def upload_resume(
    file: UploadFile = File(...),
    desired_position: str | None = Form(None),
):
    """
    Upload a PDF resume and return matching jobs.
    - file: PDF file
    - desired_position: optional
    """
    try:
        matches = process_resume_pdf(
            file=file,
            desired_position=desired_position,
        )
        return matches
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")