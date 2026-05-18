# Phase 08: Authenticated Crawl And HITL

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 07 |
| Release | Production v1 |

## Goal

Support authorized pipeline-scoped authenticated sources with encrypted session state and human-in-loop recovery for MFA/CAPTCHA, including restricted sources used for discovery or seed lead enrichment.

## Usable Outcome

An operator can configure an authenticated source for a selected pipeline, validate login, pause on auth challenge, refresh session, and resume collection or enrichment without exposing or reusing credentials across pipelines.

## Deliverables

- Pipeline-scoped credential profile schema.
- Secret adapter.
- Playwright storage-state login.
- Auth session validation.
- HITL auth queue states.
- Durable authenticated job checkpoint and resume behavior.
- Manual re-auth UI.
- CAPTCHA/MFA guard policy.
- Authenticated source operation scopes for crawl, search, import, enrichment, and outreach.
- Auth session and recovery UI with safe credential metadata, challenge state, scoped resume controls, and audit-ready decision history.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P08-T01 Add credential profile migration | Planned | 0% | migration test |
| P08-T02 Add encrypted secret adapter | Planned | 0% | redaction test |
| P08-T03 Implement storage-state login | Planned | 0% | authenticated fixture test |
| P08-T04 Add session validation job | Planned | 0% | expired session test |
| P08-T05 Add `needs_human_auth` state | Planned | 0% | job pause/resume test |
| P08-T06 Build manual re-auth UI | Planned | 0% | operator refresh flow |
| P08-T07 Add CAPTCHA/MFA policy guard | Planned | 0% | challenge routes to HITL |
| P08-T08 Add optional solver interface | Planned | 0% | disabled by default test |
| P08-T09 Add authenticated operation scopes | Planned | 0% | credentials can be approved for crawl/search/import/enrichment/outreach independently |
| P08-T10 Add authenticated job checkpointing | Planned | 0% | worker restart resumes or pauses without losing auth/review state |
| P08-FE01 Build auth sessions dashboard | Planned | 0% | valid, expired, challenged, revoked, paused, and resumed states visible |
| P08-FE02 Build manual re-auth UI | Planned | 0% | challenge instructions, secure handoff, retry, cancel, and resume controls tested |
| P08-FE03 Add auth recovery permission gates | Planned | 0% | only approved roles can refresh, revoke, or broaden credential operation scopes |
| P08-FE04 Add Phase 08 Playwright smoke test | Planned | 0% | refresh auth session and resume paused job |

## Frontend Screen Acceptance Criteria

- Auth session screens never display raw credentials, tokens, cookies, or storage-state values.
- CAPTCHA/MFA states are clearly separated from general provider errors and route to human action by default.
- Resume controls show the original job, source, operation scope, and policy decision before continuing.
- Credential scope changes use the Phase 03 permission matrix and require confirmation when access broadens.
- Audit context is visible for refresh, revoke, resume, and failed auth attempts.

## Test Plan

- Use a mocked login portal.
- Verify raw credentials never appear in logs/artifacts.
- Verify expired session pauses source and creates review task.
- Verify refreshed session resumes original job.
- Verify a credential approved for one operation scope cannot be reused for another scope.
- Verify a credential or authenticated session approved for one pipeline cannot be reused by another pipeline.
- Verify a worker restart preserves authenticated job state, storage-state metadata, policy decision, and HITL recovery task.
- Verify browser jobs run under isolated timeout, CPU, memory, and concurrency budgets.
- Component test auth states, secret redaction, permission gates, resume confirmation, and audit context.
- Playwright smoke test manual re-auth recovery with mocked portal state.

## Exit Criteria

- Authenticated crawling works for approved test source.
- Authenticated crawling uses only credentials and sessions owned by the selected pipeline.
- CAPTCHA/MFA triggers HITL by default.
- Session state is encrypted and revocable.
- Authenticated browser jobs can be paused, resumed, cancelled, retried, or dead-lettered through the shared job state model.
- Restricted profile or bid-platform workflows run only when explicitly authorized by source policy.
- Auth recovery UI lets approved operators safely refresh sessions and resume paused jobs without exposing secrets.
- Tests and lint pass.

## Handoff To Phase 09

Phase 09 can harden operations for production use.
