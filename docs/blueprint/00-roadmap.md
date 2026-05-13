# Roadmap And Progress Tracker

This is the master execution tracker. Update this file after every meaningful implementation step.

## Current State

| Field | Value |
|---|---|
| Current phase | Phase 01: Data Foundation And Workspace API |
| Last completed phase | Phase 00: Project Foundation |
| Overall progress | 8% |
| MVP progress | 11% |
| Next ticket | `P01-T01` |

Progress is approximate and should be updated manually as phase tasks are completed.

## Phase Roadmap

| Phase | Name | Status | Progress | Usable Outcome | Phase File |
|---:|---|---|---:|---|---|
| 00 | Project Foundation | Done | 100% | Runnable FastAPI health-check app | [phase-00-foundation.md](phases/phase-00-foundation.md) |
| 01 | Data Foundation And Workspace API | Ready | 0% | Persistent client workspace API | [phase-01-data-workspace-api.md](phases/phase-01-data-workspace-api.md) |
| 02 | Document Intelligence | Planned | 0% | Upload documents, parse text, create chunks | [phase-02-document-intelligence.md](phases/phase-02-document-intelligence.md) |
| 03 | Expert Config Review | Planned | 0% | Human-approved ICP config | [phase-03-expert-config-review.md](phases/phase-03-expert-config-review.md) |
| 04 | Source Registry And Policy | Planned | 0% | Configured sources and policy routing | [phase-04-source-registry-policy.md](phases/phase-04-source-registry-policy.md) |
| 05 | Public Crawl And Raw Artifacts | Planned | 0% | Public pages collected into artifact store | [phase-05-public-crawl-artifacts.md](phases/phase-05-public-crawl-artifacts.md) |
| 06 | Classification And Extraction | Planned | 0% | Artifacts become structured companies/signals/contacts | [phase-06-classification-extraction.md](phases/phase-06-classification-extraction.md) |
| 07 | Lead Review And Export | Planned | 0% | Reviewed, scored, CRM-ready lead file | [phase-07-lead-review-export.md](phases/phase-07-lead-review-export.md) |
| 08 | Authenticated Crawl And HITL | Planned | 0% | Server-safe authenticated source collection | [phase-08-authenticated-crawl-hitl.md](phases/phase-08-authenticated-crawl-hitl.md) |
| 09 | Production Hardening | Planned | 0% | Observable, secure, release-ready v1 | [phase-09-production-hardening.md](phases/phase-09-production-hardening.md) |
| 10 | v2 Intelligence Layer | Planned | 0% | Hypothesis, ROI, temporal, and skeptic intelligence | [phase-10-v2-intelligence.md](phases/phase-10-v2-intelligence.md) |
| 11 | Enterprise Scale And Integrations | Planned | 0% | CRM/outcome learning, scale, governance expansion | [phase-11-enterprise-scale-integrations.md](phases/phase-11-enterprise-scale-integrations.md) |

## Release Gates

| Release | Required Phases | Exit Meaning |
|---|---|---|
| Developer Alpha | 00-01 | App and persistent workspace API work locally |
| Document MVP | 00-03 | Client docs can become approved ICP config |
| Discovery MVP | 00-05 | Safe public sources can be configured and collected |
| Lead MVP | 00-07 | Evidence-backed lead export is usable |
| Production v1 | 00-09 | Secure, observable, authenticated-source-capable system |
| Intelligence v2 | 00-10 | ROI-aware intelligence layer is usable |
| Enterprise v3 | 00-11 | Scaled integrations and outcome learning are usable |

## Execution Rules

- Execute phases in order.
- A later phase can be designed early but should not be implemented until previous phase tests pass.
- Phase outputs must be usable without waiting for future phases.
- If a phase grows too large, split it into sub-phases and update this roadmap.

## Immediate Next Steps

1. Start [Phase 01](phases/phase-01-data-workspace-api.md).
2. Implement Alembic and SQLAlchemy setup.
3. Add `clients`, `client_users`, and `client_settings`.
4. Add `/clients` API tests.
5. Update this roadmap when Phase 01 progress changes.
