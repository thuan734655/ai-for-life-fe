import os
import google.generativeai as genai
from typing import List, Dict, Any
from dotenv import load_dotenv
import tempfile
import time
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')


def extract_text_from_pdf_ai_bytes(content: bytes) -> str:
    """Extract plain text from a PDF using Gemini (file bytes input)."""
    try:
        if model is None:
            raise RuntimeError("Gemini not configured. Set GEMINI_API_KEY to enable PDF extraction.")
        # Write to a temporary file and CLOSE it before upload (Windows safe)
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(content)
                tmp.flush()
                tmp_path = tmp.name
        finally:
            pass
        uploaded = genai.upload_file(path=tmp_path, mime_type="application/pdf")

        # Wait until uploaded file is processed (ACTIVE)
        for _ in range(30):
            file_info = genai.get_file(uploaded.name)
            if getattr(file_info, 'state', '') == 'ACTIVE':
                break
            time.sleep(1)

        prompt = (
            "Extract the plain textual content from this PDF resume. "
            "Return only raw text without extra formatting or commentary."
        )
        resp = model.generate_content([uploaded, prompt])
        return (resp.text or "").strip()
    except Exception as e:
        raise RuntimeError(f"Gemini PDF text extraction failed: {e}")
    finally:
        # Cleanup temp file
        try:
            if 'tmp_path' in locals() and tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


def extract_resume_info_ai(content: bytes) -> Dict[str, Any]:
    """Extract structured resume info (title, skills, experience years) from a PDF using Gemini.

    Returns dict with keys: title (str|None), skills (list[str]), experience (int|None)
    """
    try:
        if model is None:
            raise RuntimeError("Gemini not configured. Set GEMINI_API_KEY to enable resume parsing.")
        # Write to temp file and close before upload (Windows safe)
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(content)
                tmp.flush()
                tmp_path = tmp.name
        finally:
            pass
        uploaded = genai.upload_file(path=tmp_path, mime_type="application/pdf")

        # Wait ACTIVE
        for _ in range(30):
            file_info = genai.get_file(uploaded.name)
            if getattr(file_info, 'state', '') == 'ACTIVE':
                break
            time.sleep(1)

        prompt = (
            "You are an expert CV parser. Read the attached resume PDF and extract: "
            "1) desired job title or target position (short). "
            "2) a concise list of technical skills (as simple strings, lowercase). "
            "3) total years of professional experience as an integer (estimate if needed). "
            "Return JSON with keys: title, skills, experience. Do not add any commentary."
        )

        resp = model.generate_content([uploaded, prompt])
        raw = (resp.text or "").strip()
        data: Dict[str, Any] = {"title": None, "skills": [], "experience": None}
        try:
            data.update(json.loads(raw))
        except Exception:
            # Try to coerce if the model wrapped in code fences
            if "{" in raw and "}" in raw:
                snippet = raw[raw.find("{") : raw.rfind("}") + 1]
                try:
                    data.update(json.loads(snippet))
                except Exception:
                    pass
        # Normalize types
        title = data.get("title")
        if isinstance(title, str):
            title = title.strip()[:160]
        else:
            title = None
        skills = data.get("skills") or []
        if isinstance(skills, list):
            skills = [str(s).strip().lower() for s in skills if str(s).strip()]
        else:
            skills = []
        exp = data.get("experience")
        try:
            exp = int(exp) if exp is not None else None
        except Exception:
            exp = None
        return {"title": title, "skills": skills, "experience": exp}
    except Exception as e:
        raise RuntimeError(f"Gemini resume info extraction failed: {e}")
    finally:
        # Cleanup temp file
        try:
            if 'tmp_path' in locals() and tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


def match_jobs_with_ai(search_request: Dict[str, Any], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Match jobs with the search request using a scoring system
    Returns a list of jobs with match scores
    """
    try:
        matched_jobs = []
        
        for job in jobs:
            score = 0.0
            reasons = []
            
            # 1. Title match (30% weight)
            if search_request.get('title'):
                title_similarity = calculate_similarity(
                    search_request['title'].lower(),
                    job.get('title', '').lower()
                )
                score += title_similarity * 0.3
                reasons.append(f"Title similarity: {title_similarity:.2f}")
            
            # 2. Skills match (40% weight)
            if search_request.get('skills'):
                job_skills = {s['name'].lower() for s in job.get('skills', [])}
                search_skills = {s.lower() for s in search_request['skills']}
                
                if job_skills and search_skills:
                    skill_match_ratio = len(job_skills.intersection(search_skills)) / len(search_skills)
                    score += skill_match_ratio * 0.4
                    reasons.append(f"Skills match: {skill_match_ratio:.2f}")
            
            # 3. Experience match (20% weight)
            if search_request.get('experience') is not None:
                exp_required = job.get('experience_min', 0)
                exp_have = search_request['experience']
                
                if exp_have >= exp_required:
                    exp_score = 1.0  # Full score if meets or exceeds
                elif exp_required > 0:
                    exp_score = exp_have / exp_required  # Partial score based on ratio
                else:
                    exp_score = 0.5  # Default score if no experience required
                
                score += exp_score * 0.2
                reasons.append(f"Experience score: {exp_score:.2f}")
            
            # 4. Location match (10% weight)
            if search_request.get('location'):
                location_match = search_request['location'].lower() in job.get('location', '').lower()
                score += 0.1 if location_match else 0
                reasons.append(f"Location match: {location_match}")
            
            # Ensure score is between 0 and 1
            score = max(0, min(1, score))
            
            # Add match details to job
            job['match_score'] = round(score, 2)
            job['match_reasons'] = reasons
            
            # Only include jobs that meet minimum criteria
            if score >= 0.4:  # Adjust threshold as needed
                matched_jobs.append(job)
        
        # Sort by score in descending order
        return sorted(matched_jobs, key=lambda x: x['match_score'], reverse=True)
        
    except Exception as e:
        print(f"Error in job matching: {str(e)}")
        # Fallback: return jobs with default score
        for job in jobs:
            job['match_score'] = 0.5
            job['match_reasons'] = ["Error in matching"]
        return jobs

def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity ratio between two strings"""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, str1, str2).ratio()


def choose_best_job_from_candidates(search_summary: str, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Ask Gemini to pick the single best job from top-k candidates.
    Returns a dict with keys: best_job_id, reason. If Gemini isn't configured, fall back to first candidate.
    """
    try:
        if not candidates:
            return {"best_job_id": None, "reason": "No candidates"}
        if model is None:
            # Fallback: choose top-1 by embedding_similarity or first
            best = sorted(candidates, key=lambda x: x.get("embedding_similarity", 0), reverse=True)[0]
            return {"best_job_id": best.get("id"), "reason": "Gemini not configured"}

        prompt = (
            "You are an expert recruiter. Given a candidate overview and a list of job postings, "
            "choose the single best matching job. Respond strictly in JSON with keys: best_job_id (number) and reason (string).\n\n"
            f"Candidate overview:\n{search_summary}\n\n"
            f"Jobs (JSON array):\n{json.dumps(candidates, ensure_ascii=False)[:120000]}\n\n"
            "Return only JSON."
        )
        resp = model.generate_content(prompt)
        raw = (getattr(resp, 'text', None) or "").strip()
        try:
            data = json.loads(raw)
        except Exception:
            if "{" in raw and "}" in raw:
                snippet = raw[raw.find("{") : raw.rfind("}") + 1]
                data = json.loads(snippet)
            else:
                raise
        best_job_id = data.get("best_job_id")
        reason = data.get("reason", "")
        return {"best_job_id": best_job_id, "reason": reason}
    except Exception as e:
        # Fail-soft
        try:
            best = sorted(candidates, key=lambda x: x.get("embedding_similarity", 0), reverse=True)[0]
            return {"best_job_id": best.get("id"), "reason": f"Fallback due to error: {e}"}
        except Exception:
            return {"best_job_id": None, "reason": f"Error: {e}"}