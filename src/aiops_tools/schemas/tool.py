"""Tool-related Pydantic schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from aiops_tools.models.tool import ExecutionStatus, ToolStatus


# Base schemas
class ToolCategoryBase(BaseModel):
    """Base schema for tool category."""

    name: str
    description: str | None = None
    parent_id: UUID | None = None


class ToolBase(BaseModel):
    """Base schema for tool."""

    name: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z][a-z0-9_]*$")
    display_name: str = Field(..., min_length=1, max_length=200)
    description: str
    category_id: UUID | None = None
    tags: list[str] = []
    input_schema: dict[str, Any] = {}
    output_schema: dict[str, Any] = {}
    script_content: str | None = None
    executor_type: str = "python"
    executor_config: dict[str, Any] = {}


# Create schemas
class ToolCategoryCreate(ToolCategoryBase):
    """Schema for creating a tool category."""

    pass


class ToolCreate(ToolBase):
    """Schema for creating a tool."""

    pass


# Update schemas
class ToolCategoryUpdate(BaseModel):
    """Schema for updating a tool category."""

    name: str | None = None
    description: str | None = None
    parent_id: UUID | None = None


class ToolUpdate(BaseModel):
    """Schema for updating a tool."""

    display_name: str | None = None
    description: str | None = None
    status: ToolStatus | None = None
    category_id: UUID | None = None
    tags: list[str] | None = None
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    script_content: str | None = None
    executor_config: dict[str, Any] | None = None


# Response schemas
class ToolCategoryResponse(ToolCategoryBase):
    """Response schema for tool category."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ToolResponse(ToolBase):
    """Response schema for tool."""

    id: UUID
    status: ToolStatus
    version: int
    created_at: datetime
    updated_at: datetime
    category: ToolCategoryResponse | None = None

    model_config = {"from_attributes": True}


class ToolListResponse(BaseModel):
    """Paginated list response for tools."""

    items: list[ToolResponse]
    total: int
    page: int
    page_size: int


# Request schemas for POST-only API
class ToolListRequest(BaseModel):
    """Request schema for listing tools."""

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    status: ToolStatus | None = None
    category_id: UUID | None = None
    search: str | None = None


class ToolGetRequest(BaseModel):
    """Request schema for getting a tool by ID."""

    tool_id: UUID


class ToolDeleteRequest(BaseModel):
    """Request schema for deleting a tool."""

    tool_id: UUID


class ToolUpdateRequest(ToolUpdate):
    """Request schema for updating a tool."""

    tool_id: UUID


class CategoryGetRequest(BaseModel):
    """Request schema for getting a category by ID."""

    category_id: UUID


class CategoryDeleteRequest(BaseModel):
    """Request schema for deleting a category."""

    category_id: UUID


class CategoryUpdateRequest(ToolCategoryUpdate):
    """Request schema for updating a category."""

    category_id: UUID


class ExecutionCancelRequest(BaseModel):
    """Request schema for canceling an execution."""

    execution_id: UUID


# Execution schemas
class ToolExecutionRequest(BaseModel):
    """Request schema for tool execution."""

    tool_id: UUID
    input_data: dict[str, Any] = {}
    caller_id: str | None = None
    trace_id: str | None = None


class ToolExecutionResponse(BaseModel):
    """Response schema for tool execution."""

    id: UUID
    tool_id: UUID
    version: str
    status: ExecutionStatus
    input_data: dict[str, Any]
    output_data: dict[str, Any] | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
