# Phase 10: v2 Intelligence Layer

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 09 |
| Release | Intelligence v2 |

## Goal

Add next-generation intelligence: hypotheses, ROI-aware planning, temporal signals, authenticity, skeptic pass, counterfactuals, and attention prioritization.

## Usable Outcome

The system can prioritize discovery and review by expected business value while improving lead trust.

## Deliverables

- Hypothesis engine.
- Economic policy and budget scoring.
- Signal time series.
- Authenticity scoring.
- Skeptic agent pass.
- Counterfactual scoring.
- Human attention orchestrator.

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

## Test Plan

- Compare lead ranking before/after v2 features.
- Verify all v2 features are behind flags.
- Verify budget caps pause low-value work.
- Verify skeptic pass does not block without evidence.

## Exit Criteria

- v2 intelligence can run in staging behind flags.
- Lead review queue can sort by expected impact.
- Cost-aware planning is auditable.
- Tests and lint pass.

## Handoff To Phase 11

Phase 11 can integrate CRM outcomes and scale enterprise operations.
