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
- Prometheus metrics.
- Audit logs.
- LLM invocation tracking.
- Compliance export simulation.
- CI/CD release gates.
- Incident runbooks.
- Provider quota, enrichment quality, email verification, and bounce-rate metrics.

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

## Test Plan

- Run MVP E2E with tracing enabled.
- Verify audit coverage for config/auth/export.
- Verify audit coverage for profile search, provider enrichment, email verification, and outreach export.
- Verify export simulation blocks policy violations.
- Verify dashboards expose seed import throughput, verification pass rate, manual follow-up volume, provider cost, and bounce rate.
- Verify CI gates match developer standards.

## Exit Criteria

- Production release checklist passes.
- SLO metrics are visible.
- Deliverability and enrichment quality metrics are visible.
- Critical runbooks exist.
- Tests and lint pass.

## Handoff To Phase 10

Phase 10 can add v2 intelligence features behind feature flags.
