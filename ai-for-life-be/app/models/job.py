from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.skill import JobSkill

class Job(Base):
    __tablename__ = "job_table"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), index=True)
    company = Column(String(160))
    location = Column(String(160), default="Remote")
    salary_range = Column(String(80), nullable=True)
    description = Column(Text, nullable=True)
    experience_min = Column(Integer, default=0)
    
    # Relationship
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")