# Development Standards

Use these standards in every phase.

The authoritative development rules are in [../development-rules.md](../development-rules.md). They apply to every backend, frontend, job, model, contract, and test change.

## Local Commands

```bash
make -f devops/Makefile install
make -f devops/Makefile run
make -f devops/Makefile test
make -f devops/Makefile lint
make -f devops/Makefile format
```

## Definition Of Done

A task is done when:

- Code is implemented.
- Tests cover the changed behavior.
- `make -f devops/Makefile test` passes.
- `make -f devops/Makefile lint` passes.
- Any schema/API/worker contract changes are documented.
- Observability and audit needs are addressed for production-facing behavior.

## Testing Layers

| Layer | Purpose |
|---|---|
| Unit tests | Pure logic and helpers |
| API tests | Route behavior and validation |
| Migration tests | Database schema boots from empty |
| Contract tests | Plugins, workers, schemas, event payloads |
| Golden tests | LLM extraction and scoring regression |
| Integration tests | DB + object store + worker flows |
| E2E tests | Sample client through export |

## CI/CD Gates

```text
format check
lint
type check
unit tests
API tests
migration test
plugin contract tests
security scan
Docker build
MVP E2E smoke test
```

## Feature Flag Rule

Risky features default off:

- authenticated crawling
- CAPTCHA solver
- cloud LLM fallback
- profile/domain search automation
- contact enrichment
- email verification provider calls
- auto-export
- direct outreach sync
- v2 autonomy features

## Security Requirements

- Never log secrets.
- Never send secrets to LLMs.
- Never ask an LLM to invent or validate emails, phone numbers, or private profile details.
- Mask PII before export approval.
- Block SSRF targets before fetch.
- Treat scraped content as untrusted prompt input.
- Default crawlers to read-only behavior.
- Require suppression, unsubscribe, and do-not-contact checks before CRM or outreach export.
- Store provider terms, source policy, verification result, and audit metadata for contact enrichment.

## Migration Policy

- Prefer forward-only migrations.
- Destructive changes require approval and backfill plan.
- Long backfills run as jobs.
- Every tenant table has `client_id`.
- Every extracted record stores schema/model/prompt version when relevant.
