from fastapi import APIRouter

from .routes import files, ping

api_router = APIRouter()
api_router.include_router(ping.router, tags=["Health"])
api_router.include_router(files.router, tags=["Files"])
