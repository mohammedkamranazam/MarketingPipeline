"""
Acceptance Criteria:
- parse_document(data, mime_type) -> list[ParsedPage] extracts text from PDF, DOCX, and TXT.
- PDF parser returns one ParsedPage per PDF page with raw_text.
- DOCX parser concatenates all paragraph text into a single page (page_number=1).
- TXT parser returns the full text as a single page (page_number=1).
- Unsupported mime_type raises ValueError with the mime_type in the message.
- ParsedPage is a dataclass with page_number (int) and raw_text (str).
- Empty documents return a list with one page with empty raw_text.
- parse_document never raises on valid bytes; errors propagate only as ValueError.
"""

from dataclasses import dataclass

SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


@dataclass
class ParsedPage:
    page_number: int
    raw_text: str


def parse_document(data: bytes, mime_type: str) -> list[ParsedPage]:
    if mime_type == "application/pdf":
        return _parse_pdf(data)
    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return _parse_docx(data)
    if mime_type == "text/plain":
        return _parse_txt(data)
    raise ValueError(f"Unsupported mime_type: {mime_type}")


def _parse_pdf(data: bytes) -> list[ParsedPage]:
    import io

    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    if not reader.pages:
        return [ParsedPage(page_number=1, raw_text="")]
    return [
        ParsedPage(page_number=i + 1, raw_text=page.extract_text() or "")
        for i, page in enumerate(reader.pages)
    ]


def _parse_docx(data: bytes) -> list[ParsedPage]:
    import io

    from docx import Document

    doc = Document(io.BytesIO(data))
    text = "\n".join(p.text for p in doc.paragraphs)
    return [ParsedPage(page_number=1, raw_text=text)]


def _parse_txt(data: bytes) -> list[ParsedPage]:
    text = data.decode("utf-8", errors="replace")
    return [ParsedPage(page_number=1, raw_text=text)]
