# Phase 01: Data Foundation And Workspace API

| Field | Value |
|---|---|
| Status | Ready |
| Progress | 0% |
| Depends On | Phase 00 |
| Release | Developer Alpha |

## Goal

Add the database foundation and a persistent client workspace API.

## Usable Outcome

A developer can create, list, fetch, and update client workspaces through the API, backed by PostgreSQL migrations.

## Deliverables

- SQLAlchemy session setup.
- Alembic migration framework.
- Core tenant tables.
- Client workspace API.
- Migration and API tests.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P01-T01 Add DB dependencies | Ready | 0% | `uv sync` succeeds |
| P01-T02 Configure SQLAlchemy engine/session | Ready | 0% | Session opens in test |
| P01-T03 Configure Alembic | Ready | 0% | `alembic upgrade head` works |
| P01-T04 Create `clients` table | Ready | 0% | migration test |
| P01-T05 Create `client_users` table | Ready | 0% | migration test |
| P01-T06 Create `client_settings` table | Ready | 0% | migration test |
| P01-T07 Add Pydantic client schemas | Ready | 0% | schema unit tests |
| P01-T08 Add `/clients` create/list/get/update APIs | Ready | 0% | API tests |
| P01-T09 Add seed sample client command | Ready | 0% | seed creates tec5USA client |
| P01-T10 Add migration contract test | Ready | 0% | fresh DB migrates cleanly |

## Test Plan

- Unit test settings and DB session creation.
- Migration test against empty database.
- API tests for client CRUD.
- Verify all queries are scoped by `client_id` where applicable.

## Exit Criteria

- `alembic upgrade head` succeeds.
- `/clients` CRUD works locally.
- API tests and lint pass.
- One sample client can be seeded.

## Handoff To Phase 02

Phase 02 can attach document records and uploads to a real `client_id`.
