"""
extractor.py
------------
Pulls raw text out of an uploaded PDF or DOCX. Adapted from the
Streamlit version to work with FastAPI's UploadFile — instead of
taking a Streamlit-specific file object, it takes plain (filename,
bytes), decoupling this module from any particular web framework.
"""

import io
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))
    text_parts = [para.text for para in document.paragraphs if para.text.strip()]
    return "\n".join(text_parts)


def extract_text(filename: str, file_bytes: bytes) -> str:
    filename_lower = filename.lower()
    if filename_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {filename}. Please upload a .pdf or .docx file.")