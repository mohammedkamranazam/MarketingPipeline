"""
Acceptance Criteria:
- chunk_pages(pages, chunk_size, overlap) -> list[TextChunk] splits page text into
  fixed-size overlapping character windows.
- Each TextChunk carries page_number (nullable), chunk_index (global across pages),
  text, char_start, char_end (relative to the page text).
- chunk_size defaults to 1000 characters; overlap defaults to 200 characters.
- chunk_size must be > 0 and overlap must be >= 0 and < chunk_size.
- Invalid parameters raise ValueError.
- Empty page list returns an empty chunk list.
- Chunks from page boundaries do not merge across pages.
- chunk_index is 0-based and monotonically increasing across all pages.
"""

from dataclasses import dataclass

from core.services.parser_service import ParsedPage

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_OVERLAP = 200


@dataclass
class TextChunk:
    page_number: int | None
    chunk_index: int
    text: str
    char_start: int
    char_end: int


def chunk_pages(
    pages: list[ParsedPage],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be > 0, got {chunk_size}")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(f"overlap must be >= 0 and < chunk_size, got {overlap}")

    chunks: list[TextChunk] = []
    chunk_index = 0

    for page in pages:
        text = page.raw_text
        if not text:
            continue
        step = chunk_size - overlap
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(
                TextChunk(
                    page_number=page.page_number,
                    chunk_index=chunk_index,
                    text=text[start:end],
                    char_start=start,
                    char_end=end,
                )
            )
            chunk_index += 1
            if end == len(text):
                break
            start += step

    return chunks
