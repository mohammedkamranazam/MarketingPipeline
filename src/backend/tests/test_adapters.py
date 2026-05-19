"""
Tests for BaseAdapter contract and MockSearchAdapter.

Acceptance criteria tested:
- ADAPTER_REGISTRY maps adapter_key -> BaseAdapter subclass.
- get_adapter_class(key) returns the adapter class.
- get_adapter_class raises KeyError for unknown key.
- list_adapter_keys() returns sorted list of registered keys.
- All registered adapters are BaseAdapter subclasses.
- MockSearchAdapter.META.adapter_key == "mock_search".
- MockSearchAdapter.META.source_type == "search_provider".
- MockSearchAdapter.META.is_certified is True.
- execute with operation_type="search" returns deterministic candidates.
- Candidate count is min(limit, 5) where limit defaults to 3.
- execute with unknown operation_type raises ValueError.
"""

import pytest

from core.adapters.base import AdapterInput, BaseAdapter
from core.adapters.mock_search import MockSearchAdapter
from core.adapters.registry import ADAPTER_REGISTRY, get_adapter_class, list_adapter_keys

# ── Registry ──────────────────────────────────────────────────────────────────

def test_registry_contains_mock_search():
    assert "mock_search" in ADAPTER_REGISTRY


def test_get_adapter_class_returns_class():
    cls = get_adapter_class("mock_search")
    assert cls is MockSearchAdapter


def test_get_adapter_class_unknown_raises():
    with pytest.raises(KeyError, match="not registered"):
        get_adapter_class("does_not_exist")


def test_list_adapter_keys_sorted():
    keys = list_adapter_keys()
    assert keys == sorted(keys)
    assert "mock_search" in keys


def test_all_registered_adapters_are_base_subclasses():
    for cls in ADAPTER_REGISTRY.values():
        assert issubclass(cls, BaseAdapter)


# ── MockSearchAdapter meta ────────────────────────────────────────────────────

def test_mock_search_adapter_key():
    assert MockSearchAdapter.META.adapter_key == "mock_search"


def test_mock_search_source_type():
    assert MockSearchAdapter.META.source_type == "search_provider"


def test_mock_search_is_certified():
    assert MockSearchAdapter.META.is_certified is True


# ── MockSearchAdapter execute ─────────────────────────────────────────────────

def test_mock_search_default_limit():
    adapter = MockSearchAdapter()
    result = adapter.execute(AdapterInput(
        operation_type="search", payload={"query": "python"}
    ))
    assert result.success is True
    assert len(result.data_dict()["candidates"]) == 3


def test_mock_search_custom_limit():
    adapter = MockSearchAdapter()
    result = adapter.execute(AdapterInput(
        operation_type="search", payload={"query": "test", "limit": 5}
    ))
    assert len(result.data_dict()["candidates"]) == 5


def test_mock_search_limit_capped_at_5():
    adapter = MockSearchAdapter()
    result = adapter.execute(AdapterInput(
        operation_type="search", payload={"query": "test", "limit": 99}
    ))
    assert len(result.data_dict()["candidates"]) == 5


def test_mock_search_candidates_have_required_fields():
    adapter = MockSearchAdapter()
    result = adapter.execute(AdapterInput(
        operation_type="search", payload={"query": "fintech"}
    ))
    for candidate in result.data_dict()["candidates"]:
        assert "url" in candidate
        assert "title" in candidate
        assert "snippet" in candidate


def test_mock_search_candidates_are_deterministic():
    adapter = MockSearchAdapter()
    input_data = AdapterInput(operation_type="search", payload={"query": "saas"})
    r1 = adapter.execute(input_data)
    r2 = adapter.execute(input_data)
    assert r1.data_dict()["candidates"] == r2.data_dict()["candidates"]


def test_mock_search_unknown_operation_returns_failure():
    adapter = MockSearchAdapter()
    result = adapter.execute(AdapterInput(operation_type="crawl", payload={}))
    assert result.success is False
    assert result.error is not None
    assert "does not support" in result.error


def test_mock_search_execute_sets_latency():
    adapter = MockSearchAdapter()
    result = adapter.execute(AdapterInput(
        operation_type="search", payload={"query": "test"}
    ))
    assert result.latency_ms >= 0
