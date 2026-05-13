# Phase 04: Source Registry And Policy

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 03 |
| Release | Discovery MVP |

## Goal

Create configurable source, search, enrichment, verification, and outreach connectors plus a policy engine that decides what can be fetched, imported, enriched, reviewed, exported, or blocked.

## Usable Outcome

An admin can configure safe public sources, search providers, licensed enrichment providers, email verification providers, and outreach destinations. URL/profile candidates and provider operations are routed through policy before execution.

## Deliverables

- Source connector tables.
- Source API.
- Source policy engine.
- URL candidate table.
- Connector registry interface.
- External tool adapter contract and certification tests.
- Search provider interface.
- Provider connector types for contact enrichment, email verification, and outreach export.
- Operation policy rules for public search, restricted profiles, licensed APIs, and campaign destinations.
- Source/provider registry UI with policy simulator, credential scope picker, rate limit editor, and typed service error handling.
- Frontend API contract extensions for policy previews, credential metadata, connector test results, and operation scopes.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P04-T01 Add source tables migration | Planned | 0% | migration test |
| P04-T02 Add source connector schemas | Planned | 0% | schema tests |
| P04-T03 Add source CRUD API | Planned | 0% | API tests |
| P04-T04 Implement policy decisions | Planned | 0% | allow/block/review tests |
| P04-T05 Add URL candidate storage | Planned | 0% | unique URL test |
| P04-T06 Add connector registry | Planned | 0% | connector resolution test |
| P04-T07 Add mock search provider | Planned | 0% | deterministic candidate test |
| P04-T08 Add source test endpoint | Planned | 0% | validates config without crawl |
| P04-T09 Add provider connector policy types | Planned | 0% | enrichment, verification, and outreach operations require approved policy |
| P04-T10 Add seed profile search policy routing | Planned | 0% | restricted profile URLs route to review/API-only/block as configured |
| P04-T11 Add external tool adapter contract | Planned | 0% | adapter metadata covers terms, scope, rate limits, cost, audit, and typed IO |
| P04-T12 Add adapter certification tests | Planned | 0% | mock adapters pass contract tests before live provider enablement |
| P04-FE01 Build source and provider registry pages | Planned | 0% | list, detail, create/edit, test, disabled, and error states tested |
| P04-FE02 Build policy simulator | Planned | 0% | allow, block, review-required, credential-required, and rate-limited results visible |
| P04-FE03 Build credential scope picker | Planned | 0% | operation scopes for crawl/search/import/enrichment/outreach are explicit and tested |
| P04-FE04 Extend typed API contract strategy | Planned | 0% | policy preview and connector test errors use typed contracts, Zod validation, and request IDs |
| P04-FE05 Add Phase 04 Playwright smoke test | Planned | 0% | create source/provider and preview policy decision |

## Frontend Screen Acceptance Criteria

- Source and provider tables use server-side pagination, sorting, filters, saved views, and stable URL state.
- Connector forms show required fields, secret metadata without raw secret values, rate limits, operation scopes, and policy previews before save.
- Connector forms expose adapter metadata for terms, operation scope, quotas, cost model, timeout, retry class, and audit behavior.
- Policy simulator explains why an operation is allowed, blocked, or sent to review.
- Credential scope changes require confirmation when they broaden access.
- Typed service errors preserve backend request IDs for support and audit correlation.

## Test Plan

- Configure three safe public sources.
- Configure mock search, contact enrichment, email verification, and outreach providers.
- Route sample URLs through policy.
- Route sample profile candidates and provider operations through policy.
- Verify blocked paths are never approved for fetch.
- Verify blocked enrichment or outreach operations never call provider adapters.
- Verify adapters cannot run without a policy decision, typed input/output contract, rate-limit key, timeout, retry class, and audit event type.
- Verify managed providers can be registered only as adapter implementations, not as direct dependencies in core business logic.
- Verify default unknown source policy requires review.
- Component test connector forms, policy simulator outcomes, credential scope changes, and typed service error display.
- Playwright smoke test source/provider creation and policy preview.

## Exit Criteria

- Sources are configured from API/UI, not code.
- Policy decision exists before fetch.
- Policy decision exists before profile search, provider enrichment, email verification, or outreach export.
- URL candidates are stored before crawling.
- External tools and providers are reachable only through certified adapters with deterministic mocks and contract tests.
- Admins can configure and test sources/providers from the frontend without exposing raw credentials.
- Policy preview UI explains decisions and blocks unsafe saves.
- Tests and lint pass.

## Handoff To Phase 05

Phase 05 can execute allowed public crawl/search jobs and store raw artifacts, including permitted search/profile evidence for imported leads.
