# routers/vacancies.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import crud, schemas
from database import get_db
import uuid

router = APIRouter(
    prefix="/vacancies",
    tags=["Vacancies"]
)

@router.get("", response_model=List[schemas.VacancyListResponse])
async def get_all_vacancies(db: AsyncSession = Depends(get_db)):
    vacancies = await crud.get_all_vacancies(db)
    if not vacancies:
        raise HTTPException(status_code=404, detail="No vacancies found.")
    return vacancies

@router.get("/{vacancy_id}/candidates", response_model=List[schemas.VacancyCandidateResponse])
async def get_vacancy_candidates(vacancy_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    results = await crud.get_candidates_for_vacancy(db, vacancy_id)
    if not results:
        raise HTTPException(status_code=404, detail="No candidates found for this vacancy.")
    
    response_data = []
    for candidate, interview_id in results:
        response_data.append(
            schemas.VacancyCandidateResponse(
                id=candidate.id,
                name=candidate.name,
                status=candidate.status,
                interview_id=interview_id
            )
        )
    return response_data


@router.post("/import", status_code=201)
async def import_vacancy(
    request: schemas.VacancyImportRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        await crud.create_vacancy(db, request.fullContent)
        return {"message": "Vacancy(-ies) imported successfully.", "imported_count": 1}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error on import: {e}")