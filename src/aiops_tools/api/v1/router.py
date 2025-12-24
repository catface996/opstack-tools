"""API v1 router configuration."""

from fastapi import APIRouter

from aiops_tools.api.v1.endpoints import executions, tools

api_router = APIRouter()

api_router.include_router(tools.router, prefix="/tools", tags=["Tools"])
api_router.include_router(executions.router, prefix="/tools", tags=["Executions"])
