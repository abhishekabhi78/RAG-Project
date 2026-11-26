
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.retrieval.hybrid_search import hybrid_search

router = APIRouter()


class HybridSearchRequest(BaseModel):
    query: str
    k: int = 5


@router.post("/hybrid-search")
async def hybrid_search_documents(request: HybridSearchRequest):

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty."
        )

    try:
        results = hybrid_search(
            query=request.query,
            k=request.k
        )

        return {
            "query": request.query,
            "total_results": len(results),
            "search_type": "Hybrid Search (Dense + BM25)",
            "results": results
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Hybrid search failed: {str(error)}"
        )
