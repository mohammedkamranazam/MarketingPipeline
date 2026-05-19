from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from core.db.base import Base
from core.models import client as _client_models  # noqa: F401 — registers models
from core.models import crawl as _crawl_models  # noqa: F401 — registers models
from core.models import document as _document_models  # noqa: F401 — registers models
from core.models import extraction as _extraction_models  # noqa: F401 — registers models
from core.models import pipeline as _pipeline_models  # noqa: F401 — registers models
from core.models import review as _review_models  # noqa: F401 — registers models
from core.models import run as _run_models  # noqa: F401 — registers models
from core.models import seed_lead as _seed_lead_models  # noqa: F401 — registers models
from core.models import source as _source_models  # noqa: F401 — registers models
from core.settings import get_settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    url = config.get_main_option("sqlalchemy.url")
    if url and not url.startswith("driver://"):
        return url
    return get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(
        url=_get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = _get_url()
    connectable = engine_from_config(cfg, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
