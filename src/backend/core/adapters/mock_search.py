"""
Acceptance Criteria:
- MockSearchAdapter implements BaseAdapter with META.adapter_key="mock_search".
- MockSearchAdapter.source_type is "search_provider".
- execute(input) with operation_type="search" returns deterministic candidates
  based on the query field in input.payload.
- Each candidate has url, title, and snippet fields.
- Candidate count is min(limit, 5) where limit defaults to 3.
- execute with unknown operation_type raises ValueError.
- MockSearchAdapter.META.is_certified is True.
"""

from core.adapters.base import AdapterInput, AdapterMeta, BaseAdapter


class MockSearchAdapter(BaseAdapter):
    META = AdapterMeta(
        adapter_key="mock_search",
        display_name="Mock Search Provider",
        source_type="search_provider",
        audit_event_type="search.mock.executed",
        timeout_seconds=10,
        retry_class="fast",
        is_certified=True,
    )

    def _run(self, input_data: AdapterInput) -> dict:
        if input_data.operation_type != "search":
            raise ValueError(
                f"MockSearchAdapter does not support operation '{input_data.operation_type}'"
            )
        query = str(input_data.payload.get("query", ""))
        limit = min(int(input_data.payload.get("limit", 3)), 5)
        candidates = [
            {
                "url": f"https://example-{i}.com/{query.lower().replace(' ', '-')}",
                "title": f"Result {i} for {query}",
                "snippet": f"Snippet {i}: information about {query}.",
            }
            for i in range(1, limit + 1)
        ]
        return {"query": query, "candidates": candidates, "total": len(candidates)}
