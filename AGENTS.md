# Agent Instructions

These instructions apply to every AI agent working in this repository.

## Mandatory Startup

Before making any code change:

1. Read [docs/development-rules.md](docs/development-rules.md).
2. Read [docs/blueprint/README.md](docs/blueprint/README.md).
3. Check the current phase in [docs/blueprint/00-roadmap.md](docs/blueprint/00-roadmap.md).
4. Inspect available skills in `.agents/skills`.
5. Use every skill that is relevant to the current task.

If a skill is explicitly named by the user, use it. If a relevant skill exists but is not usable, state why before proceeding.

## Development Rules

The rules in [docs/development-rules.md](docs/development-rules.md) are mandatory. In particular:

- Always use well-defined models/DTOs/contracts.
- Never use frontend TypeScript `any`.
- Keep models and contracts in dedicated `models` or `contracts` directories.
- Write acceptance criteria at the top of code files before implementation.
- Write tests for all acceptance criteria and important edge cases.
- Keep API exposure in `src/backend/api`.
- Keep job orchestration in `src/backend/jobs`.
- Keep business logic in `src/backend/core`.
- Ensure `core` remains importable/buildable without `api` or `jobs`.
- Follow SOLID principles.
- Keep code modular and avoid repetition.
- Keep code files below 900 lines; split earlier when responsibilities are mixed.
- Maintain 90-100% coverage for newly written code.

## Architecture Boundaries

Dependency direction:

```text
api  -> core
jobs -> core
core -> contracts/models/services only
```

Forbidden:

- `core` importing from `api`.
- `core` importing from `jobs`.
- Business logic inside API route files.
- Long-lived DTOs or contracts embedded inside implementation files.
- Untyped payloads crossing module boundaries.

## Required Verification

Before marking work complete, run:

```bash
make -f devops/Makefile test
make -f devops/Makefile lint
```

For infrastructure changes, also run:

```bash
docker compose -f devops/docker-compose.yml config
```

## Repository Layout

```text
docs/
devops/
src/
  backend/
    api/
    core/
      contracts/
      models/
      services/
    jobs/
    tests/
  frontend/
    web/
```

## Completion Standard

A task is not done until:

- Acceptance criteria are documented in code.
- Contracts/models live in the proper directory.
- Tests cover the criteria and edge cases.
- Coverage target is satisfied.
- Required verification commands pass.
- Phase progress/status is updated when the task changes phase completion.
