"""Tool management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from aiops_tools.core.database import get_session
from aiops_tools.models import Tool, ToolCategory, ToolStatus
from aiops_tools.schemas import (
    ToolCategoryCreate,
    ToolCategoryResponse,
    ToolCategoryUpdate,
    ToolCreate,
    ToolListResponse,
    ToolResponse,
    ToolUpdate,
)

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


# Category endpoints
@router.post("/categories", response_model=ToolCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(session: SessionDep, category_in: ToolCategoryCreate) -> ToolCategory:
    """Create a new tool category."""
    category = ToolCategory(**category_in.model_dump())
    session.add(category)
    await session.flush()
    await session.refresh(category)
    return category


@router.get("/categories", response_model=list[ToolCategoryResponse])
async def list_categories(session: SessionDep) -> list[ToolCategory]:
    """List all tool categories."""
    result = await session.execute(select(ToolCategory))
    return list(result.scalars().all())


@router.get("/categories/{category_id}", response_model=ToolCategoryResponse)
async def get_category(session: SessionDep, category_id: UUID) -> ToolCategory:
    """Get a tool category by ID."""
    category = await session.get(ToolCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.patch("/categories/{category_id}", response_model=ToolCategoryResponse)
async def update_category(
    session: SessionDep, category_id: UUID, category_in: ToolCategoryUpdate
) -> ToolCategory:
    """Update a tool category."""
    category = await session.get(ToolCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    await session.flush()
    await session.refresh(category)
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(session: SessionDep, category_id: UUID) -> None:
    """Delete a tool category."""
    category = await session.get(ToolCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await session.delete(category)


# Tool endpoints
@router.post("/", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(session: SessionDep, tool_in: ToolCreate) -> Tool:
    """Create a new tool."""
    # Check if tool with same name exists
    existing = await session.execute(select(Tool).where(Tool.name == tool_in.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Tool with this name already exists")

    tool = Tool(**tool_in.model_dump())
    session.add(tool)
    await session.flush()
    await session.refresh(tool, ["category"])
    return tool


@router.get("/", response_model=ToolListResponse)
async def list_tools(
    session: SessionDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: ToolStatus | None = Query(None, alias="status"),
    category_id: UUID | None = None,
    search: str | None = None,
) -> ToolListResponse:
    """List tools with pagination and filtering."""
    query = select(Tool).options(selectinload(Tool.category))

    # Apply filters
    if status_filter:
        query = query.where(Tool.status == status_filter)
    if category_id:
        query = query.where(Tool.category_id == category_id)
    if search:
        query = query.where(
            Tool.name.ilike(f"%{search}%") | Tool.display_name.ilike(f"%{search}%")
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query) or 0

    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    tools = list(result.scalars().all())

    return ToolListResponse(items=tools, total=total, page=page, page_size=page_size)


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(session: SessionDep, tool_id: UUID) -> Tool:
    """Get a tool by ID."""
    query = select(Tool).where(Tool.id == tool_id).options(selectinload(Tool.category))
    result = await session.execute(query)
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


@router.patch("/{tool_id}", response_model=ToolResponse)
async def update_tool(session: SessionDep, tool_id: UUID, tool_in: ToolUpdate) -> Tool:
    """Update a tool."""
    tool = await session.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    update_data = tool_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tool, key, value)

    await session.flush()
    await session.refresh(tool, ["category"])
    return tool


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(session: SessionDep, tool_id: UUID) -> None:
    """Delete a tool."""
    tool = await session.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    await session.delete(tool)


@router.post("/{tool_id}/activate", response_model=ToolResponse)
async def activate_tool(session: SessionDep, tool_id: UUID) -> Tool:
    """Activate a tool."""
    tool = await session.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    tool.status = ToolStatus.ACTIVE
    await session.flush()
    await session.refresh(tool, ["category"])
    return tool


@router.post("/{tool_id}/deactivate", response_model=ToolResponse)
async def deactivate_tool(session: SessionDep, tool_id: UUID) -> Tool:
    """Deactivate a tool."""
    tool = await session.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    tool.status = ToolStatus.DISABLED
    await session.flush()
    await session.refresh(tool, ["category"])
    return tool
