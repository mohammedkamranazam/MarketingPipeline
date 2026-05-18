# AI Lead Intelligence Pipeline Blueprint v1

Date: 2026-05-12

Update note: on 2026-05-13, the blueprint was extended to support seed lead enrichment from bid/platform lead lists without replacing the original account-discovery use case.

Update note: the build plan now requires multiple independent pipelines under each client workspace, with pipeline-scoped datasets, configuration, credentials, run histories, evidence, reviews, exports, and diagnostics. The detailed execution overlay lives in [`multi-pipeline-plan.md`](multi-pipeline-plan.md).

Execution note: this file is the complete reference blueprint. The build-ready modular version lives in [`README.md`](README.md), with ordered phase files, progress percentages, statuses, exit criteria, and test plans.

## 1. Purpose

This blueprint defines an end-to-end architecture for an AI/ML-based lead intelligence pipeline. The pipeline should replace a manual marketing research workflow where people read client documents, understand products and target markets, search the web, inspect forums and marketplaces, find relevant accounts and contacts, and prepare outbound-ready lead lists.

The key design goal is not "scrape everything." The goal is to build a configurable, evidence-based system that can answer:

- Which companies match the client ICP?
- Why do they match?
- What recent signal makes them relevant now?
- Which people at that company should be contacted?
- Which imported seed leads can be safely matched to a company/domain/profile?
- Which verified contact details are provider-sourced and deliverability-checked?
- What source proves each recommendation?
- How confident is the system?
- What should be exported to CRM, weekly lead files, or outreach systems?

## 1.1 Supported Use-Case Lanes

The platform must support two complementary lanes:

| Lane | Starting Point | Primary Workflow | Output |
|---|---|---|---|
| Account discovery | Client documents, approved ICP, configured sources | Discover accounts and signals, extract entities, score, review | Evidence-backed CRM-ready leads |
| Seed lead enrichment | Imported rows with first name, optional last name, company name, source, and notes/project context | Normalize rows, resolve company/domain, rank profile candidates, enrich/verify email, summarize research, review | Verified outreach-ready and CRM-ready leads |

The seed lead enrichment lane reuses the same source policy, evidence, scoring, review, export, audit, and feedback core. It adds import normalization, profile/domain candidate ranking, licensed contact enrichment, email verification, and outreach handoff. It must not weaken the existing discovery controls.

## 1.2 Multi-Pipeline Requirement

Each client workspace must support multiple completely independent pipelines. A pipeline is the operational boundary for datasets, active configuration, source/provider policy, credentials, run history, artifacts, embeddings, extraction results, review decisions, exports, costs, quotas, audit, and diagnostics.

Client-level settings may provide defaults or templates, but pipeline-owned records must include both `client_id` and `pipeline_id`. Credentials are pipeline-scoped by default. A credential, source, provider, run, export, or vector retrieval operation cannot be reused across pipelines unless a later enterprise feature explicitly creates a governed cross-pipeline view or copy workflow.

The detailed phase plan, credential lifecycle, UI requirements, and roadmap plug-in are defined in [`multi-pipeline-plan.md`](multi-pipeline-plan.md).

## 2. Core Architecture Summary

The pipeline has discovery and seed-enrichment input lanes that converge into shared collection, evidence, scoring, review, export, and feedback planes:

```text
                         +------------------------------+
                         |        Expert Console         |
                         | ICP, signals, sources, rules  |
                         +---------------+--------------+
                                         |
                                         v
+----------------+       +---------------+--------------+       +-------------------+
| Client Docs    | ----> | Domain Knowledge Layer        | ----> | Query/Source Plan |
| PDFs, personas |       | structured ICP + RAG memory   |       | what to scan      |
+----------------+       +---------------+--------------+       +---------+---------+
                                                                      |
                                                                      v
                         +------------------------------+
                         | Seed Lead Import Layer       |
                         | bid/CRM/event/campaign rows |
                         +---------------+--------------+
                                         |
                                         v
                         +------------------------------+       +-------------+
                         | Crawl + Collection Layer     | ----> | Raw Store   |
                         | source/search/provider conn. |       | HTML/PDF/API |
                         +---------------+--------------+       +------+------+
                                         |                             |
                                         v                             v
                         +---------------+--------------+       +------+------+
                         | Extraction + Normalization   | <---- | Evidence    |
                         | accounts, signals, contacts, |       | snapshots   |
                         | profiles, verifications      |       |             |
                         +---------------+--------------+       +------+------+
                                         |
                                         v
                         +---------------+--------------+
                         | Scoring + Review Layer       |
                         | ICP score, confidence, HITL  |
                         +---------------+--------------+
                                         |
                                         v
                         +---------------+--------------+
                         | Export + Feedback Layer      |
                         | Excel, CRM, outreach exports |
                         +------------------------------+
```

## 3. Important Design Correction

The pipeline should not work like this:

```text
Scan many sites -> dump everything -> ask LLM to extract final contacts
```

That approach becomes expensive, hard to debug, and noisy.

Instead, use this staged approach:

```text
Scan source -> store raw artifact -> classify page -> extract entities/signals ->
normalize company/contact -> dedupe -> score -> review/export
```

The raw dump still exists, but every downstream object is structured, traceable, and tied to source evidence.

## 4. Inputs

### 4.1 Client Knowledge Documents

These are uploaded by the client or account team. Examples:

- Discovery questionnaires
- Product brochures
- Persona documents
- Competitor analysis
- Existing customer lists
- Existing prospect lists
- Sales call notes
- Case studies
- Trade show lead sheets
- CRM exports
- Campaign calendars
- Website pages
- Internal product positioning docs

For tec5USA, the questionnaire contains:

- Products: inline process spectroscopy, Raman, NIR, UV/VIS
- Target industries: Chemical and Oil & Gas first
- Geography: North America and South America
- Subsegments: refineries, downstream oil and gas, petrochemicals, specialty chemicals, polymers, fine chemicals/API, gas processing, industrial gas
- Exclusions: government RFQs, narcotics detection, defense bid work, direct competitors, lab-only users
- Competitors: Ametek, Horiba, Thermo Fisher, Kaiser/Endress+Hauser, Bruker, Metrohm, Anton Paar, FOSS, Yokogawa, and others
- Target titles: process engineers, plant managers, operations managers, engineering managers, director/VP level, COO, PAT, QA/QC, MSAT, R&D
- Signals: capacity expansion, new plant announcements, hiring, CapEx, trade shows, FDA/PAT filings, M&A
- Output: weekly Excel file for CRM import

### 4.2 Human Expert Configuration

The domain expert or marketing expert should configure the pipeline through an admin UI or database-backed config. This is separate from extracted document knowledge.

Human experts define:

- Industries
- Subsegments
- Account types
- Geography
- Target employee bands
- Target titles
- Seniority levels
- Buying signals
- Exclusion rules
- Competitors
- Source priority
- Export format
- Scoring weights
- Review thresholds
- Suppression lists
- Campaign cadence

The document extractor can suggest values, but a human should approve them before they drive automated crawling or outreach.

### 4.3 Seed Lead Imports

Seed lead imports are structured lists where a source already supplied a partial lead. The system enriches them without replacing the discovery pipeline.

Required fields:

- first name
- company name
- source

Optional fields:

- last name
- title
- location
- company website
- project/bid note
- source record ID
- campaign or inbox assignment hint

Examples:

- Civcast or Dodge bid platform exports
- trade show/event lead sheets
- CRM prospect lists
- campaign lead sheets
- approved partner or marketplace exports

Seed imports produce `lead_import_batches` and `seed_lead_rows`. Each row preserves original values, normalized values, validation errors, source context, dedupe state, and suppression state. Imported rows are not outreach-ready until profile/domain evidence, provider enrichment, email verification, scoring, and review gates pass.

## 5. Main Pipeline Stages

### Stage 1: Client Workspace Setup

Create a workspace per client.

Responsibilities:

- Create client record
- Configure tenant isolation
- Store CRM/export preferences
- Store outreach/export preferences
- Store compliance and source permissions
- Store enabled use-case lanes: account discovery, seed lead enrichment, or both
- Store initial pipeline status
- Define default scoring strategy

Outputs:

- `client_id`
- default config
- data retention policy
- allowed source categories

### Stage 2: Document Ingestion

Documents are uploaded, parsed, chunked, embedded, and stored.

Responsibilities:

- Accept PDF, DOCX, CSV, XLSX, HTML, TXT
- Extract text and tables
- Store original file
- Store extracted text
- Split into chunks for retrieval
- Generate embeddings
- Store document metadata
- Run document-level LLM extraction

Recommended tools:

- `unstructured`, `pypdf`, `python-docx`, `pandas`, `openpyxl`
- Postgres object metadata
- S3-compatible object storage (SeaweedFS or Ceph recommended for self-hosted OSS)
- pgvector for embeddings
- LLM structured output for extraction

Outputs:

- document records
- document chunks
- extracted domain facts
- suggested ICP config
- source citations

### Stage 2B: Seed Lead Import And Normalization

Seed lead files are uploaded, parsed, validated, normalized, and stored separately from document knowledge.

Responsibilities:

- Accept CSV/XLSX seed lead lists.
- Map columns to typed fields: first name, optional last name, company name, source, title, location, project/bid note, source record ID, and campaign hint.
- Preserve original row values and normalized row values.
- Detect missing required fields, invalid rows, duplicates, existing customers, and suppression matches.
- Create row-level validation results that users can inspect before enrichment.
- Route valid rows into profile/domain matching.

Outputs:

- `lead_import_batches`
- `seed_lead_rows`
- row validation errors
- dedupe and suppression state
- source/project context for enrichment and personalization

### Stage 3: Domain Knowledge Extraction

The LLM converts client documents into structured domain knowledge.

Example extracted schema:

```json
{
  "products": [
    {
      "name": "Inline Raman spectroscopy",
      "use_cases": ["factory-floor process analysis", "quality control", "automation"]
    }
  ],
  "industries": ["Chemical", "Oil & Gas"],
  "subsegments": ["refineries", "petrochemical manufacturers"],
  "target_titles": ["Process Engineer", "Plant Manager", "VP Operations"],
  "signals": ["capacity expansion", "new plant", "CapEx announcement"],
  "exclusions": ["government RFQs", "defense bid work"],
  "competitors": ["Ametek", "Horiba", "Thermo Fisher Scientific"]
}
```

Extraction rules:

- Use JSON schema / Pydantic models.
- Every extracted field should include evidence text and document reference.
- Low-confidence extractions must be marked for human review.
- Never let extracted values automatically override human-approved config.

### Stage 4: Expert Review And Configuration

The marketing/domain expert approves or edits the extracted knowledge.

The expert console should support:

- Add/edit/remove industries
- Add/edit/remove subsegments
- Add target titles and seniority mappings
- Define account type rules
- Define signal taxonomy
- Define exclusions and competitors
- Configure source connectors
- Configure search, enrichment, verification, and outreach connectors
- Approve profile/domain matching policy for imported leads
- Approve provider use and deliverability thresholds
- Define export fields
- Define outreach export fields and campaign/inbox defaults
- Adjust scoring weights

This produces the active pipeline configuration.

### Stage 5: Source Registry And Connector Configuration

Each data source should be configured in the database. Do not hardcode sources in the crawler.

Source connector fields:

- `source_id`
- `client_id`
- `source_type`
- `name`
- `base_url`
- `auth_type`
- `allowed_paths`
- `blocked_paths`
- `crawl_depth`
- `rate_limit_per_minute`
- `robots_policy`
- `terms_policy`
- `requires_human_approval`
- `enabled`
- `priority`
- `connector_class`
- `extraction_schema`

Source categories:

| Category | Examples | Recommended Method |
|---|---|---|
| Owned or public websites | News, press, careers, product pages | Scrapy, requests, Playwright, managed extraction service |
| Search providers | Keyword search results | Official API or configured search provider |
| Event directories | Exhibitor lists, agenda pages, speaker pages | API/export if available, otherwise permitted crawl |
| Job or project boards | Public listings, company career pages | API first, crawl only when permitted |
| Contact enrichment systems | Contacts and firmographics | Licensed API/export/integration |
| Email verification systems | Deliverability status and risk | Licensed API/export/integration |
| Outreach systems | Campaign/inbox handoff and engagement outcomes | CSV/API/webhook after review |
| Restricted professional profiles | Profile URLs/snippets | Official API, approved export, search result metadata, or review-only depending on policy |
| News and feeds | Industry publications | RSS/API/licensed feeds |
| Public data portals | Public company or project signals | Official data feeds |
| Forums and communities | Public discussions | Official API where available, public permitted pages |

### Stage 6: Query And Crawl Planning

The planner generates crawl jobs from active config.

Inputs:

- client domain knowledge
- active ICP config
- source registry
- previous crawl history
- seed lead import rows that passed validation
- feedback history
- campaign priority

Example query templates:

```text
"Raman" "process spectroscopy" "petrochemical" "capacity expansion"
"NIR" "fuel blending" "terminal" "process engineer"
"new plant" "specialty chemicals" "North America" "quality control"
"PAT scientist" "API manufacturing" "inline spectroscopy"
site:company.com (Raman OR NIR OR UV/VIS) ("process analytical" OR PAT)
```

The planner should create:

- search jobs
- crawl jobs
- recrawl jobs
- profile/domain search jobs
- enrichment jobs
- email verification jobs
- suppression-check jobs

Each job should be idempotent and retryable.

### Stage 7: Crawl And Raw Data Collection

The crawler fetches web/API data and stores raw artifacts.

Responsibilities:

- Fetch pages/API responses
- Respect source rate limits
- Respect robots and terms policy
- Store raw HTML, markdown, JSON, PDFs, screenshots when useful
- Store crawl metadata
- Track status and errors
- Compute content hash for dedupe

Recommended tools:

- Scrapy for scalable crawling
- Playwright for JS-rendered pages
- Managed extraction service for page-to-markdown or structured web extraction
- requests/httpx for APIs
- Prefect for orchestration
- Redis/Celery or Prefect task runners for background work

Raw artifact storage:

- Postgres for metadata
- S3-compatible object storage for large HTML/PDF/JSON/screenshot artifacts

### Stage 8: Page Classification

Before extracting contacts or leads, classify the page.

Page types:

- company profile
- press release
- job posting
- trade show exhibitor
- trade show attendee/speaker
- article/news
- contact/team page
- product page
- project/RFP page
- forum post
- irrelevant

The classifier can use:

- rules for obvious patterns
- LLM for ambiguous content
- source-specific metadata

Only relevant page types should move to expensive extraction.

### Stage 9: Entity, Signal, And Evidence Extraction

The extraction layer produces structured objects.

Extract:

- company candidates
- account-level signals
- contact candidates
- facilities/locations
- products/processes mentioned
- source evidence
- confidence scores

Example signal schema:

```json
{
  "company_name": "Example Chemicals Inc.",
  "signal_type": "capacity_expansion",
  "signal_date": "2026-04-15",
  "summary": "Company announced expansion of specialty chemical production facility.",
  "matched_industries": ["Chemical"],
  "matched_subsegments": ["specialty chemicals"],
  "matched_use_cases": ["inline process monitoring", "quality control"],
  "evidence_url": "https://example.com/news/expansion",
  "evidence_quote": "short source snippet",
  "confidence": 0.82
}
```

Extraction guardrails:

- Use strict structured output.
- Require evidence URL.
- Require source text span or quote.
- Do not infer private contact information.
- Do not invent emails or phone numbers.
- Mark uncertain results for review.

### Stage 10: Company Resolution And Deduplication

The same company can appear in many sources with different names.

Responsibilities:

- Normalize company names
- Resolve website/domain
- Resolve imported seed lead company names to canonical companies and domains
- Match subsidiaries/parent companies
- Deduplicate by domain, normalized name, and external IDs
- Check CRM suppression
- Check existing pipeline/customer lists
- Check competitor exclusions

Resolution signals:

- domain
- legal name
- DBA names
- address
- external profile URL if available from an approved source
- seed lead source record ID and project/bid context
- enrichment provider IDs if available
- CRM account ID

### Stage 11: Contact Discovery And Enrichment

Contact discovery should happen after account relevance is established. This reduces cost and avoids collecting unnecessary personal data.

For seed lead enrichment, the system starts with a partial person/company row. It should first resolve the company/domain, then collect permitted profile candidates, rank them with evidence, and only then call licensed enrichment and verification providers.

Contact sources:

- licensed contact enrichment providers
- CRM existing contacts
- event or campaign lead sheets
- company leadership/team pages when permitted
- official speaker/exhibitor pages when permitted
- approved source exports
- search-provider profile snippets or URLs when source policy allows

The LLM can extract contact candidates from permitted page text, but verified email and phone should come from licensed enrichment or first-party CRM/trade show data.

Seed enrichment workflow:

```text
seed row
  -> normalize name/company/source/project context
  -> resolve company/domain
  -> search for permitted profile/domain candidates
  -> rank candidates by company match, title relevance, source confidence, and location if available
  -> call licensed enrichment provider with approved identifiers
  -> verify email deliverability
  -> route low-confidence, missing-email, risky, or policy-blocked rows to manual follow-up
```

Email and phone rules:

- Store provider provenance for every email/phone.
- Store verification provider, verification status, confidence/risk, and checked timestamp.
- Do not export unverified, invalid, suppressed, or policy-blocked emails for outreach.
- Track provider failures and rate limits separately from lead quality.

Target title matching should support:

- exact title match
- synonym match
- seniority match
- department/function match
- industry-specific title mappings

Example title groups:

```yaml
process_engineering:
  titles:
    - Process Engineer
    - Senior Process Engineer
    - Process Development Engineer
    - Manufacturing Process Engineer

operations:
  titles:
    - Plant Manager
    - Operations Manager
    - Director of Operations
    - VP Operations
    - COO

quality_pat:
  titles:
    - PAT Scientist
    - QA/QC Manager
    - Quality Engineer
    - MSAT Lead
```

### Stage 12: Lead Scoring

Use hybrid scoring: deterministic rules plus LLM reasoning.

Recommended score:

```text
Account Fit Score: 0-40
Signal Strength Score: 0-25
Use Case Fit Score: 0-15
Contact Quality Score: 0-10
Evidence Confidence Score: 0-10
Total Lead Score: 0-100
```

Example scoring details:

| Dimension | Examples |
|---|---|
| Account fit | industry, geography, employee count, subsegment |
| Signal strength | new plant, expansion, CapEx, hiring, trade show attendance |
| Use-case fit | process monitoring, PAT, inline spectroscopy, QA/QC, automation |
| Contact quality | title relevance, seniority, profile match confidence, verified email, verified phone |
| Evidence confidence | source authority, recency, source count, extraction confidence |

Seed lead scoring should also consider:

- source row quality and completeness
- company/domain resolution confidence
- profile candidate ranking confidence
- provider enrichment confidence
- email verification status
- project/bid note relevance
- suppression and do-not-contact state

Lead tiers:

| Tier | Score | Action |
|---|---:|---|
| A | 85-100 | Send to expert review immediately |
| B | 70-84 | Include in weekly review queue |
| C | 55-69 | Keep for nurture/research |
| D | 0-54 | Do not export unless manually approved |

### Stage 13: Human Review

Human-in-the-loop review is required before CRM export or outreach.

Review statuses:

- new
- needs_research
- approved
- rejected
- duplicate
- existing_customer
- competitor
- not_icp
- bad_contact
- exported
- contacted
- replied
- sql
- opportunity
- closed_won
- closed_lost

The review UI should show:

- company
- website
- source evidence
- matched signals
- matched ICP rules
- contact candidates
- seed lead source row and project context when applicable
- profile/domain candidates and ranking evidence
- email verification and provider provenance
- score breakdown
- why this lead was recommended
- export readiness

### Stage 14: Export

For tec5USA v1, export weekly Excel files for CRM upload. For seed lead enrichment, export an approved outreach-ready CSV/XLSX or payload that can be loaded into a campaign tool only after review, suppression, and verification gates pass.

Future options:

- CRM import API
- CRM object API
- CRM lead/contact/account API
- enrichment-provider tagged list
- CSV/Excel
- webhook or API sync to marketing automation/outreach systems
- dedicated inbox/campaign assignment payloads

Minimum export columns:

- company_name
- website
- hq_city
- hq_state
- hq_country
- zip_code
- employee_band
- industry
- subsegment
- account_type
- signal_type
- signal_summary
- signal_date
- evidence_url
- icp_score
- confidence_score
- contact_name
- contact_title
- contact_email
- contact_phone
- contact_profile_url
- research_note
- source_names
- export_batch_id

Seed enrichment and outreach export columns add:

- seed_import_batch_id
- seed_row_id
- original_source
- source_record_id
- project_or_bid_context
- profile_match_url
- profile_match_confidence
- email_verification_status
- email_verification_provider
- email_verified_at
- outreach_inbox
- campaign_name
- personalization_note

### Stage 15: Feedback Loop

Feedback makes the pipeline improve over time.

Capture:

- approved/rejected leads
- sales comments
- reply/no reply
- sent/opened/replied/bounced/unsubscribed engagement events
- meeting booked
- SQL conversion
- opportunity creation
- closed won/lost
- bad contact reports
- email verification false positives and bounces
- wrong industry reports

Feedback should update:

- scoring weights
- title mappings
- negative keywords
- source priority
- provider priority and verification thresholds
- query templates
- exclusion rules
- lookalike profiles

## 6. Recommended System Components

### 6.1 Services

```text
api-service
  FastAPI backend for config, upload, review, export, and pipeline controls

worker-service
  Background workers for parsing, crawling, extraction, enrichment, scoring

enrichment-worker
  Profile/domain candidate ranking, licensed contact enrichment, and email verification

outreach-worker
  Outreach-ready export building and campaign/engagement outcome import

scheduler-service
  Prefect deployment schedules and recurring workflows

review-ui
  Streamlit for MVP or Next.js for production

storage
  Postgres + pgvector + S3-compatible object storage (SeaweedFS/Ceph)

observability
  logs, traces, prompt runs, job metrics, audit logs
```

### 6.2 AI Subsystems

```text
document_extractor
  Extracts ICP, products, titles, signals, competitors, exclusions from docs

seed_lead_normalizer
  Maps uploaded lead sheets into typed rows with validation, dedupe, and suppression state

retrieval_service
  Retrieves relevant domain chunks for extraction/scoring prompts

page_classifier
  Classifies crawled pages by type and relevance

entity_extractor
  Extracts company, contact, signal, facility, process, and evidence objects

profile_match_ranker
  Ranks permitted profile/domain candidates using evidence, title relevance, company match, and location when available

research_summarizer
  Generates cited two-to-three sentence company/project summaries for reviewed leads

lead_scorer
  Generates score breakdown and explanation

query_planner
  Generates source-specific search queries from config and feedback

feedback_learner
  Converts human decisions into scoring and source-priority improvements
```

## 7. Technology Stack Recommendation

### MVP Stack

| Layer | Tool |
|---|---|
| Language | Python 3.12+ |
| API | FastAPI |
| Workflow orchestration | Prefect |
| Agent/state orchestration | LangGraph |
| Crawling | Scrapy |
| JS rendering | Playwright |
| Managed web extraction option | managed extraction service |
| Database | Postgres |
| Vector search | pgvector |
| ORM/migrations | SQLAlchemy + Alembic |
| Data validation | Pydantic |
| Object storage | SeaweedFS (default) or Ceph, both S3-compatible |
| LLM | Ollama local-first; Claude/Gemini/OpenAI fallback via provider adapter |
| Embeddings | local embedding model via Ollama or provider fallback |
| Admin/review UI | Streamlit for MVP, Next.js for product version |
| Queue/background tasks | Prefect task runners first; Celery/Redis if needed |
| Search/enrichment providers | Provider adapter contracts with mock providers first, licensed APIs later |
| Email verification | Provider adapter contract with mock verifier first, licensed API later |
| Export | XLSX/CSV first, CRM/outreach API later |
| Observability | OpenTelemetry + Prometheus + Grafana + Loki (open-source-first) |

### Why This Stack

- Python is strongest for scraping, data pipelines, LLM tooling, and ML.
- Postgres keeps relational lead data, workflow metadata, and vector search together.
- pgvector avoids adding a separate vector DB too early.
- Prefect is good for scheduled, retryable data workflows.
- LangGraph is useful for stateful AI workflows with human review and checkpoints.
- Scrapy handles broad crawling better than ad hoc scripts.
- Playwright handles JavaScript-heavy pages when needed.
- A managed extraction service can reduce custom scraping work for some sources.
- FastAPI is simple and production-friendly for internal APIs.

### 7.1 Open-Source-First Toolchain Matrix (Consolidated)

This section consolidates tool decisions for all stages and server operations.

| Stage | Required (Open Source First) | Optional/Alternate | Notes |
|---|---|---|---|
| Stage 1 Workspace | FastAPI, PostgreSQL, Alembic, Redis | Keycloak, OPA | Tenant config, policy-aware controls |
| Stage 2 Ingestion | Python, unstructured, pypdf, python-docx, pandas, openpyxl, pgvector | Apache Tika, OCRmyPDF, Tesseract | Typed extraction and chunking |
| Stage 2B Seed Lead Import | pandas, openpyxl, Pydantic, PostgreSQL | CSVBox/import UI later | Typed row normalization and row-level validation |
| Stage 3 Domain Extraction | Ollama + schema-bound extraction (Pydantic) | Claude/Gemini fallback | Local-first with strict validation |
| Stage 4 Expert Review | Streamlit/Next.js review UI, PostgreSQL | Metabase/Superset | Mandatory approval gate |
| Stage 5 Source Registry | Connector/provider registry + encrypted credential references | Vault/SOPS | No hardcoded connectors or provider calls |
| Stage 6 Planning | Prefect + Redis + PostgreSQL | Temporal, Airflow | Prefect default for Python-heavy stack, batch provider calls |
| Stage 7 Collection | Scrapy + Playwright + scrapy-playwright + httpx | Crawlee (Node) | Public + authenticated + JS rendering |
| Stage 8 Classification | Rules + lightweight model + Ollama for edge cases | Cloud LLM fallback | Cost-efficient relevance filtering |
| Stage 9 Extraction | LangGraph + Pydantic + Ollama | Claude/Gemini fallback | Evidence-linked structured outputs |
| Stage 10 Resolution | PostgreSQL SQL + rapidfuzz | Neo4j later | Deterministic dedupe first |
| Stage 11 Enrichment | Approved connectors + policy engine + mock provider/verifier | Licensed enrichment and verification APIs | Compliance-first contact handling, no guessed emails |
| Stage 12 Scoring | Rule scoring + LLM rationale | Feature store later | Transparent hybrid scoring |
| Stage 13 Review | Review queue + audit logs | Slack/Email alerts | Human checkpoint before export |
| Stage 14 Export | pandas + openpyxl + CSV/XLSX | Direct CRM/outreach API | Weekly batch and outreach-ready export first |
| Stage 15 Feedback | PostgreSQL feedback tables + Prefect runs | MLflow | Closed-loop quality and deliverability improvements |

### 7.2 Research-Backed Tool Choices (As of 2026-05-13)

- Strong community-backed OSS core: Scrapy, Playwright, PostgreSQL, Redis, Ollama, LangGraph, Qdrant, Prefect.
- Object storage note: `minio/minio` is marked archived/read-only on GitHub (April 25, 2026). For new open-source-first builds, prefer SeaweedFS or Ceph evaluation.
- Keep cloud LLM vendors behind a provider adapter to prevent lock-in.

### 7.3 Server-Mode HITL Auth/CAPTCHA Operations

When running on a remote server, human-in-the-loop works as a pause/resume workflow:

1. Crawl job reaches auth wall (login expired, MFA, CAPTCHA).
2. Job moves to `needs_human_auth`.
3. Review task is created in UI/Slack/email.
4. Authorized operator completes re-auth in a controlled browser session.
5. Encrypted session state is refreshed.
6. Queue resumes automatically.

Required queue/job states:

```text
queued
running
needs_human_auth
awaiting_manual_review
retry_scheduled
completed
failed
blocked_by_policy
```

### 7.4 Can This Be Fully Automated?

Automation policy by source class:

- Public/API-first sources: fully automated.
- Authenticated but stable portals: semi-automated with periodic session refresh.
- CAPTCHA/MFA/anti-bot heavy sources: HITL fallback must remain available.

Default policy:

- Do not enable automatic CAPTCHA bypass globally.
- Use human re-auth as default for legal/safety/compliance.
- If business-approved, allow per-source paid CAPTCHA solver as explicit opt-in connector behavior.

### 7.5 Ollama-First Model Routing Policy

Provider adapter policy:

1. Run local Ollama model first.
2. Validate against strict schema and evidence requirements.
3. Retry once locally for repair.
4. If still invalid or low-confidence, escalate to Claude/Gemini/OpenAI fallback.
5. Persist provider/model/prompt-hash/confidence for audits.

### 7.6 Self-Hosted Baseline Runtime Stack

Recommended baseline services for first production deployment:

- PostgreSQL (+ pgvector)
- Redis
- Prefect server/worker
- Ollama
- Scrapy worker pool
- Playwright browser workers (via `scrapy-playwright`)
- SeaweedFS (master + volume + filer + S3 gateway) or Ceph
- Optional Qdrant (if vector load outgrows pgvector)
- OpenTelemetry collector + Prometheus + Grafana + Loki

This baseline keeps the full collection/extraction/export pipeline open-source-first while retaining optional cloud-model fallback when required.

## 8. Database Blueprint

### 8.1 Core Tenant Tables

```sql
clients
  id
  name
  website
  status
  created_at
  updated_at

client_users
  id
  client_id
  email
  role
  created_at

client_settings
  id
  client_id
  key
  value_json
  updated_at
```

### 8.2 Document Knowledge Tables

```sql
documents
  id
  client_id
  filename
  file_type
  storage_url
  source_type
  status
  uploaded_by
  created_at

document_pages
  id
  document_id
  page_number
  extracted_text
  extraction_metadata_json

document_chunks
  id
  client_id
  document_id
  chunk_index
  content
  embedding
  metadata_json

extracted_knowledge_items
  id
  client_id
  document_id
  item_type
  name
  value_json
  evidence_text
  confidence
  status
  created_at
```

Knowledge item types:

- product
- use_case
- industry
- subsegment
- target_title
- competitor
- exclusion
- geography
- signal
- persona
- campaign_note

### 8.3 Active ICP Configuration Tables

```sql
products
  id
  client_id
  name
  description
  active

industries
  id
  client_id
  name
  active

subsegments
  id
  client_id
  industry_id
  name
  active

geographies
  id
  client_id
  country
  region
  state
  active

target_titles
  id
  client_id
  title
  title_group
  seniority
  function_area
  priority
  active

signals
  id
  client_id
  name
  description
  weight
  recency_window_days
  active

exclusion_rules
  id
  client_id
  rule_type
  pattern
  reason
  active

competitors
  id
  client_id
  name
  website
  active
```

### 8.4 Source Registry Tables

```sql
source_connectors
  id
  client_id
  name
  source_type
  base_url
  connector_class
  auth_type
  config_json
  rate_limit_json
  compliance_status
  enabled
  priority
  created_at

crawl_jobs
  id
  client_id
  source_connector_id
  job_type
  query
  seed_url
  status
  scheduled_at
  started_at
  finished_at
  error_message

crawl_artifacts
  id
  client_id
  crawl_job_id
  source_connector_id
  url
  canonical_url
  content_hash
  content_type
  http_status
  storage_url
  fetched_at
  metadata_json
```

### 8.5 Extraction Tables

```sql
page_classifications
  id
  client_id
  crawl_artifact_id
  page_type
  relevance_score
  reason
  model_name
  created_at

company_candidates
  id
  client_id
  name
  website
  domain
  hq_city
  hq_state
  hq_country
  employee_band
  industry
  subsegment
  source_confidence
  resolution_status
  created_at

account_signals
  id
  client_id
  company_candidate_id
  signal_type
  signal_date
  summary
  evidence_url
  evidence_artifact_id
  evidence_text
  confidence
  created_at

contact_candidates
  id
  client_id
  company_candidate_id
  full_name
  title
  seniority
  function_area
  email
  phone
  profile_url
  source
  verification_status
  confidence
  created_at
```

### 8.6 Lead Scoring And Review Tables

```sql
lead_candidates
  id
  client_id
  company_candidate_id
  primary_signal_id
  status
  score_total
  score_breakdown_json
  research_note
  created_at
  updated_at

lead_contacts
  id
  lead_candidate_id
  contact_candidate_id
  priority_rank
  contact_role_reason

review_events
  id
  client_id
  lead_candidate_id
  user_id
  event_type
  notes
  created_at

export_batches
  id
  client_id
  export_type
  status
  file_url
  created_at

export_batch_items
  id
  export_batch_id
  lead_candidate_id
  exported_payload_json
  status
```

## 9. Source Connector Interface

Every source should implement the same interface.

```python
from typing import Protocol

class SourceConnector(Protocol):
    source_type: str

    def plan(self, client_config: dict) -> list[dict]:
        """Create crawl/search jobs from active client config."""

    def fetch(self, job: dict) -> list[dict]:
        """Fetch raw pages/API results and return artifacts."""

    def normalize(self, artifact: dict) -> dict:
        """Convert source-specific response into common artifact metadata."""
```

Example connector classes:

```text
CompanyWebsiteConnector
SearchApiConnector
TradeShowConnector
MarketplaceApiConnector
ContactEnrichmentConnector
SecondaryContactEnrichmentConnector
CrmConnector
SecondaryCrmConnector
RssNewsConnector
ForumConnector
```

## 10. LangGraph Workflow Shape

Use LangGraph for AI-heavy stateful flows where checkpoints and human review matter.

Example graph:

```text
START
  |
  v
load_client_config
  |
  v
retrieve_domain_context
  |
  v
plan_queries
  |
  v
dispatch_crawl_jobs
  |
  v
classify_artifacts
  |
  v
extract_entities_and_signals
  |
  v
resolve_companies
  |
  v
enrich_contacts
  |
  v
score_leads
  |
  v
needs_human_review? -- yes --> review_queue --> apply_feedback
  | no
  v
export_batch
  |
  v
END
```

Use Prefect outside LangGraph to schedule and monitor the workflow:

```text
Prefect weekly flow
  -> run source planning
  -> run crawling batches
  -> run extraction graph
  -> run scoring
  -> create review queue
  -> create export batch
```

## 11. RAG Design For Client Domain Understanding

The client docs should form a small client-specific knowledge base.

Indexing:

```text
document -> pages -> chunks -> embeddings -> pgvector
```

Retrieval is used during:

- query generation
- page extraction
- account scoring
- research note generation
- expert review explanations

Retrieval query examples:

```text
"target industries and subsegments"
"excluded account types and competitors"
"ideal customer profile titles"
"product use cases and ROI"
"signals that indicate buying intent"
```

Important:

- Use the same embedding model for indexing and retrieval.
- Store document metadata with each chunk.
- Keep extracted structured config separate from raw RAG chunks.
- Prefer structured config for rules.
- Use RAG chunks for context and explanation.

## 12. Example tec5USA Active Config

```yaml
client: tec5USA

products:
  - Raman inline process spectroscopy
  - NIR inline process spectroscopy
  - UV/VIS inline process spectroscopy

industries:
  - Chemical
  - Oil & Gas

geography:
  include:
    - North America
    - South America

employee_count:
  min: 50
  max: null

subsegments:
  - refineries
  - downstream oil and gas
  - fuel blending
  - terminals
  - petrochemical manufacturers
  - specialty chemical manufacturers
  - polymer and plastics producers
  - fine chemical API manufacturers
  - gas processing
  - industrial gas companies

target_title_groups:
  process_engineering:
    priority: 1
    titles:
      - Process Engineer
      - Senior Process Engineer
      - Process Development Engineer
      - Manufacturing Process Engineer
  operations:
    priority: 2
    titles:
      - Plant Manager
      - Operations Manager
      - Director of Operations
      - VP Operations
      - COO
  quality_pat:
    priority: 3
    titles:
      - PAT Scientist
      - QA/QC Manager
      - Quality Engineer
      - MSAT Lead
  engineering_management:
    priority: 4
    titles:
      - Engineering Manager
      - Director of Engineering
      - Automation Engineer
      - Instrumentation Engineer

signals:
  - name: capacity_expansion
    weight: 25
  - name: new_plant_announcement
    weight: 25
  - name: process_engineering_hiring
    weight: 20
  - name: capex_project
    weight: 20
  - name: trade_show_activity
    weight: 15
  - name: product_line_launch
    weight: 10

exclusions:
  - government RFQ
  - narcotics detection
  - defense bid work
  - direct competitor
  - lab-only spectroscopy user

delivery:
  cadence: weekly
  format: xlsx
  destination: crm_import
```

## 13. LLM Usage Pattern

Use LLMs for structured reasoning and extraction, not uncontrolled browsing.

Good LLM tasks:

- extract structured ICP from documents
- classify pages
- extract signals from text
- summarize why a company fits
- map messy titles into target title groups
- rank profile/domain candidates against a seed lead row
- score fit with evidence
- generate search query variants
- generate cited research and personalization notes from stored evidence

Avoid:

- asking the LLM to browse without source constraints
- asking it to guess emails or phone numbers
- treating LLM-selected email guesses as verified contact data
- accepting uncited claims
- making outreach decisions without human approval
- one LLM call per item at scale

Recommended extraction pattern:

```text
input = source text + client config + retrieved domain context
output = strict JSON schema
validation = Pydantic + evidence required
storage = structured DB rows + raw response audit
```

## 14. Compliance And Data Governance

This pipeline handles company data and personal contact data, so governance must be designed from day one.

Rules:

- Respect robots.txt and source terms.
- Prefer official APIs and licensed data providers.
- Use official APIs, approved exports, or permitted crawling modes for restricted sources.
- Keep restricted sources behind explicit connector policy controls.
- Store source evidence and terms status per connector.
- Encrypt API keys and personal data.
- Maintain suppression lists.
- Maintain unsubscribe/do-not-contact lists.
- Add audit logs for exports and contact enrichment.
- Add audit logs for profile search, email verification, and outreach export.
- Require verified deliverability status before outreach export.
- Track bounces, unsubscribes, and do-not-contact updates as compliance-impacting feedback.
- Review CAN-SPAM, GDPR, CCPA/CPRA, CASL, and LGPD requirements depending on geography.
- Export only reviewed and approved contacts.

PII controls:

- Role-based access control
- Field-level masking for emails/phones if needed
- Retention policy
- Deletion workflow
- Consent/source provenance tracking
- Export audit trail

## 15. MVP Implementation Plan

### Phase 0: Architecture And Schema

Deliverables:

- `clients`, `documents`, `lead_import_batches`, `seed_lead_rows`, `source_connectors`, `company_candidates`, `account_signals`, `contact_candidates`, `lead_candidates` tables
- FastAPI skeleton
- Postgres + pgvector setup
- Object storage setup
- Basic admin config model

### Phase 1: Document And Seed Lead Intelligence

Deliverables:

- PDF/DOCX/XLSX ingestion
- CSV/XLSX seed lead import
- Text extraction
- Seed row normalization and validation
- Chunking + embeddings
- LLM-based ICP extraction
- Human approval screen for extracted config

### Phase 2: Source Registry, Providers, And First Crawlers

Start with safe, high-value sources:

- company websites
- press/news pages
- RSS/news feeds
- trade show public pages where permitted
- job/careers pages where permitted
- search providers for permitted profile/domain discovery
- licensed enrichment and email verification providers

Deliverables:

- source connector interface
- provider connector interface
- source config UI
- crawl job scheduler
- raw artifact store
- search/profile artifact store

### Phase 3: Extraction And Scoring

Deliverables:

- page classifier
- signal extractor
- company extractor
- title/contact candidate extractor
- company resolver
- seed lead company/domain resolver
- profile candidate ranking
- first scoring model
- evidence-backed research notes

### Phase 4: Contact Enrichment

Deliverables:

- licensed contact enrichment integration
- email verification integration
- CRM dedupe
- contact verification status
- title-group matching
- manual follow-up state for missing or risky contact data

### Phase 5: Review And Export

Deliverables:

- review dashboard
- lead approval/rejection
- weekly Excel export
- CRM import mapping
- outreach-ready export mapping
- export audit log

### Phase 6: Feedback Learning

Deliverables:

- feedback capture
- scoring weight adjustment
- source quality scoring
- provider quality and deliverability scoring
- query template refinement
- lookalike profile generation

## 16. Suggested Repository Structure

```text
marketing-pipeline/
  app/
    api/
      main.py
      routes/
        clients.py
        documents.py
        config.py
        sources.py
        leads.py
        exports.py
    core/
      settings.py
      security.py
      logging.py
    db/
      models.py
      session.py
      migrations/
    schemas/
      client.py
      document.py
      icp.py
      source.py
      extraction.py
      lead.py
    services/
      document_ingestion/
      rag/
      source_registry/
      crawling/
      extraction/
      enrichment/
      scoring/
      export/
      feedback/
    workflows/
      weekly_pipeline.py
      document_ingestion_flow.py
      crawl_flow.py
      extraction_graph.py
    connectors/
      base.py
      search_api.py
      company_site.py
      rss_news.py
      trade_show.py
      marketplace_api.py
      contact_enrichment.py
      secondary_contact_enrichment.py
      crm.py
      secondary_crm.py
    review_ui/
      streamlit_app.py
  tests/
  devops/docker-compose.yml
  src/backend/pyproject.toml
  README.md
```

## 17. Key APIs And Tool References

- Scrapy: high-level crawling and scraping framework for extracting structured data from websites: https://docs.scrapy.org/
- Playwright: browser automation for JavaScript-heavy pages: https://playwright.dev/
- scrapy-playwright: Playwright integration for Scrapy: https://github.com/scrapy-plugins/scrapy-playwright
- Managed extraction service: optional structured web extraction from pages using a schema or prompt
- LangGraph: durable execution, streaming, human-in-the-loop agent orchestration: https://docs.langchain.com/langgraph
- Prefect schedules: scheduled workflow runs with cron, interval, and RRule options: https://docs.prefect.io/latest/concepts/schedules
- Temporal (alternative orchestrator): https://github.com/temporalio/temporal
- Airflow (alternative orchestrator): https://github.com/apache/airflow
- Ollama (local LLM runtime): https://github.com/ollama/ollama
- OpenAI Structured Outputs: schema-constrained model output: https://platform.openai.com/docs/guides/structured-outputs
- pgvector: vector similarity search for Postgres: https://github.com/pgvector/pgvector
- Qdrant (optional vector DB): https://github.com/qdrant/qdrant
- SeaweedFS (recommended S3-compatible OSS object storage): https://github.com/seaweedfs/seaweedfs
- Ceph (recommended OSS storage alternative): https://github.com/ceph/ceph
- CRM import API: import contacts, companies, notes, and CRM records through the chosen CRM.
- Marketplace API: use official marketplace or job-board APIs where permissions allow
- Contact enrichment API: use the chosen licensed enrichment provider API
- Search provider API: use approved search APIs for profile/domain candidate discovery
- Email verification API: use the chosen licensed deliverability verification provider API
- Outreach/marketing automation API: use the chosen campaign platform API only after review/export approval
- Restricted source terms: use official APIs or approved imports for restricted sources
- FTC CAN-SPAM compliance guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

## 18. Configurable Search And Source Scraping Architecture

The pipeline should support arbitrary configured sources without hardcoding domains into the workflow. The architecture should separate discovery, policy decisions, fetching, extraction, and enrichment.

### 18.1 Source Flow

```text
ICP config + source config
  |
  v
search provider
  Search API / custom search provider / managed search service / source-native API
  |
  v
url_candidates
  |
  v
source policy engine
  allow / block / require official API / require manual import / require review
  |
  v
connector router
  GenericWebConnector / ManagedExtractionConnector / ApiConnector / RestrictedSourceConnector
  |
  v
raw artifacts
  HTML / markdown / JSON / PDF / screenshot metadata
  |
  v
page classifier
  |
  v
entity + signal extraction
  |
  v
company/contact resolution
```

This means the pipeline can begin from:

- manually configured source URLs
- search queries generated from ICP
- managed search results
- search-provider results
- source-native APIs
- uploaded CSV/XLSX exports
- CRM exports

### 18.2 Source Policy Engine

The source policy engine is mandatory. It prevents the crawler from treating every search result URL as equally fetchable.

Policy decision values:

```text
allow_fetch
allow_authenticated_fetch
allow_api_only
allow_manual_import_only
allow_mock_only
require_human_approval
block
```

Example policy config:

```yaml
source_policies:
  default:
    decision: require_human_approval
    respect_robots_txt: true
    max_pages_per_domain: 100
    rate_limit_per_minute: 10

  owned_public_websites:
    decision: allow_fetch
    connector: GenericWebConnector
    respect_robots_txt: true

  event_directories:
    decision: allow_fetch
    connector: GenericWebConnector
    respect_robots_txt: true

  news_or_feeds:
    decision: allow_fetch
    connector: RssConnector

  authenticated_owned_site:
    decision: allow_authenticated_fetch
    connector: AuthenticatedWebConnector
    requires_authorized_access: true

  marketplace_or_job_board:
    decision: allow_api_only
    connector: MarketplaceApiConnector
```

### 18.3 URL Candidate Table

Search results should not be fetched immediately. Store them first, then route them through policy.

```sql
url_candidates
  id
  client_id
  source_query_id
  discovered_by
  url
  domain
  title
  snippet
  rank
  discovered_at
  policy_decision
  policy_reason
  routed_connector
  status
```

Statuses:

```text
new
policy_pending
approved_for_fetch
api_only
manual_import_only
mock_only
blocked
fetched
failed
```

### 18.4 Search Provider Interface

Search providers only discover URLs. They do not decide whether a URL can be fetched.

```python
from typing import Protocol

class SearchProvider(Protocol):
    name: str

    def search(self, query: str, config: dict) -> list[dict]:
        """Return URL candidates with title, snippet, rank, and metadata."""
```

Implementations:

```text
GenericSearchProvider
ProgrammableSearchProvider
SearchAggregatorProvider
ManagedSearchProvider
SourceNativeSearchProvider
CsvSeedProvider
```

### 18.5 Connector Router

The connector router picks a connector only after policy evaluation.

```python
def route_candidate(candidate: UrlCandidate, policy: SourcePolicy) -> str:
    if policy.decision == "allow_fetch":
        return policy.connector
    if policy.decision == "allow_authenticated_fetch":
        return policy.connector
    if policy.decision == "allow_api_only":
        return policy.connector
    if policy.decision == "allow_manual_import_only":
        return "ManualImportConnector"
    if policy.decision == "allow_mock_only":
        return "MockFixtureConnector"
    if policy.decision == "require_human_approval":
        return "ReviewQueue"
    return "BlockedConnector"
```

### 18.6 Generic Fetch Connector

Use this only for sources that are allowed by policy.

```python
class GenericWebConnector:
    def fetch(self, url: str, config: dict) -> dict:
        """Fetch an allowed public page and store a raw artifact."""
        # Implementation should include timeout, retry, rate limit, robots policy,
        # content hash, canonical URL, and artifact storage.
        raise NotImplementedError
```

The generic connector should support:

- HTTP fetch
- optional Playwright rendering for allowed JS-heavy sites
- rate limits
- content hash deduplication
- canonical URL extraction
- metadata extraction
- raw artifact storage
- screenshot metadata only when needed

### 18.7 Authenticated Source Configuration Page

The application should provide a source configuration page where an admin can register one or more crawlable sources. A source can be public or authenticated. Authenticated crawling is intended for sites where the operator has authorized access, such as owned portals, client-provided portals, private directories, internal tools, or paid data systems that allow this usage.

UI fields:

```text
Source name
Source type: website / portal / directory / feed / API / search provider
Base URL
Seed URLs
Allowed URL patterns
Blocked URL patterns
Crawl depth
Max pages per run
Rate limit
Render mode: HTTP only / browser rendering
Auth required: yes/no
Auth strategy
Credential profile
Login test status
Last crawl status
Enabled/disabled
```

Auth strategies:

```text
none
basic_auth
form_login
cookie_import
session_storage_state
oauth_client_credentials
api_key_header
api_key_query_param
custom_login_flow
```

### 18.8 Credential Vault And Session Manager

Credentials must not be stored directly in source config rows. Store encrypted secrets in a vault or encrypted secret table, then reference them by ID.

Credential profile table:

```sql
source_credentials
  id
  client_id
  source_connector_id
  name
  auth_strategy
  username_secret_ref
  password_secret_ref
  api_key_secret_ref
  cookie_secret_ref
  oauth_client_id_secret_ref
  oauth_client_secret_secret_ref
  browser_storage_state_secret_ref
  login_url
  login_config_json
  status
  last_validated_at
  created_at
  updated_at
```

Session manager responsibilities:

- Retrieve credentials from the vault only at runtime.
- Run login flow if no valid session exists.
- Store browser session state separately from raw credentials.
- Refresh expired sessions.
- Mark credentials invalid when login fails.
- Support manual re-auth when MFA or CAPTCHA is present.
- Never expose secrets in logs, crawl artifacts, screenshots, traces, or LLM prompts.

### 18.9 Authenticated Crawl Flow

Authenticated crawling should work like this:

```text
configured source selected
  |
  v
load source config
  |
  v
auth required?
  |
  +-- no  -> GenericWebConnector
  |
  +-- yes -> credential lookup
              |
              v
            session manager
              |
              v
            login / restore session
              |
              v
            authenticated browser or HTTP client
              |
              v
            scoped crawler
              |
              v
            raw artifacts
```

The authenticated connector should support two execution modes:

```text
HTTP session mode
  Good for form login, cookies, simple pages, APIs, server-rendered pages.

Browser session mode
  Good for JavaScript-heavy portals, dynamic navigation, client-side rendering.
```

Browser session mode should use a saved storage state when possible:

```text
login once
  -> save encrypted browser storage state
  -> reuse storage state on future runs
  -> refresh when expired
```

### 18.10 Search-Origin Flow With Authenticated Sources

The pipeline can start from search results and then decide whether a result belongs to a configured authenticated source.

```text
search query generated from ICP
  |
  v
search provider returns URL candidates
  |
  v
normalize URL and domain
  |
  v
match URL against configured source registry
  |
  +-- matching authenticated source
  |     |
  |     v
  |   use that source's credential profile and crawl scope
  |
  +-- matching unauthenticated source
  |     |
  |     v
  |   fetch with generic connector
  |
  +-- no configured source match
        |
        v
      apply default policy: ignore / require review / fetch public page
```

Matching rules:

- exact domain match
- subdomain match
- allowed URL pattern match
- source alias match
- canonical URL match

Example:

```text
Configured source:
  base_url = https://client-portal.example.com
  allowed_patterns = /companies/*, /profiles/*
  credential_profile = client_portal_admin

Search result:
  https://client-portal.example.com/companies/acme

Decision:
  Use AuthenticatedWebConnector with credential profile client_portal_admin.
```

### 18.11 Scoped Crawling Rules

Authenticated crawling must be tightly scoped so the crawler does not wander through unrelated or destructive pages.

Required controls:

- allowed domains
- allowed path patterns
- blocked path patterns
- max depth
- max pages
- max runtime
- rate limit
- content type allowlist
- query parameter rules
- duplicate URL canonicalization
- logout URL blocklist
- write-action blocklist

Blocked action examples:

```text
/logout
/delete
/remove
/update
/edit
/checkout
/payment
/settings
/admin/actions
```

The crawler should default to read-only GET requests unless a connector explicitly defines a safe POST required for search pagination or login.

### 18.12 Authenticated Connector Interface

```python
from typing import Protocol

class AuthenticatedWebConnector(Protocol):
    def validate_credentials(self, source_config: dict, credential_profile: dict) -> dict:
        """Attempt login and return validation status without crawling."""

    def create_session(self, source_config: dict, credential_profile: dict) -> object:
        """Create an authenticated HTTP or browser session."""

    def fetch(self, url: str, session: object, source_config: dict) -> dict:
        """Fetch a URL using the authenticated session and store a raw artifact."""

    def discover_links(self, artifact: dict, source_config: dict) -> list[str]:
        """Extract in-scope links for recursive crawling."""
```

### 18.13 Authenticated Source Configuration Example

```yaml
sources:
  - name: Client Portal
    type: authenticated_website
    connector: AuthenticatedWebConnector
    enabled: true
    base_url: https://client-portal.example.com
    seed_urls:
      - https://client-portal.example.com/companies
      - https://client-portal.example.com/projects
    auth:
      required: true
      strategy: form_login
      credential_profile: client_portal_admin
      login_url: https://client-portal.example.com/login
      username_selector: input[name="email"]
      password_selector: input[name="password"]
      submit_selector: button[type="submit"]
      success_selector: nav.account-menu
    crawl:
      render_mode: browser
      max_depth: 3
      max_pages_per_run: 1000
      rate_limit_per_minute: 30
      allowed_patterns:
        - /companies/*
        - /projects/*
        - /profiles/*
      blocked_patterns:
        - /logout
        - /settings/*
        - /admin/actions/*
        - /delete/*
```

### 18.14 Source Configuration Example

```yaml
sources:
  - name: Search provider
    type: search_provider
    provider: generic_search_provider
    enabled: true
    queries:
      - '"Raman" "process engineer" "specialty chemicals"'
      - '"NIR" "fuel blending" "operations manager"'

  - name: Managed extraction service search
    type: search_provider
    provider: managed_search_provider
    enabled: true
    queries:
      - '"inline spectroscopy" "petrochemical" "capacity expansion"'

  - name: Company websites
    type: crawl_source
    connector: GenericWebConnector
    enabled: true
    seed_urls:
      - https://examplechemical.com/news
      - https://examplechemical.com/careers

  - name: Event directory
    type: crawl_source
    connector: GenericWebConnector
    enabled: true
    seed_urls:
      - https://example-event-directory.com/exhibitors
```

## 19. Plugin-Based Enterprise Pipeline Architecture

Your proposed flow is aligned with the current blueprint at a conceptual level, but the architecture should be adjusted in three important ways:

- Treat scrape/crawl, API collection, file loading, and web search as first-class plugins, not hardcoded connectors.
- Split the pipeline into two knowledge-building passes: first over customer/domain input, then over discovered external data.
- Add an explicit discovery layer that uses the domain knowledge, ICP config, and knowledge graph to decide what external data is worth collecting.

The enterprise-grade version should look like this:

```text
Customer docs + domain expert config
  |
  v
Seed Knowledge Pipeline
  extract -> enrich -> embed -> build knowledge graph -> store
  |
  v
Discovery Planner
  uses ICP + KG + vector search + rules to decide what to collect
  |
  v
Plugin-Based Discovery Layer
  scrape/crawl plugin
  API plugin
  file-storage plugin
  search-and-crawl plugin
  enabled/disabled per client and per run
  |
  v
Raw Discovery Store
  raw HTML / JSON / files / search results / API responses
  |
  v
Discovered Knowledge Pipeline
  clean -> classify -> extract -> enrich -> embed -> update knowledge graph
  |
  v
Lead Intelligence Pipeline
  retrieve context -> extract contacts/signals/accounts -> score -> review -> export
```

### 19.1 Control Plane And Data Plane

Separate the system into a control plane and a data plane.

Control plane:

- Client workspace management
- Plugin registry
- Plugin enable/disable controls
- Source configuration
- Credential profile references
- Expert ICP configuration
- Pipeline schedules
- Review workflows
- Audit logs

Data plane:

- Document ingestion
- File loading
- API calls
- Web search
- Crawling/scraping
- Raw artifact storage
- Extraction
- Enrichment
- Embedding
- Knowledge graph building
- RAG retrieval
- Lead/contact extraction
- Scoring and export

This separation makes the system scalable because business users configure what should happen while workers execute collection and extraction independently.

### 19.2 Plugin Model

Every external data collection method should implement the same plugin contract.

Plugin types:

```text
scrape_crawl
api_call
file_storage
web_search
database_import
manual_upload
```

Plugin states:

```text
enabled
disabled
paused
error
requires_configuration
requires_credentials
```

Plugin interface:

```python
from typing import Protocol

class DiscoveryPlugin(Protocol):
    plugin_type: str

    def validate_config(self, config: dict) -> dict:
        """Validate plugin config before a run starts."""

    def plan(self, context: dict) -> list[dict]:
        """Create collection jobs from ICP, KG, source config, and run context."""

    def collect(self, job: dict) -> list[dict]:
        """Collect raw artifacts from the configured source."""

    def normalize(self, artifact: dict) -> dict:
        """Normalize plugin-specific output into the common raw artifact schema."""

    def healthcheck(self) -> dict:
        """Report whether the plugin is ready to run."""
```

The pipeline orchestrator should never know implementation details of a plugin. It should only call `validate_config`, `plan`, `collect`, and `normalize`.

### 19.3 Plugin Registry Tables

```sql
plugin_definitions
  id
  name
  plugin_type
  description
  handler_class
  version
  config_schema_json
  enabled_globally
  created_at
  updated_at

client_plugin_instances
  id
  client_id
  plugin_definition_id
  display_name
  enabled
  config_json
  credential_profile_id
  schedule_json
  priority
  created_at
  updated_at

plugin_runs
  id
  client_id
  client_plugin_instance_id
  run_id
  status
  started_at
  finished_at
  records_collected
  artifacts_created
  error_message
  metrics_json

plugin_jobs
  id
  plugin_run_id
  job_type
  input_json
  status
  retry_count
  started_at
  finished_at
  error_message
```

### 19.4 Plugin Examples

Scrape/crawl plugin:

```yaml
plugin_type: scrape_crawl
enabled: true
config:
  seed_urls:
    - https://example.com/companies
  auth_required: true
  credential_profile: example_portal_user
  render_mode: browser
  max_depth: 3
  max_pages_per_run: 1000
  allowed_patterns:
    - /companies/*
    - /projects/*
  blocked_patterns:
    - /logout
    - /settings/*
```

API plugin:

```yaml
plugin_type: api_call
enabled: true
config:
  base_url: https://api.example.com
  auth_strategy: api_key_header
  endpoints:
    - path: /companies
      method: GET
      pagination: cursor
    - path: /contacts
      method: GET
      pagination: page_number
  rate_limit_per_minute: 60
```

File-storage plugin:

```yaml
plugin_type: file_storage
enabled: true
config:
  storage_type: object_storage
  path_prefix: client_uploads/research/
  file_patterns:
    - "*.pdf"
    - "*.docx"
    - "*.xlsx"
    - "*.csv"
  incremental: true
```

Web-search plugin:

```yaml
plugin_type: web_search
enabled: true
config:
  provider: generic_search_provider
  query_templates:
    - '"{industry}" "{signal}" "{target_title}"'
    - '"{product_use_case}" "{subsegment}" "{geography}"'
  max_results_per_query: 20
  result_policy: store_candidates_then_route
```

### 19.5 Seed Knowledge Pipeline

This is the first mandatory step. It processes customer docs and expert configuration before any external discovery.

Inputs:

- Customer documents
- Product docs
- Questionnaires
- Persona files
- Competitor notes
- Existing customer/prospect files
- Domain expert configuration

Pipeline:

```text
load docs/config
  |
  v
parse and normalize
  |
  v
chunk for RAG
  |
  v
extract structured ICP/entities/signals
  |
  v
human approval of config
  |
  v
embed chunks
  |
  v
build seed knowledge graph
  |
  v
store in DB
```

Best practices:

- Use structured output schemas for extraction.
- Store source evidence for every extracted fact.
- Keep raw text, chunks, embeddings, entities, and graph relationships separate.
- Use human approval before extracted config drives discovery.
- Use metadata-rich chunks so retrieval can filter by client, document type, entity type, and confidence.

### 19.6 Discovery Planner

The discovery planner decides what to collect from enabled plugins.

Inputs:

- Active ICP config
- Seed knowledge graph
- Vector search over customer docs
- Existing discovered knowledge
- Feedback from previous runs
- Enabled plugin instances

Planner outputs:

- Search queries
- URLs to crawl
- API jobs
- File-load jobs
- Recrawl jobs
- Enrichment jobs

Planner logic:

```text
retrieve relevant seed knowledge
  |
  v
generate discovery hypotheses
  |
  v
convert hypotheses into plugin jobs
  |
  v
rank jobs by expected value
  |
  v
apply source policy, rate limits, and dedupe
  |
  v
dispatch jobs to enabled plugins
```

Example discovery hypothesis:

```json
{
  "hypothesis": "Companies in this subsegment announcing expansion projects are high-fit accounts.",
  "target_entities": ["company", "project", "facility", "contact"],
  "signals": ["capacity_expansion", "new_facility"],
  "plugin_types": ["web_search", "scrape_crawl", "api_call"],
  "priority": 0.87
}
```

### 19.7 Discovery Layer

The discovery layer collects external data using enabled plugins.

Collection sequence:

```text
plugin job created
  |
  v
plugin validates config and credentials
  |
  v
plugin collects raw artifacts
  |
  v
raw artifacts stored in bronze layer
  |
  v
artifact metadata emitted for processing
```

Use a medallion-style data architecture:

```text
Bronze
  Raw artifacts exactly as collected:
  HTML, JSON, PDF, CSV, XLSX, screenshots, API responses, search results.

Silver
  Cleaned and normalized records:
  page text, normalized JSON, parsed tables, detected language, canonical URLs.

Gold
  Business-ready intelligence:
  companies, contacts, signals, relationships, scores, research notes.
```

This is a proven enterprise pattern because it preserves raw lineage while letting downstream models operate on clean data.

### 19.8 Discovered Knowledge Pipeline

Every collected artifact should go through the same intelligence pipeline.

```text
raw artifact
  |
  v
content extraction
  |
  v
language detection and cleanup
  |
  v
page/document classification
  |
  v
relevance filter using ICP + vector retrieval
  |
  v
structured extraction
  |
  v
entity resolution
  |
  v
embedding
  |
  v
knowledge graph update
  |
  v
gold intelligence tables
```

Relevance filtering should happen before expensive extraction. Use a cascade:

```text
cheap rules
  keyword/domain/path filters
  |
  v
embedding similarity
  compare artifact to ICP/domain context
  |
  v
LLM classifier
  only for borderline or high-value artifacts
```

This reduces cost and improves quality.

### 19.9 Knowledge Graph Design

Use a knowledge graph to connect entities and evidence.

Core node types:

```text
Client
Product
UseCase
Industry
Subsegment
Company
Facility
Project
Signal
Person
Title
Source
Artifact
Document
Campaign
```

Core relationship types:

```text
TARGETS
BELONGS_TO_INDUSTRY
HAS_SUBSEGMENT
MENTIONS
EVIDENCED_BY
HAS_SIGNAL
EMPLOYS
HAS_TITLE
LOCATED_IN
COMPETES_WITH
MATCHES_ICP
EXCLUDED_BY
DISCOVERED_FROM
```

Start with Postgres graph tables:

```sql
kg_nodes
  id
  client_id
  node_type
  canonical_name
  properties_json
  confidence
  created_at
  updated_at

kg_edges
  id
  client_id
  source_node_id
  target_node_id
  edge_type
  properties_json
  evidence_artifact_id
  confidence
  created_at
```

If graph traversal becomes a major product feature, a dedicated graph database can be added later. For the MVP, Postgres edge tables are usually enough and keep infrastructure simpler.

### 19.10 RAG And Retrieval Optimization

Use RAG at three levels:

```text
Seed RAG
  Retrieves customer/domain docs.

Discovery RAG
  Retrieves ICP context to decide whether collected data is relevant.

Lead RAG
  Retrieves evidence around a company/person/signal before final LLM scoring.
```

Recommended retrieval techniques:

- Chunk documents with 500-1500 character chunks and 10-20% overlap.
- Store metadata: `client_id`, `source_type`, `artifact_id`, `entity_type`, `confidence`, `created_at`.
- Use metadata filters before vector search.
- Use hybrid retrieval: keyword search plus vector similarity.
- Use MMR to avoid retrieving five near-duplicate chunks.
- Rerank top results before LLM scoring when quality matters.
- Retrieve around entities, not just free text queries.
- Keep embedding model consistent across indexing and retrieval.

Lead extraction prompt context should be assembled like this:

```text
company node
  + related signals
  + related contacts
  + evidence artifacts
  + relevant seed ICP chunks
  + scoring rules
```

### 19.11 Lead Intelligence Pipeline

Once discovered data is stored as knowledge, run the final LLM lead intelligence pipeline.

```text
candidate company/person/signal nodes
  |
  v
retrieve supporting evidence
  |
  v
LLM extracts marketing intelligence
  |
  v
validate structured output
  |
  v
score account/contact/signal
  |
  v
dedupe against existing records
  |
  v
human review
  |
  v
export
```

Structured output schema:

```json
{
  "company": {
    "name": "string",
    "website": "string",
    "industry": "string",
    "subsegment": "string",
    "fit_reason": "string"
  },
  "signals": [
    {
      "type": "string",
      "summary": "string",
      "evidence_url": "string",
      "confidence": 0.0
    }
  ],
  "contacts": [
    {
      "name": "string",
      "title": "string",
      "role_relevance": "string",
      "evidence_url": "string",
      "profile_candidate_url": "string",
      "email_verification_status": "verified|risky|invalid|unknown|not_requested",
      "confidence": 0.0
    }
  ],
  "seed_context": {
    "seed_lead_row_id": "uuid or null",
    "source": "string",
    "project_context": "string"
  },
  "score": {
    "account_fit": 0,
    "signal_strength": 0,
    "contact_quality": 0,
    "evidence_quality": 0,
    "total": 0
  }
}
```

### 19.12 Orchestration Pattern

Use workflow orchestration for durable scheduled runs and graph orchestration for AI state.

Recommended split:

```text
Workflow orchestrator
  schedules, retries, task queues, backfills, plugin runs, batch processing.

AI graph orchestrator
  stateful extraction, retrieval, LLM calls, human review checkpoints.
```

Enterprise-grade run pattern:

```text
run_id created
  |
  v
load enabled plugins
  |
  v
run seed knowledge updates if docs/config changed
  |
  v
create discovery plan
  |
  v
execute plugin jobs in parallel with rate limits
  |
  v
process artifacts through bronze -> silver -> gold
  |
  v
update vector index and knowledge graph
  |
  v
extract and score leads
  |
  v
create review/export batch
```

### 19.13 Scalability And Reliability Best Practices

Use these practices from enterprise data/AI pipelines:

- Idempotent jobs: every job can be safely retried.
- Content hashing: avoid reprocessing unchanged artifacts.
- Checkpointing: resume long runs after failure.
- Dead-letter queue: failed jobs are preserved for debugging.
- Backpressure: plugin workers respect rate limits and queue capacity.
- Data contracts: every plugin outputs the same artifact schema.
- Schema versioning: extracted records include schema/model version.
- Lineage: every entity links back to artifact, source, plugin run, and evidence.
- Observability: metrics for pages collected, extraction cost, token usage, errors, lead quality.
- Human-in-the-loop gates: approval before config changes drive large discovery runs.
- Tenant isolation: every table and artifact includes `client_id`.
- Cost controls: batch LLM calls, prefilter aggressively, cache extraction results.
- Quality evaluation: maintain golden examples and regression tests for extraction/scoring.

### 19.14 Updated Repository Structure

```text
marketing-pipeline/
  app/
    api/
    db/
    schemas/
    control_plane/
      plugin_registry/
      source_config/
      credential_profiles/
      expert_config/
    data_plane/
      ingestion/
      seed_lead_import/
      discovery/
      artifact_processing/
      enrichment/
      verification/
      embeddings/
      knowledge_graph/
      lead_intelligence/
      export/
    plugins/
      base.py
      scrape_crawl/
      api_call/
      file_storage/
      web_search/
      contact_enrichment/
      email_verification/
      outreach/
      database_import/
      manual_upload/
    workflows/
      seed_knowledge_flow.py
      seed_lead_enrichment_flow.py
      discovery_flow.py
      artifact_processing_flow.py
      lead_intelligence_flow.py
    ai_graphs/
      document_extraction_graph.py
      discovery_planner_graph.py
      profile_match_graph.py
      lead_extraction_graph.py
    review_ui/
  tests/
    fixtures/
    golden_extractions/
    plugin_contract_tests/
```

### 19.15 Revised End-To-End Flow

```text
1. Customer docs, domain expert configuration, and optional seed lead files are uploaded.
2. Seed knowledge pipeline extracts, enriches, embeds, builds KG, and stores everything.
3. Seed lead import pipeline normalizes rows, validates required fields, and stores row-level errors.
4. Domain expert reviews and approves extracted ICP/config, enrichment guardrails, and suppression rules.
5. Enabled plugins are loaded from the plugin registry.
6. Discovery planner creates jobs only for relevant targets.
7. Seed enrichment planner creates profile/domain, provider enrichment, and verification jobs only for valid imported rows.
8. Scrape/crawl plugins collect configured URLs if enabled.
9. API plugins call configured APIs if enabled.
10. File-storage plugins load configured files if enabled.
11. Web-search plugins search and route discovered URLs/profile candidates if enabled.
12. Licensed enrichment and verification plugins run only after policy allows them.
13. Raw artifacts and provider results are stored in bronze.
14. Artifacts are cleaned, classified, filtered, and normalized into silver.
15. Entities, signals, contacts, profile candidates, verifications, and relationships are extracted into gold.
16. Embeddings and knowledge graph are updated.
17. LLM lead intelligence runs over retrieved evidence, not raw dumps.
18. Leads are scored, reviewed, exported to CRM/outreach formats, and fed back into future discovery/enrichment.
```

## 20. First Build Recommendation

Start with the database and config-driven workflow, not with the crawler.

The safest first milestone is:

```text
Upload tec5USA questionnaire
  -> extract structured ICP
  -> expert approves config
  -> configure 3-5 safe public sources
  -> crawl only those sources
  -> extract company/signal evidence
  -> enrich contacts from licensed provider or CRM
  -> score leads
  -> review dashboard
  -> weekly CRM-ready Excel
```

Add seed lead enrichment in the same MVP spine:

```text
Upload seed lead CSV/XLSX from Civcast/Dodge/CRM/event sheet
  -> normalize first name, optional last name, company, source, and project context
  -> expert-approved policy allows profile/domain search and provider use
  -> rank profile/domain candidates with evidence
  -> enrich contact through licensed provider
  -> verify email deliverability
  -> generate cited company/project research summary
  -> review dashboard
  -> outreach-ready CSV/XLSX and CRM-ready Excel
```

This gives a controlled, explainable MVP for both discovery-led account generation and imported seed lead enrichment. Once lead quality is proven, add more source connectors and automate more of the review/export loop.

## 21. Blueprint v2: Next-Gen Innovation Layer

This section defines concrete upgrades that push the pipeline beyond standard scraping-plus-scoring systems.

### 21.1 Design Goals

- Optimize for business outcomes, not data volume.
- Prioritize explainability under increasing automation.
- Keep human control where legal/compliance risk exists.
- Scale discovery and scoring with strict cost discipline.

### 21.2 New Architecture Blocks

Add these blocks to the existing control-plane and data-plane architecture:

```text
Hypothesis Engine
  Generates testable market hypotheses from ICP + prior feedback + campaign goals.

Economic Brain
  Allocates crawl/LLM/review budget by expected incremental revenue impact.

Temporal Signal Engine
  Tracks signal trajectories (velocity/acceleration/decay), not just point-in-time signals.

Adversarial Validation Layer
  "Skeptic" agent attempts to disprove candidate fit using exclusions and negative evidence.

Authenticity Guard
  Detects low-trust synthetic/spam SEO content and reduces evidence confidence.

Human Attention Orchestrator
  Prioritizes review tasks by expected downstream impact.

Revenue Learning Loop
  Learns from downstream outcomes (reply/meeting/pipeline/win), not only extraction quality.
```

### 21.3 Hypothesis-Driven Discovery (Before Crawl)

Replace broad query generation with hypothesis-driven planning:

```text
active ICP + campaign objective + prior outcomes
  -> hypothesis generation
  -> expected-value scoring
  -> source-plan and query-plan
  -> bounded collection jobs
```

Example hypothesis schema:

```json
{
  "hypothesis_id": "hyp_2026_05_13_001",
  "statement": "Chemical companies with expansion + PAT hiring in last 60 days are high-propensity buyers.",
  "target_signals": ["capacity_expansion", "pat_hiring"],
  "target_subsegments": ["petrochemicals", "specialty_chemicals"],
  "expected_value_score": 0.81,
  "max_budget_usd": 120.0,
  "expiry_days": 14
}
```

### 21.4 Economic Brain (ROI-Aware Autonomy)

Every connector and model invocation should be scored by marginal business value.

Core metric:

```text
value_per_cost = expected_signal_lift / (crawl_cost + llm_cost + review_cost)
```

Actions:

- Auto-throttle low-yield sources.
- Increase frequency for high-yield sources.
- Route low-complexity tasks to smaller local models.
- Reserve premium LLM calls for high-value/low-confidence cases.

### 21.5 Temporal Signal Intelligence

Add a time-series layer for signal behavior:

- signal velocity (change per time window)
- acceleration (second derivative)
- persistence/decay
- cross-signal sequencing (e.g., hiring -> capex -> plant launch)

Use temporal features in lead scoring so rankings favor accounts with active buying momentum.

### 21.6 Adversarial Scoring (Skeptic Agent)

For each candidate lead, run a second pass that tries to reject it:

- find exclusion evidence
- detect ambiguous/fake matches
- penalize weak or stale evidence
- challenge inferred claims without citations

Decision pattern:

```text
proposer score -> skeptic challenge -> arbitration policy -> final score
```

This reduces false positives and makes approvals more trustworthy.

### 21.7 Authenticity And Source Trust Scoring

Introduce evidence authenticity features:

- source authority rank
- recency and update cadence
- duplication entropy across sources
- synthetic-content probability
- contradiction rate with trusted sources

Use these features in `evidence_confidence` and downstream lead score.

### 21.8 Lead Digital Twin

Create continuously updated "digital twins" for accounts and contacts:

- current fit state
- signal timeline
- relationship graph
- confidence trend
- next-best-action suggestions

This enables explainable account evolution over weeks/months, not one-off snapshots.

### 21.9 Counterfactual Explainability

For each final lead, compute robustness:

- score without top signal
- score without weakest evidence
- score with stricter authenticity threshold

Store a `robustness_score` so teams can separate fragile leads from durable opportunities.

### 21.10 Privacy-First Enrichment

Use pseudonymous identifiers in mid-pipeline steps:

- keep PII masked until export-ready stage
- reveal sensitive fields only after review approval
- preserve full provenance and lawful-basis metadata

This lowers privacy risk while keeping intelligence quality high.

### 21.11 Self-Healing Extraction Contracts

When schema failures exceed threshold:

1. Trigger repair workflow.
2. Generate candidate parser/prompt patches.
3. Run against golden regression fixtures.
4. Promote patch only if quality gates pass.

This improves resilience without silent extraction drift.

### 21.12 Human Attention Orchestrator

Prioritize human review by expected system impact:

- accounts likely to influence many downstream recommendations
- connector-auth tasks blocking high-value jobs
- low-confidence decisions with large revenue upside

This turns HITL into a force multiplier instead of a bottleneck.

### 21.13 Revenue Learning Loop

Extend feedback labels:

- accepted/rejected lead
- email replied
- meeting booked
- opportunity created
- opportunity won/lost
- deal value and sales cycle length

Train scoring updates on business outcomes rather than proxy relevance alone.

### 21.14 Compliance-as-Code Simulation

Before export batch finalization, run policy simulation:

- region-specific contact rules
- suppression/consent constraints
- source terms restrictions
- role/title targeting policies

Produce:

- pass/fail result
- blocked row reasons
- auto-remediation suggestions

### 21.15 Mode-Based Strategy Controller

Add explicit run modes:

- `coverage_mode`: maximize discovery breadth.
- `precision_mode`: maximize confidence and export quality.
- `campaign_mode`: optimize for a campaign theme.
- `account_attack_mode`: deep-investigate named target accounts.

Mode controls planner thresholds, model routing, and review strictness.

### 21.16 New Tables For v2

```sql
hypotheses
  id
  client_id
  statement
  status
  expected_value_score
  max_budget_usd
  created_at
  expires_at

economic_policies
  id
  client_id
  mode
  max_run_budget_usd
  max_llm_budget_usd
  min_value_per_cost
  updated_at

signal_timeseries
  id
  client_id
  company_id
  signal_type
  observed_at
  signal_value
  source_confidence

authenticity_scores
  id
  client_id
  artifact_id
  authority_score
  recency_score
  duplication_score
  synthetic_probability
  overall_authenticity

counterfactual_scores
  id
  lead_id
  baseline_total
  without_top_signal_total
  strict_authenticity_total
  robustness_score

revenue_outcomes
  id
  client_id
  lead_id
  outcome_type
  outcome_value
  occurred_at

attention_tasks
  id
  client_id
  task_type
  priority_score
  impact_estimate
  status
  assigned_to
  created_at
```

### 21.17 Event Bus Contracts

Standardize high-value events:

```text
hypothesis.created
hypothesis.expired
budget.threshold_reached
connector.auth_required
artifact.authenticity_low
lead.counterfactual_computed
review.task_prioritized
revenue.outcome_recorded
```

Use these events to decouple orchestration and support safe autonomy.

### 21.18 Control-Plane Policies For Safe Autonomy

Add policy toggles per client:

- `allow_auto_budget_reallocation`
- `allow_auto_connector_throttling`
- `allow_cloud_fallback_for_low_confidence`
- `require_human_approval_for_captcha`
- `require_human_approval_for_export`
- `enable_outcome_based_retraining`

All automation must remain audit-logged and reversible.

### 21.19 v2 Rollout Plan (Safe To Advanced)

Phase A: ROI + Temporal Foundations (low risk)

- Add hypothesis table and planner outputs.
- Add economic brain scoring and budget caps.
- Add temporal signal features to scoring.

Phase B: Trust + Explainability

- Add authenticity scoring.
- Add counterfactual/robustness scoring.
- Add adversarial skeptic pass before review queue.

Phase C: Human Optimization

- Add attention orchestrator for review prioritization.
- Add auth-recovery task routing with SLA alerts.

Phase D: Outcome Learning

- Ingest CRM outcomes.
- Train revenue-aware scoring adjustments.
- Add policy simulation before export.

Phase E: Controlled Autonomy

- Enable mode-based strategy controller.
- Enable policy-bounded auto-throttling/reallocation.
- Keep mandatory HITL checkpoints for compliance-sensitive actions.

### 21.20 Success Metrics For v2

Track these KPIs weekly:

- `lead_precision_at_review` (accepted / reviewed)
- `signal_to_meeting_rate`
- `value_per_cost`
- `time_to_export_batch`
- `human_minutes_per_100_leads`
- `false_positive_rate_after_skeptic`
- `compliance_block_rate`
- `win_rate_by_signal_pattern`

### 21.21 v2 North Star

The pipeline should evolve from "collect and score" into a policy-safe, ROI-optimizing, hypothesis-driven intelligence system that continuously learns from market response and revenue outcomes.

## 22. Execution Backlog

This backlog converts the blueprint into buildable engineering work. Use the ticket IDs as stable references in GitHub Issues, Linear, Jira, or any sprint tracker.

Priority definitions:

- `P0`: required for the first working MVP.
- `P1`: required for a production-quality v1.
- `P2`: next-gen v2 capabilities after v1 is stable.
- `P3`: scale, optimization, and enterprise hardening.

Status definitions:

- `Ready`: clear enough to start.
- `Blocked`: depends on another ticket or external decision.
- `Spike`: research/prototype required before implementation.

### 22.1 Build Order Summary

Recommended implementation sequence:

```text
E00 Foundation
  -> E01 Database And Data Contracts
  -> E02 API And Control Plane
  -> E03 Document And Seed Lead Ingestion
  -> E04 Expert Config Review
  -> E05 Source Registry And Policy
  -> E06 Crawling, Search, And Raw Artifact Store
  -> E07 Authenticated Crawling And HITL
  -> E08 Classification, Extraction, And Enrichment
  -> E09 Resolution, Scoring, Review, Export
  -> E10 Observability, Security, QA
  -> E11 v2 Innovation Layer
```

### 22.2 Epic Dependency Map

| Epic | Name | Priority | Depends On | Outcome |
|---|---|---:|---|---|
| E00 | Foundation And Repo Setup | P0 | none | Runnable project skeleton |
| E01 | Database And Data Contracts | P0 | E00 | Core schema and migrations |
| E02 | API And Control Plane | P0 | E01 | Admin/config APIs |
| E03 | Document And Seed Lead Ingestion | P0 | E01, E02 | Client docs parsed and seed lead rows normalized |
| E04 | Expert Config Review | P0 | E03 | Human-approved ICP and enrichment guardrails |
| E05 | Source Registry And Policy | P0 | E02, E04 | Configured crawl/API/search/provider/outreach sources |
| E06 | Crawl And Raw Collection | P0 | E05 | Public crawl and permitted search/profile artifacts stored |
| E07 | Authenticated Crawl And HITL | P1 | E05, E06 | Server-safe auth recovery |
| E08 | Classification, Extraction, And Enrichment | P0 | E03, E06 | Entities, signals, profile matches, verifications, evidence |
| E09 | Resolution, Scoring, Review, Export | P0 | E08 | Weekly CRM-ready and outreach-ready output |
| E10 | Observability, Security, QA | P1 | E00-E09 | Production guardrails and enrichment quality metrics |
| E11 | v2 Innovation Layer | P2 | E09, E10 | Hypothesis/ROI/temporal/campaign intelligence |

### 22.3 Definition Of Done For MVP

The MVP is complete when:

- A client workspace can be created.
- Documents can be uploaded, parsed, chunked, embedded, and cited.
- Seed lead files can be uploaded, normalized, validated, deduped, and suppression-checked.
- Extracted ICP suggestions can be reviewed and approved by a human.
- At least 3 safe public sources can be configured and crawled.
- Search, enrichment, verification, and outreach provider policies can be configured with mock adapters.
- Raw artifacts are stored with metadata and source lineage.
- Pages are classified before expensive extraction.
- Companies, signals, contacts, profile candidates, verifications, and evidence are extracted into structured tables.
- Leads are scored with explanation and confidence.
- A human can approve/reject leads.
- Weekly CRM XLSX/CSV and seed-enrichment outreach-ready XLSX/CSV exports are generated with audit trail.

### 22.4 E00 Foundation And Repo Setup

| Ticket | Title | Priority | Depends On | Deliverable | Acceptance Criteria |
|---|---|---:|---|---|---|
| E00-T01 | Create Python project skeleton | P0 | none | `src/backend/api/`, `src/backend/tests/`, `src/backend/pyproject.toml` | App imports cleanly; test runner works |
| E00-T02 | Add configuration system | P0 | E00-T01 | Settings module with env loading | Local/dev/test configs are separated |
| E00-T03 | Add Docker Compose baseline | P0 | E00-T01 | Postgres, Redis, Ollama, object store | `docker compose -f devops/docker-compose.yml up` starts dependencies |
| E00-T04 | Add app logging conventions | P0 | E00-T01 | Structured logging helpers | Logs include `client_id`, `run_id`, `job_id` when available |
| E00-T05 | Add CI checks | P1 | E00-T01 | Lint, type, test workflow | PR fails on lint/type/test errors |

### 22.5 E01 Database And Data Contracts

| Ticket | Title | Priority | Depends On | Deliverable | Acceptance Criteria |
|---|---|---:|---|---|---|
| E01-T01 | Configure SQLAlchemy and Alembic | P0 | E00-T02 | DB session and migrations | Migration command runs locally |
| E01-T02 | Create tenant/workspace tables | P0 | E01-T01 | `clients`, `client_users`, `client_settings` | CRUD verified by tests |
| E01-T03 | Create document knowledge tables | P0 | E01-T01 | `documents`, `document_pages`, `document_chunks`, `extracted_knowledge_items` | Upload metadata and chunks can be persisted |
| E01-T04 | Create seed lead import tables | P0 | E01-T01 | `lead_import_batches`, `seed_lead_rows` | Imported rows preserve original/normalized values and validation state |
| E01-T05 | Create active ICP config tables | P0 | E01-T01 | Products, industries, titles, signals, exclusions, enrichment guardrails | Approved config can be versioned |
| E01-T06 | Create source/crawl/provider tables | P0 | E01-T01 | `source_connectors`, `url_candidates`, `crawl_jobs`, `crawl_artifacts` | Crawl/search/provider jobs and artifacts have lineage |
| E01-T07 | Create extraction/lead tables | P0 | E01-T01 | Classifications, candidates, signals, profile candidates, verifications, review, export | Lead lifecycle can be represented |
| E01-T08 | Add pgvector support | P0 | E01-T01 | Vector extension and embedding columns | Similarity query works in test |
| E01-T09 | Add schema contract tests | P1 | E01-T02, E01-T03, E01-T04, E01-T05, E01-T06, E01-T07, E01-T08 | Migration validation tests | Fresh DB migrates from empty state |

### 22.6 E02 API And Control Plane

| Ticket | Title | Priority | Depends On | Deliverable | Acceptance Criteria |
|---|---|---:|---|---|---|
| E02-T01 | Create FastAPI app shell | P0 | E00-T02, E01-T01 | App, health endpoint, DB dependency | `/health` returns OK |
| E02-T02 | Add client workspace APIs | P0 | E01-T02, E02-T01 | Client CRUD routes | Workspace can be created and listed |
| E02-T03 | Add source/provider connector APIs | P0 | E01-T06, E02-T01 | Source/provider CRUD routes | Source, search, enrichment, verification, and outreach config validates against schema |
| E02-T04 | Add active ICP config APIs | P0 | E01-T05, E02-T01 | Products, titles, signals, exclusions APIs | Config can be edited and activated |
| E02-T05 | Add run/job status APIs | P0 | E01-T06, E02-T01 | Pipeline run/job endpoints | UI can poll job state |
| E02-T06 | Add RBAC placeholders | P1 | E02-T01 | Role-based route guards | Admin/reviewer roles enforced in tests |

### 22.7 E03 Document And Seed Lead Ingestion

| Ticket | Title | Priority | Depends On | Deliverable | Acceptance Criteria |
|---|---|---:|---|---|---|
| E03-T01 | Add file upload endpoint | P0 | E02-T01, E01-T03 | Upload route and metadata persistence | PDF/DOCX/XLSX/CSV upload succeeds |
| E03-T02 | Store original files in object store | P0 | E03-T01 | Storage adapter | File can be retrieved by storage URL |
| E03-T03 | Parse PDF/DOCX/TXT | P0 | E03-T02 | Text extraction service | Extracted text is stored with page metadata |
| E03-T04 | Parse CSV/XLSX | P0 | E03-T02 | Tabular ingestion service | Rows and sheet metadata are captured |
| E03-T05 | Add seed lead import schemas | P0 | E01-T04, E03-T04 | Pydantic schemas for imported rows | First name, company, source, optional last name, title, location, note, and campaign hint validate |
| E03-T06 | Normalize and validate seed lead rows | P0 | E03-T05 | Row normalization service | Original/normalized values, row errors, dedupe, and suppression state are stored |
| E03-T07 | Chunk and embed documents | P0 | E03-T03, E03-T04, E01-T08 | Chunking and embedding worker | Chunks include metadata and embeddings |
| E03-T08 | Extract ICP suggestions with schema | P0 | E03-T07 | Pydantic extraction schemas | Outputs include evidence and confidence |
| E03-T09 | Add document and lead import workflows | P0 | E03-T01, E03-T02, E03-T03, E03-T04, E03-T06, E03-T07, E03-T08 | Prefect flows | Upload triggers parse/chunk/extract or seed row normalization pipeline |

### 22.8 E04 Expert Config Review

| Ticket | Title | Priority | Depends On | Deliverable | Acceptance Criteria |
|---|---|---:|---|---|---|
| E04-T01 | Create review queue table/API | P0 | E01-T07, E02-T01 | Review items endpoint | Suggested ICP items can enter review |
| E04-T02 | Build MVP review UI | P0 | E04-T01 | Streamlit or Next.js screen | Reviewer can approve/reject/edit suggestions |
| E04-T03 | Apply approved config | P0 | E04-T02, E01-T05 | Approval service | Approved items become active config |
| E04-T04 | Add config audit log | P1 | E04-T03 | Audit records | Every config change has actor/time/source |
| E04-T05 | Add suppression list UI/API | P1 | E02-T04 | Suppression management | Export respects suppression rules |
| E04-T06 | Add enrichment/outreach guardrails | P1 | E04-T03 | Guardrail config and review controls | Profile search, provider use, verification threshold, and outreach export require approval |

### 22.9 E05 Source Registry And Policy

| Ticket | Title | Priority | Depends On | Deliverable | Acceptance Criteria |
|---|---|---:|---|---|---|
| E05-T01 | Implement source/provider policy model | P0 | E01-T06 | Policy decision service | URLs and provider operations map to allow/block/review/API-only |
| E05-T02 | Implement connector registry | P0 | E02-T03 | Registry abstraction | Connector class resolves by config |
| E05-T03 | Add URL candidate pipeline | P0 | E05-T01 | Candidate storage and routing | Search results are stored before fetch |
| E05-T04 | Add search provider interface | P1 | E05-T03 | Search provider protocol | Mock provider emits candidates in tests |
| E05-T05 | Add policy admin controls | P1 | E02-T03, E05-T01 | UI/API for policy rules | Admin can set source-specific policies |
| E05-T06 | Add enrichment, verification, and outreach provider interfaces | P1 | E05-T02, E04-T06 | Provider protocols and mock adapters | Provider calls are blocked without approved policy and credentials |
| E05-T07 | Add seed profile search routing | P1 | E05-T03, E03-T06 | Seed row profile candidate routing | Restricted profile candidates are stored and routed through policy before use |

### 22.10 E06 Crawl And Raw Collection

| Ticket | Title | Priority | Depends On | Deliverable | Acceptance Criteria |
|---|---|---:|---|---|---|
| E06-T01 | Implement generic HTTP connector | P0 | E05-T02 | HTTP fetch service | Allowed URL fetch stores raw artifact |
| E06-T02 | Implement Scrapy crawl runner | P0 | E06-T01 | Crawl job worker | Seed URL crawl respects depth/page limits |
| E06-T03 | Add Playwright render mode | P0 | E06-T02 | JS-rendered fetch path | Dynamic page content is captured |
| E06-T04 | Add raw artifact storage | P0 | E06-T01 | HTML/JSON/PDF storage adapter | Artifact has hash, status, storage URL |
| E06-T05 | Add robots/rate-limit enforcement | P0 | E05-T01, E06-T02 | Crawl guards | Tests verify blocked and throttled URLs |
| E06-T06 | Add recrawl/content hash dedupe | P1 | E06-T04 | Dedupe service | Unchanged content is not reprocessed |
| E06-T07 | Add dead-letter handling | P1 | E06-T02 | Failed job preservation | Failed jobs keep error and retry metadata |
| E06-T08 | Add search/profile artifact capture | P1 | E05-T07, E06-T04 | Search result/profile evidence storage | Seed row profile evidence links to policy decision and source artifact |

### 22.11 E07 Authenticated Crawl And HITL

| Ticket | Title | Priority | Depends On | Deliverable | Acceptance Criteria |
|---|---|---:|---|---|---|
| E07-T01 | Create credential profile schema | P1 | E01-T06 | Credential refs and auth strategy fields | Secrets are referenced, not stored in config |
| E07-T02 | Add encrypted secret adapter | P1 | E07-T01 | Local/dev secret storage interface | Secrets are redacted from logs |
| E07-T03 | Implement Playwright storage-state login | P1 | E07-T02, E06-T03 | Authenticated browser session manager | Session state can be saved and reused |
| E07-T04 | Add session validation job | P1 | E07-T03 | Auth healthcheck worker | Expired sessions are detected before crawl |
| E07-T05 | Implement HITL auth queue states | P1 | E04-T01, E07-T04 | `needs_human_auth` workflow | Job pauses and resumes after re-auth |
| E07-T06 | Build manual re-auth UI flow | P1 | E07-T05 | Secure re-auth screen/session handoff | Operator can refresh session without exposing secrets |
| E07-T07 | Add CAPTCHA/MFA policy guard | P1 | E07-T05 | Policy enforcement | CAPTCHA-heavy source routes to HITL by default |
| E07-T08 | Add optional solver interface | P2 | E07-T07 | Disabled-by-default adapter | Solver can only run for approved source policy |
| E07-T09 | Add authenticated operation scopes | P1 | E07-T01, E05-T01 | Credential operation scope model | Credentials approved for crawl cannot be reused for enrichment/outreach unless explicitly allowed |

### 22.12 E08 Classification, Extraction, And Knowledge Graph

| Ticket | Title | Priority | Depends On | Deliverable | Acceptance Criteria |
|---|---|---:|---|---|---|
| E08-T01 | Implement page classifier rules | P0 | E06-T04 | Rule-based page classifier | Common page types are classified |
| E08-T02 | Add LLM fallback classifier | P0 | E08-T01, E03-T08 | Ollama/provider adapter classifier | Ambiguous pages produce typed labels |
| E08-T03 | Implement entity extraction schemas | P0 | E08-T02 | Company/contact/signal schemas | Extraction requires evidence URL/text |
| E08-T04 | Build extraction workflow | P0 | E08-T03 | Artifact-to-entities flow | Raw artifact produces normalized candidates |
| E08-T05 | Add knowledge graph tables/services | P1 | E01-T07, E08-T04 | `kg_nodes`, `kg_edges` services | Entities link to evidence artifacts |
| E08-T06 | Add retrieval service | P0 | E03-T07, E08-T04 | Seed/evidence retrieval | Lead context pulls relevant chunks/evidence |
| E08-T07 | Add extraction golden tests | P1 | E08-T03 | Fixture-based regression tests | Schema quality is tested on sample artifacts |
| E08-T08 | Add seed company/domain resolver | P0 | E03-T06, E08-T04 | Seed row to company/domain resolver | Imported rows resolve to canonical company/domain candidates with confidence |
| E08-T09 | Add profile candidate ranker | P0 | E06-T08, E08-T08 | Profile/domain ranking service | Candidate ranking uses company, title, location, and source evidence |
| E08-T10 | Add contact enrichment adapter workflow | P1 | E05-T06, E08-T09 | Mock provider enrichment workflow | Provider results produce typed contact/email candidates with provenance |
| E08-T11 | Add email verification workflow | P1 | E05-T06, E08-T10 | Mock verification workflow | Verification status gates outreach eligibility |
| E08-T12 | Add cited research summary generation | P1 | E08-T06, E08-T08 | Summary service | Summary uses stored evidence and never uncited claims |

### 22.13 E09 Resolution, Scoring, Review, Export

| Ticket | Title | Priority | Depends On | Deliverable | Acceptance Criteria |
|---|---|---:|---|---|---|
| E09-T01 | Implement company resolver | P0 | E08-T04 | Domain/name/fuzzy matching service | Duplicate company candidates merge correctly |
| E09-T02 | Implement contact candidate resolver | P0 | E08-T04, E08-T10 | Contact dedupe/title mapping | Contact roles map to target title groups and provider identities dedupe |
| E09-T03 | Implement rule-based lead scorer | P0 | E09-T01, E09-T02, E08-T06, E08-T11 | Score breakdown service | Score includes fit/signal/contact/profile/email/evidence factors |
| E09-T04 | Add LLM scoring rationale | P0 | E09-T03 | Evidence-grounded explanation | Rationale contains citations and confidence |
| E09-T05 | Build lead review UI | P0 | E09-T03, E04-T01 | Approve/reject/edit screen | Reviewer can process lead queue |
| E09-T06 | Add export batch builder | P0 | E09-T05 | XLSX/CSV export service | Approved leads export with required CRM and outreach columns |
| E09-T07 | Add export audit log | P0 | E09-T06 | Export lineage records | Every row links to lead/evidence/reviewer |
| E09-T08 | Add feedback capture | P1 | E09-T05 | Review feedback tables/API | Rejection reasons feed future scoring |
| E09-T09 | Add outreach export profile | P1 | E09-T06, E08-T11 | Outreach CSV/XLSX mapping | Only approved, verified, non-suppressed leads export to outreach format |
| E09-T10 | Add manual follow-up states | P1 | E09-T05 | Review states and filters | Missing-email, low-confidence profile, and risky-verification rows are actionable |

### 22.14 E10 Observability, Security, QA

| Ticket | Title | Priority | Depends On | Deliverable | Acceptance Criteria |
|---|---|---:|---|---|---|
| E10-T01 | Add OpenTelemetry tracing | P1 | E02-T01 | Trace instrumentation | Runs show trace IDs across API/workers |
| E10-T02 | Add Prometheus metrics | P1 | E06-T02, E08-T04, E09-T03 | Metrics endpoints/dashboards | Pages, errors, costs, leads, provider quality, verification, and bounce rates are tracked |
| E10-T03 | Add structured audit logs | P1 | E04-T04, E09-T07 | Audit logging service | Config/export/auth events are searchable |
| E10-T04 | Add LLM cost/token tracking | P1 | E08-T02, E09-T04 | Model invocation log | Provider/model/tokens/cost/confidence stored |
| E10-T05 | Add compliance export simulation | P1 | E09-T06 | Pre-export policy check | Blocked rows include reasons |
| E10-T06 | Add end-to-end MVP test | P1 | E03-T09, E04-T03, E06-T05, E08-T06, E09-T07 | Test fixture run | Sample docs -> crawl -> extract -> score -> export passes |
| E10-T07 | Add backup/retention policy | P2 | E01-T01, E06-T04 | Data lifecycle config | Retention/deletion workflow documented and tested |
| E10-T08 | Add seed enrichment E2E test | P1 | E03-T09, E04-T06, E05-T06, E08-T11, E09-T09 | Test fixture run | Seed lead import -> profile match -> enrichment -> verification -> review -> outreach export passes |

### 22.15 E11 v2 Innovation Layer

| Ticket | Title | Priority | Depends On | Deliverable | Acceptance Criteria |
|---|---|---:|---|---|---|
| E11-T01 | Add hypothesis tables and API | P2 | E09-T08 | Hypothesis CRUD and status | Planner can attach jobs to hypotheses |
| E11-T02 | Implement hypothesis generator | P2 | E11-T01, E08-T06 | Hypothesis Engine | Generates ranked hypotheses from ICP/outcomes |
| E11-T03 | Add economic policy tables | P2 | E10-T04 | Budget/cost policy service | Runs enforce configured cost caps |
| E11-T04 | Implement Economic Brain scorer | P2 | E11-T03, E09-T08 | `value_per_cost` scoring | Sources/jobs can be ranked by expected value |
| E11-T05 | Add temporal signal tables | P2 | E08-T04 | Signal time-series storage | Signal history is queryable by account |
| E11-T06 | Add temporal scoring features | P2 | E11-T05, E09-T03 | Velocity/decay scoring | Lead score changes with signal momentum |
| E11-T07 | Add authenticity scoring | P2 | E08-T04 | Source trust service | Evidence confidence includes authenticity |
| E11-T08 | Add skeptic agent pass | P2 | E09-T04, E11-T07 | Adversarial validation layer | Weak/excluded leads are down-ranked |
| E11-T09 | Add counterfactual scoring | P2 | E09-T03, E11-T08 | Robustness score | Lead stores score without top evidence/signal |
| E11-T10 | Add attention orchestrator | P2 | E04-T01, E10-T02 | Prioritized review tasks | Review queue sorts by expected impact |
| E11-T11 | Add CRM outcome ingestion | P2 | E09-T07 | Outcome import service | Reply/meeting/opportunity/win events attach to leads |
| E11-T12 | Add revenue-aware learning loop | P3 | E11-T11, E11-T04 | Scoring adjustment workflow | Scoring weights update through approved policy |
| E11-T13 | Add mode-based strategy controller | P3 | E11-T02, E11-T04, E11-T10 | Coverage/precision/campaign/account modes | Mode changes planner thresholds and review strictness |
| E11-T14 | Add outreach integration connector | P2 | E09-T09 | Outreach sandbox connector | Campaign/inbox payload sync works in sandbox |
| E11-T15 | Add engagement outcome ingestion | P2 | E11-T14 | Engagement import service | Sent, opened, replied, bounced, unsubscribed events attach to leads |
| E11-T16 | Add provider quality learning loop | P3 | E11-T15, E11-T04 | Provider/source quality workflow | Provider and verification weights update through approved policy |

### 22.16 First Four Sprint Plan

Sprint 1: Foundation and schema

- E00-T01, E00-T02, E00-T03
- E01-T01, E01-T02, E01-T03, E01-T04, E01-T05, E01-T08
- E02-T01, E02-T02

Sprint 2: Document intelligence, seed lead import, and config review

- E01-T07, E01-T09
- E03-T01, E03-T02, E03-T03, E03-T04, E03-T05, E03-T06
- E03-T07, E03-T08, E03-T09
- E04-T01, E04-T02, E04-T03, E04-T05, E04-T06

Sprint 3: Source/provider registry and public/search crawl

- E01-T06
- E02-T03, E02-T04, E02-T05
- E05-T01, E05-T02, E05-T03, E05-T04, E05-T06, E05-T07
- E06-T01, E06-T02, E06-T03, E06-T04, E06-T05, E06-T08

Sprint 4: Extraction, enrichment, scoring, review, export

- E08-T01, E08-T02, E08-T03, E08-T04, E08-T06, E08-T08, E08-T09, E08-T10, E08-T11
- E09-T01, E09-T02, E09-T03, E09-T04
- E09-T05, E09-T06, E09-T07, E09-T09, E09-T10
- E10-T06, E10-T08

### 22.17 Immediate Engineering Starting Point

Start with these tickets:

1. `E00-T01`: create project skeleton.
2. `E00-T02`: add configuration system.
3. `E01-T01`: configure SQLAlchemy and Alembic.
4. `E01-T02`: create tenant/workspace tables.
5. `E02-T01`: create FastAPI app shell.

This creates the minimum base for parallel work across ingestion, config, and crawling without forcing premature crawler implementation.

## 23. Developer Implementation Standards

This section defines how the system should be built, tested, deployed, and operated. It should be treated as the engineering contract for implementation.

### 23.1 Service Boundaries

| Service | Responsibility | Owns | Must Not Own |
|---|---|---|---|
| `api-service` | Public/internal APIs, auth checks, control-plane CRUD | FastAPI routes, request validation, DB transactions | Long-running crawl/extraction jobs |
| `scheduler-service` | Scheduled runs and workflow dispatch | Prefect deployments, cron/interval schedules | Business extraction logic |
| `worker-service` | General async jobs | Document parsing, embeddings, scoring, exports | Browser sessions |
| `crawler-worker` | Public and authenticated collection | Scrapy, Playwright, HTTP fetch, raw artifacts | Lead scoring decisions |
| `llm-worker` | LLM calls and schema validation | Provider adapter, prompt registry, structured outputs | Source fetching or exports |
| `review-ui` | Human review and operations | Config review, lead approval, auth recovery screens | Backend policy enforcement |
| `observability-stack` | Metrics, logs, traces | Prometheus, Grafana, Loki, OpenTelemetry | Product data mutation |

Default rule: each service owns one lifecycle. APIs mutate configuration, workers mutate pipeline state, crawlers collect artifacts, and review UI records human decisions.

### 23.2 API Contract Groups

Implement APIs in these route groups:

```text
/health
/clients
/documents
/knowledge
/config/icp
/sources
/source-policies
/credentials
/crawl-jobs
/artifacts
/extractions
/leads
/review
/exports
/feedback
/auth-sessions
/admin/runs
```

API requirements:

- Every mutating request includes actor identity.
- Every pipeline mutation writes audit metadata.
- Every long-running action returns a job/run ID.
- Every list endpoint supports `client_id`, status, pagination, and created/updated filters.
- Every export endpoint requires explicit reviewed/approved state.

### 23.3 Pipeline Data Contracts

Every pipeline stage must define:

- Input schema.
- Output schema.
- Idempotency key.
- Retry policy.
- Terminal failure state.
- Lineage fields: `client_id`, `run_id`, `job_id`, `source_connector_id`, `artifact_id` when applicable.

Standard job envelope:

```json
{
  "job_id": "uuid",
  "run_id": "uuid",
  "client_id": "uuid",
  "stage": "crawl_fetch",
  "idempotency_key": "source_id:url_hash:config_version",
  "input": {},
  "status": "queued",
  "attempt": 0,
  "max_attempts": 3,
  "created_at": "timestamp"
}
```

### 23.4 Local Development Workflow

Required developer commands:

```bash
docker compose -f devops/docker-compose.yml up -d
cd src/backend && alembic upgrade head
cd src/backend && pytest
cd src/backend && uvicorn api.main:app --reload
prefect server start
```

Seed data requirements:

- One sample client (`tec5USA`).
- One sample PDF/DOCX input.
- Three safe public source configs.
- One mocked authenticated source.
- Golden artifacts for extraction tests.

Local mode constraints:

- Use low crawl limits.
- Disable auto-export.
- Disable CAPTCHA solver adapters.
- Prefer Ollama/local model provider.
- Use mock CRM/contact enrichment by default.

### 23.5 Environment Strategy

| Environment | Purpose | Crawl Limits | LLM Provider | Export Behavior | Secrets |
|---|---|---:|---|---|---|
| `local` | Developer testing | Very low | Ollama/mock | Disabled | `.env.local` only |
| `dev` | Shared integration | Low | Ollama + optional fallback | Disabled | Dev secret store |
| `staging` | Production rehearsal | Medium | Same as prod | Test destinations only | Staging secret store |
| `prod` | Live client runs | Policy-driven | Ollama + approved fallback | Human-approved only | Production vault |

Production must require explicit approval for authenticated crawling, CAPTCHA solver usage, cloud LLM fallback, and CRM export.

### 23.6 Feature Flags

Required flags:

```text
enable_authenticated_crawling
enable_manual_reauth
enable_captcha_solver
enable_cloud_llm_fallback
enable_auto_export
enable_contact_enrichment
enable_revenue_learning
enable_economic_brain
enable_skeptic_agent
enable_counterfactual_scoring
enable_mode_strategy_controller
```

Feature flag rules:

- Risky features default to off.
- Flags can be scoped by environment and client.
- Flag changes are audit-logged.
- Production flag changes require admin role.

### 23.7 Testing Strategy

| Test Type | Purpose | Required For |
|---|---|---|
| Unit tests | Pure functions, validators, scoring helpers | Every module |
| API tests | Route validation and permissions | All API route groups |
| Migration tests | Fresh DB and migration sequence | Every schema change |
| Plugin contract tests | Connector compatibility | Every plugin/connector |
| Crawler fixture tests | Deterministic HTML/JS/PDF examples | Crawlers and parsers |
| Golden extraction tests | LLM/schema quality regression | Classifiers and extractors |
| Integration tests | DB + object store + worker flows | Core workflows |
| End-to-end test | Sample client to export | MVP release gate |
| Security tests | SSRF, prompt injection, secret leakage | Crawl/auth/LLM/export paths |

Minimum release gate:

```text
lint + type check + unit tests + API tests + migration test + plugin contract tests + MVP E2E test
```

### 23.8 Plugin Contract Test Suite

Every plugin must pass the same test contract:

- `validate_config` rejects invalid config.
- `healthcheck` reports readiness.
- `plan` creates deterministic jobs from fixed context.
- `collect` respects rate limits and source policy.
- `normalize` emits the common artifact schema.
- Failures include retryable/non-retryable classification.
- Secrets are never logged or included in artifacts.

### 23.9 Database Migration Policy

Migration rules:

- Migrations are forward-only by default.
- Destructive changes require a backfill plan and production approval.
- Every table includes `created_at` and `updated_at` unless intentionally immutable.
- Tenant-owned rows include `client_id`.
- Long-running backfills run as jobs, not request-time code.
- Schema versions are recorded for extracted records and plugin outputs.

### 23.10 Observability Requirements

Every job must emit:

- Structured log events for state transitions.
- Metrics for duration, success/failure, retries, and record counts.
- Trace IDs across API, worker, crawler, and LLM calls.
- Cost metadata for LLM calls and paid APIs.
- Lineage IDs linking outputs to inputs.

Core metrics:

```text
crawl_pages_fetched_total
crawl_failures_total
extraction_schema_failures_total
llm_tokens_total
llm_cost_estimated_total
lead_candidates_created_total
review_items_pending_total
exports_created_total
policy_blocks_total
auth_reauth_required_total
```

### 23.11 Security And Threat Model

Primary risks:

- SSRF from arbitrary crawl URLs.
- Secret leakage through logs, screenshots, artifacts, traces, or prompts.
- Prompt injection from scraped pages.
- PII overexposure before review/export approval.
- Unapproved contact enrichment or export.
- Authenticated crawler performing destructive actions.
- Cloud LLM fallback receiving restricted data without approval.

Required controls:

- URL allow/block policy before fetch.
- Egress allowlist for sensitive environments.
- Secret redaction in logs and traces.
- Prompt-injection guardrails for scraped content.
- Read-only crawler defaults with write-action blocklist.
- PII masking until export approval.
- Audit logs for config, auth, enrichment, export, and flag changes.
- Provider policy check before sending data to cloud models.

### 23.12 LLM Evaluation Harness

Maintain golden datasets for:

- ICP extraction.
- Page classification.
- Company extraction.
- Signal extraction.
- Contact/title mapping.
- Lead scoring rationale.
- Citation correctness.

Metrics:

- Schema validity rate.
- Citation coverage.
- Hallucination rate.
- Precision/recall against golden labels.
- Confidence calibration.
- Cost per accepted lead.

LLM changes must pass regression tests before promotion.

### 23.13 CI/CD Plan

Required CI stages:

```text
format check
lint
type check
unit tests
API tests
migration test
plugin contract tests
security scan
Docker build
MVP E2E smoke test
```

Deployment rules:

- Every deploy uses immutable image tags.
- Migrations run before app rollout.
- Workers roll after API/schema compatibility is confirmed.
- Rollback plan must be documented for each release.
- Production deploy requires passing staging smoke test.

### 23.14 Deployment Architecture

Scale these independently:

- API replicas.
- General worker replicas.
- Crawler worker replicas.
- Browser worker concurrency.
- LLM worker concurrency.
- Prefect workers.
- Review UI.

Deployment constraints:

- Browser workers need memory/CPU isolation.
- Crawler workers need per-source rate limits.
- LLM workers need provider concurrency limits.
- Export jobs must run exactly once per approved batch.
- Auth session storage must be encrypted and backed up.

### 23.15 Incident Runbooks

Runbooks required before production:

| Incident | Detection | First Action |
|---|---|---|
| Expired authenticated session | `auth_reauth_required_total` spike | Pause source and create HITL task |
| Crawl ban/rate-limit spike | HTTP 403/429 spike | Reduce source concurrency and review policy |
| Bad extraction release | Golden test or review rejection spike | Roll back prompt/model/schema version |
| High token spend | Cost threshold alert | Disable cloud fallback and inspect batch |
| Bad export | Export audit alert/user report | Freeze export destination and open remediation |
| Storage outage | Artifact write failures | Pause crawlers and retry after recovery |
| Migration failure | Deploy pipeline failure | Stop rollout and restore from pre-migration backup |
| Secret exposure suspicion | Log scanner or manual report | Rotate secret and invalidate sessions |

### 23.16 Engineering Review Checklist

Every PR should answer:

- Does this change preserve tenant isolation?
- Are secrets and PII protected?
- Is the job idempotent and retry-safe?
- Are failure states explicit?
- Are logs/metrics/traces included?
- Is lineage preserved from input to output?
- Are tests appropriate for the blast radius?
- Does this change require a feature flag?
- Does this change affect compliance or export behavior?

## 24. Product, Quality, And Governance Layer

This section defines product behavior, quality gates, governance controls, and operational standards. It turns the system from buildable software into a measurable production product.

### 24.1 Product Requirements

Primary personas:

- `Admin`: configures clients, policies, sources, credentials, exports, and feature flags.
- `Domain expert`: reviews extracted ICP, signals, exclusions, industries, and title mappings.
- `Research reviewer`: approves/rejects leads and corrects evidence or scoring issues.
- `Sales/marketing operator`: downloads exports and reviews campaign-ready lead batches.
- `Compliance/security reviewer`: inspects source policies, exports, audit logs, and PII handling.

Core workflows:

- Create client workspace.
- Upload and process client documents.
- Review and approve extracted ICP.
- Configure sources and connector policies.
- Monitor crawl and extraction runs.
- Recover authenticated sessions.
- Review lead candidates with evidence.
- Export approved lead batches.
- Capture outcome feedback.
- Audit system decisions and policy blocks.

Product success states:

- A non-engineer can configure a client without code changes.
- Every lead has evidence and score reasoning.
- Every export has human approval and audit lineage.
- Every blocked item explains why it was blocked.
- Operators can recover from auth/crawl/model failures without developer intervention.

### 24.2 Architecture Decision Records

Maintain ADRs for major decisions. Each ADR should include context, decision, alternatives, tradeoffs, and rollback plan.

Initial ADR backlog:

| ADR | Decision | Status |
|---|---|---|
| ADR-001 | Python/FastAPI as primary backend stack | Accepted |
| ADR-002 | Prefect as default workflow orchestrator | Accepted |
| ADR-003 | LangGraph for stateful AI workflows | Accepted |
| ADR-004 | PostgreSQL + pgvector before separate vector DB | Accepted |
| ADR-005 | SeaweedFS/Ceph over MinIO for new OSS object storage | Accepted |
| ADR-006 | Ollama-first model routing with cloud fallback | Accepted |
| ADR-007 | Human-in-loop default for CAPTCHA/MFA | Accepted |
| ADR-008 | Plugin-based connector architecture | Accepted |
| ADR-009 | Pydantic schemas for extraction contracts | Accepted |
| ADR-010 | Human approval required before CRM/export | Accepted |

### 24.3 Data Lifecycle Model

Standard data states:

```text
raw
parsed
classified
extracted
resolved
scored
review_pending
approved
exported
suppressed
archived
deleted
```

Lifecycle rules:

- `raw` artifacts are immutable.
- `parsed`, `classified`, and `extracted` records can be regenerated from raw artifacts.
- `resolved` records must preserve merge lineage.
- `scored` records must store score version and model/prompt version.
- `approved` records must store reviewer and timestamp.
- `exported` records must be immutable except for compliance redaction metadata.
- `deleted` must preserve minimal audit tombstone where legally allowed.

### 24.4 Quality Gates Per Stage

| Stage | Gate | Blocker |
|---|---|---|
| Document ingestion | Text extraction success and page count captured | Empty document with no parser error |
| ICP extraction | Evidence required for suggested config | Field without source citation |
| Source config | Policy decision and rate limit present | Missing source policy |
| Crawl | Robots/terms policy checked | Blocked policy or destructive URL |
| Classification | Page type and relevance score present | Unknown high-value page without review |
| Extraction | Schema-valid JSON and evidence URL/text | Invalid schema after retry |
| Resolution | Canonical company/contact identity present | Duplicate ambiguity above threshold |
| Scoring | Score breakdown and confidence present | No evidence for fit reason |
| Review | Human approve/reject action recorded | Missing reviewer identity |
| Export | Compliance simulation passed | Suppression, consent, or policy violation |

### 24.5 Prompt, Model, And Schema Governance

Registry requirements:

- `prompt_id`
- `prompt_version`
- `model_provider`
- `model_name`
- `schema_name`
- `schema_version`
- `temperature`
- `input_hash`
- `output_hash`
- `golden_eval_score`
- `approved_by`
- `approved_at`

Promotion rules:

- Prompt/model/schema changes must pass golden tests.
- Production changes require version bump.
- Failed release can roll back to previous prompt/model/schema version.
- Every LLM output stores prompt, model, schema, and parser versions.

### 24.6 UX Workflow Specifications

Required screens:

| Screen | Primary Actions | Must Show |
|---|---|---|
| Client setup | Create/edit workspace | Status, owner, retention, export settings |
| Document ingestion | Upload/reprocess docs | Parse status, extracted facts, citations |
| ICP editor | Approve/edit ICP | Products, industries, titles, exclusions, confidence |
| Source registry | Configure sources | Policy, auth type, rate limit, last run |
| Crawl monitor | Inspect runs | Jobs, failures, artifacts, policy blocks |
| Auth recovery | Complete re-auth | Source, reason, last success, secure session handoff |
| Lead review | Approve/reject/edit | Score, evidence, contacts, exclusion warnings |
| Export batch | Generate/download export | Approved rows, blocked rows, audit record |
| Feedback dashboard | Record outcomes | Acceptance, reply, meeting, opportunity, win/loss |
| Admin audit | Inspect changes | Actor, timestamp, entity, before/after |

UX requirements:

- No lead can be approved without visible evidence.
- Every blocked action should show a plain reason and next action.
- Review queues should be sortable by score, confidence, recency, and expected impact.
- Auth recovery should never reveal raw secrets to operators.

### 24.7 Error Taxonomy

Standard error codes:

```text
CONFIG_INVALID
POLICY_BLOCKED
ROBOTS_BLOCKED
TERMS_BLOCKED
AUTH_MISSING
AUTH_EXPIRED
CAPTCHA_REQUIRED
MFA_REQUIRED
RATE_LIMITED
FETCH_TIMEOUT
FETCH_HTTP_ERROR
CONTENT_UNSUPPORTED
PARSER_FAILED
SCHEMA_INVALID
LLM_TIMEOUT
LLM_PROVIDER_ERROR
LLM_LOW_CONFIDENCE
EVIDENCE_MISSING
RESOLUTION_AMBIGUOUS
EXPORT_BLOCKED
PII_POLICY_VIOLATION
SECRET_ACCESS_DENIED
STORAGE_WRITE_FAILED
```

Error requirements:

- Every error includes retryability.
- Every blocked item includes user-facing reason.
- Every internal error includes correlation ID.
- Every policy error includes policy ID/version.

### 24.8 Cost And Quota Governance

Budget scopes:

- per client
- per run
- per connector
- per LLM provider
- per workflow stage

Required controls:

- hard budget cap
- soft warning threshold
- provider concurrency limit
- token/request budget
- crawl page cap
- review queue cap
- automatic pause on budget breach

Cost actions:

- At 70% budget: warn.
- At 90% budget: throttle low-priority jobs.
- At 100% budget: pause non-critical jobs and require approval.

### 24.9 Data Retention And Deletion Workflow

Default retention proposal:

| Data Type | Retention |
|---|---:|
| Raw crawl artifacts | 180 days |
| Parsed text | 365 days |
| Evidence snapshots | 365 days |
| Lead candidates | 365 days |
| Export audit logs | 7 years or legal requirement |
| Secrets/session state | Until revoked or expired |
| Suppression records | Indefinite where legally allowed |

Deletion workflow:

1. Receive deletion request.
2. Identify client/person/company records.
3. Remove or redact PII fields.
4. Delete raw artifacts where required.
5. Preserve minimal audit tombstone where allowed.
6. Record deletion job status and actor.

### 24.10 Multi-Tenant Isolation Strategy

Required isolation:

- Every tenant-owned table includes `client_id`.
- Every query is scoped by `client_id`.
- Object storage uses tenant-specific prefixes.
- Feature flags are tenant-scoped.
- Source rate limits are tenant-scoped.
- Model/provider policy can be tenant-specific.
- Audit logs include tenant and actor.

Production hardening:

- Consider PostgreSQL row-level security.
- Separate high-risk tenants into separate storage buckets/prefixes.
- Use per-tenant encryption keys if compliance requires.
- Prevent cross-tenant retrieval in vector search with metadata filters.

### 24.11 Evaluation Benchmark Plan

Benchmark datasets:

- `doc_icp_gold`: client documents with expected ICP output.
- `page_classification_gold`: pages labeled by type and relevance.
- `entity_extraction_gold`: artifacts with expected companies/signals/contacts.
- `lead_scoring_gold`: candidates with expected score bands.
- `citation_gold`: claims mapped to supporting evidence.
- `export_gold`: approved/rejected examples with compliance outcomes.

Weekly scorecard:

- ICP extraction precision/recall.
- Page classification accuracy.
- Entity extraction F1.
- Citation validity rate.
- Schema validity rate.
- Lead acceptance rate.
- Cost per accepted lead.
- Human minutes per approved export row.

### 24.12 Release Roadmap

| Release | Theme | Exit Criteria |
|---|---|---|
| MVP | Controlled evidence-backed weekly export | One client can go docs -> sources -> leads -> reviewed XLSX |
| v1 Production | Reliable multi-client operations | Auth recovery, audit, observability, CI/CD, compliance checks |
| v2 Intelligence | Hypothesis and ROI-aware pipeline | Economic Brain, temporal signals, skeptic pass, counterfactuals |
| v3 Autonomous Optimization | Policy-bounded self-optimization | Outcome learning, auto-throttling, strategy modes, connector suggestions |

### 24.13 Build-Vs-Buy Policy

Use this decision rule:

| Need | Preferred Option |
|---|---|
| Official API exists and is permitted | Use API |
| Licensed export is available | Use import/export connector |
| Public page is permitted and low-risk | Crawl with policy controls |
| Authenticated source is authorized | Use scoped authenticated connector |
| CAPTCHA/MFA blocks automation | HITL re-auth by default |
| Contact email/phone verification | Licensed provider or first-party CRM |
| High-risk restricted source | Manual import or block |
| Commodity infrastructure | Open-source self-hosted by default |
| Specialized enrichment data | Buy if legal/commercial value justifies it |

### 24.14 Operational SLOs

Initial SLO targets:

| Capability | Target |
|---|---:|
| API availability | 99.5% monthly |
| Weekly export freshness | Export ready within 24h of scheduled run |
| Crawl job completion | 95% complete within configured run window |
| Auth recovery task response | 1 business day |
| Review queue age | 90% reviewed within 2 business days |
| LLM schema validity | 98% after retry |
| Export audit completeness | 100% |
| Critical incident acknowledgement | 1 business hour |

### 24.15 Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Source terms violation | Legal/compliance exposure | Policy engine, source approval, audit logs |
| Anti-bot blocking | Data collection interruption | Rate limits, APIs/imports, HITL fallback |
| Hallucinated evidence | Bad lead recommendations | Evidence requirement, citation validation, skeptic pass |
| Noisy extraction | Low reviewer trust | Golden tests, feedback loop, confidence thresholds |
| Bad export | CRM pollution/compliance issue | Human approval, compliance simulation, audit trail |
| Cloud fallback leakage | Data governance breach | Provider policy, feature flags, redaction |
| Cross-tenant data leak | Severe security incident | Tenant scoping, RLS, metadata filters |
| High LLM spend | Cost overrun | Budgets, throttles, local-first routing |
| Credential/session leakage | Account compromise | Vaulting, redaction, encrypted session state |
| Crawler destructive action | Source damage/account issue | Read-only defaults, blocked path/action list |

### 24.16 Governance Review Cadence

Weekly:

- Review lead quality scorecard.
- Review cost and quota usage.
- Review failed crawls/auth tasks.
- Review export blocks and compliance warnings.

Monthly:

- Review source policies.
- Review model/prompt performance.
- Review risk register.
- Review retention/deletion jobs.

Quarterly:

- Review ADRs.
- Review vendor/provider usage.
- Review security controls.
- Review roadmap and automation policy.

## 25. Appendices For Implementation And Scale

These appendices make the blueprint concrete enough for engineering, product, security, operations, and commercial planning.

### 25.1 Data Model Appendix

Use UUID primary keys, timezone-aware timestamps, and `client_id` on every tenant-owned table. All `jsonb` fields must have schema validation at the application layer.

Core tenant and user tables:

| Table | Columns | Constraints And Indexes |
|---|---|---|
| `clients` | `id uuid pk`, `name text`, `website text`, `status text`, `retention_policy_json jsonb`, `created_at timestamptz`, `updated_at timestamptz` | unique `lower(name)`, index `status` |
| `client_users` | `id uuid pk`, `client_id uuid fk`, `email text`, `role text`, `status text`, `created_at timestamptz` | unique `(client_id, lower(email))`, index `(client_id, role)` |
| `client_settings` | `id uuid pk`, `client_id uuid fk`, `key text`, `value_json jsonb`, `updated_at timestamptz` | unique `(client_id, key)` |

Document and RAG tables:

| Table | Columns | Constraints And Indexes |
|---|---|---|
| `documents` | `id uuid pk`, `client_id uuid fk`, `filename text`, `file_type text`, `storage_url text`, `source_type text`, `status text`, `content_hash text`, `uploaded_by uuid`, `created_at timestamptz` | unique `(client_id, content_hash)`, index `(client_id, status)` |
| `document_pages` | `id uuid pk`, `document_id uuid fk`, `page_number int`, `extracted_text text`, `metadata_json jsonb` | unique `(document_id, page_number)` |
| `document_chunks` | `id uuid pk`, `client_id uuid fk`, `document_id uuid fk`, `chunk_index int`, `content text`, `embedding vector`, `metadata_json jsonb`, `created_at timestamptz` | unique `(document_id, chunk_index)`, vector index on `embedding`, index `(client_id, document_id)` |
| `extracted_knowledge_items` | `id uuid pk`, `client_id uuid fk`, `document_id uuid fk`, `item_type text`, `name text`, `value_json jsonb`, `evidence_text text`, `confidence numeric`, `status text`, `created_at timestamptz` | index `(client_id, item_type, status)` |

Seed lead import tables:

| Table | Columns | Constraints And Indexes |
|---|---|---|
| `lead_import_batches` | `id uuid pk`, `client_id uuid fk`, `source_name text`, `source_type text`, `filename text`, `storage_url text`, `status text`, `row_count int`, `valid_row_count int`, `uploaded_by uuid`, `created_at timestamptz` | index `(client_id, status, created_at)` |
| `seed_lead_rows` | `id uuid pk`, `client_id uuid fk`, `lead_import_batch_id uuid fk`, `row_number int`, `first_name text`, `last_name text`, `company_name text`, `source text`, `title text`, `location text`, `project_context text`, `source_record_id text`, `campaign_hint text`, `normalized_json jsonb`, `validation_errors_json jsonb`, `dedupe_key text`, `suppression_status text`, `status text`, `created_at timestamptz` | unique `(lead_import_batch_id, row_number)`, index `(client_id, status)`, index `(client_id, dedupe_key)` |

Source and crawl tables:

| Table | Columns | Constraints And Indexes |
|---|---|---|
| `source_connectors` | `id uuid pk`, `client_id uuid fk`, `name text`, `source_type text`, `base_url text`, `connector_class text`, `auth_type text`, `config_json jsonb`, `rate_limit_json jsonb`, `compliance_status text`, `enabled bool`, `priority int`, `created_at timestamptz` | unique `(client_id, name)`, index `(client_id, enabled, priority)` |
| `source_credentials` | `id uuid pk`, `client_id uuid fk`, `source_connector_id uuid fk`, `auth_strategy text`, `secret_refs_json jsonb`, `status text`, `last_validated_at timestamptz` | index `(client_id, source_connector_id, status)` |
| `url_candidates` | `id uuid pk`, `client_id uuid fk`, `source_query_id uuid`, `url text`, `domain text`, `title text`, `snippet text`, `rank int`, `policy_decision text`, `routed_connector text`, `status text`, `discovered_at timestamptz` | unique `(client_id, url)`, index `(client_id, status, policy_decision)` |
| `crawl_jobs` | `id uuid pk`, `client_id uuid fk`, `source_connector_id uuid fk`, `job_type text`, `query text`, `seed_url text`, `status text`, `scheduled_at timestamptz`, `started_at timestamptz`, `finished_at timestamptz`, `error_code text`, `error_message text` | index `(client_id, status, scheduled_at)` |
| `crawl_artifacts` | `id uuid pk`, `client_id uuid fk`, `crawl_job_id uuid fk`, `source_connector_id uuid fk`, `url text`, `canonical_url text`, `content_hash text`, `content_type text`, `http_status int`, `storage_url text`, `fetched_at timestamptz`, `metadata_json jsonb` | unique `(client_id, canonical_url, content_hash)`, index `(client_id, source_connector_id, fetched_at)` |

Extraction, lead, and export tables:

| Table | Columns | Constraints And Indexes |
|---|---|---|
| `page_classifications` | `id uuid pk`, `client_id uuid fk`, `crawl_artifact_id uuid fk`, `page_type text`, `relevance_score numeric`, `confidence numeric`, `model_version text`, `created_at timestamptz` | unique `(crawl_artifact_id, model_version)` |
| `company_candidates` | `id uuid pk`, `client_id uuid fk`, `canonical_name text`, `website text`, `industry text`, `subsegment text`, `confidence numeric`, `source_artifact_id uuid`, `status text` | unique `(client_id, website)`, index `(client_id, canonical_name)` |
| `account_signals` | `id uuid pk`, `client_id uuid fk`, `company_candidate_id uuid fk`, `signal_type text`, `summary text`, `observed_at timestamptz`, `evidence_artifact_id uuid`, `confidence numeric` | index `(client_id, signal_type, observed_at)` |
| `contact_candidates` | `id uuid pk`, `client_id uuid fk`, `company_candidate_id uuid fk`, `name text`, `title text`, `title_group text`, `email_hash text`, `phone_hash text`, `evidence_artifact_id uuid`, `confidence numeric`, `status text` | index `(client_id, company_candidate_id, title_group)` |
| `profile_candidates` | `id uuid pk`, `client_id uuid fk`, `seed_lead_row_id uuid fk`, `company_candidate_id uuid fk`, `profile_url text`, `profile_source text`, `display_name text`, `title text`, `location text`, `ranking_score numeric`, `evidence_artifact_id uuid`, `rank_reason_json jsonb`, `status text`, `created_at timestamptz` | unique `(client_id, seed_lead_row_id, profile_url)`, index `(client_id, seed_lead_row_id, ranking_score desc)` |
| `email_enrichment_results` | `id uuid pk`, `client_id uuid fk`, `contact_candidate_id uuid fk`, `profile_candidate_id uuid fk`, `provider_name text`, `provider_record_id text`, `email_hash text`, `phone_hash text`, `confidence numeric`, `provenance_json jsonb`, `status text`, `created_at timestamptz` | index `(client_id, provider_name, status)`, index `(client_id, contact_candidate_id)` |
| `email_verifications` | `id uuid pk`, `client_id uuid fk`, `email_enrichment_result_id uuid fk`, `provider_name text`, `verification_status text`, `risk_score numeric`, `checked_at timestamptz`, `raw_status_json jsonb` | index `(client_id, verification_status, checked_at)` |
| `lead_candidates` | `id uuid pk`, `client_id uuid fk`, `origin_type text`, `seed_lead_row_id uuid`, `company_candidate_id uuid fk`, `primary_contact_id uuid`, `primary_profile_candidate_id uuid`, `score_total int`, `score_json jsonb`, `confidence numeric`, `status text`, `created_at timestamptz` | index `(client_id, status, score_total desc)`, index `(client_id, origin_type)` |
| `review_items` | `id uuid pk`, `client_id uuid fk`, `entity_type text`, `entity_id uuid`, `queue text`, `priority_score numeric`, `status text`, `assigned_to uuid`, `created_at timestamptz`, `resolved_at timestamptz` | index `(client_id, queue, status, priority_score desc)` |
| `export_batches` | `id uuid pk`, `client_id uuid fk`, `export_type text`, `status text`, `created_by uuid`, `created_at timestamptz`, `approved_at timestamptz` | index `(client_id, status, created_at)` |
| `export_batch_items` | `id uuid pk`, `export_batch_id uuid fk`, `lead_candidate_id uuid fk`, `exported_payload_json jsonb`, `status text`, `blocked_reason text` | unique `(export_batch_id, lead_candidate_id)` |

Operational tables:

| Table | Columns | Constraints And Indexes |
|---|---|---|
| `audit_logs` | `id uuid pk`, `client_id uuid`, `actor_id uuid`, `action text`, `entity_type text`, `entity_id uuid`, `before_json jsonb`, `after_json jsonb`, `created_at timestamptz` | index `(client_id, action, created_at)` |
| `llm_invocations` | `id uuid pk`, `client_id uuid`, `run_id uuid`, `provider text`, `model text`, `prompt_id text`, `prompt_version text`, `schema_version text`, `tokens_in int`, `tokens_out int`, `cost_estimated numeric`, `status text`, `created_at timestamptz` | index `(client_id, provider, model, created_at)` |
| `feature_flags` | `id uuid pk`, `client_id uuid`, `flag_key text`, `enabled bool`, `environment text`, `updated_by uuid`, `updated_at timestamptz` | unique `(client_id, environment, flag_key)` |
| `policy_decisions` | `id uuid pk`, `client_id uuid`, `policy_type text`, `policy_version text`, `input_hash text`, `decision text`, `reason text`, `created_at timestamptz` | index `(client_id, policy_type, decision, created_at)` |

### 25.2 Event-Driven Architecture Appendix

All events use this envelope:

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

Core event catalog:

| Event | Producer | Consumers | Required Payload |
|---|---|---|---|
| `document.uploaded` | API | ingestion worker | `document_id`, `storage_url`, `file_type` |
| `document.parsed` | worker | chunker, extractor | `document_id`, `page_count`, `content_hash` |
| `document.embedded` | worker | domain extractor | `document_id`, `chunk_count`, `embedding_model` |
| `icp.suggested` | llm-worker | review UI | `knowledge_item_ids`, `prompt_version`, `confidence` |
| `source.configured` | API | planner | `source_connector_id`, `policy_version` |
| `url.discovered` | search plugin | policy engine | `url_candidate_id`, `domain`, `rank` |
| `policy.decided` | policy engine | router | `entity_id`, `decision`, `reason` |
| `crawl.job.created` | planner | crawler-worker | `crawl_job_id`, `connector_class`, `seed_url` |
| `artifact.collected` | crawler-worker | classifier | `artifact_id`, `content_type`, `content_hash` |
| `artifact.classified` | classifier | extractor | `artifact_id`, `page_type`, `relevance_score` |
| `entity.extracted` | extractor | resolver | `artifact_id`, `entity_type`, `entity_id` |
| `lead.scored` | scorer | review UI | `lead_candidate_id`, `score_total`, `confidence` |
| `review.completed` | review UI | export service, feedback learner | `entity_type`, `entity_id`, `decision` |
| `export.completed` | export service | audit, feedback | `export_batch_id`, `row_count`, `destination` |
| `auth.required` | crawler-worker | review UI | `source_connector_id`, `reason`, `job_id` |

### 25.3 API Appendix

Main endpoint contracts:

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/clients` | Create client workspace |
| `GET` | `/clients/{client_id}` | Fetch client workspace |
| `POST` | `/clients/{client_id}/documents` | Upload document |
| `GET` | `/clients/{client_id}/documents/{document_id}` | Document status and extraction summary |
| `POST` | `/clients/{client_id}/config/icp/approve` | Approve extracted ICP items |
| `POST` | `/clients/{client_id}/sources` | Create source connector |
| `POST` | `/clients/{client_id}/sources/{source_id}/test` | Validate config/auth/policy |
| `POST` | `/clients/{client_id}/crawl-jobs` | Create crawl job |
| `GET` | `/clients/{client_id}/runs/{run_id}` | Run status and metrics |
| `GET` | `/clients/{client_id}/review` | Review queue |
| `POST` | `/clients/{client_id}/review/{review_item_id}/decision` | Submit review decision |
| `POST` | `/clients/{client_id}/exports` | Create export batch |
| `GET` | `/clients/{client_id}/exports/{export_batch_id}/download` | Download export |

Example source create request:

```json
{
  "name": "Company News Pages",
  "source_type": "crawl_source",
  "base_url": "https://example.com",
  "connector_class": "GenericWebConnector",
  "auth_type": "none",
  "enabled": true,
  "priority": 50,
  "config": {
    "seed_urls": ["https://example.com/news"],
    "allowed_patterns": ["/news/*"],
    "blocked_patterns": ["/logout", "/admin/*"],
    "max_depth": 2,
    "max_pages_per_run": 200
  }
}
```

Example lead review decision:

```json
{
  "decision": "approved",
  "reason_code": "high_fit_recent_signal",
  "notes": "Expansion signal and process engineering title are both well evidenced.",
  "field_overrides": {}
}
```

### 25.4 Worker And Job Contract Appendix

Queue names:

```text
documents.parse
documents.embed
documents.extract_icp
planning.discovery
crawl.public
crawl.authenticated
artifacts.classify
artifacts.extract
entities.resolve
leads.score
exports.build
auth.recovery
```

Retry classes:

| Class | Examples | Retry Policy |
|---|---|---|
| `transient` | timeout, 429, temporary provider failure | exponential backoff, max 3 |
| `policy_blocked` | robots, terms, denied source | no retry |
| `auth_required` | expired session, MFA, CAPTCHA | pause and create HITL task |
| `schema_repairable` | invalid LLM JSON | repair retry, max 2 |
| `fatal` | missing config, unsupported content | no retry until config/code change |

Standard idempotency keys:

| Job | Key |
|---|---|
| document parse | `document_id:content_hash:parser_version` |
| document embed | `document_id:chunk_hash:embedding_model` |
| crawl fetch | `source_id:canonical_url:config_version` |
| classify artifact | `artifact_id:classifier_version` |
| extract artifact | `artifact_id:schema_version:prompt_version` |
| score lead | `lead_id:scoring_version` |
| export batch | `export_batch_id:export_schema_version` |

### 25.5 UI Wireframe-Level Product Spec

Client setup screen:

- Components: client details form, export settings, retention policy, feature flags summary.
- Filters/states: active/inactive clients, missing config, pending documents.
- Empty state: prompt to create first client workspace.

Document review screen:

- Components: upload dropzone, document list, parse status, extracted knowledge table, citation preview.
- Actions: upload, reprocess, approve suggestion, reject suggestion, edit suggestion.
- Error states: parser failed, unsupported file, low extraction confidence.

Source registry screen:

- Components: source table, policy badge, auth badge, rate limit, last run, enable toggle.
- Actions: add source, test source, pause source, edit policy, view artifacts.
- Error states: policy blocked, auth expired, CAPTCHA required, rate limited.

Crawl monitor screen:

- Components: run timeline, job table, artifact count, failure summary, cost panel.
- Actions: retry failed job, pause run, resume run, open artifact.
- Filters: source, status, error code, time window.

Lead review screen:

- Components: lead list, score breakdown, evidence panel, contact panel, exclusion warnings.
- Actions: approve, reject, edit fields, request more evidence, suppress company/contact.
- Required states: loading evidence, missing evidence, compliance blocked, already exported.

Export screen:

- Components: batch builder, approved lead count, blocked row count, compliance simulation, download link.
- Actions: create batch, run simulation, approve export, download XLSX/CSV.
- Error states: suppression conflict, missing approval, policy violation.

### 25.6 Permissions Matrix

| Action | Admin | Domain Expert | Research Reviewer | Sales Operator | Compliance Reviewer |
|---|---:|---:|---:|---:|---:|
| Create client | yes | no | no | no | no |
| Upload documents | yes | yes | no | no | no |
| Approve ICP config | yes | yes | no | no | no |
| Configure sources | yes | no | no | no | review |
| Manage credentials | yes | no | no | no | review |
| Recover auth session | yes | no | no | no | review |
| Review leads | yes | yes | yes | no | review |
| Create export batch | yes | no | yes | yes | review |
| Approve export | yes | no | no | yes | required for restricted |
| Manage feature flags | yes | no | no | no | review |
| View audit logs | yes | no | no | no | yes |

### 25.7 Pricing And Cost Model

Cost components:

| Category | Driver | Control |
|---|---|---|
| Infrastructure | DB, object storage, Redis, workers | scale workers separately |
| Browser crawling | Playwright CPU/memory/time | render only when needed |
| LLM local | GPU/CPU runtime | batch and use smaller models |
| LLM cloud fallback | tokens and requests | fallback only on low-confidence/high-value items |
| Enrichment APIs | per lookup/export | dedupe before enrichment |
| Human review | reviewer minutes | attention prioritization |
| Storage | raw artifacts and evidence | retention lifecycle |

Unit economics to track:

```text
cost_per_artifact_collected
cost_per_valid_signal
cost_per_lead_candidate
cost_per_reviewed_lead
cost_per_accepted_lead
cost_per_meeting_booked
```

Planning assumptions for MVP:

- Prefer `pgvector` before dedicated vector DB.
- Prefer public/API sources before authenticated browser sources.
- Use local Ollama for high-volume extraction trials.
- Use cloud fallback only for quality gates and high-value cases.

### 25.8 Source Acquisition Strategy

Initial source priority list:

| Rank | Source Type | Why It Matters | Preferred Method |
|---:|---|---|---|
| 1 | Client documents, seed lead lists, and CRM exports | Highest signal and permission clarity | upload/import |
| 2 | Bid/platform lead exports | Seed enrichment starting point with project context | approved export/API/import |
| 3 | Company news/press pages | Expansion, launches, facilities | permitted crawl/RSS |
| 4 | Company careers pages | Hiring signals and target titles | permitted crawl |
| 5 | Search providers | Profile/domain candidate discovery | official search API/configured provider |
| 6 | RSS/news feeds | Recency and broad coverage | RSS/API |
| 7 | Trade show exhibitor pages | Account discovery | API/export/permitted crawl |
| 8 | Industry associations | Qualified account lists | API/export/permitted crawl |
| 9 | Public SEC/company filings | CapEx, M&A, facility context | official feeds |
| 10 | Government public data portals | Facility/project signals | official feeds |
| 11 | Job boards | Hiring velocity | API/licensed export preferred |
| 12 | Marketplace/directories | Vendor/account discovery | API/export preferred |
| 13 | CRM historical opportunities | Outcome learning | CRM connector |
| 14 | Email campaign engagement | Feedback loop and deliverability | marketing automation connector |
| 15 | Contact enrichment providers | Verified emails/phones | licensed API |
| 16 | Email verification providers | Deliverability and bounce prevention | licensed API |
| 17 | Patent/public research databases | R&D/technology signals | official API |
| 18 | Conference agendas/speakers | Buyer/contact signals | permitted crawl/export |
| 19 | Investor relations pages | CapEx and strategy | crawl/RSS |
| 20 | Local economic development announcements | New plant/facility signals | public feeds |
| 21 | Press release wires | Timely announcements | API/RSS |
| 22 | Forums/communities | Weak qualitative signals | official API/permitted public pages |
| 23 | Authenticated client portals | Proprietary high-value data | scoped connector + HITL |

### 25.9 Sales And Outreach Integration Strategy

CRM object mapping:

| Pipeline Entity | CRM Object |
|---|---|
| `company_candidate` | Account/company |
| `contact_candidate` | Contact/lead |
| `profile_candidate` | Contact profile or enrichment evidence |
| `account_signal` | Note/task/custom signal object |
| `lead_candidate` | Lead/opportunity candidate |
| `export_batch` | Campaign/import batch |
| `lead_import_batch` | Source campaign/list/import batch |

Required sync fields:

- source system ID
- client ID
- company domain
- seed import batch and source row ID when applicable
- contact email hash or verified email
- email verification status and checked timestamp
- title and title group
- score band
- evidence URL
- fit reason
- research/personalization note
- outreach inbox or campaign assignment when applicable
- export batch ID
- suppression status

Feedback sync:

- sent
- opened
- bounced
- replied
- unsubscribed
- meeting booked
- opportunity created
- opportunity won/lost
- disqualified reason

### 25.10 Evaluation Dataset Design

Dataset creation workflow:

1. Select representative client docs and artifacts.
2. Human-label ICP, companies, signals, contacts, and lead quality.
3. Store labels separately from model outputs.
4. Run every prompt/model/schema candidate against gold labels.
5. Promote only if metrics meet threshold.

Gold dataset requirements:

- At least 50 document chunks for ICP extraction.
- At least 200 page artifacts across page types.
- At least 100 company/signal examples.
- At least 100 seed lead rows with known profile/domain outcomes.
- At least 100 provider/verification fixture rows including invalid, risky, and unknown statuses.
- At least 100 lead scoring examples.
- Include negative/exclusion examples.
- Include stale, duplicate, noisy, and ambiguous evidence.

### 25.11 Compliance Deep Dive

Operational compliance mapping:

| Regulation/Area | Product Control |
|---|---|
| CAN-SPAM | suppression list, sender identity, unsubscribe handling, export audit |
| GDPR | lawful basis metadata, deletion workflow, PII minimization, export controls |
| CCPA/CPRA | deletion/access workflow, data category tracking, opt-out support |
| CASL | consent/source provenance, regional export checks |
| LGPD | lawful basis, deletion workflow, data minimization |
| Source terms | source policy approval, API/import preference, audit records |
| PII handling | masking, RBAC, export approval, retention policy |

Required pre-export compliance checks:

- suppression match
- region-specific rule check
- source permission check
- PII reveal approval
- evidence availability
- export destination approval

### 25.12 Threat Model Appendix (STRIDE)

| Threat | Example | Control |
|---|---|---|
| Spoofing | Fake reviewer identity | SSO/RBAC/session validation |
| Tampering | Modified score/export payload | audit logs, immutable export rows |
| Repudiation | User denies approving export | actor/time/IP audit trail |
| Information disclosure | PII in logs or prompts | redaction, provider policy, masking |
| Denial of service | Crawl storm or model queue overload | rate limits, quotas, backpressure |
| Elevation of privilege | Reviewer changes credentials | role checks and approval workflow |
| SSRF | Crawler fetches internal IP | URL policy, DNS/IP blocking, egress rules |
| Prompt injection | Scraped page instructs model to ignore rules | prompt isolation, content labeling, schema validation |
| Malicious file | PDF exploit or zip bomb | sandbox parsing, file size/type limits |
| Cross-tenant leakage | Vector retrieval returns wrong tenant data | `client_id` filters, RLS, contract tests |

### 25.13 Scalability Model

Initial capacity assumptions:

| Dimension | MVP Target | v1 Target |
|---|---:|---:|
| Clients | 1-5 | 25-50 |
| Documents/day | 20 | 500 |
| Pages crawled/day | 5,000 | 250,000 |
| Artifacts classified/day | 5,000 | 250,000 |
| LLM extraction calls/day | 1,000 | 50,000 |
| Leads reviewed/week | 100 | 5,000 |
| Export rows/week | 50-500 | 5,000-25,000 |

Expected bottlenecks:

- Browser rendering CPU/memory.
- LLM throughput and schema repair retries.
- Vector retrieval latency at high chunk count.
- Human review queue growth.
- Object storage write/read throughput.

Scaling levers:

- Prefer HTTP fetch over browser rendering.
- Batch classification/extraction where possible.
- Cache extraction by content hash.
- Partition workers by client/source priority.
- Add Qdrant when pgvector query latency becomes limiting.
- Use attention orchestrator to reduce review minutes per lead.

### 25.14 Rollout And Migration Plan

Rollout phases:

| Phase | Environment | Goal |
|---|---|---|
| 0 | local | Developer can run sample pipeline |
| 1 | dev | Team integration with sample data |
| 2 | staging | Full rehearsal with test exports |
| 3 | pilot prod | One client, limited sources, manual export approval |
| 4 | expanded prod | More clients, authenticated sources, observability SLOs |
| 5 | v2 prod | ROI-aware and outcome-learning features behind flags |

First client onboarding checklist:

- Confirm source permissions.
- Upload client docs and CRM exclusions.
- Approve ICP config.
- Configure 3-5 safe public sources.
- Run dry crawl.
- Review first 25 leads manually.
- Generate test export.
- Confirm CRM import mapping.
- Enable weekly run schedule.

Migration rules:

- Schema changes deploy to staging first.
- Backfills run with dry-run mode before production.
- Export schemas are versioned.
- Prompt/model changes can roll back independently from app deploys.
- Feature flags gate v2 autonomy features.

### 25.15 Investor And Product Narrative

Positioning:

```text
An evidence-first AI lead intelligence system that turns client knowledge,
public signals, approved private data, and human feedback into explainable,
CRM-ready opportunities.
```

Defensibility:

- Evidence graph links every recommendation to sources.
- Source policy engine creates compliance-aware collection.
- Feedback loop learns from reviewer and revenue outcomes.
- Hypothesis engine focuses discovery on likely buying windows.
- Economic Brain optimizes spend by expected business value.
- Human Attention Orchestrator reduces review burden.
- Prompt/schema/model governance makes AI behavior auditable.
- Plugin architecture allows rapid source expansion without rewriting pipeline.

Why this beats a generic scraper:

- It does not collect blindly.
- It reasons from client ICP and approved configuration.
- It preserves raw evidence and lineage.
- It separates source discovery from source permission.
- It uses humans where judgment/compliance matter most.
- It learns from downstream commercial outcomes.

### 25.16 Implementation Readiness Checklist

Before engineering starts:

- Backlog section 22 is imported into the issue tracker.
- Section 23 standards are accepted by engineering.
- Section 24 governance policies are accepted by product/security.
- Initial ADRs are created.
- Local stack boots on one developer machine.
- First client sample data is available.
- MVP success metrics are agreed.
- First four sprint plan is assigned.
