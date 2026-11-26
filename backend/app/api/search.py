
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.retrieval.vector_store import search_chunks

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    k: int = 5


@router.post("/search")
async def search_documents(request: SearchRequest):

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty."
        )

    try:
        results = search_chunks(
            query=request.query,
            k=request.k
        )

        return {
            "query": request.query,
            "total_results": len(results),
            "results": results
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(error)}"
        )
