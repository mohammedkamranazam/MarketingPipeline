# Data, API, Event, And Worker Contracts

This file summarizes stable contracts. Detailed implementation belongs in migrations, Pydantic schemas, and OpenAPI docs as phases are built.

## Core Tables By Phase

| Phase | Tables |
|---|---|
| 01 | `clients`, `client_users`, `client_settings` |
| 02 | `documents`, `document_pages`, `document_chunks`, `extracted_knowledge_items`, `lead_import_batches`, `seed_lead_rows`, first async `pipeline_runs`, `job_runs`, `event_outbox`, `event_inbox` |
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
  "job_id": "uuid",
  "correlation_id": "uuid",
  "trace_id": "trace-id",
  "idempotency_key": "string",
  "occurred_at": "timestamp",
  "producer": "crawler-worker",
  "payload": {}
}
```

## Job Run Envelope

Every long-running action returns or records a typed job/run contract before execution:

```json
{
  "job_id": "uuid",
  "run_id": "uuid",
  "client_id": "uuid",
  "queue": "crawl.public",
  "job_type": "crawl_fetch",
  "status": "queued",
  "attempt": 0,
  "max_attempts": 3,
  "priority": 100,
  "idempotency_key": "source_id:canonical_url:config_version",
  "dedupe_key": "optional-string",
  "retry_class": "transient",
  "lease_owner": null,
  "lease_expires_at": null,
  "heartbeat_at": null,
  "scheduled_at": "timestamp",
  "started_at": null,
  "finished_at": null,
  "error_code": null,
  "error_message": null,
  "trace_id": "trace-id"
}
```

Job states:

```text
queued
leased
running
retrying
paused_auth
policy_blocked
rate_limited
manual_review_required
dead_lettered
cancelled
succeeded
failed
```

State changes must be append-auditable. Worker leases must expire if the worker stops heartbeating. Retried jobs must preserve the original `job_id`, increment `attempt`, and retain the original idempotency key.

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

## Worker Queue Rules

- API requests create run/job records and return IDs; long-running work does not run inside request handlers.
- Workers acquire jobs by queue, priority, tenant budget, source budget, provider budget, and lease availability.
- Every queue has dead-letter handling, retry-class behavior, timeout settings, and dashboard metrics.
- Every job is idempotent or explicitly marked as non-retryable with a policy reason.
- Export, enrichment, verification, and outreach operations require idempotency keys and duplicate-result handling before calling external providers.
- Browser jobs have separate concurrency budgets from HTTP crawl jobs.
- Provider jobs respect per-provider rate limits, tenant quotas, and budget stop thresholds.

## Event Reliability Rules

- Use a transactional outbox for domain events emitted by API and core services.
- Use an inbox/deduplication record for consumed events so workers can safely retry after crashes.
- Event payloads must reference typed contracts in `src/backend/core/contracts`.
- Event schema changes must be versioned and covered by contract tests.
- Events must include `client_id`, `run_id`, `job_id` when applicable, `correlation_id`, and `trace_id`.

## Tool Adapter Operation Contract

Every external tool operation, including crawl, search, browser, enrichment, verification, LLM, CRM, and outreach calls, must include:

| Field | Purpose |
|---|---|
| `adapter_key` | Stable adapter identifier, such as `scrapy_public`, `playwright_auth`, or a provider key |
| `operation_type` | `crawl`, `search`, `browser_render`, `contact_enrich`, `email_verify`, `llm_extract`, `crm_export`, or `outreach_export` |
| `input_contract` / `output_contract` | Pydantic contract names for typed boundary validation |
| `policy_decision_id` | Policy decision that allowed, blocked, or routed the operation |
| `credential_scope` | Approved operation scope required for credentials or sessions |
| `terms_reference` | Source/provider terms, license, or internal approval reference |
| `rate_limit_key` | Provider/source/tenant key used for throttling |
| `timeout_seconds` | Hard timeout for the operation |
| `retry_class` | Retry behavior from the table below |
| `cost_estimate` | Expected cost or quota unit for budget controls |
| `pii_classification` | Whether the operation can read, write, or expose PII |
| `trace_span_name` | OpenTelemetry span name for correlation |
| `audit_event_type` | Audit log event emitted for execution and result |

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
