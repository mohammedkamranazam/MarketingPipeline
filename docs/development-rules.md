# Development Rules

These rules apply to every development activity in this repository.

## Agent Startup Rule

- Every agent must read this file before making code changes.
- Every agent must read `AGENTS.md` or `CLAUDE.md` when present.
- Every agent must inspect `.agents/skills` and use every skill relevant to the current task.
- If the user explicitly names a skill, the agent must use it or state why it cannot be applied.

## Architecture Boundaries

- `src/backend/api` contains only API exposure code: routes, request/response wiring, HTTP-specific validation, status codes, and dependency injection.
- `src/backend/jobs` contains only job orchestration code: scheduling, queue/workflow coordination, retries, and job entrypoints.
- `src/backend/core` contains all business logic and functional behavior.
- If `api` and `jobs` are removed, `core` must still contain the full project logic and remain importable/buildable.

## Docker-First Development

- The entire project must be runnable from inside Docker for local development and verification.
- New services, tools, scripts, and dependencies must be designed so they run in the repository's Docker workflow, not only on host machines.
- Do not introduce development steps that require host-only runtimes or global host tooling when an equivalent Docker-based step can be used.

## Models, DTOs, And Contracts

- Always use well-defined model/DTO classes for backend and frontend.
- Never use `any` in frontend TypeScript code.
- Never use untyped dictionaries as long-lived backend contracts when a model/DTO can be defined.
- Keep all models and contracts in dedicated `models` or `contracts` directories.
- Do not define persistent models, DTOs, request/response contracts, event contracts, or worker payload contracts inside implementation files.

Backend locations:

```text
src/backend/core/models/
src/backend/core/contracts/
```

Frontend locations:

```text
src/frontend/web/src/models/
src/frontend/web/src/contracts/
```

## Acceptance Criteria First

- Before implementation, write acceptance criteria at the top of the code file as code documentation.
- Unit tests must cover every acceptance criterion.
- Unit tests must also cover important edge cases.
- Only after criteria and tests are written should implementation begin.

For Python files, use a module docstring:

```python
"""
Acceptance Criteria:
- ...
- ...
"""
```

For TypeScript files, use a file header comment:

```ts
/**
 * Acceptance Criteria:
 * - ...
 * - ...
 */
```

## Testing And Coverage

- Code coverage must be between 90% and 100% for newly written code before work is marked done.
- Tests must include success paths, validation failures, edge cases, and integration boundaries when relevant.
- If coverage cannot be measured for a change, document the reason and add the closest practical verification.

## SOLID, Modularity, And Simplicity

- Follow SOLID principles.
- Prefer explicit interfaces/contracts at boundaries.
- Use design patterns only when they simplify the code or protect a real variation point.
- Keep modules cohesive and small.
- Avoid repetition; extract shared behavior when duplication becomes meaningful.
- No code file should exceed 900 lines.
- Prefer splitting files before they exceed 500 lines when responsibilities are becoming mixed.

## Dependency Direction

- `api` may depend on `core`.
- `jobs` may depend on `core`.
- `core` must not depend on `api` or `jobs`.
- Contracts/models must be imported by implementation code, not hidden inside implementation files.

## Completion Rule

A development task is not done until:

- Acceptance criteria exist in code documentation.
- Models/contracts are defined in the proper directories.
- Unit tests cover acceptance criteria and edge cases.
- Coverage target is met for new code.
- `make -f devops/Makefile test` passes.
- `make -f devops/Makefile lint` passes.
