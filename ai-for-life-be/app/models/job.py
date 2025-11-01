from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.skill import JobSkill

class Job(Base):
    __tablename__ = "job_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    company: Mapped[str] = mapped_column(String(160))
    location: Mapped[str] = mapped_column(String(160), default="Remote")
    salary_range: Mapped[str | None] = mapped_column(String(80), default=None)
    description: Mapped[str | None] = mapped_column(String(4000), default=None)
    experience_min: Mapped[int] = mapped_column(Integer, default=0)

    skills: Mapped[list[JobSkill]] = relationship("JobSkill", cascade="all, delete-orphan")
