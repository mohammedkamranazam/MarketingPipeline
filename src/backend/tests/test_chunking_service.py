"""
Tests for chunking_service.

Acceptance criteria tested:
- Empty pages return empty chunks.
- Single page produces correct number of chunks with correct boundaries.
- Overlap produces correct start/end offsets.
- Invalid chunk_size raises ValueError.
- Invalid overlap raises ValueError.
- chunk_index is monotonically increasing across pages.
- Page boundaries do not merge across pages.
"""

import pytest

from core.services.chunking_service import chunk_pages
from core.services.parser_service import ParsedPage


def _page(n: int, text: str) -> ParsedPage:
    return ParsedPage(page_number=n, raw_text=text)


def test_empty_pages_returns_empty():
    assert chunk_pages([]) == []


def test_empty_text_page_skipped():
    chunks = chunk_pages([_page(1, "")])
    assert chunks == []


def test_single_page_no_overlap():
    text = "A" * 2500
    chunks = chunk_pages([_page(1, text)], chunk_size=1000, overlap=0)
    assert len(chunks) == 3
    assert chunks[0].char_start == 0
    assert chunks[0].char_end == 1000
    assert chunks[1].char_start == 1000
    assert chunks[1].char_end == 2000
    assert chunks[2].char_start == 2000
    assert chunks[2].char_end == 2500


def test_single_page_with_overlap():
    text = "A" * 1500
    chunks = chunk_pages([_page(1, text)], chunk_size=1000, overlap=200)
    # step = 800; start positions: 0, 800
    assert len(chunks) == 2
    assert chunks[0].char_start == 0
    assert chunks[0].char_end == 1000
    assert chunks[1].char_start == 800
    assert chunks[1].char_end == 1500


def test_chunk_index_monotonic_across_pages():
    p1 = _page(1, "X" * 1200)
    p2 = _page(2, "Y" * 800)
    chunks = chunk_pages([p1, p2], chunk_size=1000, overlap=0)
    indices = [c.chunk_index for c in chunks]
    assert indices == list(range(len(indices)))


def test_page_boundaries_not_merged():
    p1 = _page(1, "A" * 500)
    p2 = _page(2, "B" * 500)
    chunks = chunk_pages([p1, p2], chunk_size=1000, overlap=0)
    page_numbers = [c.page_number for c in chunks]
    assert page_numbers == [1, 2]


def test_invalid_chunk_size_raises():
    with pytest.raises(ValueError, match="chunk_size must be > 0"):
        chunk_pages([_page(1, "text")], chunk_size=0)


def test_invalid_overlap_negative_raises():
    with pytest.raises(ValueError, match="overlap must be >= 0"):
        chunk_pages([_page(1, "text")], chunk_size=100, overlap=-1)


def test_invalid_overlap_gte_chunk_size_raises():
    with pytest.raises(ValueError, match="overlap must be >= 0"):
        chunk_pages([_page(1, "text")], chunk_size=100, overlap=100)


def test_short_text_single_chunk():
    text = "Short"
    chunks = chunk_pages([_page(1, text)], chunk_size=1000, overlap=0)
    assert len(chunks) == 1
    assert chunks[0].text == text
    assert chunks[0].char_start == 0
    assert chunks[0].char_end == len(text)
