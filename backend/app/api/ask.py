
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.rag.rag_chain import run_rag

router = APIRouter()


class AskRequest(BaseModel):
    query: str
    k: int = 5
    filename: str | None = None


@router.post("/ask")
async def ask_question(request: AskRequest):

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        result = run_rag(
    query=request.query,
    k=request.k,
    filename=request.filename
)

        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"RAG question answering failed: {str(error)}"
        )
