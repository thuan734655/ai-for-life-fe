from typing import Any, Dict, List
from sqlalchemy.orm import Session, joinedload
from app.ai.gemini_service import match_jobs_with_ai
from app.models.job import Job
from app.models.skill import JobSkill
from app.schemas.job import JobCreate, JobSearchRequest
from app.crud.skill import get_or_create_skill

def create_job(db: Session, payload: JobCreate) -> Job:
    job = Job(
        title=payload.title,
        company=payload.company,
        location=payload.location,
        salary_range=payload.salary_range,
        description=payload.description,
        experience_min=payload.experience_min,
    )
    db.add(job)
    db.flush()

    for s in payload.skills:
        skill = get_or_create_skill(db, s.name)
        db.add(JobSkill(job_id=job.id, skill_id=skill.id, weight=s.weight))

    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id: int) -> Job | None:
    return db.query(Job).options(
        joinedload(Job.skills).joinedload(JobSkill.skill)
    ).filter(Job.id == job_id).first()

def list_jobs(db: Session) -> list[Job]:
    return db.query(Job).all()
def search_jobs_ai(db: Session, search_request: JobSearchRequest) -> List[Dict[str, Any]]:
    """
    Search for jobs using AI-powered matching
    """
    # First, get all jobs with their skills
    jobs = db.query(Job).options(
        joinedload(Job.skills).joinedload(JobSkill.skill)
    ).all()
    
    # Convert SQLAlchemy objects to dictionaries
    job_dicts = []
    for job in jobs:
        job_dict = {
            'id': job.id,
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'salary_range': job.salary_range,
            'description': job.description,
            'experience_min': job.experience_min,
            'skills': [{'id': js.skill.id, 'name': js.skill.name} for js in job.skills]
        }
        job_dicts.append(job_dict)
    
    # Prepare search request for AI
    search_criteria = {
        'title': search_request.title,
        'skills': search_request.skills,
        'experience': search_request.experience,
        'location': search_request.location
    }
    
    # Get AI-matched jobs with scores
    matched_jobs = match_jobs_with_ai(search_criteria, job_dicts)
    
    # Filter out low-scoring jobs (optional)
    matched_jobs = [job for job in matched_jobs if job.get('match_score', 0) > 0.3]
    
    return matched_jobs