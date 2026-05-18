# Phase 05: Public Crawl And Raw Artifacts

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 04 |
| Release | Discovery MVP |

## Goal

Collect permitted public web/API/search content and preserve pipeline-scoped raw artifacts with lineage.

## Usable Outcome

The system can crawl configured safe public sources for a selected pipeline, collect permitted search/profile evidence for seed lead enrichment, and show stored artifacts for inspection without mixing another pipeline's runs or artifacts.

## Deliverables

- Crawl job worker.
- HTTP connector.
- Scrapy runner.
- Optional Playwright render mode.
- Optional managed crawl/browser adapter slots such as Firecrawl or Browserbase behind the standard adapter contract.
- Raw artifact storage.
- Rate limit and robots controls.
- Per-client, per-pipeline, per-source, per-provider, and browser-worker concurrency budgets.
- Search result and profile-evidence artifact capture.
- Imported/provider artifact lineage for non-crawl records.
- Crawl/search run monitor UI with polling-first real-time status, retry/cancel controls, cost/quota indicators, and artifact inspector.
- Data-heavy artifact tables with saved views, row drawers, server filtering/sorting, and virtualization threshold.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P05-T01 Add crawl job/artifact migration | Planned | 0% | migration test |
| P05-T02 Implement HTTP fetch connector | Planned | 0% | fixture fetch test |
| P05-T03 Implement Scrapy runner | Planned | 0% | seed URL crawl test |
| P05-T04 Add artifact storage adapter | Planned | 0% | artifact write/read test |
| P05-T05 Add content hash dedupe | Planned | 0% | duplicate artifact test |
| P05-T06 Enforce rate limits | Planned | 0% | throttling test |
| P05-T07 Enforce robots/source policy | Planned | 0% | blocked URL test |
| P05-T08 Add Playwright render option | Planned | 0% | JS fixture test |
| P05-T09 Add crawl monitor API | Planned | 0% | run status API test |
| P05-T10 Store permitted search/profile artifacts | Planned | 0% | search result artifact links back to seed lead row |
| P05-T11 Store provider/import artifacts | Planned | 0% | provider response metadata is queryable without exposing secrets |
| P05-T12 Add crawl/browser adapter certification | Planned | 0% | HTTP, Scrapy, Playwright, and managed-provider mocks satisfy adapter contract |
| P05-T13 Add crawl concurrency budgets | Planned | 0% | client/pipeline/source/provider/browser limits throttle jobs without losing state |
| P05-FE01 Build crawl/search run monitor | Planned | 0% | polling status, retry/cancel/resume affordances, errors, and cost/quota states visible |
| P05-FE02 Build artifact inspector | Planned | 0% | raw, parsed, source metadata, policy decision, citation anchors, and lineage visible |
| P05-FE03 Add table virtualization and saved views rules | Planned | 0% | large artifact tables keep stable layout and responsive detail drawers |
| P05-FE04 Define real-time job update strategy | Planned | 0% | polling interval, backoff, stale status, and future SSE/WebSocket upgrade path documented/tested |
| P05-FE05 Add Phase 05 Playwright smoke test | Planned | 0% | inspect crawl/search job and artifact lineage |

## Frontend Screen Acceptance Criteria

- Run monitor shows queued, running, paused, failed, retrying, completed, blocked, and stale states.
- Polling backs off on background tabs and stops when the run reaches a terminal state.
- Retry/cancel/resume controls appear only when the current role and run state allow them.
- Artifact inspector shows source policy, content hash, storage metadata, raw/parsed tabs, and related seed row or job lineage.
- Tables switch to virtualization or constrained rendering before large result sets degrade interaction.

## Test Plan

- Crawl one static fixture site.
- Crawl one JS-rendered fixture.
- Collect one mocked search-result fixture for a seed lead row.
- Run adapter contract fixtures for HTTP, Scrapy, Playwright render mode, and one managed-provider mock.
- Confirm blocked paths are skipped.
- Confirm per-client, per-pipeline, per-source, per-provider, and browser concurrency limits are enforced.
- Confirm crawl jobs, artifacts, budgets, costs, failures, and run monitor results are isolated by `client_id` and `pipeline_id`.
- Confirm artifacts include content hash, source, job, and storage URL.
- Confirm profile/search artifacts include policy decision and seed row lineage.
- Component test run states, polling backoff, retry/cancel permissions, artifact inspector tabs, saved views, and table virtualization threshold.
- Playwright smoke test run monitor to artifact inspector navigation.

## Exit Criteria

- Public crawl job can run locally.
- Permitted search/profile evidence can be collected for seed lead enrichment without bypassing source policy.
- Raw artifacts are queryable by client/pipeline/source/job.
- Raw artifacts are visible only in their owning pipeline unless a governed cross-pipeline enterprise view is explicitly introduced later.
- Failed jobs preserve retry/error metadata.
- HTTP crawling is the default path, with Playwright and managed browser/crawl providers used only when policy and adapter metadata require them.
- Crawl and browser jobs respect concurrency budgets, leases, heartbeats, rate limits, and idempotency keys.
- Frontend run monitor exposes status, errors, cost/quota, retry controls, and artifact lineage.
- Real-time status is polling-first with a documented SSE/WebSocket upgrade path.
- Tests and lint pass.

## Handoff To Phase 06

Phase 06 can classify and extract structured entities from collected artifacts and rank profile/domain candidates for imported leads.
