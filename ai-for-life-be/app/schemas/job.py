from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
from fastapi import UploadFile, File
import re

class JobSkillBase(BaseModel):
    skill_id: int  # Thay name bằng skill_id
    weight: int = Field(ge=1, le=5, default=3)
    
    class Config:
        from_attributes = True

class JobSkillCreate(BaseModel):
    name: str  # Chỉ dùng khi tạo mới    
    weight: int = Field(ge=1, le=5, default=3)    
    class Config:
        from_attributes = True

class JobSkillOut(JobSkillBase):
    name: Optional[str] = None  # Thêm trường name tùy chọn
    
    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    title: str
    company: str
    location: str = "Remote"
    salary_range: str | None = None
    description: str | None = None
    experience_min: int = 0
    skills: List[JobSkillCreate] = []

class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: str
    salary_range: str | None
    description: str | None
    experience_min: int
    skills: List[JobSkillOut]  # Sử dụng JobSkillOut thay vì JobSkillReq

    class Config:
        from_attributes = True

class JobSearchRequest(BaseModel):
    title: Optional[str] = None
    skills: List[str] = []
    experience: Optional[int] = None
    location: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Backend Developer",
                "skills": ["Python", "FastAPI", "SQL"],
                "experience": 3,
                "location": "Hanoi"
            }
        }