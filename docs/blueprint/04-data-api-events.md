# Data, API, Event, And Worker Contracts

This file summarizes stable contracts. Detailed implementation belongs in migrations, Pydantic schemas, and OpenAPI docs as phases are built.

## Core Tables By Phase

| Phase | Tables |
|---|---|
| 01 | `clients`, `client_users`, `client_settings` |
| 02 | `documents`, `document_pages`, `document_chunks`, `extracted_knowledge_items`, `lead_import_batches`, `seed_lead_rows` |
| 03 | `review_items`, active ICP config tables |
| 04 | `source_connectors`, `source_credentials`, `url_candidates`, `policy_decisions`, provider connector config in `source_connectors` |
| 05 | `crawl_jobs`, `crawl_artifacts`, search/profile artifacts in `crawl_artifacts` |
| 06 | `page_classifications`, `company_candidates`, `account_signals`, `contact_candidates`, `profile_candidates`, `email_enrichment_results`, `email_verifications` |
| 07 | `lead_candidates`, `export_batches`, `export_batch_items`, outreach export payloads in `export_batch_items` |
| 08 | auth session state and credential validation records |
| 09 | `audit_logs`, `llm_invocations`, feature flag records |
| 10 | hypotheses, economic policies, signal timeseries, authenticity, counterfactuals |
| 11 | CRM/outreach connector mappings, outcome ingestion records, provider quality metrics |

## API Groups

```text
/health
/clients
/documents
/lead-imports
/knowledge
/config/icp
/sources
/source-policies
/credentials
/crawl-jobs
/artifacts
/extractions
/profile-candidates
/enrichment-providers
/email-verifications
/leads
/review
/exports
/outreach-exports
/feedback
/auth-sessions
/admin/runs
```

## Event Envelope

```json
{
  "event_id": "uuid",
  "event_type": "artifact.collected",
  "event_version": "1.0",
  "client_id": "uuid",
  "run_id": "uuid",
  "occurred_at": "timestamp",
  "producer": "crawler-worker",
  "payload": {}
}
```

## Core Events

| Event | Producer | Consumer |
|---|---|---|
| `document.uploaded` | API | ingestion worker |
| `document.parsed` | worker | chunker |
| `document.embedded` | worker | domain extractor |
| `lead_import.uploaded` | API | import worker |
| `seed_lead.normalized` | import worker | profile planner |
| `icp.suggested` | llm-worker | review UI |
| `source.configured` | API | planner |
| `url.discovered` | search plugin | policy engine |
| `policy.decided` | policy engine | connector router |
| `crawl.job.created` | planner | crawler-worker |
| `artifact.collected` | crawler-worker | classifier |
| `artifact.classified` | classifier | extractor |
| `entity.extracted` | extractor | resolver |
| `profile.candidate_ranked` | enrichment-worker | resolver/review UI |
| `contact.enriched` | enrichment provider adapter | verifier |
| `email.verified` | verification provider adapter | scorer/review UI |
| `lead.scored` | scorer | review UI |
| `review.completed` | review UI | export/feedback |
| `export.completed` | export service | audit/feedback |
| `outreach.export.completed` | export service | audit/feedback |
| `auth.required` | crawler-worker | review UI |

## Worker Queues

```text
documents.parse
documents.embed
documents.extract_icp
lead_imports.parse
lead_imports.normalize
planning.discovery
profiles.search
profiles.rank
crawl.public
crawl.authenticated
artifacts.classify
artifacts.extract
entities.resolve
contacts.enrich
contacts.verify_email
leads.score
exports.build
outreach.exports.build
auth.recovery
```

## Retry Classes

| Class | Retry Behavior |
|---|---|
| `transient` | exponential backoff, max 3 |
| `policy_blocked` | no retry |
| `auth_required` | pause and create HITL task |
| `provider_rate_limited` | provider-specific backoff and quota alert |
| `manual_research_required` | no retry until reviewer or operator action |
| `schema_repairable` | repair retry, max 2 |
| `fatal` | no retry until config/code change |
