"""
Tests for storage adapter.

Acceptance criteria tested:
- LocalStorageAdapter.upload writes file to disk and returns key.
- LocalStorageAdapter.download retrieves uploaded bytes.
- LocalStorageAdapter.download raises FileNotFoundError for missing key.
- generate_storage_key returns a key with the expected category/pipeline_id prefix.
- generate_storage_key sanitizes filename spaces.
- StubEmbeddingAdapter returns zero-vectors with correct dimension.
- StubEmbeddingAdapter model_name is 'stub-384'.
"""

import tempfile

import pytest

from core.services.embedding_service import StubEmbeddingAdapter
from core.storage.adapter import LocalStorageAdapter, generate_storage_key


def test_upload_and_download_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        adapter = LocalStorageAdapter(base_dir=tmp)
        key = "documents/pipe-1/myfile.txt"
        data = b"Hello, storage!"
        returned_key = adapter.upload(key, data, "text/plain")
        assert returned_key == key
        downloaded = adapter.download(key)
        assert downloaded == data


def test_download_missing_key_raises():
    with tempfile.TemporaryDirectory() as tmp:
        adapter = LocalStorageAdapter(base_dir=tmp)
        with pytest.raises(FileNotFoundError):
            adapter.download("nonexistent/path/file.txt")


def test_upload_creates_subdirectories():
    with tempfile.TemporaryDirectory() as tmp:
        adapter = LocalStorageAdapter(base_dir=tmp)
        key = "deep/nested/path/file.bin"
        adapter.upload(key, b"bytes", "application/octet-stream")
        downloaded = adapter.download(key)
        assert downloaded == b"bytes"


def test_generate_storage_key_structure():
    key = generate_storage_key("pipeline-abc", "documents", "report.pdf")
    parts = key.split("/")
    assert parts[0] == "documents"
    assert parts[1] == "pipeline-abc"
    assert "report.pdf" in parts[2]


def test_generate_storage_key_sanitizes_spaces():
    key = generate_storage_key("p1", "documents", "my file.txt")
    assert " " not in key


def test_stub_embedding_returns_correct_dimension():
    adapter = StubEmbeddingAdapter()
    results = adapter.embed(["text one", "text two"])
    assert len(results) == 2
    assert all(len(r.vector) == 384 for r in results)
    assert all(all(v == 0.0 for v in r.vector) for r in results)


def test_stub_embedding_model_name():
    adapter = StubEmbeddingAdapter()
    assert adapter.model_name == "stub-384"
    results = adapter.embed(["hello"])
    assert results[0].model == "stub-384"
