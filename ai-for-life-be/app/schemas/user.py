from pydantic import BaseModel, Field
from typing import List

class SkillInput(BaseModel):
    name: str
    level: int = Field(ge=1, le=5, default=3)

class UserCreate(BaseModel):
    desired_position: str
    years_experience: int = 0
    summary: str | None = None
    skills: List[SkillInput] = []

class UserOut(BaseModel):
    id: int
    desired_position: str
    years_experience: int
    summary: str | None
    skills: list[SkillInput]

    class Config:
        from_attributes = True
