# Phase 01: Data Foundation And Workspace API

| Field | Value |
|---|---|
| Status | Ready |
| Progress | 0% |
| Depends On | Phase 00 |
| Release | Developer Alpha |

## Goal

Add the database foundation and a persistent client workspace API that can hold multiple independent pipelines for discovery-led and seed-lead-enrichment work.

## Usable Outcome

A developer can create, list, fetch, and update client workspaces and independent pipelines through the API, backed by PostgreSQL migrations. An admin can perform the same client and pipeline setup flow through the first React/daisyUI frontend slice.

## Deliverables

- SQLAlchemy session setup.
- Alembic migration framework.
- Core tenant tables.
- Pipeline foundation tables.
- Client workspace API.
- Pipeline API under a client workspace.
- Workspace settings for client defaults.
- Pipeline settings for use-case modes, target, data needs, export preferences, schedules, budgets, and default enrichment guardrails.
- Immutable pipeline config version baseline.
- Migration and API tests.
- React, Vite, TypeScript, Tailwind CSS, and daisyUI app shell.
- Client workspace frontend pages: list, create/edit, detail, settings, users placeholder, pipeline list, pipeline detail, pipeline settings, and pipeline switcher.
- Typed frontend client contracts, models, services, and MSW fixtures.
- Phase 01 Playwright smoke test for workspace CRUD.

## Steps

| Step | Status | Progress | Verification |
|---|---|---:|---|
| P01-T01 Add DB dependencies | Ready | 0% | `uv sync` succeeds |
| P01-T02 Configure SQLAlchemy engine/session | Ready | 0% | Session opens in test |
| P01-T03 Configure Alembic | Ready | 0% | `alembic upgrade head` works |
| P01-T04 Create `clients` table | Ready | 0% | migration test |
| P01-T05 Create `client_users` table | Ready | 0% | migration test |
| P01-T06 Create `client_settings` table | Ready | 0% | migration test includes client default keys |
| P01-T07 Create `pipelines` table | Ready | 0% | migration test verifies unique pipeline names per client and lifecycle fields |
| P01-T08 Create `pipeline_settings` table | Ready | 0% | migration test includes lane, target, schedule, budget, export, and guardrail settings keys |
| P01-T09 Create `pipeline_config_versions` table | Ready | 0% | migration test verifies active/draft/superseded config snapshots per pipeline |
| P01-T10 Add Pydantic client and pipeline schemas | Ready | 0% | schema unit tests |
| P01-T11 Add `/clients` create/list/get/update APIs | Ready | 0% | API tests |
| P01-T12 Add `/clients/{client_id}/pipelines` create/list/get/update APIs | Ready | 0% | API tests prove two independent pipelines under one client |
| P01-T13 Add seed sample client command | Ready | 0% | seed creates tec5USA client with at least two example pipelines |
| P01-T14 Add migration and isolation contract tests | Ready | 0% | fresh DB migrates cleanly and pipeline settings do not bleed across pipelines |
| P01-FE01 Scaffold React/Vite/TypeScript/Tailwind/daisyUI app | Ready | 0% | frontend install, typecheck, and build run through Docker-first workflow |
| P01-FE02 Define frontend design-system baseline | Ready | 0% | typography, density, elevation, status colors, action hierarchy, focus rings, and theme tokens documented in code/docs |
| P01-FE03 Add app shell and route boundaries | Ready | 0% | shell renders sidebar, topbar, workspace region, loading, empty, error, and 403/404 states |
| P01-FE04 Add strict TypeScript and frontend quality gates | Ready | 0% | `strict`, `noUncheckedIndexedAccess`, `noImplicitReturns`, and no frontend `any` enforced |
| P01-FE05 Add typed `/clients` and pipeline contracts and API services | Ready | 0% | Zod validation, typed errors, request ID propagation, retries, and stale-data rules covered by tests |
| P01-FE06 Build client workspace and pipeline pages | Ready | 0% | admin can list, create, fetch, edit settings, switch pipelines, and view users placeholder |
| P01-FE07 Add MSW fixtures and component/unit tests | Ready | 0% | success, validation failure, auth failure, and server error states tested |
| P01-FE08 Add Phase 01 Playwright smoke test | Ready | 0% | create/list/update client workspace and create/list/update two pipelines flow passes |

## Frontend Screen Acceptance Criteria

- `/clients` shows loading, empty, populated, error, and permission-denied states.
- `/clients/new` validates required fields before submit and maps server validation errors to fields.
- `/clients/:clientId` shows workspace metadata, enabled lanes, settings summary, and last updated metadata.
- `/clients/:clientId/settings` edits client-level defaults with a dirty-state guard.
- `/clients/:clientId/users` is route-complete with an empty-state placeholder until user APIs are available.
- `/clients/:clientId/pipelines` shows loading, empty, populated, error, and permission-denied states.
- `/clients/:clientId/pipelines/new` creates a pipeline from blank values, client defaults, or a clone source placeholder.
- `/clients/:clientId/pipelines/:pipelineId` shows pipeline objective, enabled lane, target, data needs, status, active config version, and last run placeholder.
- `/clients/:clientId/pipelines/:pipelineId/settings` edits pipeline-specific target, schedule, budget, export, and guardrail settings with a dirty-state guard.
- The app shell includes a pipeline switcher when a client has pipelines.
- The app shell includes workspace switching, theme switching, route-level error boundaries, and accessible navigation.
- API data crosses the frontend boundary only through typed contracts in `src/frontend/web/src/contracts` and UI models in `src/frontend/web/src/models`.
- TanStack Query owns server state; React local state is used only for page-local UI controls.

## Test Plan

- Unit test settings and DB session creation.
- Migration test against empty database.
- API tests for client CRUD.
- API tests for pipeline CRUD under a client.
- Verify all queries are scoped by `client_id` where applicable.
- Verify pipeline-owned queries are scoped by both `client_id` and `pipeline_id`.
- Verify client settings can represent client defaults without schema drift.
- Verify pipeline settings can represent enabled use-case lanes, targets, schedules, budgets, export defaults, and contact enrichment defaults without schema drift.
- Verify two pipelines under one client can have different settings and config versions.
- Unit test frontend model mappers, API service errors, form validation, and route guards.
- Component test client pages with MSW success, empty, validation failure, server error, and 403 fixtures.
- Playwright smoke test the admin workspace CRUD and two-pipeline CRUD happy path.

## Exit Criteria

- `alembic upgrade head` succeeds.
- `/clients` CRUD works locally.
- `/clients/{client_id}/pipelines` CRUD works locally.
- One client can contain at least two pipelines with independent settings and config version records.
- React/daisyUI app shell works locally and exposes the Phase 01 client workspace flow.
- React/daisyUI app shell exposes the Phase 01 pipeline list/detail/settings flow and pipeline switcher.
- Frontend contracts, models, services, and tests satisfy the no-`any` rule.
- API tests and lint pass.
- One sample client can be seeded.
- Phase 01 frontend smoke test passes for client and pipeline CRUD.

## Handoff To Phase 02

Phase 02 can attach document records, seed lead imports, upload metadata, embeddings, and run history to a real `client_id` and `pipeline_id`, then surface those workflows inside the established app shell.
