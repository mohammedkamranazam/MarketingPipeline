# Phase 07: Lead Review And Export

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 06 |
| Release | Lead MVP |

## Goal

Resolve pipeline candidates into scored leads, route them through review, and generate pipeline-specific CRM-ready and outreach-ready exports.

## Usable Outcome

A user can review evidence-backed leads from both discovery and seed-enrichment lanes in the selected pipeline, then download an approved CRM or outreach XLSX/CSV export that cannot include another pipeline's rows.

## Deliverables

- Company resolver.
- Contact resolver.
- Lead scorer.
- Review UI/API for leads.
- Export batch builder.
- Outreach export profile for campaign tools and inbox assignment.
- Export audit trail.
- Feedback capture.
- Full lead review workspace with keyboard review mode, side-by-side evidence, decision history, bulk safeguards, manual follow-up queue, and export blocker explanations.
- Export wizard with eligibility simulation, field mapping, compliance gates, and outreach payload preview.

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
| P07-FE01 Build lead review workspace | Planned | 0% | queue, lead detail, Evidence Rail, score breakdown, decision history, and decision toolbar tested |
| P07-FE02 Add keyboard review mode and accessibility guardrails | Planned | 0% | shortcuts are opt-in, discoverable, reversible, and never required |
| P07-FE03 Add bulk approval safeguards | Planned | 0% | bulk actions show eligibility, blockers, sample evidence, and confirmation before mutation |
| P07-FE04 Build manual follow-up queue | Planned | 0% | low-confidence, email-not-found, policy-blocked, and reviewer-needed states tested |
| P07-FE05 Build export wizard | Planned | 0% | compliance simulation, blocker explanations, field mapping, CRM/outreach preview, and download states tested |
| P07-FE06 Add Phase 07 Playwright smoke test | Planned | 0% | approve lead and create compliant export batch |

## Frontend Screen Acceptance Criteria

- Lead review queue supports saved views, server filters, keyboard navigation, selected-row URL state, and row detail drawers.
- Lead detail shows company fit, contact fit, profile match confidence, verified email status, suppression status, evidence, score rationale, and reviewer history.
- Review decisions can approve, reject, edit, or route to manual follow-up, with optimistic UI only when rollback is implemented and tested.
- Bulk actions cannot approve leads with hidden blockers; the UI must show blocker counts and sampled evidence before confirmation.
- Export wizard blocks unreviewed, unverified, invalid, suppressed, or policy-blocked rows with human-readable reasons.
- Outreach payload preview includes verified email, research summary, profile URL, source, campaign/inbox fields, and audit metadata.

## Test Plan

- Resolve duplicate company examples.
- Score leads with deterministic rules.
- Score imported seed leads with company fit, profile match confidence, verified email status, and project context.
- Approve/reject leads in review queue.
- Export only approved leads.
- Block outreach export for unverified, invalid, suppressed, or unreviewed emails.
- Verify every export row links to evidence and reviewer.
- Verify an export batch cannot mix leads from two pipelines unless a future governed enterprise combined export explicitly enables it.
- Component test review queue states, keyboard mode, score breakdown, decision history, bulk safeguards, manual follow-up states, export blockers, and payload preview.
- Playwright smoke test lead approval and compliant export creation.

## Exit Criteria

- Weekly CRM-ready export can be generated.
- Outreach-ready export can be generated for reviewed leads with verified emails and personalization notes.
- Export batches, review decisions, blocker summaries, and feedback records are isolated by `client_id` and `pipeline_id`.
- Export blocks unreviewed or compliance-blocked leads.
- Export blocks rows that fail email verification, suppression, or source policy gates.
- Review decisions feed feedback records.
- MVP E2E test passes.
- Lead review UI is the primary route for evidence-backed lead decisions and exposes all export blockers before download.
- Frontend review and export smoke tests pass.

## Handoff To Phase 08

Phase 08 can expand discovery and enrichment to authorized authenticated sources while preserving HITL safety.
