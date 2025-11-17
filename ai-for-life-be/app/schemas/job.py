from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
from fastapi import UploadFile, File
import re

class JobCreate(BaseModel):
    title: str
    company: str
    location: str = "Remote"
    salary_range: str | None = None
    description: str | None = None
    experience_min: int = 0
    skills: List[str] = []
    
    class Config:
        from_attributes = True

class JobOut(BaseModel):
    id: str
    title: str
    company: str
    location: str
    salary_range: str | None
    description: str | None
    experience_min: int
    skills: List[str]
    
    class Config:
        from_attributes = True

class JobSearchRequest(BaseModel):
    title: Optional[str] = None
    skills: List[str] = []
    experience: Optional[int] = None
    location: Optional[str] = None
    query: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Backend Developer",
                "skills": ["Python", "FastAPI", "SQL"],
                "experience": 3,
                "location": "Hanoi",
                "query": "backend developer python fastapi, 3 years, remote"
            }
        }