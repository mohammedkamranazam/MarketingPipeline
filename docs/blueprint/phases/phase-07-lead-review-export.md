# Phase 07: Lead Review And Export

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 06 |
| Release | Lead MVP |

## Goal

Resolve candidates into scored leads, route them through review, and generate CRM-ready exports.

## Usable Outcome

A user can review evidence-backed leads and download an approved XLSX/CSV export.

## Deliverables

- Company resolver.
- Contact resolver.
- Lead scorer.
- Review UI/API for leads.
- Export batch builder.
- Export audit trail.
- Feedback capture.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P07-T01 Add lead/export migrations | Planned | 0% | migration test |
| P07-T02 Implement company resolver | Planned | 0% | dedupe tests |
| P07-T03 Implement contact resolver | Planned | 0% | title/contact dedupe tests |
| P07-T04 Implement rule scorer | Planned | 0% | scoring unit tests |
| P07-T05 Add LLM score rationale | Planned | 0% | citation-required tests |
| P07-T06 Build lead review API | Planned | 0% | approve/reject/edit API tests |
| P07-T07 Build lead review UI | Planned | 0% | manual review flow |
| P07-T08 Add export builder | Planned | 0% | XLSX/CSV fixture test |
| P07-T09 Add export audit log | Planned | 0% | export lineage test |
| P07-T10 Add feedback capture | Planned | 0% | feedback API test |
| P07-T11 Add MVP E2E test | Planned | 0% | docs -> crawl -> leads -> export |

## Test Plan

- Resolve duplicate company examples.
- Score leads with deterministic rules.
- Approve/reject leads in review queue.
- Export only approved leads.
- Verify every export row links to evidence and reviewer.

## Exit Criteria

- Weekly CRM-ready export can be generated.
- Export blocks unreviewed or compliance-blocked leads.
- Review decisions feed feedback records.
- MVP E2E test passes.

## Handoff To Phase 08

Phase 08 can expand discovery to authorized authenticated sources while preserving HITL safety.
