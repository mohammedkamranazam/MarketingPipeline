"""
Tests for review API routes.

Acceptance criteria tested:
- POST /review-items returns 201 with ReviewItemResponse.
- GET /review-items returns list; ?status= filter works.
- GET /review-items/{id} returns 404 when not found.
- POST /review-items/{id}/decide returns 200 with updated item.
- POST /review-items/{id}/decide returns 422 when item not pending.
- GET /icp-config returns 404 when no config exists.
- PUT /icp-config returns 200/201 with config; repeated PUT returns updated.
- POST /suppression-rules returns 201.
- GET /suppression-rules lists rules.
- DELETE /suppression-rules/{id} returns 204.
- DELETE /suppression-rules/{id} returns 404 for unknown id.
- PUT /guardrails returns 200/201.
- GET /guardrails lists guardrails.
- GET /audit-log returns audit entries.
- Cross-pipeline isolation for review items and suppression rules.
"""

import uuid


def _create_client(api_client) -> dict:
    r = api_client.post(
        "/clients",
        json={"name": f"C-{uuid.uuid4()}", "slug": f"c-{uuid.uuid4()}", "status": "active"},
    )
    assert r.status_code == 201
    return r.json()


def _create_pipeline(api_client, client_id: str) -> dict:
    r = api_client.post(
        f"/clients/{client_id}/pipelines",
        json={
            "name": f"P-{uuid.uuid4()}",
            "slug": f"p-{uuid.uuid4()}",
            "lane": "discovery",
            "status": "active",
        },
    )
    assert r.status_code == 201
    return r.json()


def _base(client_id: str, pipeline_id: str) -> str:
    return f"/clients/{client_id}/pipelines/{pipeline_id}"


def _review_item_body(**kwargs) -> dict:
    defaults = dict(
        item_type="company_name",
        content="Acme Corp",
        evidence_text="Found on page 1",
        confidence=0.9,
    )
    defaults.update(kwargs)
    return defaults


def _icp_body(**kwargs) -> dict:
    defaults = dict(
        vertical="SaaS",
        titles=["CTO"],
        geographies=["US"],
        signals=["hiring"],
        exclusions=[],
        activated_by="admin",
    )
    defaults.update(kwargs)
    return defaults


# ── ReviewItems ───────────────────────────────────────────────────────────────

def test_create_review_item_201(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.post(f"{_base(c['id'], p['id'])}/review-items", json=_review_item_body())
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "pending"
    assert data["item_type"] == "company_name"


def test_list_review_items(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    api_client.post(f"{_base(c['id'], p['id'])}/review-items", json=_review_item_body())
    api_client.post(
        f"{_base(c['id'], p['id'])}/review-items", json=_review_item_body(content="Beta")
    )
    r = api_client.get(f"{_base(c['id'], p['id'])}/review-items")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_list_review_items_status_filter(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r1 = api_client.post(
        f"{_base(c['id'], p['id'])}/review-items", json=_review_item_body()
    ).json()
    api_client.post(
        f"{_base(c['id'], p['id'])}/review-items/{r1['id']}/decide",
        json={"status": "approved"},
    )
    api_client.post(f"{_base(c['id'], p['id'])}/review-items", json=_review_item_body(content="B"))
    pending = api_client.get(f"{_base(c['id'], p['id'])}/review-items?status=pending").json()
    approved = api_client.get(f"{_base(c['id'], p['id'])}/review-items?status=approved").json()
    assert len(pending) == 1
    assert len(approved) == 1


def test_get_review_item_404(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.get(f"{_base(c['id'], p['id'])}/review-items/{uuid.uuid4()}")
    assert r.status_code == 404


def test_decide_review_item_approved(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    item = api_client.post(
        f"{_base(c['id'], p['id'])}/review-items", json=_review_item_body()
    ).json()
    r = api_client.post(
        f"{_base(c['id'], p['id'])}/review-items/{item['id']}/decide",
        json={"status": "approved", "actor_id": "user1"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "approved"


def test_decide_review_item_edited_and_approved(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    item = api_client.post(
        f"{_base(c['id'], p['id'])}/review-items", json=_review_item_body()
    ).json()
    r = api_client.post(
        f"{_base(c['id'], p['id'])}/review-items/{item['id']}/decide",
        json={"status": "edited_and_approved", "edited_content": "Fixed Corp"},
    )
    assert r.status_code == 200
    assert r.json()["edited_content"] == "Fixed Corp"


def test_decide_review_item_not_pending_returns_422(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    item = api_client.post(
        f"{_base(c['id'], p['id'])}/review-items", json=_review_item_body()
    ).json()
    api_client.post(
        f"{_base(c['id'], p['id'])}/review-items/{item['id']}/decide",
        json={"status": "approved"},
    )
    r = api_client.post(
        f"{_base(c['id'], p['id'])}/review-items/{item['id']}/decide",
        json={"status": "rejected"},
    )
    assert r.status_code == 422


# ── ICP Config ────────────────────────────────────────────────────────────────

def test_get_icp_config_404_when_missing(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.get(f"{_base(c['id'], p['id'])}/icp-config")
    assert r.status_code == 404


def test_put_icp_config_creates(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.put(f"{_base(c['id'], p['id'])}/icp-config", json=_icp_body())
    assert r.status_code == 200
    data = r.json()
    assert data["vertical"] == "SaaS"
    assert data["titles"] == ["CTO"]


def test_put_icp_config_updates(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    api_client.put(f"{_base(c['id'], p['id'])}/icp-config", json=_icp_body())
    r = api_client.put(f"{_base(c['id'], p['id'])}/icp-config", json=_icp_body(vertical="FinTech"))
    assert r.status_code == 200
    assert r.json()["vertical"] == "FinTech"


def test_get_icp_config_after_put(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    api_client.put(f"{_base(c['id'], p['id'])}/icp-config", json=_icp_body())
    r = api_client.get(f"{_base(c['id'], p['id'])}/icp-config")
    assert r.status_code == 200
    assert r.json()["vertical"] == "SaaS"


# ── Suppression Rules ─────────────────────────────────────────────────────────

def test_add_suppression_rule_201(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.post(
        f"{_base(c['id'], p['id'])}/suppression-rules",
        json={"rule_type": "domain", "value": "spam.com"},
    )
    assert r.status_code == 201
    assert r.json()["value"] == "spam.com"


def test_list_suppression_rules(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    api_client.post(
        f"{_base(c['id'], p['id'])}/suppression-rules",
        json={"rule_type": "domain", "value": "a.com"},
    )
    api_client.post(
        f"{_base(c['id'], p['id'])}/suppression-rules",
        json={"rule_type": "email", "value": "b@c.com"},
    )
    r = api_client.get(f"{_base(c['id'], p['id'])}/suppression-rules")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_delete_suppression_rule_204(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    rule = api_client.post(
        f"{_base(c['id'], p['id'])}/suppression-rules",
        json={"rule_type": "domain", "value": "evil.com"},
    ).json()
    r = api_client.delete(f"{_base(c['id'], p['id'])}/suppression-rules/{rule['id']}")
    assert r.status_code == 204
    assert api_client.get(f"{_base(c['id'], p['id'])}/suppression-rules").json() == []


def test_delete_suppression_rule_404(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.delete(f"{_base(c['id'], p['id'])}/suppression-rules/{uuid.uuid4()}")
    assert r.status_code == 404


# ── Guardrails ────────────────────────────────────────────────────────────────

def test_put_guardrail_creates(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.put(
        f"{_base(c['id'], p['id'])}/guardrails",
        json={"guardrail_type": "enrichment_provider", "enabled": True, "approved_by": "admin"},
    )
    assert r.status_code == 200
    assert r.json()["enabled"] is True


def test_put_guardrail_updates(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    api_client.put(
        f"{_base(c['id'], p['id'])}/guardrails",
        json={"guardrail_type": "enrichment_provider", "enabled": True, "approved_by": "admin"},
    )
    r = api_client.put(
        f"{_base(c['id'], p['id'])}/guardrails",
        json={"guardrail_type": "enrichment_provider", "enabled": False},
    )
    assert r.status_code == 200
    assert r.json()["enabled"] is False


def test_list_guardrails(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    api_client.put(
        f"{_base(c['id'], p['id'])}/guardrails",
        json={"guardrail_type": "enrichment_provider", "enabled": True},
    )
    api_client.put(
        f"{_base(c['id'], p['id'])}/guardrails",
        json={"guardrail_type": "email_verification", "enabled": False},
    )
    r = api_client.get(f"{_base(c['id'], p['id'])}/guardrails")
    assert r.status_code == 200
    assert len(r.json()) == 2


# ── Audit Log ─────────────────────────────────────────────────────────────────

def test_audit_log_records_mutations(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    api_client.post(f"{_base(c['id'], p['id'])}/review-items", json=_review_item_body())
    api_client.put(f"{_base(c['id'], p['id'])}/icp-config", json=_icp_body())
    r = api_client.get(f"{_base(c['id'], p['id'])}/audit-log")
    assert r.status_code == 200
    assert len(r.json()) >= 2


# ── Pipeline isolation ────────────────────────────────────────────────────────

def test_review_items_isolation_across_pipelines(api_client):
    c = _create_client(api_client)
    p_a = _create_pipeline(api_client, c["id"])
    p_b = _create_pipeline(api_client, c["id"])
    api_client.post(f"{_base(c['id'], p_a['id'])}/review-items", json=_review_item_body())
    r = api_client.get(f"{_base(c['id'], p_b['id'])}/review-items")
    assert r.json() == []


def test_suppression_rules_isolation_across_pipelines(api_client):
    c = _create_client(api_client)
    p_a = _create_pipeline(api_client, c["id"])
    p_b = _create_pipeline(api_client, c["id"])
    api_client.post(
        f"{_base(c['id'], p_a['id'])}/suppression-rules",
        json={"rule_type": "domain", "value": "x.com"},
    )
    r = api_client.get(f"{_base(c['id'], p_b['id'])}/suppression-rules")
    assert r.json() == []
