from pydantic import BaseModel
from typing import List

class CandidateProfile(BaseModel):
    desired_position: str
    skills: List[str] = []
    years_experience: int = 0
    summary: str | None = None

class MatchResult(BaseModel):
    job_id: int
    title: str
    company: str
    score: float
    matched_skills: List[str]
    missing_skills: List[str]
