# Product And Governance Reference

## Personas

| Persona | Primary Work |
|---|---|
| Admin | Client setup, sources, feature flags, credentials |
| Domain expert | ICP, signals, exclusions, title mappings |
| Research reviewer | Lead approval, evidence correction |
| Sales operator | Export batches and CRM handoff |
| Compliance reviewer | Source policies, PII, audit review |

## Core Screens

| Screen | Must Support |
|---|---|
| Client setup | workspace, retention, export settings |
| Document ingestion | upload, status, extracted facts, citations |
| ICP editor | approve/edit/reject suggested config |
| Source registry | policy, auth, rate limit, last run |
| Crawl monitor | runs, artifacts, failures, cost |
| Auth recovery | secure re-auth for blocked sources |
| Lead review | evidence, score, contacts, approve/reject |
| Export batch | compliance simulation and XLSX/CSV download |
| Feedback dashboard | replies, meetings, opportunities, win/loss |
| Admin audit | actor, timestamp, before/after |

## Quality Gates

| Stage | Required Gate |
|---|---|
| Ingestion | text extracted or explicit parser error |
| ICP extraction | every suggestion has evidence |
| Source config | policy and rate limit exist |
| Crawl | robots/terms/source policy checked |
| Classification | page type and relevance score exist |
| Extraction | schema-valid output with evidence |
| Scoring | score breakdown and confidence exist |
| Review | reviewer identity and decision captured |
| Export | compliance simulation passed |

## Governance Cadence

Weekly:

- Review lead quality.
- Review costs and quota usage.
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
