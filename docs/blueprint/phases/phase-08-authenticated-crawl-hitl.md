# Phase 08: Authenticated Crawl And HITL

| Field | Value |
|---|---|
| Status | Planned |
| Progress | 0% |
| Depends On | Phase 07 |
| Release | Production v1 |

## Goal

Support authorized authenticated sources with encrypted session state and human-in-loop recovery for MFA/CAPTCHA.

## Usable Outcome

An operator can configure an authenticated source, validate login, pause on auth challenge, refresh session, and resume collection.

## Deliverables

- Credential profile schema.
- Secret adapter.
- Playwright storage-state login.
- Auth session validation.
- HITL auth queue states.
- Manual re-auth UI.
- CAPTCHA/MFA guard policy.

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

## Test Plan

- Use a mocked login portal.
- Verify raw credentials never appear in logs/artifacts.
- Verify expired session pauses source and creates review task.
- Verify refreshed session resumes original job.

## Exit Criteria

- Authenticated crawling works for approved test source.
- CAPTCHA/MFA triggers HITL by default.
- Session state is encrypted and revocable.
- Tests and lint pass.

## Handoff To Phase 09

Phase 09 can harden operations for production use.
