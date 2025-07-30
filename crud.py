# crud.py
import uuid
from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
import models, schemas
import re

def parse_experience_years(exp_str: Optional[str]) -> Optional[tuple[int, int]]:
    """Converts '3-5 years' or '5+ years' or '2 years' into a tuple of min/max months."""
    if not exp_str:
        return None

    exp_str = exp_str.lower().replace("years", "").replace("year", "").strip()
    
    # Handle "N+ years"
    if "+" in exp_str:
        try:
            min_years = int(exp_str.replace("+", "").strip())
            return (min_years * 12, float('inf'))
        except ValueError:
            return None
            
    # Handle "N-M years"
    if "-" in exp_str:
        try:
            min_years, max_years = map(int, exp_str.split('-'))
            return (min_years * 12, max_years * 12)
        except ValueError:
            return None

    # Handle "N years"
    try:
        years = int(exp_str)
        return (years * 12, years * 12)
    except ValueError:
        return None

async def search_candidates(
    db: AsyncSession,
    role: Optional[str],
    skills: Optional[List[str]],
    experience_years: Optional[str],
) -> List[models.Candidate]:
    query = select(models.Candidate)
    
    if role:
        # Simple search in the name/title
        query = query.where(models.Candidate.name.ilike(f"%{role}%"))
        
    if skills:
        # OR logic for skills: candidate must have at least one of the skills
        # JSONB containment: skills @> '["Python"]'
        skill_conditions = [models.Candidate.skills.contains([skill]) for skill in skills]
        query = query.where(or_(*skill_conditions))

    exp_range_months = parse_experience_years(experience_years)
    if exp_range_months:
        min_months, max_months = exp_range_months
        if max_months == float('inf'):
            query = query.where(models.Candidate.total_experience_months >= min_months)
        else:
            query = query.where(models.Candidate.total_experience_months.between(min_months, max_months))

    result = await db.execute(query)
    return result.scalars().all()

async def create_candidate(db: AsyncSession, candidate_data: schemas.CandidateImportContent) -> models.Candidate:
    total_months = candidate_data.total_experience.get("months") if candidate_data.total_experience else 0
    
    db_candidate = models.Candidate(
        name=candidate_data.title,
        email=f"{uuid.uuid4().hex[:12]}@dummy.com", # Create dummy email
        phone="+1234567890",
        skills=candidate_data.skills_atomic,
        experience=candidate_data.experience,
        education=candidate_data.education,
        main_url=candidate_data.alternate_url,
        total_experience_months=total_months,
        status="New"
    )
    db.add(db_candidate)
    await db.commit()
    await db.refresh(db_candidate)
    return db_candidate

async def get_all_vacancies(db: AsyncSession) -> List[models.Vacancy]:
    result = await db.execute(select(models.Vacancy).order_by(models.Vacancy.created_at.desc()))
    return result.scalars().all()

async def create_vacancy(db: AsyncSession, vacancy_data: schemas.VacancyImportContent) -> models.Vacancy:
    published_date = vacancy_data.published_at.date() if vacancy_data.published_at else None
    db_vacancy = models.Vacancy(
        title=vacancy_data.title,
        published_date=published_date,
        responsibilities=vacancy_data.responsibilities,
        requirements_experience=vacancy_data.requirements_experience,
        requirements_skills=vacancy_data.skills_atomic,
        status="Open"
    )
    db.add(db_vacancy)
    await db.commit()
    await db.refresh(db_vacancy)
    return db_vacancy

async def get_candidates_for_vacancy(db: AsyncSession, vacancy_id: uuid.UUID) -> List[tuple[models.Candidate, Optional[uuid.UUID]]]:
    # We need to find candidates linked via an interview for this vacancy
    query = (
        select(models.Candidate, models.Interview.id)
        .join(models.Interview, models.Candidate.id == models.Interview.candidate_id)
        .where(models.Interview.vacancy_id == vacancy_id)
    )
    result = await db.execute(query)
    return result.all()

async def get_interview_by_id(db: AsyncSession, interview_id: uuid.UUID) -> Optional[models.Interview]:
    result = await db.execute(select(models.Interview).where(models.Interview.id == interview_id))
    return result.scalars().one_or_none()

async def get_candidate_by_id(db: AsyncSession, candidate_id: uuid.UUID) -> Optional[models.Candidate]:
    result = await db.execute(select(models.Candidate).where(models.Candidate.id == candidate_id))
    return result.scalars().one_or_none()

async def get_vacancy_by_id(db: AsyncSession, vacancy_id: uuid.UUID) -> Optional[models.Vacancy]:
    result = await db.execute(select(models.Vacancy).where(models.Vacancy.id == vacancy_id))
    return result.scalars().one_or_none()
    
async def schedule_interview(db: AsyncSession, interview_data: schemas.InterviewScheduleRequest, analysis_result: schemas.InterviewAnalysis) -> models.Interview:
    # 1. Create the Interview record
    db_interview = models.Interview(
        candidate_id=interview_data.candidate_id,
        vacancy_id=interview_data.vacancy_id,
        interview_name=interview_data.interview_name,
        interview_date=interview_data.interview_date,
        interview_text=interview_data.interview_text,
        interview_analysis=analysis_result.model_dump() # Store analysis as JSON
    )
    db.add(db_interview)
    
    # 2. Update the candidate's status
    candidate = await get_candidate_by_id(db, interview_data.candidate_id)
    if candidate:
        candidate.status = "Interview Scheduled"
        candidate.vacancy_id = interview_data.vacancy_id

    await db.commit()
    await db.refresh(db_interview)
    return db_interview