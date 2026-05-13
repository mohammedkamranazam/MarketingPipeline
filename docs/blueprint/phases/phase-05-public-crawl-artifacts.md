# Phase 05: Public Crawl And Raw Artifacts

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 04 |
| Release | Discovery MVP |

## Goal

Collect permitted public web/API content and preserve raw artifacts with lineage.

## Usable Outcome

The system can crawl configured safe public sources and show stored artifacts for inspection.

## Deliverables

- Crawl job worker.
- HTTP connector.
- Scrapy runner.
- Optional Playwright render mode.
- Raw artifact storage.
- Rate limit and robots controls.

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

## Test Plan

- Crawl one static fixture site.
- Crawl one JS-rendered fixture.
- Confirm blocked paths are skipped.
- Confirm artifacts include content hash, source, job, and storage URL.

## Exit Criteria

- Public crawl job can run locally.
- Raw artifacts are queryable by client/source/job.
- Failed jobs preserve retry/error metadata.
- Tests and lint pass.

## Handoff To Phase 06

Phase 06 can classify and extract structured entities from collected artifacts.
