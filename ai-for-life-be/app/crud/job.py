from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.skill import JobSkill
from app.schemas.job import JobCreate
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


def list_jobs(db: Session) -> list[Job]:
    return db.query(Job).all()
