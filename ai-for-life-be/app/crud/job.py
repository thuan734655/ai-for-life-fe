from typing import Any, Dict, List
from app.ai.gemini_service import match_jobs_with_ai
from app.schemas.job import JobCreate, JobSearchRequest
from app.ai.embedding_service import get_text_embedding, build_jd_text
from app.ai.embedding_service import build_query_text, get_query_embedding
from app.ai.chroma_store import get_jobs_collection
import json
import uuid

def create_job(payload: JobCreate) -> Dict[str, Any]:
    # Generate a string ID for Chroma
    job_id = str(uuid.uuid4())
    job_meta = {
        "job_id": job_id,
        "title": payload.title,
        "company": payload.company,
        "location": payload.location,
        "salary_range": payload.salary_range,
        "description": payload.description,
        "experience_min": payload.experience_min,
        # Store skills as JSON string so Chroma metadata values stay scalar
        "skills": json.dumps(payload.skills or []),
    }

    # Create and store JD embedding using standardized text format
    try:
        jd_text = build_jd_text(
            title=payload.title,
            company=payload.company,
            location=payload.location,
            description=payload.description,
            experience_min=payload.experience_min,
            skills=payload.skills,
        )
        print("JD TEXT:\n", jd_text)

        emb = get_text_embedding(jd_text)
        print("Embedding length:", len(emb))

        if not emb:
            print("WARNING: Embedding is empty, skipping save to ChromaDB.")
        else:
            col = get_jobs_collection()
            col.add(
                ids=[job_id],
                embeddings=[emb],
                metadatas=[job_meta],
                documents=[jd_text],
            )
            print("Saved job to ChromaDB with id:", job_id)
    except Exception as e:
        print("ERROR while saving job to ChromaDB:", repr(e))

    # Return created job metadata
    return {
        "id": job_id,
        **{k: v for k, v in job_meta.items() if k != "job_id"}
    }

def get_job(job_id: str) -> Dict[str, Any] | None:
    try:
        col = get_jobs_collection()
        res = col.get(ids=[str(job_id)], include=["metadatas", "documents"])
        metas = (res.get("metadatas") or [[]])[0]
        if not metas:
            return None
        meta = metas[0] or {}
        # Decode skills JSON string back to list, with safe fallback
        raw_skills = meta.get("skills")
        if isinstance(raw_skills, str):
            try:
                skills_list = json.loads(raw_skills)
            except Exception:
                skills_list = []
        else:
            skills_list = raw_skills or []
        return {
            "id": str(job_id),
            "title": meta.get("title"),
            "company": meta.get("company"),
            "location": meta.get("location"),
            "salary_range": meta.get("salary_range"),
            "description": meta.get("description"),
            "experience_min": meta.get("experience_min"),
            "skills": skills_list,
        }
    except Exception:
        return None

def list_jobs() -> List[Dict[str, Any]]:
    try:
        col = get_jobs_collection()
        res = col.get(include=["ids", "metadatas"], limit=10000)
        ids = res.get("ids") or []
        metas = res.get("metadatas") or []
        out: List[Dict[str, Any]] = []
        for i, m in zip(ids, metas):
            meta = m or {}
            raw_skills = meta.get("skills")
            if isinstance(raw_skills, str):
                try:
                    skills_list = json.loads(raw_skills)
                except Exception:
                    skills_list = []
            else:
                skills_list = raw_skills or []
            out.append({
                "id": i,
                "title": meta.get("title"),
                "company": meta.get("company"),
                "location": meta.get("location"),
                "salary_range": meta.get("salary_range"),
                "description": meta.get("description"),
                "experience_min": meta.get("experience_min"),
                "skills": skills_list,
            })
        return out
    except Exception:
        return []
def search_jobs_ai(search_request: JobSearchRequest) -> List[Dict[str, Any]]:
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
    candidates = top_k_jobs_by_embedding(query_emb, k=10)
    print("candidates",candidates)
    # No fallback to SQL: results come only from Chroma

    # Stage 2: Re-rank with AI matcher
    search_criteria = {
        'title': search_request.title,
        'skills': search_request.skills,
        'experience': search_request.experience,
        'location': search_request.location,
    }
    matched_jobs = match_jobs_with_ai(search_criteria, candidates)
    print("matched_jobs",matched_jobs)
    # Only keep jobs with at least 30% match score
    matched_jobs = [job for job in matched_jobs if job.get('match_score', 0) >= 0.3]
    print("matched_jobs",matched_jobs)  
    return matched_jobs

def top_k_jobs_by_embedding(query_embedding: List[float], k: int = 20) -> List[Dict[str, Any]]:
    """Return top-k jobs most similar to the query embedding by cosine similarity."""
    if not query_embedding:
        return []
    # Query Chroma for nearest neighbors
    try:
        col = get_jobs_collection()
        q = col.query(
            query_embeddings=[query_embedding],
            n_results=k,
            # ids are always returned; include controls optional arrays like distances, metadatas, documents
            include=["distances", "metadatas", "documents"],
        )
        ids = (q.get("ids") or [[]])[0]
        distances = (q.get("distances") or [[]])[0]
        metadatas = (q.get("metadatas") or [[]])[0]
        # Build results only from Chroma, preserving order
        results: List[Dict[str, Any]] = []
        for i, d, meta in zip(ids, distances, metadatas):
            # Convert cosine distance to similarity: sim = 1 - distance
            sim = 1.0 - float(d) if d is not None else 0.0
            raw_skills = (meta or {}).get('skills')
            if isinstance(raw_skills, str):
                try:
                    skills_list = json.loads(raw_skills)
                except Exception:
                    skills_list = []
            else:
                skills_list = raw_skills or []
            results.append({
                'id': i,
                'title': (meta or {}).get('title'),
                'company': (meta or {}).get('company'),
                'location': (meta or {}).get('location'),
                'salary_range': (meta or {}).get('salary_range'),
                'description': (meta or {}).get('description'),
                'experience_min': (meta or {}).get('experience_min'),
                'skills': skills_list,
                'embedding_similarity': round(float(sim), 4),
            })
        return results
    except Exception as e:
        print("ERROR during top_k_jobs_by_embedding:", repr(e))
        return []