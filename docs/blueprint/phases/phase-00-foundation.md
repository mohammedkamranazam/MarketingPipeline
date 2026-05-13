# Phase 00: Project Foundation

| Field | Value |
|---|---|
| Status | Done |
| Progress | 100% |
| Depends On | none |
| Release | Developer Alpha base |

## Goal

Create a runnable application shell that proves the repo can install, run, lint, and test locally.

## Usable Outcome

Developers can run the FastAPI service and verify `/health`.

## Deliverables

- Python project metadata.
- Environment settings.
- FastAPI app factory.
- Health endpoint.
- Developer commands.
- First API test.
- Repository structure under `src/backend`, `src/frontend/web`, `docs`, and `devops`.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P00-T01 Create `src/backend/pyproject.toml` | Done | 100% | `make -f devops/Makefile install` |
| P00-T02 Add `src/backend/.env.example` | Done | 100% | Settings load defaults |
| P00-T03 Add `devops/Makefile` commands | Done | 100% | `make -f devops/Makefile test`, `make -f devops/Makefile lint` |
| P00-T04 Create FastAPI app shell | Done | 100% | App imports successfully |
| P00-T05 Add `/health` route | Done | 100% | `GET /health` returns status |
| P00-T06 Add first API test | Done | 100% | `make -f devops/Makefile test` |
| P00-T07 Add lint config | Done | 100% | `make -f devops/Makefile lint` |

## Exit Criteria

- `make -f devops/Makefile test` passes.
- `make -f devops/Makefile lint` passes.
- `GET /health` returns `status=ok`.
- README explains local startup.

## Handoff To Phase 01

Phase 01 can now add database dependencies, migrations, and persistent client workspace APIs.
