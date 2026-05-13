# Phase 02: Document Intelligence

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 01 |
| Release | Document MVP |

## Goal

Turn uploaded client documents into parsed text, chunks, embeddings, and evidence-backed ICP suggestions.

## Usable Outcome

A user can upload a document for a client and view extracted domain knowledge suggestions with citations.

## Deliverables

- Document upload API.
- Object storage adapter.
- PDF/DOCX/TXT/CSV/XLSX parsers.
- Chunking service.
- Local embedding adapter.
- ICP extraction schema.
- Ingestion workflow.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P02-T01 Add document tables migration | Planned | 0% | migration test |
| P02-T02 Add object storage adapter | Planned | 0% | upload/download test |
| P02-T03 Add document upload API | Planned | 0% | API test with sample file |
| P02-T04 Add PDF/DOCX/TXT parser | Planned | 0% | parser fixture tests |
| P02-T05 Add CSV/XLSX parser | Planned | 0% | tabular fixture tests |
| P02-T06 Add chunking service | Planned | 0% | deterministic chunk tests |
| P02-T07 Add embedding adapter | Planned | 0% | embedding metadata stored |
| P02-T08 Add ICP extraction schema | Planned | 0% | schema validation tests |
| P02-T09 Add document ingestion workflow | Planned | 0% | upload triggers parse/chunk/extract |
| P02-T10 Add citation preview endpoint | Planned | 0% | extracted item links to evidence |

## Test Plan

- Use the tec5USA questionnaire as the first fixture.
- Verify original file storage and retrieval.
- Verify parsed text is non-empty.
- Verify chunks include `client_id`, `document_id`, page metadata.
- Verify extracted suggestions require evidence text.

## Exit Criteria

- Uploading a sample document creates document, pages, chunks, and suggestions.
- Suggestions include confidence and citations.
- Parser failures are visible and retryable.
- Tests and lint pass.

## Handoff To Phase 03

Phase 03 can put extracted suggestions into a human review workflow and activate approved ICP config.
