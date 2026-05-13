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
- Search provider interface.
- Provider connector types for contact enrichment, email verification, and outreach export.
- Operation policy rules for public search, restricted profiles, licensed APIs, and campaign destinations.

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

## Test Plan

- Configure three safe public sources.
- Configure mock search, contact enrichment, email verification, and outreach providers.
- Route sample URLs through policy.
- Route sample profile candidates and provider operations through policy.
- Verify blocked paths are never approved for fetch.
- Verify blocked enrichment or outreach operations never call provider adapters.
- Verify default unknown source policy requires review.

## Exit Criteria

- Sources are configured from API/UI, not code.
- Policy decision exists before fetch.
- Policy decision exists before profile search, provider enrichment, email verification, or outreach export.
- URL candidates are stored before crawling.
- Tests and lint pass.

## Handoff To Phase 05

Phase 05 can execute allowed public crawl/search jobs and store raw artifacts, including permitted search/profile evidence for imported leads.
