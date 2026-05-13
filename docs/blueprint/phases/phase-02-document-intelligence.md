# Phase 02: Document And Seed Lead Ingestion

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 01 |
| Release | Ingestion MVP |

## Goal

Turn uploaded client documents into parsed text, chunks, embeddings, and evidence-backed ICP suggestions, and turn uploaded seed lead sheets into normalized import rows.

## Usable Outcome

A user can upload a document for a client and view extracted domain knowledge suggestions with citations. A user can also upload a CSV/XLSX seed lead list from bid platforms, CRM, events, or campaigns and see row-level validation results.

## Deliverables

- Document upload API.
- Object storage adapter.
- PDF/DOCX/TXT/CSV/XLSX parsers.
- Seed lead import schemas and tables.
- Seed lead row normalization and validation.
- Chunking service.
- Local embedding adapter.
- ICP extraction schema.
- Ingestion workflow.
- First async job/run, transactional outbox, and inbox deduplication contracts.
- Document ingestion frontend pages with upload, parse timeline, citation preview, and retry/error states.
- Seed lead import frontend pages with upload wizard, column mapping, validation grid, duplicate/suppression indicators, and row detail drawer.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P02-T01 Add document tables migration | Planned | 0% | migration test |
| P02-T02 Add object storage adapter | Planned | 0% | upload/download test |
| P02-T03 Add document upload API | Planned | 0% | API test with sample file |
| P02-T04 Add PDF/DOCX/TXT parser | Planned | 0% | parser fixture tests |
| P02-T05 Add CSV/XLSX parser | Planned | 0% | tabular fixture tests |
| P02-T06 Add seed lead import tables | Planned | 0% | migration test |
| P02-T07 Add seed lead import schemas | Planned | 0% | required/optional field schema tests |
| P02-T08 Normalize seed lead rows | Planned | 0% | first name/company/source/project context fixture tests |
| P02-T09 Add chunking service | Planned | 0% | deterministic chunk tests |
| P02-T10 Add embedding adapter | Planned | 0% | embedding metadata stored |
| P02-T11 Add ICP extraction schema | Planned | 0% | schema validation tests |
| P02-T12 Add document and lead import ingestion workflows | Planned | 0% | upload triggers parse/chunk/extract or row normalization |
| P02-T13 Add citation/import preview endpoint | Planned | 0% | extracted item links to evidence and seed rows show validation errors |
| P02-T14 Add async job and event durability contracts | Planned | 0% | duplicate event replay is deduped and retry resumes from `job_runs` |
| P02-FE01 Build document ingestion pages | Planned | 0% | upload, status, retry, extracted facts, citations, and parser errors are visible |
| P02-FE02 Build seed lead import wizard | Planned | 0% | CSV/XLSX upload, field mapping, preview, validation, duplicate, and suppression states are tested |
| P02-FE03 Add ingestion typed services and MSW fixtures | Planned | 0% | upload, polling, validation failure, parse failure, and retry states tested |
| P02-FE04 Add data-heavy import grid behavior | Planned | 0% | server pagination, stable URL filters, row detail drawer, column presets, and bulk selection work |
| P02-FE05 Add Phase 02 Playwright smoke test | Planned | 0% | document upload and seed lead upload show parse or validation result |

## Frontend Screen Acceptance Criteria

- Document list supports loading, empty, populated, failed, and retryable parser states.
- Document detail shows original file metadata, parse timeline, extracted knowledge suggestions, and citation snippets.
- Upload forms validate file type and size before submit and display backend parser errors without losing the batch.
- Seed import batch detail preserves original values, normalized values, row errors, duplicates, suppression indicators, and source context.
- Import grids keep filter, sort, page, selected columns, and selected row in URL state where useful for support handoff.
- Evidence Rail opens for selected knowledge suggestions and seed rows with source file, page/row, confidence, and lineage.

## Test Plan

- Use the tec5USA questionnaire as the first fixture.
- Use the AI lead enrichment case study fields as the first seed lead sheet fixture: first name, optional last name, company name, source, and notes/project context.
- Verify original file storage and retrieval.
- Verify parsed text is non-empty.
- Verify chunks include `client_id`, `document_id`, page metadata.
- Verify extracted suggestions require evidence text.
- Verify malformed seed rows are retained with actionable row-level errors.
- Verify seed rows are tenant-scoped and deduplicated by import batch, normalized person fields, company, and source context.
- Verify ingestion workflows create `pipeline_runs`, `job_runs`, outbox events, and inbox deduplication records before async processing.
- Verify a retried ingestion job preserves `job_id`, increments attempt count, and does not duplicate extracted records or review suggestions.
- Component test upload, parser failure, row validation, row detail, filter URL state, and Evidence Rail states.
- Playwright smoke test document upload and seed lead upload to visible status/validation outcomes.

## Exit Criteria

- Uploading a sample document creates document, pages, chunks, and suggestions.
- Uploading a sample seed lead file creates an import batch and normalized seed lead rows.
- Suggestions include confidence and citations.
- Seed lead rows preserve original values, normalized values, source, and project context.
- First async workflows use the shared job/run and outbox/inbox contracts from `04-data-api-events.md`.
- Parser failures are visible and retryable.
- Frontend ingestion pages expose document and seed lead status without requiring API console use.
- Frontend tests cover loading, empty, error, permission, validation, and retry states.
- Tests and lint pass.

## Handoff To Phase 03

Phase 03 can put extracted suggestions into a human review workflow, activate approved ICP config, and approve enrichment/suppression rules for imported leads.
