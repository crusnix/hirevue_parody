# models.py
import uuid
from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, Date, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(50))
    summary = Column(Text)
    skills = Column(JSONB)
    experience = Column(JSONB)
    education = Column(JSONB)
    main_url = Column(Text)
    total_experience_months = Column(Integer)
    status = Column(String(50), default="New")
    vacancy_id = Column(UUID(as_uuid=True), ForeignKey("vacancies.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    vacancy = relationship("Vacancy")
    interviews = relationship("Interview", back_populates="candidate")

class Vacancy(Base):
    __tablename__ = "vacancies"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    published_date = Column(Date)
    responsibilities = Column(JSONB)
    requirements_experience = Column(String(50))
    requirements_skills = Column(JSONB)
    status = Column(String(50), default="Open")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Interview(Base):
    __tablename__ = "interviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    vacancy_id = Column(UUID(as_uuid=True), ForeignKey("vacancies.id"), nullable=False)
    interview_name = Column(String(255))
    interview_date = Column(TIMESTAMP)
    interview_text = Column(Text)
    interview_analysis = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    candidate = relationship("Candidate", back_populates="interviews")
    vacancy = relationship("Vacancy")