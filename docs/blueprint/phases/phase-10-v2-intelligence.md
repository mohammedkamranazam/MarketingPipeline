# Phase 10: v2 Intelligence Layer

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 09 |
| Release | Intelligence v2 |

## Goal

Add pipeline-specific next-generation intelligence: hypotheses, ROI-aware planning, temporal signals, authenticity, skeptic pass, counterfactuals, attention prioritization, and campaign-aware enrichment strategy.

## Usable Outcome

The system can prioritize discovery, seed lead enrichment, and review by expected business value while improving lead trust and deliverability inside each pipeline.

## Deliverables

- Hypothesis engine.
- Economic policy and budget scoring.
- Signal time series.
- Authenticity scoring.
- Skeptic agent pass.
- Counterfactual scoring.
- Human attention orchestrator.
- Value-per-verified-lead and campaign-mode prioritization.
- Feature-flagged intelligence UI for hypotheses, temporal signals, attention prioritization, strategy mode, and cost/value explanation.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P10-T01 Add hypothesis tables/API | Planned | 0% | hypothesis CRUD tests |
| P10-T02 Implement hypothesis generator | Planned | 0% | ranked hypothesis fixture |
| P10-T03 Add economic policy tables | Planned | 0% | budget policy tests |
| P10-T04 Implement value-per-cost scorer | Planned | 0% | source/job ranking tests |
| P10-T05 Add signal timeseries | Planned | 0% | signal history query test |
| P10-T06 Add temporal scoring features | Planned | 0% | score changes with momentum |
| P10-T07 Add authenticity scoring | Planned | 0% | low-trust evidence downranked |
| P10-T08 Add skeptic pass | Planned | 0% | exclusion evidence reduces score |
| P10-T09 Add counterfactual scoring | Planned | 0% | robustness score stored |
| P10-T10 Add attention orchestrator | Planned | 0% | review queue priority test |
| P10-T11 Add enrichment value scoring | Planned | 0% | profile search and provider work ranked by expected verified lead value |
| P10-T12 Add campaign-aware strategy mode | Planned | 0% | campaign mode changes source, title, verification, and review thresholds |
| P10-FE01 Build feature-flagged hypothesis and signal views | Planned | 0% | disabled, enabled, loading, empty, and error states tested |
| P10-FE02 Build attention queue prioritization UI | Planned | 0% | expected value, urgency, confidence, and blocker explanations visible |
| P10-FE03 Build strategy mode selector | Planned | 0% | campaign mode changes are previewed, audited, and guarded by role |
| P10-FE04 Add Phase 10 Playwright smoke test | Planned | 0% | sort attention queue by intelligence score behind feature flag |

## Frontend Screen Acceptance Criteria

- v2 intelligence routes are hidden or read-only unless feature flags and permissions allow access.
- Attention queues explain score drivers, expected value, confidence, and why items outrank other work.
- Strategy changes show projected effects on sources, titles, verification thresholds, review workload, and cost before save.
- Intelligence widgets degrade to auditable explanations, not opaque numbers.
- Feature flag changes do not break existing Phase 07 review and export workflows.

## Test Plan

- Compare lead ranking before/after v2 features.
- Verify all v2 features are behind flags.
- Verify budget caps pause low-value work.
- Verify provider calls are prioritized by expected value per verified lead.
- Verify v2 ranking, dataset selection, and attention queues do not mix data across pipelines unless an explicit enterprise cross-pipeline analysis is enabled.
- Verify skeptic pass does not block without evidence.
- Component test feature-flag disabled/enabled states, attention sorting, score explanations, and strategy preview.
- Playwright smoke test attention queue sorting behind an enabled flag.

## Exit Criteria

- v2 intelligence can run in staging behind flags.
- Lead review queue can sort by expected impact.
- Cost-aware planning is auditable.
- Cost-aware planning is auditable by `client_id` and `pipeline_id`.
- Campaign-aware enrichment can run behind feature flags.
- Frontend intelligence views are feature-flagged, permission-aware, and explain score/strategy decisions.
- Tests and lint pass.

## Handoff To Phase 11

Phase 11 can integrate CRM/outreach outcomes and scale enterprise operations.
