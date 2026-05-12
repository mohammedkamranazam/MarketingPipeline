# AI Lead Intelligence Pipeline Blueprint v1

Date: 2026-05-12

## 1. Purpose

This blueprint defines an end-to-end architecture for an AI/ML-based lead intelligence pipeline. The pipeline should replace a manual marketing research workflow where people read client documents, understand products and target markets, search the web, inspect forums and marketplaces, find relevant accounts and contacts, and prepare outbound-ready lead lists.

The key design goal is not "scrape everything." The goal is to build a configurable, evidence-based system that can answer:

- Which companies match the client ICP?
- Why do they match?
- What recent signal makes them relevant now?
- Which people at that company should be contacted?
- What source proves each recommendation?
- How confident is the system?
- What should be exported to CRM or a weekly lead file?

## 2. Core Architecture Summary

The pipeline has four major planes:

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
                         +------------------------------+       +------+------+
                         | Crawl + Collection Layer     | ----> | Raw Store   |
                         | source connectors            |       | HTML/PDF/API |
                         +---------------+--------------+       +------+------+
                                         |                             |
                                         v                             v
                         +---------------+--------------+       +------+------+
                         | Extraction + Normalization   | <---- | Evidence    |
                         | accounts, signals, contacts  |       | snapshots   |
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
                         | Excel, CRM, enrichment exports     |
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

## 5. Main Pipeline Stages

### Stage 1: Client Workspace Setup

Create a workspace per client.

Responsibilities:

- Create client record
- Configure tenant isolation
- Store CRM/export preferences
- Store compliance and source permissions
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
- S3/MinIO for original files
- pgvector for embeddings
- LLM structured output for extraction

Outputs:

- document records
- document chunks
- extracted domain facts
- suggested ICP config
- source citations

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
- Define export fields
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
- enrichment jobs
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
- S3/MinIO for large HTML/PDF/JSON/screenshot artifacts

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
- enrichment provider IDs if available
- CRM account ID

### Stage 11: Contact Discovery And Enrichment

Contact discovery should happen after account relevance is established. This reduces cost and avoids collecting unnecessary personal data.

Contact sources:

- licensed contact enrichment providers
- CRM existing contacts
- event or campaign lead sheets
- company leadership/team pages when permitted
- official speaker/exhibitor pages when permitted
- approved source exports

The LLM can extract contact candidates from permitted page text, but verified email and phone should come from licensed enrichment or first-party CRM/trade show data.

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
| Contact quality | title relevance, seniority, verified email, verified phone |
| Evidence confidence | source authority, recency, source count, extraction confidence |

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
- score breakdown
- why this lead was recommended
- export readiness

### Stage 14: Export

For tec5USA v1, export weekly Excel files for CRM upload.

Future options:

- CRM import API
- CRM object API
- CRM lead/contact/account API
- enrichment-provider tagged list
- CSV/Excel
- webhook to marketing automation

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

### Stage 15: Feedback Loop

Feedback makes the pipeline improve over time.

Capture:

- approved/rejected leads
- sales comments
- reply/no reply
- meeting booked
- SQL conversion
- opportunity creation
- closed won/lost
- bad contact reports
- wrong industry reports

Feedback should update:

- scoring weights
- title mappings
- negative keywords
- source priority
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

scheduler-service
  Prefect deployment schedules and recurring workflows

review-ui
  Streamlit for MVP or Next.js for production

storage
  Postgres + pgvector + S3/MinIO

observability
  logs, traces, prompt runs, job metrics, audit logs
```

### 6.2 AI Subsystems

```text
document_extractor
  Extracts ICP, products, titles, signals, competitors, exclusions from docs

retrieval_service
  Retrieves relevant domain chunks for extraction/scoring prompts

page_classifier
  Classifies crawled pages by type and relevance

entity_extractor
  Extracts company, contact, signal, facility, process, and evidence objects

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
| Object storage | S3, MinIO, or cloud object store |
| LLM | OpenAI/Azure OpenAI, Anthropic, or Gemini behind a provider adapter |
| Embeddings | OpenAI text embeddings or equivalent |
| Admin/review UI | Streamlit for MVP, Next.js for product version |
| Queue/background tasks | Prefect task runners first; Celery/Redis if needed |
| Export | XLSX/CSV first, CRM API later |
| Observability | LangSmith, OpenTelemetry, Sentry, structured logs |

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
- score fit with evidence
- generate search query variants

Avoid:

- asking the LLM to browse without source constraints
- asking it to guess emails or phone numbers
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

- `clients`, `documents`, `source_connectors`, `company_candidates`, `account_signals`, `contact_candidates`, `lead_candidates` tables
- FastAPI skeleton
- Postgres + pgvector setup
- Object storage setup
- Basic admin config model

### Phase 1: Document Intelligence

Deliverables:

- PDF/DOCX/XLSX ingestion
- Text extraction
- Chunking + embeddings
- LLM-based ICP extraction
- Human approval screen for extracted config

### Phase 2: Source Registry And First Crawlers

Start with safe, high-value sources:

- company websites
- press/news pages
- RSS/news feeds
- trade show public pages where permitted
- job/careers pages where permitted

Deliverables:

- source connector interface
- source config UI
- crawl job scheduler
- raw artifact store

### Phase 3: Extraction And Scoring

Deliverables:

- page classifier
- signal extractor
- company extractor
- title/contact candidate extractor
- company resolver
- first scoring model
- evidence-backed research notes

### Phase 4: Contact Enrichment

Deliverables:

- licensed contact enrichment integration
- CRM dedupe
- contact verification status
- title-group matching

### Phase 5: Review And Export

Deliverables:

- review dashboard
- lead approval/rejection
- weekly Excel export
- CRM import mapping
- export audit log

### Phase 6: Feedback Learning

Deliverables:

- feedback capture
- scoring weight adjustment
- source quality scoring
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
  docker-compose.yml
  pyproject.toml
  README.md
```

## 17. Key APIs And Tool References

- Scrapy: high-level crawling and scraping framework for extracting structured data from websites: https://docs.scrapy.org/
- Playwright: browser automation for JavaScript-heavy pages: https://playwright.dev/
- Managed extraction service: optional structured web extraction from pages using a schema or prompt
- LangGraph: durable execution, streaming, human-in-the-loop agent orchestration: https://docs.langchain.com/langgraph
- Prefect schedules: scheduled workflow runs with cron, interval, and RRule options: https://docs.prefect.io/latest/concepts/schedules
- OpenAI Structured Outputs: schema-constrained model output: https://platform.openai.com/docs/guides/structured-outputs
- pgvector: vector similarity search for Postgres: https://github.com/pgvector/pgvector
- CRM import API: import contacts, companies, notes, and CRM records through the chosen CRM.
- Marketplace API: use official marketplace or job-board APIs where permissions allow
- Contact enrichment API: use the chosen licensed enrichment provider API
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
      "confidence": 0.0
    }
  ],
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
      discovery/
      artifact_processing/
      enrichment/
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
      database_import/
      manual_upload/
    workflows/
      seed_knowledge_flow.py
      discovery_flow.py
      artifact_processing_flow.py
      lead_intelligence_flow.py
    ai_graphs/
      document_extraction_graph.py
      discovery_planner_graph.py
      lead_extraction_graph.py
    review_ui/
  tests/
    fixtures/
    golden_extractions/
    plugin_contract_tests/
```

### 19.15 Revised End-To-End Flow

```text
1. Customer docs and domain expert configuration are uploaded.
2. Seed knowledge pipeline extracts, enriches, embeds, builds KG, and stores everything.
3. Domain expert reviews and approves extracted ICP/config.
4. Enabled plugins are loaded from the plugin registry.
5. Discovery planner creates jobs only for relevant targets.
6. Scrape/crawl plugins collect configured URLs if enabled.
7. API plugins call configured APIs if enabled.
8. File-storage plugins load configured files if enabled.
9. Web-search plugins search and route discovered URLs if enabled.
10. Raw artifacts are stored in bronze.
11. Artifacts are cleaned, classified, filtered, and normalized into silver.
12. Entities, signals, contacts, and relationships are extracted into gold.
13. Embeddings and knowledge graph are updated.
14. LLM lead intelligence runs over retrieved evidence, not raw dumps.
15. Leads are scored, reviewed, exported, and fed back into future discovery.
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

This gives a controlled, explainable MVP. Once lead quality is proven, add more source connectors and automate more of the review/export loop.
