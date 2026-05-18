# Phase 03: Expert Config Review

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 02 |
| Release | Ingestion MVP |

## Goal

Let a human approve, edit, or reject pipeline-specific ICP suggestions and enrichment guardrails before they drive discovery, profile matching, contact enrichment, or outreach.

## Usable Outcome

A pipeline has an active, human-approved ICP configuration plus suppression, title, enrichment, and outreach guardrails that can be used by source planning and seed lead enrichment.

## Deliverables

- Pipeline-scoped active ICP config tables.
- Review queue.
- Review APIs.
- Minimal review UI.
- Config audit log.
- Enrichment provider, email verification, and outreach eligibility guardrails.
- Frontend role and permission matrix for admin, domain expert, reviewer, sales operator, and compliance reviewer.
- Config review workspace with Evidence Rail, edit/approve/reject decisions, before/after diff, and audit prompt.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P03-T01 Add active ICP config migration | Planned | 0% | migration test |
| P03-T02 Add review queue table | Planned | 0% | migration test |
| P03-T03 Convert suggestions to review items | Planned | 0% | workflow test |
| P03-T04 Add review decision API | Planned | 0% | approve/reject/edit API tests |
| P03-T05 Apply approved config | Planned | 0% | active pipeline config version rows created |
| P03-T06 Add config audit log | Planned | 0% | audit test |
| P03-T07 Build minimal review UI | Planned | 0% | manual local review flow |
| P03-T08 Add suppression list basics | Planned | 0% | suppression API test |
| P03-T09 Add enrichment and outreach guardrails | Planned | 0% | approved guardrails control profile search, provider use, and export eligibility |
| P03-FE01 Add frontend permission matrix and route guards | Planned | 0% | role-based route, field, action, and export-operation access tests |
| P03-FE02 Build config review workspace | Planned | 0% | queue, selected item, Evidence Rail, diff, decision toolbar, and audit note work |
| P03-FE03 Build ICP and guardrail editors | Planned | 0% | field validation, dirty-state guard, policy preview, and server errors tested |
| P03-FE04 Add review keyboard interaction baseline | Planned | 0% | shortcuts require explicit enablement and remain accessible by mouse/keyboard |
| P03-FE05 Add Phase 03 Playwright smoke test | Planned | 0% | approve, edit, and reject suggestion flows pass |

## Frontend Permission Matrix

| Persona | Allowed in this phase | Blocked in this phase |
|---|---|---|
| Admin | Manage client settings, users, and view config status | Override expert review decisions without permission |
| Domain expert | Approve, edit, or reject ICP, title, exclusion, and guardrail suggestions | Manage credentials or production audit records |
| Research reviewer | View suggestions and evidence for context | Activate config unless granted expert role |
| Sales operator | View outreach guardrail readiness | Change enrichment, verification, or suppression policy |
| Compliance reviewer | Review suppression, PII, source-use implications, and audit diffs | Edit sales ICP content unless granted expert role |

## Frontend Screen Acceptance Criteria

- Review queue supports loading, empty, filtered, selected, decision-pending, and decision-failed states.
- Every config suggestion shows evidence, confidence, source, before/after diff when edited, and reviewer identity after decision.
- Guardrail editors show policy impact before save and block activation when required enrichment or outreach gates are missing.
- Permission-denied states explain the missing role and provide a safe navigation path.
- Keyboard review mode never hides visible decision controls and can be disabled per user preference.

## Test Plan

- Approve extracted product/industry/title/signal suggestions.
- Approve title mappings and contact quality rules used for seed lead enrichment.
- Edit a suggestion before approval.
- Reject a noisy suggestion.
- Verify only approved config becomes active.
- Verify approved config is active only for the selected pipeline and does not change another pipeline under the same client.
- Verify email enrichment, verification, and outreach export remain disabled until approved guardrails exist.
- Verify audit entries include actor and timestamp.
- Component test route guards, role-gated actions, diff viewer, Evidence Rail, and decision toolbar.
- Playwright smoke test approve, edit, reject, and permission-denied flows.

## Exit Criteria

- A reviewer can approve an ICP config without code changes.
- Active config can be retrieved by API for a selected pipeline.
- Config approvals, rejections, guardrails, and suppression rules are isolated by `client_id` and `pipeline_id`.
- Rejected suggestions do not influence discovery.
- Rejected or missing enrichment guardrails do not influence profile search, provider calls, or outreach export.
- Frontend permission matrix is implemented and tested for phase routes and actions.
- Config review UI exposes evidence, diff, policy impact, and audit context for every decision.
- Tests and lint pass.

## Handoff To Phase 04

Phase 04 can use active pipeline ICP and enrichment config to validate source, search, provider, verification, and outreach policy decisions.
