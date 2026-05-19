"""
Acceptance Criteria:
- MockEmailVerifierAdapter is a certified BaseAdapter with
  adapter_key="mock_email_verifier", source_type="email_verification".
- Supports operation_type="verify_email": accepts email, returns
  verification_status (verified/risky/invalid/unknown), deliverability,
  is_risky, reason, provenance, provider_request_id.
- Deterministic: emails ending in @risky.com → risky; @invalid.com → invalid;
  @unknown.com → unknown; all others → verified.
- provenance and provider_request_id always present.
- Unknown operation raises ValueError.
- No raw secrets.
"""
from __future__ import annotations

import uuid

from core.adapters.base import AdapterInput, AdapterMeta, BaseAdapter

_RULES: list[tuple[str, str, str, bool, str]] = [
    ("@risky.com", "risky", "risky", True, "Domain flagged as risky"),
    ("@invalid.com", "invalid", "undeliverable", False, "Domain does not accept mail"),
    ("@unknown.com", "unknown", "unknown", False, "Cannot verify this domain"),
]


class MockEmailVerifierAdapter(BaseAdapter):
    META = AdapterMeta(
        adapter_key="mock_email_verifier",
        display_name="Mock Email Verification Provider",
        source_type="email_verification",
        audit_event_type="email_verification.mock.executed",
        timeout_seconds=10,
        retry_class="fast",
        is_certified=True,
    )

    def _run(self, input_data: AdapterInput) -> dict:
        op = input_data.operation_type
        if op != "verify_email":
            raise ValueError(f"MockEmailVerifierAdapter does not support operation '{op}'")

        email = str(input_data.payload.get("email", ""))
        provider_request_id = str(uuid.uuid4())

        for suffix, status, deliverability, is_risky, reason in _RULES:
            if email.endswith(suffix):
                return {
                    "email": email,
                    "verification_status": status,
                    "deliverability": deliverability,
                    "is_risky": is_risky,
                    "reason": reason,
                    "provenance": f"mock_email_verifier:{email}",
                    "provider_request_id": provider_request_id,
                }

        return {
            "email": email,
            "verification_status": "verified",
            "deliverability": "deliverable",
            "is_risky": False,
            "reason": None,
            "provenance": f"mock_email_verifier:{email}",
            "provider_request_id": provider_request_id,
        }
