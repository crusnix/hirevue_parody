# routers/search.py
from fastapi import APIRouter, HTTPException
import schemas, llm_service

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)

@router.post("/parse-description", response_model=schemas.SearchDescriptionParseResponse)
async def parse_candidate_description(request: schemas.SearchDescriptionParseRequest):
    if not request.description:
        raise HTTPException(status_code=400, detail="Description cannot be empty.")
    try:
        parsed_result = await llm_service.parse_search_query(request.description)
        return parsed_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process description with LLM: {e}")