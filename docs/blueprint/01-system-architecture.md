# System Architecture Reference

This is the stable reference architecture for all phases.

## Core Principle

The system should not scrape broadly and ask an LLM to guess leads. It should collect permitted evidence, classify it, extract structured objects, resolve duplicates, score with citations, route to human review, and export only approved records.

## High-Level Flow

```text
client docs + expert config
  -> seed knowledge
  -> discovery plan
  -> source policy
  -> crawl/API/import plugins
  -> raw artifacts
  -> classification
  -> extraction
  -> resolution
  -> scoring
  -> human review
  -> export
  -> feedback learning
```

## Service Boundaries

| Service | Responsibility |
|---|---|
| `api-service` | Control-plane APIs and request validation |
| `scheduler-service` | Prefect schedules and workflow dispatch |
| `worker-service` | Parsing, embeddings, scoring, exports |
| `crawler-worker` | HTTP/Scrapy/Playwright collection |
| `llm-worker` | Model calls, schema validation, prompt governance |
| `review-ui` | Human review, config approval, auth recovery |
| `observability-stack` | Logs, metrics, traces, dashboards |

## Open-Source-First Stack

| Layer | Default |
|---|---|
| API | FastAPI |
| Workflow orchestration | Prefect |
| AI graph/state | LangGraph |
| Database | PostgreSQL |
| Vector search | pgvector first, Qdrant later if needed |
| Queue/cache | Redis |
| Crawling | Scrapy, httpx, Playwright, scrapy-playwright |
| Object storage | SeaweedFS or Ceph |
| Local LLM | Ollama |
| Observability | OpenTelemetry, Prometheus, Grafana, Loki |

## Required Product Guarantees

- Every recommendation has evidence.
- Every source fetch passes policy first.
- Every export has human approval.
- Every LLM output is schema-validated.
- Every stage preserves lineage.
- Every tenant-owned record is scoped by `client_id`.

## Authenticated Source Rule

Authenticated crawling is allowed only for authorized sources. CAPTCHA/MFA defaults to human-in-loop re-auth. Automatic solver adapters are disabled unless explicitly approved per source policy.
