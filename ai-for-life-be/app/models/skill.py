from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
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
    job_id: Mapped[int] = mapped_column(ForeignKey("job_table.id"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skill_table.id"), primary_key=True)
    weight: Mapped[int] = mapped_column(Integer, default=1)
    __table_args__ = (UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),)
