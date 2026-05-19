"""
Tests for source API routes.

Acceptance criteria tested:
- POST /sources returns 201 with SourceConnectorResponse.
- GET /sources returns list; ?source_type= filter works.
- GET /sources/{id} returns 404 when not found.
- PATCH /sources/{id} returns 422 when connector not found.
- DELETE /sources/{id} returns 204; returns 404 for unknown id.
- POST /sources/{id}/test returns SourceTestResult.
- POST /policy-rules returns 201.
- GET /policy-rules returns list.
- DELETE /policy-rules/{id} returns 204; 404 for unknown.
- POST /policy/decide returns PolicyDecisionResponse.
- POST /url-candidates returns 201; idempotent returns 200.
- GET /url-candidates returns list; ?status= filter works.
- POST /credentials returns 201 with CredentialProfileResponse.
- GET /credentials returns list.
- GET /credentials/{id} returns 404 for unknown.
- PATCH /credentials/{id} returns 422 for unknown.
- POST /credentials/{id}/validate returns CredentialValidationRunResponse.
- GET /adapters returns list.
- POST /adapters returns 201.
- Pipeline isolation across connectors, rules, and credentials.
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


def _connector_body(**kwargs) -> dict:
    defaults = dict(source_type="public_web", name="My Source", adapter_key="mock_search")
    defaults.update(kwargs)
    return defaults


def _rule_body(**kwargs) -> dict:
    defaults = dict(
        entity_type="url_pattern",
        pattern="https://allowed.com",
        decision="allow",
    )
    defaults.update(kwargs)
    return defaults


def _credential_body(**kwargs) -> dict:
    defaults = dict(
        name="My Cred",
        adapter_key="mock_search",
        secret_reference="env:MY_API_KEY",
        scopes=["read"],
    )
    defaults.update(kwargs)
    return defaults


def _adapter_body(**kwargs) -> dict:
    defaults = dict(
        adapter_key=f"adapter_{uuid.uuid4().hex[:8]}",
        display_name="Test Adapter",
        source_type="search_provider",
        audit_event_type="search.test.executed",
        is_certified=True,
    )
    defaults.update(kwargs)
    return defaults


# ── SourceConnector ───────────────────────────────────────────────────────────

def test_create_source_connector_201(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    r = api_client.post(f"{base}/sources", json=_connector_body())
    assert r.status_code == 201
    data = r.json()
    assert data["pipeline_id"] == p["id"]
    assert data["status"] == "active"
    assert "id" in data


def test_list_source_connectors(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    api_client.post(f"{base}/sources", json=_connector_body(name="S1"))
    api_client.post(f"{base}/sources", json=_connector_body(name="S2", source_type="search_provider"))  # noqa: E501
    r = api_client.get(f"{base}/sources")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_list_source_connectors_type_filter(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    api_client.post(f"{base}/sources", json=_connector_body(name="A", source_type="public_web"))
    api_client.post(f"{base}/sources", json=_connector_body(name="B", source_type="search_provider"))  # noqa: E501
    r = api_client.get(f"{base}/sources", params={"source_type": "public_web"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["source_type"] == "public_web"


def test_get_source_connector_404(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    r = api_client.get(f"{base}/sources/{uuid.uuid4()}")
    assert r.status_code == 404


def test_update_source_connector(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    created = api_client.post(f"{base}/sources", json=_connector_body()).json()
    r = api_client.patch(f"{base}/sources/{created['id']}", json={"name": "Renamed"})
    assert r.status_code == 200
    assert r.json()["name"] == "Renamed"


def test_update_source_connector_422_not_found(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    r = api_client.patch(f"{base}/sources/{uuid.uuid4()}", json={"name": "x"})
    assert r.status_code == 422


def test_delete_source_connector_204(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    created = api_client.post(f"{base}/sources", json=_connector_body()).json()
    r = api_client.delete(f"{base}/sources/{created['id']}")
    assert r.status_code == 204


def test_delete_source_connector_404(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    r = api_client.delete(f"{base}/sources/{uuid.uuid4()}")
    assert r.status_code == 404


def test_test_source_connector(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    api_client.post("/adapters", json=_adapter_body(
        adapter_key="mock_search",
        display_name="Mock Search",
        source_type="search_provider",
        audit_event_type="search.mock.executed",
        is_certified=True,
    ))
    created = api_client.post(f"{base}/sources", json=_connector_body()).json()
    r = api_client.post(f"{base}/sources/{created['id']}/test")
    assert r.status_code == 200
    data = r.json()
    assert "success" in data
    assert "adapter_key" in data


# ── PolicyRules ───────────────────────────────────────────────────────────────

def test_create_policy_rule_201(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    r = api_client.post(f"{base}/policy-rules", json=_rule_body())
    assert r.status_code == 201
    data = r.json()
    assert data["decision"] == "allow"
    assert data["pipeline_id"] == p["id"]


def test_list_policy_rules(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    api_client.post(f"{base}/policy-rules", json=_rule_body(priority=100))
    api_client.post(f"{base}/policy-rules", json=_rule_body(priority=50))
    r = api_client.get(f"{base}/policy-rules")
    assert r.status_code == 200
    rules = r.json()
    assert len(rules) == 2
    assert rules[0]["priority"] == 50


def test_delete_policy_rule_204(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    created = api_client.post(f"{base}/policy-rules", json=_rule_body()).json()
    r = api_client.delete(f"{base}/policy-rules/{created['id']}")
    assert r.status_code == 204


def test_delete_policy_rule_404(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    r = api_client.delete(f"{base}/policy-rules/{uuid.uuid4()}")
    assert r.status_code == 404


# ── Policy decide ─────────────────────────────────────────────────────────────

def test_decide_policy_allow(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    api_client.post(f"{base}/policy-rules", json=_rule_body(
        entity_type="url_pattern", pattern="https://good.com", decision="allow"
    ))
    r = api_client.post(f"{base}/policy/decide", json={
        "operation_type": "fetch",
        "url": "https://good.com/page",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["decision"] == "allow"
    assert data["matched_rule_id"] is not None


def test_decide_policy_default_review(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    r = api_client.post(f"{base}/policy/decide", json={
        "operation_type": "fetch",
        "url": "https://unknown.org",
    })
    assert r.status_code == 200
    assert r.json()["decision"] == "review"


# ── URLCandidates ─────────────────────────────────────────────────────────────

def test_submit_url_candidate_201(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    r = api_client.post(f"{base}/url-candidates", json={"url": "https://ex.com"})
    assert r.status_code == 201
    data = r.json()
    assert data["url"] == "https://ex.com"
    assert "policy_decision" in data


def test_submit_url_candidate_idempotent(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    r1 = api_client.post(f"{base}/url-candidates", json={"url": "https://ex.com"})
    r2 = api_client.post(f"{base}/url-candidates", json={"url": "https://ex.com"})
    assert r1.json()["id"] == r2.json()["id"]


def test_list_url_candidates_status_filter(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    api_client.post(f"{base}/policy-rules", json=_rule_body(
        entity_type="url_pattern", pattern="https://ok.com", decision="allow"
    ))
    api_client.post(f"{base}/url-candidates", json={"url": "https://ok.com/1"})
    api_client.post(f"{base}/url-candidates", json={"url": "https://other.com"})
    r = api_client.get(f"{base}/url-candidates", params={"status": "allow"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["policy_decision"] == "allow"


# ── CredentialProfiles ────────────────────────────────────────────────────────

def test_create_credential_profile_201(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    r = api_client.post(f"{base}/credentials", json=_credential_body())
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "active"
    assert data["pipeline_id"] == p["id"]


def test_list_credentials(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    api_client.post(f"{base}/credentials", json=_credential_body(name="A"))
    api_client.post(f"{base}/credentials", json=_credential_body(name="B"))
    r = api_client.get(f"{base}/credentials")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_get_credential_404(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    r = api_client.get(f"{base}/credentials/{uuid.uuid4()}")
    assert r.status_code == 404


def test_update_credential_profile(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    created = api_client.post(f"{base}/credentials", json=_credential_body()).json()
    r = api_client.patch(f"{base}/credentials/{created['id']}", json={"status": "expiring"})
    assert r.status_code == 200
    assert r.json()["status"] == "expiring"


def test_update_credential_422_not_found(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    r = api_client.patch(f"{base}/credentials/{uuid.uuid4()}", json={"status": "expiring"})
    assert r.status_code == 422


def test_validate_credential(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    created = api_client.post(f"{base}/credentials", json=_credential_body()).json()
    r = api_client.post(f"{base}/credentials/{created['id']}/validate")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert data["status"] in ("passed", "failed")


def test_validate_credential_404(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    base = _base(c["id"], p["id"])
    r = api_client.post(f"{base}/credentials/{uuid.uuid4()}/validate")
    assert r.status_code == 404


# ── AdapterRegistry ───────────────────────────────────────────────────────────

def test_list_adapters(api_client):
    r = api_client.get("/adapters")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_register_adapter_201(api_client):
    body = _adapter_body()
    r = api_client.post("/adapters", json=body)
    assert r.status_code == 201
    data = r.json()
    assert data["adapter_key"] == body["adapter_key"]
    assert data["is_certified"] is True


def test_register_adapter_upserts(api_client):
    key = f"adapter_{uuid.uuid4().hex[:8]}"
    api_client.post("/adapters", json=_adapter_body(adapter_key=key, display_name="First"))
    api_client.post("/adapters", json=_adapter_body(adapter_key=key, display_name="Updated"))
    r = api_client.get("/adapters")
    adapters = r.json()
    match = next((a for a in adapters if a["adapter_key"] == key), None)
    assert match is not None
    assert match["display_name"] == "Updated"


# ── Pipeline isolation ────────────────────────────────────────────────────────

def test_connectors_pipeline_isolation(api_client):
    c = _create_client(api_client)
    p_a = _create_pipeline(api_client, c["id"])
    p_b = _create_pipeline(api_client, c["id"])
    api_client.post(f"{_base(c['id'], p_a['id'])}/sources", json=_connector_body())
    r = api_client.get(f"{_base(c['id'], p_b['id'])}/sources")
    assert r.status_code == 200
    assert r.json() == []


def test_policy_rules_pipeline_isolation(api_client):
    c = _create_client(api_client)
    p_a = _create_pipeline(api_client, c["id"])
    p_b = _create_pipeline(api_client, c["id"])
    api_client.post(f"{_base(c['id'], p_a['id'])}/policy-rules", json=_rule_body())
    r = api_client.get(f"{_base(c['id'], p_b['id'])}/policy-rules")
    assert r.status_code == 200
    assert r.json() == []


def test_credentials_pipeline_isolation(api_client):
    c = _create_client(api_client)
    p_a = _create_pipeline(api_client, c["id"])
    p_b = _create_pipeline(api_client, c["id"])
    api_client.post(f"{_base(c['id'], p_a['id'])}/credentials", json=_credential_body())
    r = api_client.get(f"{_base(c['id'], p_b['id'])}/credentials")
    assert r.status_code == 200
    assert r.json() == []
