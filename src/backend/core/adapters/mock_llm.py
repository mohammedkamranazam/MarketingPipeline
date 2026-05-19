"""
Acceptance Criteria:
- MockLLMAdapter is a certified BaseAdapter with adapter_key="mock_llm",
  source_type="enrichment_provider".
- Supports operation_type="classify": returns page_type, relevance_score, confidence.
- Supports operation_type="extract_company": returns name, domain, industry,
  employee_count, location, description, confidence, evidence_text.
- Supports operation_type="extract_signals": returns list of signal dicts with
  signal_type, value, confidence, evidence_text.
- Supports operation_type="extract_contacts": returns list of contact dicts with
  first_name, last_name, title, linkedin_url, confidence.
- Supports operation_type="summarize": returns summary_text and citations list.
- Unknown operation returns failure via BaseAdapter exception path.
- Responses are deterministic based on payload content.
- No raw secrets. No email/phone invented for contacts (LLM cannot create PII).
"""
from __future__ import annotations

import hashlib

from core.adapters.base import AdapterInput, AdapterMeta, BaseAdapter

_PAGE_TYPES = ["company_homepage", "team_page", "blog_post", "pricing_page", "about_page"]


def _stable_index(text: str, n: int) -> int:
    digest = int(hashlib.md5(text.encode()).hexdigest(), 16)  # noqa: S324
    return digest % n


class MockLLMAdapter(BaseAdapter):
    META = AdapterMeta(
        adapter_key="mock_llm",
        display_name="Mock LLM Classifier/Extractor",
        source_type="enrichment_provider",
        audit_event_type="llm.mock.executed",
        timeout_seconds=30,
        retry_class="standard",
        is_certified=True,
    )

    def _run(self, input_data: AdapterInput) -> dict:
        op = input_data.operation_type
        payload = input_data.payload

        if op == "classify":
            return self._classify(payload)
        if op == "extract_company":
            return self._extract_company(payload)
        if op == "extract_signals":
            return self._extract_signals(payload)
        if op == "extract_contacts":
            return self._extract_contacts(payload)
        if op == "summarize":
            return self._summarize(payload)
        raise ValueError(f"MockLLMAdapter does not support operation '{op}'")

    def _classify(self, payload: dict) -> dict:
        content = str(payload.get("content", ""))
        url = str(payload.get("url", ""))
        seed = url or content[:64]
        page_type = _PAGE_TYPES[_stable_index(seed, len(_PAGE_TYPES))]
        is_relevant = any(
            kw in content.lower()
            for kw in ["saas", "software", "platform", "enterprise", "cloud", "api"]
        )
        relevance_score = 0.85 if is_relevant else 0.4
        return {
            "page_type": page_type,
            "relevance_score": relevance_score,
            "confidence": 0.9,
            "classifier": "mock_llm",
        }

    def _extract_company(self, payload: dict) -> dict:
        content = str(payload.get("content", ""))
        url = str(payload.get("url", ""))
        domain = url.split("/")[2] if url.startswith("http") else None
        slug = domain.replace("www.", "").split(".")[0].title() if domain else "Example Corp"
        return {
            "name": f"{slug} Inc",
            "domain": domain,
            "industry": "Software",
            "employee_count": 150,
            "location": "San Francisco, CA",
            "description": f"A software company operating at {domain or 'example.com'}.",
            "confidence": 0.82,
            "evidence_url": url or None,
            "evidence_text": content[:200] if content else None,
            "extractor": "mock_llm",
        }

    def _extract_signals(self, payload: dict) -> dict:
        content = str(payload.get("content", "")).lower()
        signals = []
        if "hiring" in content or "job" in content or "career" in content:
            signals.append({
                "signal_type": "hiring",
                "value": "Actively hiring",
                "confidence": 0.88,
                "evidence_text": "Found hiring-related keywords",
                "extractor": "mock_llm",
            })
        if "funding" in content or "series" in content or "raised" in content:
            signals.append({
                "signal_type": "funding",
                "value": "Recent funding activity",
                "confidence": 0.80,
                "evidence_text": "Found funding-related keywords",
                "extractor": "mock_llm",
            })
        if not signals:
            signals.append({
                "signal_type": "web_presence",
                "value": "Public web presence detected",
                "confidence": 0.70,
                "evidence_text": None,
                "extractor": "mock_llm",
            })
        return {"signals": signals}

    def _extract_contacts(self, payload: dict) -> dict:
        content = str(payload.get("content", ""))
        url = str(payload.get("url", ""))
        domain = url.split("/")[2] if url.startswith("http") else "example.com"
        slug = domain.replace("www.", "").split(".")[0].title()
        contacts = [
            {
                "first_name": "Alex",
                "last_name": slug,
                "title": "CTO",
                "linkedin_url": None,
                "confidence": 0.75,
                "evidence_url": url or None,
                "evidence_text": content[:100] if content else None,
                "extractor": "mock_llm",
            }
        ]
        return {"contacts": contacts}

    def _summarize(self, payload: dict) -> dict:
        company_name = str(payload.get("company_name", "the company"))
        evidence_urls = payload.get("evidence_urls", [])
        citations = [{"url": u, "text": f"Source: {u}"} for u in evidence_urls[:3]]
        summary = (
            f"{company_name} is an enterprise software company providing cloud-based"
            f" solutions to mid-market and enterprise customers."
            f" Based on crawled public sources, the company shows strong hiring and"
            f" growth signals."
        )
        return {
            "summary_text": summary,
            "citations": citations,
            "generator": "mock_llm",
        }
