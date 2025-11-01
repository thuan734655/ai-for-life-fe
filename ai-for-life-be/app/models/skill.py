from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column,relationship  
from app.db.base import Base

class Skill(Base):
    __tablename__ = "skill_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

class UserSkill(Base):
    __tablename__ = "user_skills"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skill_table.id"), primary_key=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),)

class JobSkill(Base):
    __tablename__ = "job_skill_table"
    
    job_id = Column(Integer, ForeignKey('job_table.id'), primary_key=True)
    skill_id = Column(Integer, ForeignKey('skill_table.id'), primary_key=True)
    weight = Column(Integer, default=1)
    
    # Relationships
    job = relationship("Job", back_populates="skills")
    skill = relationship("Skill")
