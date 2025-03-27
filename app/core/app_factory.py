from fastapi import FastAPI

from app.api.router import api_router
from app.config.settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title="Simple Data Keeper",
        debug=settings.debug,
        docs_url="/docs" if settings.env in ["development", "diagnostic"] else None,
        openapi_url="/openapi.json" if settings.env in ["development", "diagnostic"] else None,
    )

    app.include_router(api_router)
    return app
