# System Architecture Reference

This is the stable reference architecture for all phases.

## Core Principle

The system should not scrape broadly and ask an LLM to guess leads. It should collect permitted evidence, classify it, extract structured objects, resolve duplicates, score with citations, route to human review, and export only approved records.

Seed lead enrichment follows the same rule. Imported rows with only a first name, company, source, and project note may start the workflow, but profile/domain matching, contact enrichment, email verification, and outreach export must still pass policy, evidence, review, and audit gates. LLMs may rank candidates and summarize evidence; they must not invent private contact data.

## Supported Use-Case Lanes

| Lane | Starts With | Shared Core | Ends With |
|---|---|---|---|
| Account discovery | Client docs, expert ICP, source policy | Evidence store, extraction, resolution, scoring, review | CRM-ready lead export |
| Seed lead enrichment | CSV/XLSX lead rows from bid platforms, CRM, events, or campaign sheets | Policy, profile/domain evidence, provider enrichment, verification, review | Outreach-ready and CRM-ready lead export |

## Customer And Pipeline Scope

A client workspace may contain many independent pipelines. A pipeline is the operational boundary for datasets, active configuration, sources, providers, credentials, runs, artifacts, embeddings, review decisions, exports, costs, quotas, and diagnostics.

Client-level records are limited to users, access, billing/compliance shell, and optional default templates. Pipeline-owned records must include both `client_id` and `pipeline_id`. A pipeline may be cloned from another pipeline, but the clone gets separate config versions, credential profiles, schedules, runs, and history.

```text
client workspace
  -> users and client defaults
  -> pipeline A
       -> data, config, credentials, runs, evidence, exports
  -> pipeline B
       -> data, config, credentials, runs, evidence, exports
```

No retrieval, source operation, provider call, review queue, or export may mix pipeline data unless a later enterprise feature explicitly creates a governed cross-pipeline view.

## High-Level Flow

```text
pipeline docs + expert config      pipeline seed lead imports
  -> seed knowledge                  -> row normalization
  -> discovery plan                  -> profile/domain search plan
             \                      /
              -> source/provider policy
              -> crawl/API/import/enrichment plugins
              -> raw artifacts + provider results
              -> classification, extraction, profile ranking
              -> company/contact resolution
              -> email verification and suppression checks
              -> scoring
              -> human review
              -> CRM/outreach export
              -> feedback learning
```

## Service Boundaries

| Service | Responsibility |
|---|---|
| `api-service` | Control-plane APIs and request validation |
| `scheduler-service` | Prefect schedules and workflow dispatch |
| `worker-service` | Parsing, embeddings, scoring, exports |
| `crawler-worker` | HTTP/Scrapy/Playwright collection |
| `enrichment-worker` | Search result routing, profile/domain candidate ranking, licensed contact enrichment, email verification |
| `llm-worker` | Model calls, schema validation, prompt governance |
| `outreach-worker` | Outreach-ready export building, campaign payload preparation, outcome import orchestration |
| `review-ui` | Human review, config approval, auth recovery |
| `observability-stack` | Logs, metrics, traces, dashboards |

## Open-Source-First Stack

| Layer | Default |
|---|---|
| API | FastAPI |
| Workflow orchestration | Prefect first, with a Temporal evaluation gate before Production v1 |
| AI graph/state | LangGraph with durable checkpoints, bounded iterations, and human-in-loop recovery |
| Database | PostgreSQL |
| Vector search | pgvector first, Qdrant later if needed |
| Queue/cache | Redis |
| Crawling | httpx and Scrapy by default; Playwright only for JS-rendered or authenticated workflows |
| Managed crawl/browser providers | Optional adapters such as Firecrawl or Browserbase, never hard dependencies |
| Search/enrichment providers | Adapter interfaces with mock providers first, licensed APIs later |
| Email verification | Adapter interface with mock verifier first, licensed API later |
| Object storage | SeaweedFS or Ceph |
| Local LLM | Ollama |
| Observability | OpenTelemetry, Prometheus, Grafana, Loki, and Tempo or Jaeger for traces |

## Production Tooling Posture

Use open-source-first defaults, but keep every external tool behind typed adapters. The product owns policy, lineage, audit, cost tracking, and evidence contracts even when a managed provider performs collection, browser execution, enrichment, verification, or outreach delivery.

Prefect remains the default workflow orchestrator for early scheduled pipelines, ingestion flows, backfills, and batch processing. Before Production v1, evaluate Temporal for workflows that require durable execution across worker crashes, long-running human pauses, exactly-once external side effects, or customer-visible recovery guarantees. The system must not depend on Prefect-specific business logic; orchestration code belongs in `src/backend/jobs`, while retry-safe business operations stay in `src/backend/core`.

LangGraph should be used for AI graph state, planning, and human-in-loop agent flows when checkpointing and review recovery matter. Agent loops must have iteration limits, timeout limits, budget limits, typed tool contracts, and explicit failure states.

## External Tool Adapter Contract

Every crawl, search, browser, enrichment, verification, LLM, or outreach adapter must declare:

- `adapter_key`, operation type, supported source/provider categories, and typed input/output contract names.
- Pipeline scope, source terms reference, credential operation scope, PII classification, and whether human approval is required.
- Timeout, retry class, rate-limit key, concurrency budget, cost estimate, and quota metadata.
- Policy decision ID, trace span name, audit event type, and redaction behavior.
- Deterministic mock implementation and contract tests before live provider calls are enabled.

Default adapters should cover local fixtures and mocked providers first. Managed providers such as Firecrawl, Browserbase, licensed data APIs, email verifiers, CRM systems, and outreach platforms are enabled only through the same adapter contract and feature-flag rules.

Credential profiles are pipeline-scoped. Adapters receive only short-lived resolved secrets from the secret adapter at execution time and must never store or log raw secret values.

## Job Durability Principles

All long-running work must be represented by typed run and job records before execution. Jobs must be idempotent, lease-based, heartbeat-aware, retry-classified, and safe to resume after worker restart. External side effects such as contact enrichment, email verification, CRM export, and outreach export require idempotency keys and unique constraints.

Event publication must use a transactional outbox/inbox pattern once async workflows begin. API writes, job state changes, and events must not drift apart.

## Container And Supply Chain Posture

Docker Compose is the local development baseline. Production-ready images must use multi-stage Dockerfiles with separate development, test, and production targets; non-root runtime users; pinned base images; explicit healthchecks; small build contexts; and no secrets baked into layers.

Production release gates must include image vulnerability scanning, SBOM/provenance generation, image signing or attestations, Compose/Kubernetes manifest validation, and runtime hardening for browser workers, crawler workers, LLM workers, and export workers. Browser workers need explicit CPU, memory, timeout, and concurrency isolation.

## Required Product Guarantees

- Every recommendation has evidence.
- Every source fetch passes policy first.
- Every export has human approval.
- Every LLM output is schema-validated.
- No email or phone number is generated by an LLM; verified contact data comes from licensed providers, first-party records, or approved source exports.
- Outreach-ready exports require verified email status, suppression checks, and a reviewer decision unless an explicitly approved automation policy permits otherwise.
- Provider, search, verification, and outreach operations are logged with source terms, credentials, cost, and rate-limit metadata.
- Every stage preserves lineage.
- Every tenant-owned record is scoped by `client_id`.
- Every pipeline-owned record is scoped by `client_id` and `pipeline_id`.
- Credential health, expiry, validation, rotation, and revoked/disabled status are visible in the pipeline configuration area before runs start.

## Authenticated Source Rule

Authenticated crawling is allowed only for authorized sources. CAPTCHA/MFA defaults to human-in-loop re-auth. Automatic solver adapters are disabled unless explicitly approved per source policy.
