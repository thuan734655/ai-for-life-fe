from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.job import JobCreate, JobOut, JobSearchRequest
from app.crud.job import create_job, list_jobs, search_jobs_ai
from app.services.pdf_processor import process_resume_pdf

router = APIRouter(prefix="/jobs", tags=["jobs"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=JobOut)
def create(payload: JobCreate, db: Session = Depends(get_db)):
    return create_job(db, payload)

@router.get("", response_model=list[JobOut])
def get_all(db: Session = Depends(get_db)):
    return list_jobs(db)

@router.post("/search", response_model=List[Dict[str, Any]])
async def search_jobs(
    search_request: JobSearchRequest,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Search for jobs using AI-powered matching
    
    - **title**: Job title to search for (optional)
    - **skills**: List of skills to match (optional)
    - **experience**: Years of experience (optional)
    - **location**: Job location (optional)
    """
    try:
        return search_jobs_ai(db, search_request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching for jobs: {str(e)}"
        )

@router.post("/upload-resume", response_model=List[Dict[str, Any]])
async def upload_resume(
    file: UploadFile = File(...),
    desired_position: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """
    Upload a PDF resume and return matching jobs.
    - file: PDF file
    - desired_position: optional
    """
    try:
        matches = process_resume_pdf(
            db=db,
            file=file,
            desired_position=desired_position,
        )
        return matches
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")