# Modular Blueprint

This folder is the execution version of `Blueprint_v1.md`.

Use it this way:

1. Start with [00-roadmap.md](00-roadmap.md).
2. Work phases in numeric order.
3. Do not begin a later phase until the current phase exit criteria pass.
4. Update progress/status in both the phase file and the roadmap when work changes.

The original [Blueprint_v1.md](Blueprint_v1.md) remains the full reference artifact. These files are intentionally smaller, phase-oriented, and build-ready.

## File Map

| File | Purpose |
|---|---|
| [00-roadmap.md](00-roadmap.md) | Master phase order, status, progress, and releases |
| [01-system-architecture.md](01-system-architecture.md) | Stable architecture reference |
| [02-development-standards.md](02-development-standards.md) | Engineering rules, testing, CI/CD, security |
| [03-product-governance.md](03-product-governance.md) | Product workflows, governance, SLOs, risks |
| [04-data-api-events.md](04-data-api-events.md) | Data, API, event, and worker contracts |
| [phases/](phases/) | Executable phase plans |

## Status Values

| Status | Meaning |
|---|---|
| `Done` | Implemented, tested, and usable |
| `In Progress` | Currently being built |
| `Ready` | Clear enough to begin |
| `Blocked` | Waiting on dependency or decision |
| `Planned` | Not ready to start yet |

## Progress Rules

- A task is `0%` until implementation starts.
- A task is `50%` when implementation exists but verification is incomplete.
- A task is `100%` only when tests and acceptance criteria pass.
- A phase is complete only when every exit criterion passes.

## Execution Principle

Every phase must end with a usable product increment. Some phases depend on earlier outputs, but no phase should require future work to be testable or valuable.
