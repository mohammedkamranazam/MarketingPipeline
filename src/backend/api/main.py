from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.clients import router as clients_router
from api.routes.crawl import router as crawl_router
from api.routes.documents import router as documents_router
from api.routes.extraction import router as extraction_router
from api.routes.health import router as health_router
from api.routes.lead_imports import router as lead_imports_router
from api.routes.review import router as review_router
from api.routes.source import router as source_router
from core.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url="/redoc" if settings.enable_docs else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(clients_router)
    app.include_router(documents_router)
    app.include_router(lead_imports_router)
    app.include_router(review_router)
    app.include_router(source_router)
    app.include_router(crawl_router)
    app.include_router(extraction_router)
    return app


app = create_app()
