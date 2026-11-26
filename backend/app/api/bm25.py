
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.retrieval.bm25_search import search_bm25

router = APIRouter()


class BM25SearchRequest(BaseModel):
    query: str
    k: int = 5


@router.post("/bm25-search")
async def bm25_search_documents(request: BM25SearchRequest):

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty."
        )

    try:
        results = search_bm25(
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
            detail=f"BM25 search failed: {str(error)}"
        )
