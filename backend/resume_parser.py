"""Resume parsing module supporting PDF, DOCX, and TXT files with skill extraction."""

import io
import re
from typing import Dict, List, Optional
import fitz  # PyMuPDF
from docx import Document
from fastapi import HTTPException

from skills import extract_skills_from_text, normalize_skill


def extract_text_from_pdf(content: bytes) -> str:
    """Extract plain text from PDF bytes using PyMuPDF."""
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        text_parts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts).strip()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract text from PDF: {str(exc)}"
        )


def extract_text_from_docx(content: bytes) -> str:
    """Extract plain text and tables from DOCX bytes."""
    try:
        doc = Document(io.BytesIO(content))
        text_parts = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    text_parts.append(" | ".join(row_text))
        return "\n".join(text_parts).strip()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract text from DOCX: {str(exc)}"
        )


def extract_text_from_txt(content: bytes) -> str:
    """Extract plain text from TXT bytes with UTF-8 fallback."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="replace")


def parse_resume_file(filename: str, content: bytes) -> str:
    """Parse resume content based on file extension."""
    if not filename:
        raise HTTPException(status_code=400, detail="Filename cannot be empty.")
    
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    
    if ext == "pdf":
        text = extract_text_from_pdf(content)
    elif ext in ("docx", "doc"):
        text = extract_text_from_docx(content)
    elif ext == "txt":
        text = extract_text_from_txt(content)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a PDF, DOCX, or TXT resume."
        )

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="The uploaded resume appears to be empty or unreadable."
        )

    return text


def extract_resume_metadata(text: str) -> dict:
    """Extract basic structural candidate information from resume text using heuristics."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # Heuristic for name: usually first non-empty line under 50 chars without common header keywords
    candidate_name = ""
    for line in lines[:5]:
        lower_line = line.lower()
        if not any(kw in lower_line for kw in ["resume", "curriculum", "cv", "page", "email", "phone", "http"]):
            if len(line.split()) <= 4 and re.match(r"^[A-Za-z\s\.\-]+$", line):
                candidate_name = line.strip()
                break

    # Email extraction
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    email = email_match.group(0) if email_match else ""

    # Phone extraction
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    phone = phone_match.group(0) if phone_match else ""

    # Skills extraction
    skills = extract_skills_from_text(text)

    # Experience heuristic: find years mentioned
    years_match = re.findall(r"(\d{1,2})\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience", text, re.IGNORECASE)
    years_experience = max([int(y) for y in years_match]) if years_match else None

    # Education degree heuristic
    degrees = []
    degree_keywords = ["bachelor", "master", "phd", "b.tech", "m.tech", "b.e", "m.e", "bs", "ms", "computer science", "information technology"]
    for line in lines:
        for d in degree_keywords:
            if d in line.lower() and len(line) < 100:
                degrees.append(line.strip())
                break

    return {
        "candidate_name": candidate_name or "Candidate",
        "email": email,
        "phone": phone,
        "years_experience": years_experience,
        "education": degrees[:2] if degrees else ["Relevant Technical Background"],
        "extracted_skills": skills,
        "word_count": len(text.split()),
        "raw_text_preview": text[:1000] + ("..." if len(text) > 1000 else "")
    }
