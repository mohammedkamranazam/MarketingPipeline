# Roadmap And Progress Tracker

This is the master execution tracker. Update this file after every meaningful implementation step.

## Current State

| Field | Value |
|---|---|
| Current phase | Phase 06: Classification, Extraction, And Enrichment |
| Last completed phase | Phase 05: Public Crawl And Raw Artifacts |
| Overall progress | 45% |
| MVP progress | 71% |
| Next ticket | `P06-T01` |

Progress is approximate and should be updated manually as phase tasks are completed.

## Phase Roadmap

| Phase | Name | Status | Progress | Usable Outcome | Phase File |
|---:|---|---|---:|---|---|
| 00 | Project Foundation | Done | 100% | Runnable FastAPI health-check app | [phase-00-foundation.md](phases/phase-00-foundation.md) |
| 01 | Data Foundation And Workspace API | Done | 100% | Persistent client and independent pipeline workspace API | [phase-01-data-workspace-api.md](phases/phase-01-data-workspace-api.md) |
| 02 | Document And Seed Lead Ingestion | Done | 100% | Upload pipeline-scoped documents and seed lead files, parse text/tables, create chunks/import rows | [phase-02-document-intelligence.md](phases/phase-02-document-intelligence.md) |
| 03 | Expert Config Review | Done | 100% | Human-approved ICP, enrichment, suppression, and outreach guardrails | [phase-03-expert-config-review.md](phases/phase-03-expert-config-review.md) |
| 04 | Source Registry And Policy | Done | 100% | Configured source, search, enrichment, verification, and outreach policy routing | [phase-04-source-registry-policy.md](phases/phase-04-source-registry-policy.md) |
| 05 | Public Crawl And Raw Artifacts | Done | 100% | Public pages and permitted search/profile artifacts collected into artifact store | [phase-05-public-crawl-artifacts.md](phases/phase-05-public-crawl-artifacts.md) |
| 06 | Classification, Extraction, And Enrichment | In Progress | 0% | Artifacts and seed rows become structured companies/signals/contacts/profile matches | [phase-06-classification-extraction.md](phases/phase-06-classification-extraction.md) |
| 07 | Lead Review And Export | Planned | 0% | Reviewed, scored, CRM/outreach-ready lead file | [phase-07-lead-review-export.md](phases/phase-07-lead-review-export.md) |
| 08 | Authenticated Crawl And HITL | Planned | 0% | Server-safe authenticated source collection | [phase-08-authenticated-crawl-hitl.md](phases/phase-08-authenticated-crawl-hitl.md) |
| 09 | Production Hardening | Planned | 0% | Observable, secure, release-ready v1 | [phase-09-production-hardening.md](phases/phase-09-production-hardening.md) |
| 10 | v2 Intelligence Layer | Planned | 0% | Hypothesis, ROI, temporal, and skeptic intelligence | [phase-10-v2-intelligence.md](phases/phase-10-v2-intelligence.md) |
| 11 | Enterprise Scale And Integrations | Planned | 0% | CRM/outreach outcome learning, scale, governance expansion | [phase-11-enterprise-scale-integrations.md](phases/phase-11-enterprise-scale-integrations.md) |

## Use-Case Coverage

| Use Case | Supported By | MVP Completion Gate |
|---|---|---|
| Multiple independent pipelines under one customer | Phases 01-09 | One client can run multiple isolated pipelines with separate settings, data, credentials, runs, diagnostics, and exports |
| Account discovery from ICP and public signals | Phases 01-07 | Evidence-backed companies, signals, contacts, review, and CRM-ready export |
| Seed lead enrichment from bid/platform lists | Phases 01-07 | Imported first-name/company rows resolved to profile/domain candidates, enriched with verified provider email, reviewed, and exported for outreach |
| Authenticated or restricted source expansion | Phases 08-09 | Approved authenticated sources with HITL recovery and audit controls |
| Direct CRM/outreach outcome loop | Phase 11 | CRM, marketing automation, and email engagement outcomes feed scoring and source quality |

## Release Gates

| Release | Required Phases | Exit Meaning |
|---|---|---|
| Developer Alpha | 00-01 | App and persistent workspace API work locally with multiple independent pipelines per client |
| Ingestion MVP | 00-03 | Pipeline-scoped client docs can become approved ICP config and seed lead files can be normalized for review |
| Discovery MVP | 00-05 | Safe public/search sources can be configured and collected per pipeline |
| Lead MVP | 00-07 | Evidence-backed discovery exports and verified seed-lead enrichment exports are usable per pipeline |
| Production v1 | 00-09 | Secure, observable, authenticated-source-capable system with pipeline-level runs, audit, metrics, and credential health |
| Intelligence v2 | 00-10 | ROI-aware intelligence layer is usable |
| Enterprise v3 | 00-11 | Scaled CRM/outreach integrations and outcome learning are usable |

## Production Readiness Gates

The following gates apply across phases and should be treated as enterprise-grade design constraints, not late cleanup:

- Phase 02 introduces shared run/job records, idempotency keys, worker leases, heartbeats, retry classes, and transactional outbox/inbox records before async workflows expand.
- Phase 04 introduces the external tool adapter contract so crawl, search, browser, enrichment, verification, LLM, CRM, and outreach providers are certified through typed mocks before live use.
- Phase 04 also introduces pipeline-scoped credential profiles, secret references, validation runs, expiry/rotation status, and config-area health checks before live provider calls are enabled.
- Phase 05 enforces crawl/browser/provider concurrency budgets and keeps managed crawl or browser services behind optional adapters.
- Phase 08 proves authenticated browser workflows can pause, resume, recover after worker restart, and preserve human-in-loop state.
- Phase 09 verifies trace storage, worker operations dashboards, container supply-chain gates, and the Prefect vs Temporal durability decision before Production v1.

## Execution Rules

- Execute phases in order.
- A later phase can be designed early but should not be implemented until previous phase tests pass.
- Phase outputs must be usable without waiting for future phases.
- Phase outputs must satisfy the diagnostic and UI evidence gates in [testable_blueprint.md](testable_blueprint.md).
- Pipeline-owned records must follow [multi-pipeline-plan.md](multi-pipeline-plan.md): every dataset, run, credential, source, artifact, extraction, review, and export is scoped by `client_id` and `pipeline_id`.
- If a phase grows too large, split it into sub-phases and update this roadmap.

## Immediate Next Steps

1. Start [Phase 06](phases/phase-06-classification-extraction.md).
2. Add classification/extraction/enrichment/verification ORM models and Alembic migration.
3. Add rule classifier and LLM provider mock adapter.
4. Add extraction schemas and workflow (companies, signals, contacts).
5. Add seed lead resolver, profile candidate ranking, enrichment adapter, email verification.
6. Add Phase 06 frontend: extraction views, profile comparison, enrichment monitor, evidence components.
