"""
Seed script: creates the tec5USA client with two example pipelines.

Usage:
    uv run python scripts/seed_sample.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.exc import IntegrityError

from core.contracts.client import ClientCreate, PipelineCreate
from core.db.session import get_session_factory
from core.services.client_service import (
    create_client,
    create_pipeline,
    list_clients,
    list_pipelines,
)


def main() -> None:
    factory = get_session_factory()
    db = factory()
    try:
        existing = [c for c in list_clients(db) if c.slug == "tec5usa"]
        if existing:
            client = existing[0]
            print(f"Client already exists: {client.name} ({client.id})")
        else:
            client = create_client(
                db,
                ClientCreate(name="tec5USA", slug="tec5usa"),
            )
            print(f"Created client: {client.name} ({client.id})")

        existing_pipelines = {p.slug for p in list_pipelines(db, client.id)}

        for slug, name, lane, description in [
            (
                "tec5usa-discovery-2024",
                "tec5USA Discovery 2024",
                "discovery",
                "Account discovery pipeline for 2024 ICP expansion",
            ),
            (
                "tec5usa-seed-enrichment-q1",
                "tec5USA Seed Enrichment Q1",
                "seed_enrichment",
                "Seed lead enrichment from bid platform exports",
            ),
        ]:
            if slug in existing_pipelines:
                print(f"  Pipeline already exists: {name}")
                continue
            pipeline = create_pipeline(
                db,
                client.id,
                PipelineCreate(name=name, slug=slug, lane=lane, description=description),
            )
            print(f"  Created pipeline: {pipeline.name} ({pipeline.id})")

    except IntegrityError as exc:
        db.rollback()
        print(f"Seed failed with integrity error: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
