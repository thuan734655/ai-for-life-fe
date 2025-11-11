from typing import Any, Dict, List
from sqlalchemy.orm import Session, joinedload
from app.ai.gemini_service import match_jobs_with_ai
from app.models.job import Job
from app.models.skill import JobSkill
from app.schemas.job import JobCreate, JobSearchRequest
from app.crud.skill import get_or_create_skill
from app.models.embedding import JobEmbedding
from app.ai.embedding_service import get_text_embedding, cosine_similarity, build_jd_text
from app.ai.embedding_service import build_query_text, get_query_embedding
import json

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

    # Create and store JD embedding using standardized text format
    try:
        jd_text = build_jd_text(
            title=payload.title,
            company=payload.company,
            location=payload.location,
            description=payload.description,
            experience_min=payload.experience_min,
            skills=[s.name for s in payload.skills],
        )
        emb = get_text_embedding(jd_text)
        if emb:
            db.add(JobEmbedding(job_id=job.id, embedding=json.dumps(emb)))
    except Exception:
        # Fail soft on embedding generation
        pass

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
    print("search_request",search_request)
    # Build query text and embed it (prefer manual free-text query if provided)
    if (getattr(search_request, 'query', None) or "").strip():
        query_text = (search_request.query or "").strip()
    else:
        query_text = build_query_text(
            title=search_request.title,
            skills=search_request.skills or [],
            experience=search_request.experience,
            location=search_request.location,
        )
    
    print("query_text",query_text)
    query_emb = get_query_embedding(query_text)
    print("query_emb",len(query_emb))
    # Stage 1: retrieve top-10 by embedding similarity
    candidates = top_k_jobs_by_embedding(db, query_emb, k=10)
    print("candidates",candidates)
    # Fallback: if no embeddings yet, retrieve all jobs as candidates
    if not candidates:
        jobs = db.query(Job).options(
            joinedload(Job.skills).joinedload(JobSkill.skill)
        ).all()
        candidates = [{
            'id': j.id,
            'title': j.title,
            'company': j.company,
            'location': j.location,
            'salary_range': j.salary_range,
            'description': j.description,
            'experience_min': j.experience_min,
            'skills': [{'id': js.skill.id, 'name': js.skill.name} for js in j.skills],
        } for j in jobs]

    # Stage 2: Re-rank with AI matcher
    search_criteria = {
        'title': search_request.title,
        'skills': search_request.skills,
        'experience': search_request.experience,
        'location': search_request.location,
    }
    matched_jobs = match_jobs_with_ai(search_criteria, candidates)
    print("matched_jobs",matched_jobs)
    matched_jobs = [job for job in matched_jobs if job.get('match_score', 0) >= 0.0]
    print("matched_jobs",matched_jobs)  
    return matched_jobs

def top_k_jobs_by_embedding(db: Session, query_embedding: List[float], k: int = 20) -> List[Dict[str, Any]]:
    """Return top-k jobs most similar to the query embedding by cosine similarity."""
    if not query_embedding:
        return []
    # Load all job embeddings and related jobs/skills
    jobs = db.query(Job).options(
        joinedload(Job.skills).joinedload(JobSkill.skill)
    ).all()
    # Map job_id -> job for quick lookup
    job_map = {j.id: j for j in jobs}
    # Retrieve embeddings
    rows = db.query(JobEmbedding).all()
    scored: List[tuple[float, Job]] = []
    for row in rows:
        try:
            emb = json.loads(row.embedding)
            sim = cosine_similarity(query_embedding, emb)
            job = job_map.get(row.job_id)
            if job is not None:
                scored.append((sim, job))
        except Exception:
            continue
    # Sort by similarity desc and take top-k
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:k]
    # Convert to dicts
    results: List[Dict[str, Any]] = []
    for sim, job in top:
        results.append({
            'id': job.id,
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'salary_range': job.salary_range,
            'description': job.description,
            'experience_min': job.experience_min,
            'skills': [{'id': js.skill.id, 'name': js.skill.name} for js in job.skills],
            'embedding_similarity': round(float(sim), 4),
        })
    return results