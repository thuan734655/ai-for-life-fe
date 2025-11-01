from sqlalchemy.orm import Session
from app.models.skill import Skill

def get_or_create_skill(db: Session, name: str) -> Skill:
    normalized = name.strip().lower()
    skill = db.query(Skill).filter(Skill.name == normalized).first()
    if not skill:
        skill = Skill(name=normalized)
        db.add(skill)
        db.commit()
        db.refresh(skill)
    return skill
