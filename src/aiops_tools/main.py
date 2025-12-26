"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

from aiops_tools.api.v1.router import api_router
from aiops_tools.core.config import settings
from aiops_tools.core.database import init_db
from aiops_tools.core.redis import close_redis, get_redis


# OpenAPI tags metadata for better documentation organization
tags_metadata = [
    {
        "name": "Categories",
        "description": "Tool category management - Organize tools into categories",
    },
    {
        "name": "Tools",
        "description": "Tool CRUD and execution - Create, manage, and invoke tools",
    },
    {
        "name": "LLM",
        "description": "LLM-compatible API - OpenAI function calling format for tool discovery",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    await init_db()
    await get_redis()
    yield
    # Shutdown
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=None,  # Disable default docs, we'll add custom routes
    redoc_url=None,  # Disable default redoc
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    contact={
        "name": "AIOps Tools Team",
    },
    license_info={
        "name": "MIT",
    },
)


# Custom Swagger UI at root /docs for convenience
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Swagger UI documentation."""
    return get_swagger_ui_html(
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        title=f"{settings.app_name} - Swagger UI",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


# Also available at /api/v1/docs
@app.get(f"{settings.api_v1_prefix}/docs", include_in_schema=False)
async def api_swagger_ui_html():
    """Swagger UI documentation (API prefix)."""
    return get_swagger_ui_html(
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        title=f"{settings.app_name} - Swagger UI",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


# ReDoc at /redoc
@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    """ReDoc documentation."""
    return get_redoc_html(
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        title=f"{settings.app_name} - ReDoc",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


# Also available at /api/v1/redoc
@app.get(f"{settings.api_v1_prefix}/redoc", include_in_schema=False)
async def api_redoc_html():
    """ReDoc documentation (API prefix)."""
    return get_redoc_html(
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        title=f"{settings.app_name} - ReDoc",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": f"{settings.api_v1_prefix}/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "aiops_tools.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
