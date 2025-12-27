"""Tool and related models."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from aiops_tools.models.base import BaseModel


class ToolStatus(str, Enum):
    """Tool status enumeration."""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"


class ExecutionStatus(str, Enum):
    """Execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ToolCategory(BaseModel, table=True):
    """Tool category for organizing tools."""

    __tablename__ = "tool_categories"

    name: str = Field(index=True, unique=True)
    description: str | None = None
    parent_id: UUID | None = Field(default=None, foreign_key="tool_categories.id")

    # Relationships
    tools: list["Tool"] = Relationship(back_populates="category")


class Tool(BaseModel, table=True):
    """Tool definition model."""

    __tablename__ = "tools"

    name: str = Field(index=True)
    display_name: str
    description: str
    status: ToolStatus = Field(default=ToolStatus.DRAFT)

    # Tool metadata
    category_id: UUID | None = Field(default=None, foreign_key="tool_categories.id")
    tags: list[str] = Field(default=[], sa_column=Column(JSONB))

    # Tool schema (JSON Schema format for parameters)
    input_schema: dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    output_schema: dict[str, Any] = Field(default={}, sa_column=Column(JSONB))

    # Python script content (for executor_type="python")
    script_content: str | None = None

    # Execution configuration
    executor_type: str = Field(default="python")  # python, http, shell, mcp
    executor_config: dict[str, Any] = Field(default={}, sa_column=Column(JSONB))

    # Versioning (auto-incremented on each save)
    version: int = Field(default=1)

    # Relationships
    category: ToolCategory | None = Relationship(back_populates="tools")
    versions: list["ToolVersion"] = Relationship(
        back_populates="tool",
        sa_relationship_kwargs={"passive_deletes": True},
    )
    executions: list["ToolExecution"] = Relationship(
        back_populates="tool",
        sa_relationship_kwargs={"passive_deletes": True},
    )


class ToolVersion(BaseModel, table=True):
    """Tool version for version control."""

    __tablename__ = "tool_versions"

    tool_id: UUID = Field(foreign_key="tools.id", ondelete="CASCADE")
    version: str
    changelog: str | None = None

    # Snapshot of tool configuration at this version
    input_schema: dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    output_schema: dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    executor_config: dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    script_content: str | None = None

    is_latest: bool = Field(default=True)

    # Relationships
    tool: Tool = Relationship(back_populates="versions")


class ToolExecution(BaseModel, table=True):
    """Tool execution record."""

    __tablename__ = "tool_executions"

    tool_id: UUID = Field(foreign_key="tools.id", ondelete="CASCADE")
    version: str

    # Execution details
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING)
    input_data: dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    output_data: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))
    error_message: str | None = None

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None

    # Context
    caller_id: str | None = None  # Agent or user who called this tool
    trace_id: str | None = None  # For distributed tracing

    # Relationships
    tool: Tool = Relationship(back_populates="executions")
