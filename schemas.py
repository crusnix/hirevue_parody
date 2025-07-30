# schemas.py
import uuid
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any, Dict
from datetime import datetime, date

class Config:
    from_attributes = True

# --- LLM Service Schemas ---
class SearchDescriptionParseRequest(BaseModel):
    description: str

class SearchDescriptionParseResponse(BaseModel):
    role: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[str] = None

class InterviewAnalysis(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    assessment_aspects: Dict[str, str]
    red_flags_identified: List[str]
    overall_score: int

# --- Candidate Schemas ---
class CandidateSearchResponse(BaseModel):
    id: uuid.UUID
    name: str
    skills: Optional[List[str]] = []
    total_experience_months: Optional[int] = None
    status: str
    main_url: Optional[str] = None

    class Config(Config):
        pass

class CandidateImportContent(BaseModel):
    title: str
    skills_atomic: Optional[List[str]] = Field(None, alias="skills_atomic")
    experience: Optional[List[Any]] = None
    education: Optional[List[Any]] = None
    alternate_url: Optional[str] = None
    total_experience: Optional[Dict[str, int]] = None

class CandidateImportRequest(BaseModel):
    fullContent: CandidateImportContent

# --- Vacancy Schemas ---
class VacancyListResponse(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    published_date: Optional[date] = None

    class Config(Config):
        pass

class VacancyCandidateResponse(BaseModel):
    id: uuid.UUID
    name: str
    status: str
    interview_id: Optional[uuid.UUID] = None

    class Config(Config):
        pass

class VacancyImportContent(BaseModel):
    title: str
    published_at: Optional[datetime] = None
    responsibilities: Optional[List[str]] = None
    requirements_experience: Optional[str] = Field(None, alias="requirements.experience")
    skills_atomic: Optional[List[str]] = None

class VacancyImportRequest(BaseModel):
    fullContent: VacancyImportContent


# --- Interview Schemas ---
class InterviewScheduleRequest(BaseModel):
    candidate_id: uuid.UUID
    vacancy_id: uuid.UUID
    interview_name: str
    interview_date: datetime
    interview_text: str

class InterviewScheduleResponse(BaseModel):
    message: str
    interview_id: uuid.UUID
    candidate_id: uuid.UUID

class InterviewAnalysisResponse(BaseModel):
    interview_text: str
    interview_analysis: InterviewAnalysis

    class Config(Config):
        pass