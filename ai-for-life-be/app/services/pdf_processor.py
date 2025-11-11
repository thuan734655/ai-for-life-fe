import re
from typing import Dict, List, Optional, Any

import fitz  # PyMuPDF
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.schemas.job import JobSearchRequest
from app.crud.job import search_jobs_ai, top_k_jobs_by_embedding
from app.ai.gemini_service import extract_text_from_pdf_ai_bytes, extract_resume_info_ai, match_jobs_with_ai
from app.ai.embedding_service import get_query_embedding

try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        nlp = None
except Exception:
    nlp = None


def extract_text_from_pdf(file: UploadFile) -> str:
    # Read once
    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty PDF file")

    # Try AI extraction first
    try:
        ai_text = extract_text_from_pdf_ai_bytes(content)
        if ai_text and len(ai_text.strip()) >= 10:
            return ai_text.strip()
    except Exception:
        pass

    # Fallback to local extraction
    try:
        with fitz.open(stream=content, filetype="pdf") as doc:
            text = "".join(page.get_text() for page in doc)
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")


def extract_skills(text: str) -> List[str]:
    common = [
        'python','java','javascript','typescript','c++','c#','ruby','php','go','rust',
        'django','flask','fastapi','spring','react','angular','vue','node','express',
        'sql','postgresql','mysql','mongodb','redis','aws','gcp','azure','docker','kubernetes',
        'git','jenkins','ci/cd','rest','graphql','microservices'
    ]
    text_lower = text.lower()
    matched = [s for s in common if s in text_lower]

    # light NER if spaCy available
    if nlp is not None:
        try:
            doc = nlp(text)
            candidates = [ent.text.lower() for ent in doc.ents if ent.label_ not in {''}]
            matched = list(set(matched + candidates))
        except Exception:
            pass

    return sorted(set(matched))


def extract_experience(text: str) -> int:
    patterns = [
        r"(\d+)\s*\+?\s*years?\s*(?:of)?\s*experience",
        r"experience\s*[:\-]?\s*(\d+)\s*\+?\s*years?",
        r"(\d+)\s*\+?\s*yrs"
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                continue
    return 0


def extract_title(text: str) -> Optional[str]:
    """Try to extract desired job title from CV content (EN + VI heuristics)."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    joined = "\n".join(lines)

    # Explicit label patterns (EN + VI)
    patterns = [
        r"(?i)(?:position|applying for|job target|objective|career objective)\s*[:\-]?\s*(.+)",
        r"(?i)(?:desired position)\s*[:\-]?\s*(.+)",
        r"(?i)(?:role)\s*[:\-]?\s*(.+)",
        r"(?i)(?:title)\s*[:\-]?\s*(.+)",
        r"(?iu)(?:vị trí ứng tuyển|ứng tuyển vị trí|vị trí|chức danh)\s*[:\-]?\s*(.+)",
        r"(?iu)(?:mục tiêu nghề nghiệp)\s*[:\-]?\s*(.+)",
    ]
    for p in patterns:
        m = re.search(p, joined)
        if m:
            cand = m.group(1).strip()
            # stop at end of line
            cand = cand.splitlines()[0]
            # limit length
            return cand[:160]

    # Heuristic: first line near top that looks like a role
    role_keywords = [
        "developer","engineer","designer","manager","data","ai","ml","backend","front-end","frontend",
        "fullstack","full-stack","devops","qa","test","android","ios","mobile","product","business analyst",
        "analyst","architect","administrator","security","cloud","network","embedded","game"
    ]
    for i, l in enumerate(lines[:30]):  # focus on top part of CV
        low = l.lower()
        if any(k in low for k in role_keywords) and len(l) <= 120:
            return l

    return None


def _extract_salary(s: str) -> float:
    if not s:
        return 0.0
    nums = re.findall(r"\d+", s.replace(',', ''))
    return float(nums[0]) if nums else 0.0


def process_resume_pdf(
    db: Session,
    file: UploadFile,
    desired_position: Optional[str] = None,
) -> List[Dict[str, Any]]:
    # Read bytes once
    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty PDF file")

    # Try AI structured extraction first
    ai_title: Optional[str] = None
    ai_skills: List[str] = []
    ai_exp: Optional[int] = None
    try:
        info = extract_resume_info_ai(content)
        print(info)
        ai_title = (info.get("title") or None)
        ai_skills = list({s.strip().lower() for s in (info.get("skills") or []) if str(s).strip()})
        ai_exp = info.get("experience")
        if ai_exp is not None:
            try:
                ai_exp = int(ai_exp)
            except Exception:
                ai_exp = None
    except Exception as e:
        print("AI extraction failed", e)
        pass
    print(ai_title)
    # If AI fails or returns empty, fallback to text + heuristics
    if not ai_title or not ai_skills or ai_exp is None:
        # Try AI text extraction, then fallback to local
        try:
            text = extract_text_from_pdf_ai_bytes(content)
        except Exception:
            try:
                with fitz.open(stream=content, filetype="pdf") as doc:
                    text = "".join(page.get_text() for page in doc)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

        text = (text or "").strip()
        if not ai_title:
            ai_title = extract_title(text)
        if not ai_skills:
            ai_skills = extract_skills(text)
        if ai_exp is None:
            ai_exp = extract_experience(text)

    search_request = JobSearchRequest(
        title=ai_title,
        skills=ai_skills,
        experience=(ai_exp if ai_exp is not None else 0),
        location=None
    )
    print(search_request)

    # Build a short summary text for the candidate query
    parts = []
    if ai_title:
        parts.append(f"title: {ai_title}")
    if ai_skills:
        parts.append("skills: " + ", ".join(ai_skills[:30]))
    if ai_exp is not None:
        parts.append(f"experience: {ai_exp} years")
    query_text = " | ".join(parts) if parts else (desired_position or "")

    # Compute query embedding and retrieve top-10 similar jobs
    query_emb = get_query_embedding(query_text)
    top10 = top_k_jobs_by_embedding(db, query_emb, k=10)

    # If no embeddings available yet, fallback to existing AI search (limited to 10)
    candidates = top10 if top10 else search_jobs_ai(db, search_request)[:10]

    # Re-rank top candidates using AI matcher
    search_criteria = {
        'title': search_request.title,
        'skills': search_request.skills,
        'experience': search_request.experience,
        'location': search_request.location,
    }
    reranked = match_jobs_with_ai(search_criteria, candidates)
    # keep top 10
    return reranked[:10]
