"""
Acceptance Criteria:
- StorageAdapter defines upload(key, data, content_type) -> str and download(key) -> bytes.
- LocalStorageAdapter stores files under a configurable base directory.
- LocalStorageAdapter.upload writes bytes to {base_dir}/{key} (creating subdirectories).
- LocalStorageAdapter.download raises FileNotFoundError when key does not exist.
- generate_storage_key(pipeline_id, category, filename) returns a deterministic,
  path-safe key: {category}/{pipeline_id}/{uuid4}_{filename}.
- No TypeScript any (Python equivalent: no untyped dicts as public API).
"""

import uuid
from pathlib import Path


def generate_storage_key(pipeline_id: str, category: str, filename: str) -> str:
    """Return a deterministic, path-safe storage key for an uploaded file."""
    safe_name = Path(filename).name.replace(" ", "_")
    return f"{category}/{pipeline_id}/{uuid.uuid4()}_{safe_name}"


class StorageAdapter:
    def upload(self, key: str, data: bytes, content_type: str) -> str:
        raise NotImplementedError

    def download(self, key: str) -> bytes:
        raise NotImplementedError


class LocalStorageAdapter(StorageAdapter):
    def __init__(self, base_dir: str = "/tmp/marketing_pipeline_storage") -> None:
        self._base = Path(base_dir)

    def upload(self, key: str, data: bytes, content_type: str) -> str:  # noqa: ARG002
        dest = self._base / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return key

    def download(self, key: str) -> bytes:
        path = self._base / key
        if not path.exists():
            raise FileNotFoundError(f"Storage key not found: {key}")
        return path.read_bytes()


_adapter: StorageAdapter | None = None


def get_storage_adapter() -> StorageAdapter:
    global _adapter
    if _adapter is None:
        _adapter = LocalStorageAdapter()
    return _adapter
