from pydantic import BaseModel, Field
from typing import List

class JobSkillReq(BaseModel):
    name: str
    weight: int = Field(ge=1, le=5, default=3)
    class Config:
        orm_mode = True

class JobCreate(BaseModel):
    title: str
    company: str
    location: str = "Remote"
    salary_range: str | None = None
    description: str | None = None
    experience_min: int = 0
    skills: List[JobSkillReq] = []

class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: str
    salary_range: str | None
    description: str | None
    experience_min: int
    skills: List[JobSkillReq]

    class Config:
        from_attributes = True
        orm_mode = True

