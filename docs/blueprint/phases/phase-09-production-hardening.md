# Phase 09: Production Hardening

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 08 |
| Release | Production v1 |

## Goal

Make the v1 pipeline observable, secure, testable, and deployable for production clients across discovery and seed lead enrichment lanes.

## Usable Outcome

The system can run scheduled production jobs with monitoring, audit logs, CI/CD gates, incident runbooks, and enrichment/outreach quality metrics.

## Deliverables

- OpenTelemetry traces.
- Trace backend using Tempo or Jaeger.
- Prometheus metrics.
- Audit logs.
- LLM invocation tracking.
- Compliance export simulation.
- CI/CD release gates.
- Container supply-chain gates: pinned images, SBOM/provenance, image scanning, and signing or attestations.
- Prefect vs Temporal durability evaluation ADR.
- Worker capacity, dead-letter, lease, and backpressure dashboards.
- Incident runbooks.
- Provider quota, enrichment quality, email verification, and bounce-rate metrics.
- Frontend production quality gates: strict TypeScript, accessibility checks, visual regression screenshots, bundle budgets, and route smoke tests.
- Storybook or equivalent component catalog for daisyUI wrappers, domain components, states, themes, and accessibility examples.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P09-T01 Add OpenTelemetry tracing | Planned | 0% | trace ID across API/worker |
| P09-T02 Add Prometheus metrics | Planned | 0% | metrics endpoint/dashboard |
| P09-T03 Add structured audit logs | Planned | 0% | audit search test |
| P09-T04 Add LLM cost/token tracking | Planned | 0% | invocation log test |
| P09-T05 Add compliance export simulation | Planned | 0% | blocked export test |
| P09-T06 Add security tests | Planned | 0% | SSRF/secret/prompt tests |
| P09-T07 Add CI/CD workflow | Planned | 0% | PR checks pass |
| P09-T08 Add backup/retention jobs | Planned | 0% | retention dry run |
| P09-T09 Add incident runbooks | Planned | 0% | runbook links in ops docs |
| P09-T10 Add enrichment/outreach metrics | Planned | 0% | lead processed, profile match, email found, verified, blocked, bounce, and provider error metrics |
| P09-T11 Add trace backend | Planned | 0% | API, worker, crawler, provider, LLM, and export spans are queryable |
| P09-T12 Add container supply-chain gates | Planned | 0% | pinned builds produce SBOM/provenance, scan results, and signed or attested images |
| P09-T13 Add Prefect vs Temporal durability ADR | Planned | 0% | ADR covers crash recovery, HITL pauses, exports, costs, and migration path |
| P09-T14 Add worker operations dashboards | Planned | 0% | queue age, leases, heartbeats, retries, dead letters, concurrency, and budget stops visible |
| P09-FE01 Add frontend CI quality gates | Planned | 0% | typecheck, lint, unit/component tests, accessibility checks, and Playwright smoke run in CI |
| P09-FE02 Add visual regression coverage | Planned | 0% | app shell, tables, review workspace, forms, modals, drawers, light/dark themes, and mobile breakpoints captured |
| P09-FE03 Add component catalog | Planned | 0% | daisyUI wrappers, domain components, loading/empty/error states, themes, and accessibility examples documented |
| P09-FE04 Add production metrics dashboards | Planned | 0% | SLO, audit, LLM cost, provider quota, enrichment quality, and bounce-rate views tested |
| P09-FE05 Add bundle and performance budgets | Planned | 0% | large route chunks, table rendering, and interaction latency thresholds checked |

## Frontend Quality Gates

- TypeScript uses `strict`, `noUncheckedIndexedAccess`, `noImplicitReturns`, and `exactOptionalPropertyTypes` where feasible.
- Frontend code introduces no `any`; unknown payloads are validated before mapping to contracts or models.
- Component files split before responsibilities mix and should normally stay below 300 lines.
- Server state remains in TanStack Query and is not copied into local state.
- Dialogs, drawers, forms, review actions, and tables pass accessibility checks.
- Visual regression screenshots cover desktop, tablet, mobile, light theme, and dark theme.
- Component catalog examples cover loading, empty, error, permission-denied, and long-content states.

## Test Plan

- Run MVP E2E with tracing enabled.
- Verify audit coverage for config/auth/export.
- Verify audit coverage for profile search, provider enrichment, email verification, and outreach export.
- Verify export simulation blocks policy violations.
- Verify trace backend queries can follow one sample lead from API request through worker, crawler/provider, LLM, review, and export.
- Verify container images run as non-root, expose healthchecks, use pinned base images, and pass image scans.
- Verify release builds produce SBOM/provenance metadata and signed or attested images.
- Verify the Prefect vs Temporal ADR is linked from production runbooks and records the decision criteria.
- Verify worker dashboards expose queue age, retries, dead letters, stuck leases, and browser-worker concurrency.
- Verify dashboards expose seed import throughput, verification pass rate, manual follow-up volume, provider cost, and bounce rate.
- Verify CI gates match developer standards.
- Run frontend typecheck, unit/component tests, accessibility checks, visual regression checks, and Playwright route smoke tests in CI.
- Verify component catalog examples render with the custom daisyUI themes and no accessibility violations.

## Exit Criteria

- Production release checklist passes.
- SLO metrics are visible.
- Distributed traces are queryable in a trace backend, not only emitted by instrumentation.
- Container supply-chain gates pass for API, worker, crawler, LLM, outreach, and frontend images.
- The workflow orchestrator decision is documented with a clear Temporal migration trigger if Prefect remains the default.
- Deliverability and enrichment quality metrics are visible.
- Critical runbooks exist.
- Frontend quality gates, component catalog, visual regression, accessibility, and bundle budgets are part of production release checks.
- Tests and lint pass.

## Handoff To Phase 10

Phase 10 can add v2 intelligence features behind feature flags.
