"""
Acceptance Criteria:
- ADAPTER_REGISTRY maps adapter_key -> BaseAdapter subclass.
- get_adapter(key) returns the adapter class or raises KeyError.
- list_adapter_keys() returns sorted list of registered keys.
- All registered adapters must be BaseAdapter subclasses.
"""

from core.adapters.base import BaseAdapter
from core.adapters.mock_crawl import MockCrawlAdapter
from core.adapters.mock_email_verifier import MockEmailVerifierAdapter
from core.adapters.mock_enrichment import MockEnrichmentAdapter
from core.adapters.mock_llm import MockLLMAdapter
from core.adapters.mock_search import MockSearchAdapter

ADAPTER_REGISTRY: dict[str, type[BaseAdapter]] = {
    MockSearchAdapter.META.adapter_key: MockSearchAdapter,
    MockCrawlAdapter.META.adapter_key: MockCrawlAdapter,
    MockLLMAdapter.META.adapter_key: MockLLMAdapter,
    MockEnrichmentAdapter.META.adapter_key: MockEnrichmentAdapter,
    MockEmailVerifierAdapter.META.adapter_key: MockEmailVerifierAdapter,
}


def get_adapter_class(key: str) -> type[BaseAdapter]:
    if key not in ADAPTER_REGISTRY:
        raise KeyError(f"Adapter '{key}' is not registered")
    return ADAPTER_REGISTRY[key]


def list_adapter_keys() -> list[str]:
    return sorted(ADAPTER_REGISTRY.keys())
