# Phase 01: Data Foundation And Workspace API

| Field | Value |
|---|---|
| Status | Ready |
| Progress | 0% |
| Depends On | Phase 00 |
| Release | Developer Alpha |

## Goal

Add the database foundation and a persistent client workspace API that can hold both discovery-led and seed-lead-enrichment settings.

## Usable Outcome

A developer can create, list, fetch, and update client workspaces through the API, backed by PostgreSQL migrations. An admin can perform the same workspace flow through the first React/daisyUI frontend slice.

## Deliverables

- SQLAlchemy session setup.
- Alembic migration framework.
- Core tenant tables.
- Client workspace API.
- Workspace settings for use-case modes, export preferences, and default enrichment guardrails.
- Migration and API tests.
- React, Vite, TypeScript, Tailwind CSS, and daisyUI app shell.
- Client workspace frontend pages: list, create/edit, detail, settings, and users placeholder.
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
| P01-T06 Create `client_settings` table | Ready | 0% | migration test includes discovery/enrichment/export settings keys |
| P01-T07 Add Pydantic client schemas | Ready | 0% | schema unit tests |
| P01-T08 Add `/clients` create/list/get/update APIs | Ready | 0% | API tests |
| P01-T09 Add seed sample client command | Ready | 0% | seed creates tec5USA client |
| P01-T10 Add migration contract test | Ready | 0% | fresh DB migrates cleanly |
| P01-FE01 Scaffold React/Vite/TypeScript/Tailwind/daisyUI app | Ready | 0% | frontend install, typecheck, and build run through Docker-first workflow |
| P01-FE02 Define frontend design-system baseline | Ready | 0% | typography, density, elevation, status colors, action hierarchy, focus rings, and theme tokens documented in code/docs |
| P01-FE03 Add app shell and route boundaries | Ready | 0% | shell renders sidebar, topbar, workspace region, loading, empty, error, and 403/404 states |
| P01-FE04 Add strict TypeScript and frontend quality gates | Ready | 0% | `strict`, `noUncheckedIndexedAccess`, `noImplicitReturns`, and no frontend `any` enforced |
| P01-FE05 Add typed `/clients` contracts and API service | Ready | 0% | Zod validation, typed errors, request ID propagation, retries, and stale-data rules covered by tests |
| P01-FE06 Build client workspace pages | Ready | 0% | admin can list, create, fetch, edit settings, and view users placeholder |
| P01-FE07 Add MSW fixtures and component/unit tests | Ready | 0% | success, validation failure, auth failure, and server error states tested |
| P01-FE08 Add Phase 01 Playwright smoke test | Ready | 0% | create/list/update client workspace flow passes |

## Frontend Screen Acceptance Criteria

- `/clients` shows loading, empty, populated, error, and permission-denied states.
- `/clients/new` validates required fields before submit and maps server validation errors to fields.
- `/clients/:clientId` shows workspace metadata, enabled lanes, settings summary, and last updated metadata.
- `/clients/:clientId/settings` edits use-case modes, export defaults, and enrichment guardrails with a dirty-state guard.
- `/clients/:clientId/users` is route-complete with an empty-state placeholder until user APIs are available.
- The app shell includes workspace switching, theme switching, route-level error boundaries, and accessible navigation.
- API data crosses the frontend boundary only through typed contracts in `src/frontend/web/src/contracts` and UI models in `src/frontend/web/src/models`.
- TanStack Query owns server state; React local state is used only for page-local UI controls.

## Test Plan

- Unit test settings and DB session creation.
- Migration test against empty database.
- API tests for client CRUD.
- Verify all queries are scoped by `client_id` where applicable.
- Verify client settings can represent enabled use-case lanes, export defaults, and contact enrichment defaults without schema drift.
- Unit test frontend model mappers, API service errors, form validation, and route guards.
- Component test client pages with MSW success, empty, validation failure, server error, and 403 fixtures.
- Playwright smoke test the admin workspace CRUD happy path.

## Exit Criteria

- `alembic upgrade head` succeeds.
- `/clients` CRUD works locally.
- React/daisyUI app shell works locally and exposes the Phase 01 client workspace flow.
- Frontend contracts, models, services, and tests satisfy the no-`any` rule.
- API tests and lint pass.
- One sample client can be seeded.
- Phase 01 frontend smoke test passes.

## Handoff To Phase 02

Phase 02 can attach document records, seed lead imports, and upload metadata to a real `client_id`, then surface those workflows inside the established app shell.
