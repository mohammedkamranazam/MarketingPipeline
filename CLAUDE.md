# Claude Instructions

Before working in this repository, read and follow:

- [docs/development-rules.md](docs/development-rules.md)
- [docs/blueprint/README.md](docs/blueprint/README.md)
- [docs/blueprint/00-roadmap.md](docs/blueprint/00-roadmap.md)
- [AGENTS.md](AGENTS.md)

## Skill Usage

Inspect `.agents/skills` before development work. Use every skill that is relevant to the current task. If the user names a skill, use it. If a relevant skill cannot be applied, explain the reason and continue with the closest safe fallback.

## Non-Negotiable Development Rules

- Use typed models/DTOs/contracts for backend and frontend.
- Never use TypeScript `any`.
- Keep contracts and models out of implementation files.
- Put backend contracts in `src/backend/core/contracts`.
- Put backend models in `src/backend/core/models`.
- Put frontend contracts/models under `src/frontend/web/src/contracts` and `src/frontend/web/src/models`.
- API files expose HTTP only.
- Job files orchestrate jobs only.
- Business logic belongs in `src/backend/core`.
- `core` must remain buildable without `api` or `jobs`.
- Write acceptance criteria at the top of code files before implementation.
- Write tests for all acceptance criteria and edge cases before marking work done.
- Keep coverage between 90% and 100% for new code.
- Follow SOLID, modularity, simplicity, and low repetition.
- Keep files below 900 lines; split earlier when responsibilities blur.

## Required Commands

Run before completion:

```bash
make -f devops/Makefile test
make -f devops/Makefile lint
```

Run for compose/devops changes:

```bash
docker compose -f devops/docker-compose.yml config
```
