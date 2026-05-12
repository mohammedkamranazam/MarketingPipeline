# Toolchain Matrix v1 (Open-Source-First)

Date: 2026-05-13

This matrix maps tools to the `Blueprint_v1.md` stages with an open-source-first policy. Cloud APIs (Claude/Gemini) are optional fallbacks behind a provider adapter.

## 1) Stage-by-Stage Matrix

| Stage | Required Tools | Optional Tools | Why This Choice | OSS License Notes |
|---|---|---|---|---|
| Stage 1: Client Workspace Setup | FastAPI, PostgreSQL, Alembic, Redis | Keycloak (SSO), OPA (policy) | Multi-tenant setup, config storage, policy-ready controls | All OSS; permissive stack possible |
| Stage 2: Document Ingestion | Python, unstructured, pypdf, python-docx, pandas, openpyxl, PostgreSQL, pgvector | Apache Tika, OCRmyPDF, Tesseract | Handles mixed file formats and structured extraction prep | OSS; check model/data licenses for OCR packs |
| Stage 3: Domain Knowledge Extraction | Ollama + local models, Pydantic, LangChain/LangGraph adapter | Claude/Gemini fallback via provider adapter | Schema-bound extraction with evidence and confidence | Ollama OSS runtime; model licenses vary by model |
| Stage 4: Expert Review & Config | FastAPI, React/Next.js admin UI, PostgreSQL | Superset/Metabase for quick ops dashboards | Human approval gate before crawl/outreach | OSS core stack |
| Stage 5: Source Registry & Connectors | Connector registry in PostgreSQL, Secrets manager abstraction, Playwright storage-state vaulting | Vault, SOPS/age | Avoid hardcoded sources; secure auth and scope rules | OSS; secret tooling OSS |
| Stage 6: Query & Crawl Planning | Prefect, Redis queues, PostgreSQL state tables | Temporal, Airflow | Reliable scheduling, retries, recrawl planning | Prefect OSS available |
| Stage 7: Crawl & Raw Collection | Scrapy, scrapy-playwright, Playwright, httpx, lxml/bs4 | Crawlee (Node), Browser automation pool | Best Python-native crawl throughput + JS rendering + auth sessions | Scrapy/Playwright strong OSS communities |
| Stage 8: Page Classification | Rule engine + lightweight ML + Ollama classifier | Cloud LLM fallback for ambiguous pages | Cost control by rule-first, LLM-second | OSS-first flow |
| Stage 9: Entity/Signal/Evidence Extraction | Pydantic schemas, LangGraph, Ollama | Claude/Gemini fallback | Deterministic typed outputs + evidence links | OSS with optional cloud fallback |
| Stage 10: Company Resolution & Dedupe | PostgreSQL + SQL matching, rapidfuzz, domain normalization libs | Graph DB (Neo4j) | Transparent deterministic dedupe baseline | OSS |
| Stage 11: Contact Discovery & Enrichment | Approved connectors only, policy engine, evidence store | Licensed enrichment APIs | Compliance-safe sourcing; no blind scraping of restricted sources | Mixed (OSS + licensed APIs) |
| Stage 12: Lead Scoring | Rule scorer in Python + LLM rationale via adapter | Feature store tooling | Hybrid scoring with auditability | OSS-first |
| Stage 13: Human Review | Review queue UI, audit logs, evidence snapshots | Slack/Email notification integrations | Mandatory HITL before export/outreach | OSS core + optional SaaS notif |
| Stage 14: Export | pandas/openpyxl, CSV/XLSX writers, CRM adapter layer | Direct CRM APIs | Weekly file export + future direct sync | OSS core |
| Stage 15: Feedback Loop | PostgreSQL feedback tables, Prefect scheduled retraining/reweighting flows | MLflow | Closed-loop improvement and traceability | OSS |

## 2) Required Platform Components (Baseline)

1. API and services: `FastAPI`.
2. Workflow orchestration: `Prefect`.
3. AI/state orchestration: `LangGraph`.
4. Crawl and browser: `Scrapy` + `scrapy-playwright` + `Playwright`.
5. Datastores: `PostgreSQL` (+ `pgvector`), `Redis`.
6. Object storage (raw artifacts): `SeaweedFS` (recommended default), or `Ceph` for larger infra teams.
7. LLM runtime: `Ollama` local first.
8. Observability: `OpenTelemetry` + `Prometheus` + `Grafana` + `Loki`.

## 3) Authenticated Pages + CAPTCHA Strategy

1. Source-level policy gate (`allow`, `allow_authenticated_fetch`, `deny`).
2. Login bootstrap job via Playwright and encrypted `storageState`.
3. Session validation job before crawl batches.
4. If CAPTCHA/MFA blocks automation:
   - Pause connector.
   - Route to human re-auth task in review queue.
   - Resume after refreshed session.
5. Keep CAPTCHA solvers optional and per-source approved only.

Recommended policy default:
- No automatic CAPTCHA bypass by default.
- Human-in-the-loop re-auth first.
- Use paid solver only when legal/compliance approves that specific source.

## 4) Ollama-First Model Routing

Use provider adapter with per-task routing:

- `extract_small`: local Ollama (`qwen2.5:7b` or equivalent).
- `extract_complex`: local Ollama larger model (`qwen2.5:14b/32b` depending hardware).
- `reasoning_fallback`: Claude/Gemini only when confidence or latency SLO fails.

Routing rules:
1. Run local model first.
2. If output schema validation fails twice, escalate to cloud fallback.
3. Persist model/provider, prompt hash, and confidence for audits.

## 5) Community/Support Check (as of 2026-05-13)

- Strong OSS community and adoption: Scrapy, Playwright, PostgreSQL, Redis, Ollama, LangGraph, Qdrant, Prefect.
- Important ecosystem note: `minio/minio` GitHub is archived/read-only; prefer evaluating SeaweedFS/Ceph for new builds.

## 6) Implementation Order (Practical MVP)

1. Core DB schema + connector registry + policy engine.
2. Scrapy + Playwright connector framework with one public source + one authenticated source.
3. Raw artifact/evidence storage and stage-level audit logs.
4. Extraction pipeline with Pydantic schema enforcement.
5. Review queue and weekly export.
6. Feedback loop and scoring iteration.

## 7) Optional Alternatives

- Orchestration: Temporal (strong durability) or Airflow (mature ecosystem), if team preference differs from Prefect.
- Vector store: Keep `pgvector` first; adopt Qdrant only when scale/filter needs justify split.
- Observability alternative: OpenObserve all-in-one if team prefers single tool.
