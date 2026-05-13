# Phase 03: Expert Config Review

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 02 |
| Release | Document MVP |

## Goal

Let a human approve, edit, or reject extracted ICP suggestions before they drive discovery.

## Usable Outcome

A client has an active, human-approved ICP configuration that can be used by source planning.

## Deliverables

- Active ICP config tables.
- Review queue.
- Review APIs.
- Minimal review UI.
- Config audit log.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P03-T01 Add active ICP config migration | Planned | 0% | migration test |
| P03-T02 Add review queue table | Planned | 0% | migration test |
| P03-T03 Convert suggestions to review items | Planned | 0% | workflow test |
| P03-T04 Add review decision API | Planned | 0% | approve/reject/edit API tests |
| P03-T05 Apply approved config | Planned | 0% | active config rows created |
| P03-T06 Add config audit log | Planned | 0% | audit test |
| P03-T07 Build minimal review UI | Planned | 0% | manual local review flow |
| P03-T08 Add suppression list basics | Planned | 0% | suppression API test |

## Test Plan

- Approve extracted product/industry/title/signal suggestions.
- Edit a suggestion before approval.
- Reject a noisy suggestion.
- Verify only approved config becomes active.
- Verify audit entries include actor and timestamp.

## Exit Criteria

- A reviewer can approve an ICP config without code changes.
- Active config can be retrieved by API.
- Rejected suggestions do not influence discovery.
- Tests and lint pass.

## Handoff To Phase 04

Phase 04 can use active ICP config to validate source setup and policy decisions.
