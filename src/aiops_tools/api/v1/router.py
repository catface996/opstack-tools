"""API v1 router configuration."""

from fastapi import APIRouter

from aiops_tools.api.v1.endpoints import llm, tools

api_router = APIRouter()

api_router.include_router(tools.router, prefix="/tools")
api_router.include_router(llm.router, prefix="/llm", tags=["LLM"])
