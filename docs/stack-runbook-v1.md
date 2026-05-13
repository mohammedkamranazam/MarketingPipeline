# Stack Runbook v1

## Start

```bash
cd /Users/abuazka/VSCodeProjects/MarketingPipeline
docker compose -f devops/docker-compose.yml up -d
```

## Verify

```bash
docker compose -f devops/docker-compose.yml ps
```

Expected endpoints:
- Prefect UI: http://localhost:4200
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Ollama API: http://localhost:11434
- Qdrant API: http://localhost:6333
- SeaweedFS master: http://localhost:9333
- SeaweedFS filer: http://localhost:8888
- SeaweedFS S3 endpoint: http://localhost:8333

## Pull local models (Ollama)

```bash
docker exec -it mp_ollama ollama pull qwen2.5:7b
docker exec -it mp_ollama ollama pull qwen2.5-coder:14b
```

## Stop

```bash
docker compose -f devops/docker-compose.yml down
```

## Reset data volumes (destructive)

```bash
docker compose -f devops/docker-compose.yml down -v
```

## Security notes

- Replace default database password before shared/staging use.
- Keep authenticated browser storage state encrypted and out of git.
- Route CAPTCHA/MFA connectors to human re-auth queue by default.
