
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ingestion.text_splitter import split_text
from app.ingestion.document_loader import extract_text
from app.retrieval.vector_store import store_chunks

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    allowed_extensions = [".pdf", ".docx"]

    filename = file.filename or ""
    extension = filename.lower().rsplit(".", 1)[-1]

    if "." not in filename or f".{extension}" not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed."
        )

    try:
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        text = extract_text(file_bytes, filename)
        chunks = split_text(text)
        stored_chunks = store_chunks(chunks, filename)
        if not text:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the document."
            )

        return {
            "filename": filename,
            "message": "Document uploaded and processed successfully!",
            "characters": len(text),
            "total_chunks": len(chunks),
            "stored_chunks": stored_chunks,
            "chunks": chunks,
            "extracted_text": text
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(error)}"
        )
