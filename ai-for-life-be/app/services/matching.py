from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.skill import Skill, JobSkill
from app.schemas.match import CandidateProfile, MatchResult


def _collect_job_skills(db: Session, job: Job) -> dict[str, int]:
    rows = db.query(JobSkill).filter(JobSkill.job_id == job.id).all()
    result: dict[str, int] = {}
    for r in rows:
        name = db.query(Skill).filter(Skill.id == r.skill_id).first().name
        result[name] = r.weight
    return result


def compute_match(db: Session, profile: CandidateProfile) -> list[MatchResult]:
    jobs = db.query(Job).all()
    cand_skills = {s.strip().lower() for s in profile.skills if s.strip()}
    results: list[MatchResult] = []

    for job in jobs:
        job_skills = _collect_job_skills(db, job)
        if not job_skills:
            continue

        total_weight = sum(job_skills.values()) or 1
        matched = [s for s in cand_skills if s in job_skills]
        missing = [s for s in job_skills.keys() if s not in cand_skills]

        skill_score = sum(job_skills[s] for s in matched) / total_weight

        exp_bonus = 0.1 if profile.years_experience >= job.experience_min else 0.0
        title_bonus = 0.1 if profile.desired_position.lower() in job.title.lower() else 0.0

        score = min(1.0, 0.8 * skill_score + exp_bonus + title_bonus) * 100.0

        results.append(
            MatchResult(
                job_id=job.id,
                title=job.title,
                company=job.company,
                score=round(score, 2),
                matched_skills=matched,
                missing_skills=missing,
            )
        )

    results.sort(key=lambda x: x.score, reverse=True)
    return results
