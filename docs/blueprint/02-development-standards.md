# Development Standards

Use these standards in every phase.

The authoritative development rules are in [../development-rules.md](../development-rules.md). They apply to every backend, frontend, job, model, contract, and test change.

## Local Commands

```bash
make -f devops/Makefile install
make -f devops/Makefile run
make -f devops/Makefile test
make -f devops/Makefile lint
make -f devops/Makefile format
```

## Definition Of Done

A task is done when:

- Code is implemented.
- Tests cover the changed behavior.
- `make -f devops/Makefile test` passes.
- `make -f devops/Makefile lint` passes.
- Any schema/API/worker contract changes are documented.
- Observability and audit needs are addressed for production-facing behavior.

## Testing Layers

| Layer | Purpose |
|---|---|
| Unit tests | Pure logic and helpers |
| API tests | Route behavior and validation |
| Migration tests | Database schema boots from empty |
| Contract tests | Plugins, workers, schemas, event payloads |
| Golden tests | LLM extraction and scoring regression |
| Integration tests | DB + object store + worker flows |
| E2E tests | Sample client through export |

## CI/CD Gates

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
container image scan
SBOM/provenance generation
image signing or attestation for release builds
Docker Compose config validation for infrastructure changes
MVP E2E smoke test
```

## Container And Supply-Chain Gates

- Application Dockerfiles use multi-stage builds with separate development, test, and production targets.
- Production images run as non-root users, use pinned base image versions, and keep build tools out of runtime layers.
- Production images must not use `latest` tags unless an ADR explicitly approves the risk for a local-only service.
- Docker build contexts must use `.dockerignore` to exclude virtual environments, caches, test artifacts, secrets, and local data volumes.
- Secrets must be injected through a secret manager or Docker/Compose secrets, not baked into images or logged from environment dumps.
- Runtime services expose healthchecks, resource limits, and internal networks where possible.
- Browser, crawler, LLM, and export workers require explicit CPU, memory, timeout, and concurrency budgets.
- Release builds generate SBOM/provenance metadata, run image and dependency vulnerability scans, and produce an image signature or attestation.

## Feature Flag Rule

Risky features default off:

- authenticated crawling
- CAPTCHA solver
- cloud LLM fallback
- profile/domain search automation
- contact enrichment
- email verification provider calls
- auto-export
- direct outreach sync
- v2 autonomy features

## Orchestration And Tool Review Rule

- Prefect is the default orchestrator for scheduled workflows, ingestion flows, backfills, and batch jobs.
- Before Production v1, evaluate Temporal for workflows with long human pauses, crash-safe resume requirements, exactly-once external side effects, or customer-visible durability guarantees.
- Workflow decisions must be documented as ADRs before changing the orchestrator baseline.
- Business logic stays in `src/backend/core`; Prefect, Temporal, queue, and scheduler integration code stays in `src/backend/jobs`.
- External tools are used through typed adapters with deterministic mocks and contract tests before live provider calls are enabled.

## Observability Gates

- OpenTelemetry spans must connect API requests, job records, worker attempts, crawler operations, provider calls, LLM invocations, and export actions.
- Prometheus metrics must cover queue age, attempts, failures, dead letters, provider quotas, costs, and review backlog.
- Logs must be structured and include `client_id`, `pipeline_id`, `run_id`, `job_id`, `correlation_id`, and `trace_id` when available.
- A trace backend such as Tempo or Jaeger is required before Production v1; OpenTelemetry instrumentation alone is not enough.

## Security Requirements

- Never log secrets.
- Never send secrets to LLMs.
- Never ask an LLM to invent or validate emails, phone numbers, or private profile details.
- Mask PII before export approval.
- Block SSRF targets before fetch.
- Treat scraped content as untrusted prompt input.
- Default crawlers to read-only behavior.
- Require suppression, unsubscribe, and do-not-contact checks before CRM or outreach export.
- Store provider terms, source policy, verification result, and audit metadata for contact enrichment.

## Migration Policy

- Prefer forward-only migrations.
- Destructive changes require approval and backfill plan.
- Long backfills run as jobs.
- Every tenant table has `client_id`.
- Every pipeline-owned table has both `client_id` and `pipeline_id`.
- Every extracted record stores schema/model/prompt version when relevant.
