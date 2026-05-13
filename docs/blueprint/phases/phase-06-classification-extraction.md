# Phase 06: Classification And Extraction

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 05 |
| Release | Lead MVP |

## Goal

Convert raw artifacts into classified pages and structured company, signal, and contact candidates.

## Usable Outcome

Collected artifacts become searchable, evidence-backed structured intelligence.

## Deliverables

- Page classification tables.
- Rule classifier.
- LLM fallback classifier.
- Extraction schemas.
- Extraction workflow.
- Retrieval service.
- Optional knowledge graph tables.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P06-T01 Add classification/extraction migrations | Planned | 0% | migration test |
| P06-T02 Implement rule page classifier | Planned | 0% | fixture tests |
| P06-T03 Add LLM provider adapter | Planned | 0% | mock provider test |
| P06-T04 Add LLM fallback classifier | Planned | 0% | ambiguous fixture test |
| P06-T05 Define extraction schemas | Planned | 0% | schema tests |
| P06-T06 Extract companies | Planned | 0% | golden fixture test |
| P06-T07 Extract account signals | Planned | 0% | golden fixture test |
| P06-T08 Extract contact candidates | Planned | 0% | golden fixture test |
| P06-T09 Add retrieval service | Planned | 0% | context retrieval test |
| P06-T10 Add extraction workflow | Planned | 0% | artifact-to-candidate integration test |

## Test Plan

- Golden tests for known artifact examples.
- Schema validation for every LLM output.
- Evidence URL/text required for extracted claims.
- Low-confidence extraction routes to review.

## Exit Criteria

- Artifact classification produces page type and relevance score.
- Extraction produces structured candidates with evidence.
- Schema failures are retryable or visible.
- Tests and lint pass.

## Handoff To Phase 07

Phase 07 can resolve duplicates, score leads, review them, and export approved rows.
