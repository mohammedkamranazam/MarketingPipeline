"""
Acceptance Criteria:
- MockCrawlAdapter implements BaseAdapter with META.adapter_key="mock_crawl".
- MockCrawlAdapter.META.source_type is "public_web".
- MockCrawlAdapter.META.is_certified is True.
- execute with operation_type="fetch" returns deterministic page content based on url.
- execute with operation_type="robots" returns a mock robots.txt response.
- execute with unknown operation_type raises ValueError (caught by BaseAdapter -> success=False).
"""

from core.adapters.base import AdapterInput, AdapterMeta, BaseAdapter


class MockCrawlAdapter(BaseAdapter):
    META = AdapterMeta(
        adapter_key="mock_crawl",
        display_name="Mock Public Web Crawler",
        source_type="public_web",
        audit_event_type="crawl.mock.executed",
        timeout_seconds=30,
        retry_class="transient",
        is_certified=True,
    )

    def _run(self, input_data: AdapterInput) -> dict:
        op = input_data.operation_type
        url = str(input_data.payload.get("url", "https://example.com"))
        if op == "fetch":
            slug = url.rstrip("/").split("/")[-1] or "home"
            return {
                "url": url,
                "status_code": 200,
                "mime_type": "text/html",
                "content": (
                    f"<html><head><title>Mock Page: {slug}</title></head>"
                    f"<body><h1>{slug}</h1><p>Mock crawl content for {url}.</p></body></html>"
                ),
                "content_hash": _stable_hash(url),
                "size_bytes": 256,
            }
        if op == "robots":
            return {
                "url": f"{url.rstrip('/')}/robots.txt",
                "status_code": 200,
                "content": "User-agent: *\nDisallow: /private/\nAllow: /\n",
            }
        raise ValueError(
            f"MockCrawlAdapter does not support operation '{op}'"
        )


def _stable_hash(url: str) -> str:
    """Deterministic short hash for test reproducibility (not cryptographic)."""
    return format(hash(url) & 0xFFFFFFFFFFFFFFFF, "016x")
