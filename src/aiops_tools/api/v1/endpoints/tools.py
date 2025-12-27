"""Tool management API endpoints - All POST mode."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from aiops_tools.core.database import get_session
from aiops_tools.core.errors import (
    DuplicateError,
    ErrorCode,
    ErrorDetail,
    ErrorResponse,
    MultiValidationError,
    NotFoundError,
)
from aiops_tools.models import Tool, ToolCategory, ToolStatus, ToolVersion
from aiops_tools.schemas import (
    CategoryDeleteRequest,
    CategoryGetRequest,
    CategoryUpdateRequest,
    PaginatedData,
    ToolCategoryCreate,
    ToolCategoryResponse,
    ToolCreate,
    ToolDeleteRequest,
    ToolGetRequest,
    ToolListRequest,
    ToolListResponse,
    ToolResponse,
    ToolUpdateRequest,
)
from aiops_tools.services.tool_validator import validate_tool

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


# Category endpoints
@router.post("/categories/create", response_model=ToolCategoryResponse, status_code=status.HTTP_201_CREATED, tags=["Categories"])
async def create_category(session: SessionDep, category_in: ToolCategoryCreate) -> ToolCategory:
    """Create a new tool category."""
    # Check if category with same name exists
    existing = await session.execute(select(ToolCategory).where(ToolCategory.name == category_in.name))
    if existing.scalar_one_or_none():
        raise DuplicateError(
            resource="Category",
            field="name",
            value=category_in.name,
        )

    # Validate parent_id if provided
    if category_in.parent_id:
        parent = await session.get(ToolCategory, category_in.parent_id)
        if not parent:
            raise NotFoundError(
                resource="Parent Category",
                identifier=str(category_in.parent_id),
                suggestion="Use POST /api/tools/v1/categories/list to see available categories.",
            )

    try:
        category = ToolCategory(**category_in.model_dump())
        session.add(category)
        await session.flush()
        await session.refresh(category)
        return category
    except IntegrityError as e:
        await session.rollback()
        # Handle race condition where category was created between check and insert
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise DuplicateError(
                resource="Category",
                field="name",
                value=category_in.name,
            )
        raise


@router.post("/categories/list", response_model=list[ToolCategoryResponse], tags=["Categories"])
async def list_categories(session: SessionDep) -> list[ToolCategory]:
    """List all tool categories."""
    result = await session.execute(select(ToolCategory))
    return list(result.scalars().all())


@router.post("/categories/get", response_model=ToolCategoryResponse, tags=["Categories"])
async def get_category(session: SessionDep, request: CategoryGetRequest) -> ToolCategory:
    """Get a tool category by ID."""
    category = await session.get(ToolCategory, request.category_id)
    if not category:
        raise NotFoundError(
            resource="Category",
            identifier=str(request.category_id),
            suggestion="Use POST /api/tools/v1/categories/list to see all available categories.",
        )
    return category


@router.post("/categories/update", response_model=ToolCategoryResponse, tags=["Categories"])
async def update_category(session: SessionDep, request: CategoryUpdateRequest) -> ToolCategory:
    """Update a tool category."""
    category = await session.get(ToolCategory, request.category_id)
    if not category:
        raise NotFoundError(
            resource="Category",
            identifier=str(request.category_id),
        )

    update_data = request.model_dump(exclude={"category_id"}, exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    await session.flush()
    await session.refresh(category)
    return category


@router.post("/categories/delete", tags=["Categories"])
async def delete_category(session: SessionDep, request: CategoryDeleteRequest) -> dict:
    """Delete a tool category."""
    category = await session.get(ToolCategory, request.category_id)
    if not category:
        raise NotFoundError(
            resource="Category",
            identifier=str(request.category_id),
        )
    await session.delete(category)
    return {"success": True, "message": "Category deleted successfully"}


# Tool endpoints
@router.post("/tools/create", response_model=ToolResponse, status_code=status.HTTP_201_CREATED, tags=["Tools"])
async def create_tool(session: SessionDep, tool_in: ToolCreate) -> Tool:
    """Create a new tool."""
    # Check if tool with same name exists
    existing = await session.execute(select(Tool).where(Tool.name == tool_in.name))
    if existing.scalar_one_or_none():
        raise DuplicateError(
            resource="Tool",
            field="name",
            value=tool_in.name,
        )

    # Validate category_id if provided
    if tool_in.category_id:
        category = await session.get(ToolCategory, tool_in.category_id)
        if not category:
            raise NotFoundError(
                resource="Category",
                identifier=str(tool_in.category_id),
                suggestion="Use POST /api/tools/v1/categories/list to see available categories, "
                "or set category_id to null.",
            )

    # Validate tool (Python syntax, JSON schema)
    validation_result = validate_tool(
        script_content=tool_in.script_content,
        input_schema=tool_in.input_schema,
        executor_type=tool_in.executor_type,
    )
    if not validation_result.valid:
        raise MultiValidationError(errors=validation_result.errors)

    tool = Tool(**tool_in.model_dump())
    session.add(tool)
    await session.flush()
    await session.refresh(tool, ["category"])
    return tool


@router.post("/tools/list", response_model=ToolListResponse, tags=["Tools"])
async def list_tools(session: SessionDep, request: ToolListRequest) -> ToolListResponse:
    """List tools with pagination and filtering (Constitution Principle V & VI compliant)."""
    query = select(Tool).options(selectinload(Tool.category))

    # Apply filters
    if request.status:
        query = query.where(Tool.status == request.status)
    if request.category_id:
        query = query.where(Tool.category_id == request.category_id)
    if request.search:
        query = query.where(
            Tool.name.ilike(f"%{request.search}%") | Tool.display_name.ilike(f"%{request.search}%")
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_elements = await session.scalar(count_query) or 0

    # Apply pagination (using 'size' per constitution standard)
    query = query.offset((request.page - 1) * request.size).limit(request.size)
    result = await session.execute(query)
    tools = list(result.scalars().all())

    # Calculate pagination metadata per constitution standard
    total_pages = (total_elements + request.size - 1) // request.size if request.size > 0 else 0
    is_first = request.page == 1
    is_last = request.page >= total_pages if total_pages > 0 else True

    return ToolListResponse(
        code=0,
        message="success",
        success=True,
        data=PaginatedData(
            content=tools,
            page=request.page,
            size=request.size,
            totalElements=total_elements,
            totalPages=total_pages,
            first=is_first,
            last=is_last,
        ),
    )


@router.post("/tools/get", response_model=ToolResponse, tags=["Tools"])
async def get_tool(session: SessionDep, request: ToolGetRequest) -> Tool:
    """Get a tool by ID."""
    query = select(Tool).where(Tool.id == request.tool_id).options(selectinload(Tool.category))
    result = await session.execute(query)
    tool = result.scalar_one_or_none()
    if not tool:
        raise NotFoundError(
            resource="Tool",
            identifier=str(request.tool_id),
            suggestion="Use POST /api/tools/v1/tools/list to see all available tools.",
        )
    return tool


@router.post("/tools/update", response_model=ToolResponse, tags=["Tools"])
async def update_tool(session: SessionDep, request: ToolUpdateRequest) -> Tool:
    """Update a tool with auto-increment version."""
    tool = await session.get(Tool, request.tool_id)
    if not tool:
        raise NotFoundError(
            resource="Tool",
            identifier=str(request.tool_id),
        )

    update_data = request.model_dump(exclude={"tool_id"}, exclude_unset=True)

    # Validate if script_content or input_schema is being updated
    script_content = update_data.get("script_content", tool.script_content)
    input_schema = update_data.get("input_schema", tool.input_schema)
    validation_result = validate_tool(
        script_content=script_content,
        input_schema=input_schema,
        executor_type=tool.executor_type,
    )
    if not validation_result.valid:
        raise MultiValidationError(errors=validation_result.errors)

    # Create a version snapshot before updating
    tool_version = ToolVersion(
        tool_id=tool.id,
        version=str(tool.version),
        input_schema=tool.input_schema,
        output_schema=tool.output_schema,
        executor_config=tool.executor_config,
        script_content=tool.script_content,
    )
    session.add(tool_version)

    # Apply updates
    for key, value in update_data.items():
        setattr(tool, key, value)

    # Auto-increment version
    tool.version += 1

    await session.flush()
    await session.refresh(tool, ["category"])
    return tool


@router.post("/tools/delete", tags=["Tools"])
async def delete_tool(session: SessionDep, request: ToolDeleteRequest) -> dict:
    """Delete a tool."""
    tool = await session.get(Tool, request.tool_id)
    if not tool:
        raise NotFoundError(
            resource="Tool",
            identifier=str(request.tool_id),
        )
    await session.delete(tool)
    return {"success": True, "message": "Tool deleted successfully"}


@router.post("/tools/activate", response_model=ToolResponse, tags=["Tools"])
async def activate_tool(session: SessionDep, request: ToolGetRequest) -> Tool:
    """Activate a tool."""
    tool = await session.get(Tool, request.tool_id)
    if not tool:
        raise NotFoundError(
            resource="Tool",
            identifier=str(request.tool_id),
        )

    tool.status = ToolStatus.ACTIVE
    await session.flush()
    await session.refresh(tool, ["category"])
    return tool


@router.post("/tools/deactivate", response_model=ToolResponse, tags=["Tools"])
async def deactivate_tool(session: SessionDep, request: ToolGetRequest) -> Tool:
    """Deactivate a tool."""
    tool = await session.get(Tool, request.tool_id)
    if not tool:
        raise NotFoundError(
            resource="Tool",
            identifier=str(request.tool_id),
        )

    tool.status = ToolStatus.DISABLED
    await session.flush()
    await session.refresh(tool, ["category"])
    return tool
