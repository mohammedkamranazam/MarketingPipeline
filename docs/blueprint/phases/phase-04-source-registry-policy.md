# Phase 04: Source Registry And Policy

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 03 |
| Release | Discovery MVP |

## Goal

Create configurable source connectors and a policy engine that decides what can be fetched, imported, reviewed, or blocked.

## Usable Outcome

An admin can configure safe public sources and see URL candidates routed through policy before crawl.

## Deliverables

- Source connector tables.
- Source API.
- Source policy engine.
- URL candidate table.
- Connector registry interface.
- Search provider interface.

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

## Test Plan

- Configure three safe public sources.
- Route sample URLs through policy.
- Verify blocked paths are never approved for fetch.
- Verify default unknown source policy requires review.

## Exit Criteria

- Sources are configured from API/UI, not code.
- Policy decision exists before fetch.
- URL candidates are stored before crawling.
- Tests and lint pass.

## Handoff To Phase 05

Phase 05 can execute allowed public crawl jobs and store raw artifacts.
