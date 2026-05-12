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
                         | Excel, HubSpot, ZoomInfo     |
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
- Output: weekly Excel file for HubSpot import

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
| Company websites | News, press, careers, product pages | Scrapy, requests, Playwright, Firecrawl |
| Search APIs | Bing, Google Programmable Search, SerpAPI | Official API |
| Trade shows | Exhibitor lists, agenda pages, speaker pages | API/export if available, otherwise permitted crawl |
| Job boards | Company career pages, selected public boards | API first, crawl only when permitted |
| Upwork | Marketplace jobs | Official Upwork GraphQL API |
| LinkedIn | Company/person info | Official API, approved partner, Sales Navigator/CRM sync, or licensed export only |
| ZoomInfo | Contacts and firmographics | Licensed API/export/integration only |
| Apollo/Clearbit/etc. | Contact enrichment | Licensed enrichment API |
| News/RSS | Industry publications | RSS/API/licensed feeds |
| SEC/filings | Public company signals | Official data feeds |
| Forums | Reddit, niche forums | Official API where available, public permitted pages |

Compliance note: LinkedIn should not be crawled by browser automation or scraping outside official APIs or licensed workflows. ZoomInfo should be treated as a licensed data provider, not a website to scrape.

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
- Firecrawl for managed page-to-markdown or structured web extraction
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
- Check Salesforce/HubSpot suppression
- Check existing pipeline/customer lists
- Check competitor exclusions

Resolution signals:

- domain
- legal name
- DBA names
- address
- LinkedIn company URL if licensed
- ZoomInfo/Apollo/Clearbit IDs if licensed
- CRM account ID

### Stage 11: Contact Discovery And Enrichment

Contact discovery should happen after account relevance is established. This reduces cost and avoids collecting unnecessary personal data.

Contact sources:

- licensed providers such as ZoomInfo, Apollo, Clearbit, Cognism, People Data Labs
- HubSpot/Salesforce existing contacts
- trade show lead sheets
- company leadership/team pages when permitted
- official conference speaker/exhibitor pages when permitted
- LinkedIn only via approved API/partner/export workflow

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

For tec5USA v1, export weekly Excel files for HubSpot upload.

Future options:

- HubSpot Imports API
- HubSpot CRM object API
- Salesforce Lead/Contact/Account API
- ZoomInfo tagged list
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
- contact_linkedin_url
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
| Managed web extraction option | Firecrawl |
| Database | Postgres |
| Vector search | pgvector |
| ORM/migrations | SQLAlchemy + Alembic |
| Data validation | Pydantic |
| Object storage | S3, MinIO, or cloud object store |
| LLM | OpenAI/Azure OpenAI, Anthropic, or Gemini behind a provider adapter |
| Embeddings | OpenAI text embeddings or equivalent |
| Admin/review UI | Streamlit for MVP, Next.js for product version |
| Queue/background tasks | Prefect task runners first; Celery/Redis if needed |
| Export | XLSX/CSV first, HubSpot API later |
| Observability | LangSmith, OpenTelemetry, Sentry, structured logs |

### Why This Stack

- Python is strongest for scraping, data pipelines, LLM tooling, and ML.
- Postgres keeps relational lead data, workflow metadata, and vector search together.
- pgvector avoids adding a separate vector DB too early.
- Prefect is good for scheduled, retryable data workflows.
- LangGraph is useful for stateful AI workflows with human review and checkpoints.
- Scrapy handles broad crawling better than ad hoc scripts.
- Playwright handles JavaScript-heavy pages when needed.
- Firecrawl can reduce custom scraping work for some sources.
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
  linkedin_url
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
UpworkGraphQLConnector
ZoomInfoApiConnector
ApolloEnrichmentConnector
HubSpotConnector
SalesforceConnector
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
  destination: hubspot_import
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
- Do not scrape LinkedIn outside approved APIs or licensed workflows.
- Do not scrape ZoomInfo; use licensed API/export/integration.
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

- licensed provider integration such as ZoomInfo, Apollo, or Clearbit
- CRM dedupe against Salesforce/HubSpot
- contact verification status
- title-group matching

### Phase 5: Review And Export

Deliverables:

- review dashboard
- lead approval/rejection
- weekly Excel export
- HubSpot import mapping
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
      upwork.py
      zoominfo.py
      apollo.py
      hubspot.py
      salesforce.py
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
- Firecrawl Extract: structured web extraction from pages using a schema/prompt: https://docs.firecrawl.dev/api-reference/v2-endpoint/extract
- LangGraph: durable execution, streaming, human-in-the-loop agent orchestration: https://docs.langchain.com/langgraph
- Prefect schedules: scheduled workflow runs with cron, interval, and RRule options: https://docs.prefect.io/latest/concepts/schedules
- OpenAI Structured Outputs: schema-constrained model output: https://platform.openai.com/docs/guides/structured-outputs
- pgvector: vector similarity search for Postgres: https://github.com/pgvector/pgvector
- HubSpot Imports API: import contacts, companies, notes, and CRM records: https://developers.hubspot.com/docs/api-reference/crm-imports-v3/guide
- Upwork GraphQL API: official API for marketplace/job data where permissions allow: https://www.upwork.com/developer/documentation/graphql/api/docs/index.html
- Apollo People API: example of licensed people search/enrichment API: https://docs.apollo.io/reference/people-api-search
- LinkedIn API Terms: use official APIs and avoid non-official scraping/crawling: https://www.linkedin.com/legal/l/api-terms-of-use
- FTC CAN-SPAM compliance guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

## 18. First Build Recommendation

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
  -> weekly HubSpot-ready Excel
```

This gives a controlled, explainable MVP. Once lead quality is proven, add more source connectors and automate more of the review/export loop.
