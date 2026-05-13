# Phase 06: Classification, Extraction, And Enrichment

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 05 |
| Release | Lead MVP |

## Goal

Convert raw artifacts and seed lead rows into classified pages, structured company/signal/contact candidates, ranked profile/domain matches, and verified enrichment records.

## Usable Outcome

Collected artifacts and imported seed rows become searchable, evidence-backed structured intelligence. Seed leads can be matched to likely professional profiles/domains, enriched through approved providers, and prepared for review without guessing private contact data.

## Deliverables

- Page classification tables.
- Rule classifier.
- LLM fallback classifier.
- Extraction schemas.
- Extraction workflow.
- Retrieval service.
- Seed lead company/domain resolver.
- Profile candidate ranking with evidence.
- Licensed enrichment provider adapter contracts.
- Email verification schemas and workflow.
- Company research summary generation with citations.
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
| P06-T11 Resolve seed lead companies/domains | Planned | 0% | seed row to company/domain candidate test |
| P06-T12 Rank profile candidates | Planned | 0% | company/title/location evidence ranking test |
| P06-T13 Add enrichment provider adapter contracts | Planned | 0% | mock provider returns typed contact/email candidates |
| P06-T14 Add email verification workflow | Planned | 0% | verified, risky, invalid, and unknown fixture tests |
| P06-T15 Generate cited research summaries | Planned | 0% | 2-3 sentence summary requires evidence and source links |

## Test Plan

- Golden tests for known artifact examples.
- Golden tests for seed lead imports with multiple possible profile matches.
- Schema validation for every LLM output.
- Evidence URL/text required for extracted claims.
- Provider email results require provider provenance and verification status before scoring.
- LLM ranking can choose among candidates but cannot create email, phone, or profile values.
- Low-confidence extraction routes to review.

## Exit Criteria

- Artifact classification produces page type and relevance score.
- Extraction produces structured candidates with evidence.
- Seed lead rows produce company/domain candidates and ranked profile candidates with evidence.
- Approved provider adapters produce contact enrichment and email verification records with lineage.
- Research summaries cite stored artifacts or provider-approved evidence.
- Schema failures are retryable or visible.
- Tests and lint pass.

## Handoff To Phase 07

Phase 07 can resolve duplicates, score both discovered and imported/enriched leads, review them, and export approved rows.
