"""
Acceptance Criteria:
- EmbeddingAdapter defines embed(texts) -> list[list[float]] for a batch of texts.
- StubEmbeddingAdapter returns a deterministic zero-vector of dimension 384 per text.
- StubEmbeddingAdapter records the model name "stub-384" for metadata tracking.
- get_embedding_adapter() returns the globally configured adapter (stub by default).
- EmbeddingResult carries the model name alongside the vector so callers can store it.
- No external network calls are made by the stub; this is safe for unit tests.
"""

from dataclasses import dataclass

STUB_MODEL_NAME = "stub-384"
STUB_DIMENSION = 384


@dataclass
class EmbeddingResult:
    model: str
    vector: list[float]


class EmbeddingAdapter:
    @property
    def model_name(self) -> str:
        raise NotImplementedError

    def embed(self, texts: list[str]) -> list[EmbeddingResult]:
        raise NotImplementedError


class StubEmbeddingAdapter(EmbeddingAdapter):
    @property
    def model_name(self) -> str:
        return STUB_MODEL_NAME

    def embed(self, texts: list[str]) -> list[EmbeddingResult]:
        return [
            EmbeddingResult(model=STUB_MODEL_NAME, vector=[0.0] * STUB_DIMENSION)
            for _ in texts
        ]


_adapter: EmbeddingAdapter | None = None


def get_embedding_adapter() -> EmbeddingAdapter:
    global _adapter
    if _adapter is None:
        _adapter = StubEmbeddingAdapter()
    return _adapter
