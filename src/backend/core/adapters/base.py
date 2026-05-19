"""
Acceptance Criteria:
- AdapterMeta carries adapter_key, display_name, source_type, terms_url, cost_model,
  timeout_seconds, retry_class, audit_event_type, and is_certified.
- BaseAdapter defines execute(input_data) -> AdapterOutput contract.
- AdapterInput carries operation_type (str) and payload (typed dict via JSON text).
- AdapterOutput carries success (bool), data (JSON text | None), error (str | None),
  latency_ms (int).
- Adapters must declare metadata via class-level META: AdapterMeta.
- No TypeScript `any`. No untyped dicts in public interface.
"""

from __future__ import annotations

import abc
import json
import time
from dataclasses import dataclass, field
from typing import Literal

SourceType = Literal[
    "public_web", "search_provider", "enrichment_provider",
    "email_verification", "outreach_export",
]


@dataclass(frozen=True)
class AdapterMeta:
    adapter_key: str
    display_name: str
    source_type: SourceType
    audit_event_type: str
    timeout_seconds: int = 30
    retry_class: str = "standard"
    terms_url: str | None = None
    cost_model: str | None = None
    is_certified: bool = False


@dataclass
class AdapterInput:
    operation_type: str
    payload: dict = field(default_factory=dict)

    def payload_json(self) -> str:
        return json.dumps(self.payload)


@dataclass
class AdapterOutput:
    success: bool
    data: str | None = None
    error: str | None = None
    latency_ms: int = 0

    def data_dict(self) -> dict:
        if self.data is None:
            return {}
        return json.loads(self.data)  # type: ignore[no-any-return]


class BaseAdapter(abc.ABC):
    META: AdapterMeta

    def execute(self, input_data: AdapterInput) -> AdapterOutput:
        start = time.monotonic()
        try:
            result = self._run(input_data)
            latency = int((time.monotonic() - start) * 1000)
            return AdapterOutput(
                success=True,
                data=json.dumps(result),
                latency_ms=latency,
            )
        except Exception as exc:  # noqa: BLE001
            latency = int((time.monotonic() - start) * 1000)
            return AdapterOutput(
                success=False,
                error=str(exc),
                latency_ms=latency,
            )

    @abc.abstractmethod
    def _run(self, input_data: AdapterInput) -> dict:
        """Execute the operation and return a result dict."""
