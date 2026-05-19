# Marketing Pipeline

AI lead intelligence pipeline for evidence-backed account and contact discovery.

The full architecture, backlog, and governance plan live in [`docs/blueprint/Blueprint_v1.md`](docs/blueprint/Blueprint_v1.md).

For day-to-day execution, use the modular blueprint in [`docs/blueprint/`](docs/blueprint/README.md). It breaks the work into ordered phases where each phase ends with a usable and testable product increment.

Development rules for all future code live in [`docs/development-rules.md`](docs/development-rules.md).

Agent-specific instructions live in [`AGENTS.md`](AGENTS.md) and [`CLAUDE.md`](CLAUDE.md).

## Local Setup

```bash
cp src/backend/.env.example src/backend/.env
make -f devops/Makefile install
make -f devops/Makefile up
make -f devops/Makefile run
```

API health check:

```bash
curl http://localhost:8000/health
```

## Developer Commands

```bash
make -f devops/Makefile test
make -f devops/Makefile lint
make -f devops/Makefile format
```

## Running Project on DEV

```bash
./run-dev.sh --stop-docker   # also brings down Docker containers on Ctrl-C
```

## Repository Layout

```text
docs/
devops/
  docker-compose.yml
  Makefile
  prometheus/
src/
  backend/
    api/
    core/
    jobs/
    tests/
  frontend/
    web/
```

## First Build Scope

This scaffold implements the first execution tickets:

- `E00-T01`: Python project skeleton.
- `E00-T02`: configuration system.
- `E02-T01`: FastAPI app shell and health endpoint.
