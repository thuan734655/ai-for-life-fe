from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.skill import UserSkill

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    desired_position: Mapped[str] = mapped_column(String(120), index=True)
    years_experience: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[str | None] = mapped_column(String(2000), default=None)

    skills: Mapped[list[UserSkill]] = relationship("UserSkill", cascade="all, delete-orphan")
