from sqlalchemy.orm import Session
from app.models.user import User
from app.models.skill import UserSkill
from app.schemas.user import UserCreate
from app.crud.skill import get_or_create_skill

def create_user(db: Session, payload: UserCreate) -> User:
    user = User(
        desired_position=payload.desired_position,
        years_experience=payload.years_experience,
        summary=payload.summary,
    )
    db.add(user)
    db.flush()

    for s in payload.skills:
        skill = get_or_create_skill(db, s.name)
        db.add(UserSkill(user_id=user.id, skill_id=skill.id, level=s.level))

    db.commit()
    db.refresh(user)
    return user
