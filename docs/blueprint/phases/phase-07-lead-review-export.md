# Phase 07: Lead Review And Export

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 06 |
| Release | Lead MVP |

## Goal

Resolve candidates into scored leads, route them through review, and generate CRM-ready and outreach-ready exports.

## Usable Outcome

A user can review evidence-backed leads from both discovery and seed-enrichment lanes, then download an approved CRM or outreach XLSX/CSV export.

## Deliverables

- Company resolver.
- Contact resolver.
- Lead scorer.
- Review UI/API for leads.
- Export batch builder.
- Outreach export profile for campaign tools and inbox assignment.
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
| P07-T12 Add outreach export profile | Planned | 0% | verified email, research summary, profile URL, source, and inbox/campaign fields export only after approval |
| P07-T13 Add manual follow-up queue states | Planned | 0% | email-not-found and low-confidence profile rows route to manual follow-up |

## Test Plan

- Resolve duplicate company examples.
- Score leads with deterministic rules.
- Score imported seed leads with company fit, profile match confidence, verified email status, and project context.
- Approve/reject leads in review queue.
- Export only approved leads.
- Block outreach export for unverified, invalid, suppressed, or unreviewed emails.
- Verify every export row links to evidence and reviewer.

## Exit Criteria

- Weekly CRM-ready export can be generated.
- Outreach-ready export can be generated for reviewed leads with verified emails and personalization notes.
- Export blocks unreviewed or compliance-blocked leads.
- Export blocks rows that fail email verification, suppression, or source policy gates.
- Review decisions feed feedback records.
- MVP E2E test passes.

## Handoff To Phase 08

Phase 08 can expand discovery and enrichment to authorized authenticated sources while preserving HITL safety.
