"""Pydantic schemas for request/response."""

from aiops_tools.schemas.llm import (
    LLMTool,
    LLMToolFunction,
    LLMToolListResponse,
    LLMToolParameter,
    ToolInvokeRequest,
    ToolInvokeResponse,
    transform_to_llm_format,
)
from aiops_tools.schemas.tool import (
    CategoryDeleteRequest,
    CategoryGetRequest,
    CategoryUpdateRequest,
    ExecutionCancelRequest,
    ToolCategoryCreate,
    ToolCategoryResponse,
    ToolCategoryUpdate,
    ToolCreate,
    ToolDeleteRequest,
    ToolExecutionRequest,
    ToolExecutionResponse,
    ToolGetRequest,
    ToolListRequest,
    ToolListResponse,
    ToolResponse,
    ToolUpdate,
    ToolUpdateRequest,
)

__all__ = [
    # Tool schemas
    "ToolCategoryCreate",
    "ToolCategoryResponse",
    "ToolCategoryUpdate",
    "ToolCreate",
    "ToolExecutionRequest",
    "ToolExecutionResponse",
    "ToolListResponse",
    "ToolResponse",
    "ToolUpdate",
    # Request schemas for POST-only API
    "ToolListRequest",
    "ToolGetRequest",
    "ToolDeleteRequest",
    "ToolUpdateRequest",
    "CategoryGetRequest",
    "CategoryDeleteRequest",
    "CategoryUpdateRequest",
    "ExecutionCancelRequest",
    # LLM schemas
    "LLMTool",
    "LLMToolFunction",
    "LLMToolListResponse",
    "LLMToolParameter",
    "ToolInvokeRequest",
    "ToolInvokeResponse",
    "transform_to_llm_format",
]
