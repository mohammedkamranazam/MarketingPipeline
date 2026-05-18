# Product And Governance Reference

## Personas

| Persona | Primary Work |
|---|---|
| Admin | Client setup, pipeline setup, sources, feature flags, credentials |
| Domain expert | ICP, signals, exclusions, title mappings |
| Research reviewer | Lead approval, evidence correction |
| Sales operator | Export batches, campaign handoff, and outreach outcome review |
| Compliance reviewer | Source policies, PII, audit review |

## Core Screens

| Screen | Must Support |
|---|---|
| Client setup | workspace, retention, export settings |
| Pipeline setup | independent pipeline objective, lane, target, data needs, schedule, budget, config version, and credential health |
| Document ingestion | upload, status, extracted facts, citations |
| Seed lead import | CSV/XLSX upload, row validation, source mapping, duplicate/suppression status |
| ICP editor | approve/edit/reject suggested config |
| Source registry | policy, auth, rate limit, last run |
| Provider registry | search, enrichment, verification, and outreach connector policy/credentials |
| Crawl monitor | runs, artifacts, failures, cost |
| Enrichment monitor | profile/domain match rate, verified email rate, provider errors, manual follow-up |
| Auth recovery | secure re-auth for blocked sources |
| Lead review | evidence, score, contacts, approve/reject |
| Export batch | compliance simulation, CRM XLSX/CSV download, outreach-ready payload download |
| Feedback dashboard | replies, meetings, opportunities, win/loss |
| Admin audit | actor, timestamp, before/after |

## Quality Gates

| Stage | Required Gate |
|---|---|
| Ingestion | text extracted or explicit parser error |
| Seed lead import | required fields normalized, row errors visible, duplicates and suppression checked |
| ICP extraction | every suggestion has evidence |
| Source/provider config | pipeline-specific policy, rate limit, credentials, and allowed operation mode exist |
| Crawl | robots/terms/source policy checked |
| Classification | page type and relevance score exist |
| Extraction | schema-valid output with evidence |
| Profile/domain matching | candidate URL/domain has search/provider evidence and confidence |
| Contact enrichment | verified provider or first-party provenance exists before email/phone use |
| Email verification | deliverability result stored before outreach eligibility |
| Scoring | score breakdown and confidence exist |
| Review | reviewer identity and decision captured |
| Export | compliance simulation, suppression check, and verification gates passed |

## Governance Cadence

Weekly:

- Review lead quality.
- Review seed lead import quality and manual follow-up backlog.
- Review costs and quota usage.
- Review pipeline-level config, credential expiry, and run isolation health.
- Review provider match, email verification, and bounce metrics.
- Review failed crawls and auth tasks.
- Review export blocks.

Monthly:

- Review source policies.
- Review prompt/model performance.
- Review retention/deletion jobs.
- Review risk register.

Quarterly:

- Review ADRs.
- Review vendors/providers.
- Review roadmap and automation policy.

## Operational SLOs

| Capability | Initial Target |
|---|---:|
| API availability | 99.5% monthly |
| Export freshness | ready within 24h of scheduled run |
| Crawl completion | 95% within configured window |
| Review queue age | 90% within 2 business days |
| LLM schema validity | 98% after retry |
| Export audit completeness | 100% |
| Seed lead import processing | 95% within configured 24h window |
| Verified outreach bounce rate | target below 2% after engagement data is available |
