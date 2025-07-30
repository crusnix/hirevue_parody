# routers/candidates.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import crud, schemas
from database import get_db

router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)

@router.get("/search", response_model=List[schemas.CandidateSearchResponse])
async def search_for_candidates(
    role: Optional[str] = None,
    skills: Optional[str] = None, # Comma-separated string
    experience_years: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    skill_list = skills.split(',') if skills else []
    candidates = await crud.search_candidates(db, role, skill_list, experience_years)
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found matching the criteria.")
    return candidates

@router.post("/import", status_code=201)
async def import_candidate(
    request: schemas.CandidateImportRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        await crud.create_candidate(db, request.fullContent)
        return {"message": "Candidate(s) imported successfully.", "imported_count": 1}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error on import: {e}")