
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader
from docx import Document


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Extract text from PDF or DOCX documents.
    """

    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        pdf = PdfReader(BytesIO(file_bytes))

        pages = []

        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)

        return "\n".join(pages).strip()

    elif extension == ".docx":
        document = Document(BytesIO(file_bytes))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs).strip()

    else:
        raise ValueError("Only PDF and DOCX files are supported.")
