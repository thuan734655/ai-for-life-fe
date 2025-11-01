from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.match import CandidateProfile, MatchResult
from app.services.matching import compute_match

router = APIRouter(prefix="/match", tags=["match"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=list[MatchResult])
def match(profile: CandidateProfile, db: Session = Depends(get_db)):
    return compute_match(db, profile)
