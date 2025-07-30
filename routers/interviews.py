# routers/interviews.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import crud, schemas, llm_service
from database import get_db
import uuid

router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"]
)

@router.post("/schedule", response_model=schemas.InterviewScheduleResponse)
async def schedule_new_interview(
    request: schemas.InterviewScheduleRequest,
    db: AsyncSession = Depends(get_db)
):
    # Check if candidate and vacancy exist
    candidate = await crud.get_candidate_by_id(db, request.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with ID {request.candidate_id} not found.")
    
    vacancy = await crud.get_vacancy_by_id(db, request.vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail=f"Vacancy with ID {request.vacancy_id} not found.")

    try:
        # Trigger LLM analysis
        analysis_result = await llm_service.analyze_interview_text(request.interview_text)
        
        # Schedule interview and update candidate status in one transaction
        interview = await crud.schedule_interview(db, request, analysis_result)
        
        return {
            "message": "Interview scheduled and analysis completed.",
            "interview_id": interview.id,
            "candidate_id": interview.candidate_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule interview: {e}")


@router.get("/{interview_id}/analysis", response_model=schemas.InterviewAnalysisResponse)
async def get_interview_analysis(interview_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    interview = await crud.get_interview_by_id(db, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")
    if not interview.interview_analysis:
        raise HTTPException(status_code=404, detail="Analysis not found for this interview.")
        
    return interview