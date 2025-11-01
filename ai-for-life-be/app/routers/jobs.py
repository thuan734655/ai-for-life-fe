from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.job import JobCreate, JobOut
from app.crud.job import create_job, list_jobs

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
