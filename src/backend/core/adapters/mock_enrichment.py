"""
Acceptance Criteria:
- MockEnrichmentAdapter is a certified BaseAdapter with adapter_key="mock_enrichment",
  source_type="enrichment_provider".
- Supports operation_type="enrich_contact": returns first_name, last_name, email,
  phone, title, company, linkedin_url, cost_credits, provenance, provider_request_id.
- Email returned is a masked placeholder — NEVER a guessed real address.
- provenance and provider_request_id are always present.
- Unknown operation raises ValueError.
- No raw secrets.
"""
from __future__ import annotations

import hashlib
import uuid

from core.adapters.base import AdapterInput, AdapterMeta, BaseAdapter


def _masked_email(first: str, domain: str) -> str:
    """Return a deterministic masked placeholder, not a real address."""
    tag = hashlib.md5(f"{first}{domain}".encode()).hexdigest()[:6]  # noqa: S324
    return f"{first.lower()[:1]}***{tag}@{domain}"


class MockEnrichmentAdapter(BaseAdapter):
    META = AdapterMeta(
        adapter_key="mock_enrichment",
        display_name="Mock Contact Enrichment Provider",
        source_type="enrichment_provider",
        audit_event_type="enrichment.mock.executed",
        timeout_seconds=15,
        retry_class="standard",
        is_certified=True,
    )

    def _run(self, input_data: AdapterInput) -> dict:
        op = input_data.operation_type
        if op != "enrich_contact":
            raise ValueError(f"MockEnrichmentAdapter does not support operation '{op}'")

        payload = input_data.payload
        first_name = str(payload.get("first_name", "Alex"))
        last_name = str(payload.get("last_name", "Smith"))
        company = str(payload.get("company", "Example Corp"))
        domain = str(payload.get("domain", "example.com"))
        title = str(payload.get("title", "VP Engineering"))
        provider_request_id = str(uuid.uuid4())

        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": _masked_email(first_name, domain),
            "phone": None,
            "title": title,
            "company": company,
            "linkedin_url": None,
            "cost_credits": 1.0,
            "provenance": f"mock_enrichment:{domain}:{first_name}",
            "provider_request_id": provider_request_id,
            "status": "completed",
        }
