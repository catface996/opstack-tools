"""LLM-compatible API endpoints for tool discovery and invocation - All POST mode."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aiops_tools.core.database import get_session
from aiops_tools.models import ExecutionStatus, Tool, ToolExecution, ToolStatus
from aiops_tools.schemas.llm import (
    LLMTool,
    LLMToolGetRequest,
    LLMToolListResponse,
    ToolInvokeRequest,
    ToolInvokeResponse,
    transform_to_llm_format,
)
from aiops_tools.services.tool_executor import execute_script
from aiops_tools.services.tool_validator import validate_input_against_schema

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/tools/list", response_model=LLMToolListResponse)
async def list_tools_for_llm(session: SessionDep) -> LLMToolListResponse:
    """List all active tools in OpenAI function calling format.

    This endpoint returns tools formatted for LLM function calling,
    compatible with OpenAI's function calling API format.
    """
    query = select(Tool).where(Tool.status == ToolStatus.ACTIVE)
    result = await session.execute(query)
    tools = result.scalars().all()

    llm_tools = [transform_to_llm_format(tool) for tool in tools]
    return LLMToolListResponse(tools=llm_tools)


@router.post("/tools/get", response_model=LLMTool)
async def get_tool_for_llm(session: SessionDep, request: LLMToolGetRequest) -> LLMTool:
    """Get a single tool by name in OpenAI function calling format.

    Args:
        request: Request containing the tool name.

    Returns:
        Tool in OpenAI function calling format.

    Raises:
        HTTPException: If tool not found or not active.
    """
    query = select(Tool).where(Tool.name == request.tool_name)
    result = await session.execute(query)
    tool = result.scalar_one_or_none()

    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")

    if tool.status != ToolStatus.ACTIVE:
        raise HTTPException(status_code=400, detail=f"Tool '{request.tool_name}' is not active")

    return transform_to_llm_format(tool)


@router.post("/tools/invoke", response_model=ToolInvokeResponse)
async def invoke_tool(session: SessionDep, request: ToolInvokeRequest) -> ToolInvokeResponse:
    """Invoke a tool with the given arguments.

    This endpoint executes a tool's script with the provided arguments
    and returns the result immediately.

    Args:
        request: The invocation request containing tool name and arguments.

    Returns:
        ToolInvokeResponse with execution result.

    Raises:
        HTTPException: If tool not found, not active, or validation fails.
    """
    # Find the tool by name
    query = select(Tool).where(Tool.name == request.tool_name)
    result = await session.execute(query)
    tool = result.scalar_one_or_none()

    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")

    if tool.status != ToolStatus.ACTIVE:
        raise HTTPException(status_code=400, detail=f"Tool '{request.tool_name}' is not active")

    # Validate input against schema
    if tool.input_schema:
        validation = validate_input_against_schema(request.arguments, tool.input_schema)
        if not validation.valid:
            raise HTTPException(
                status_code=422,
                detail={"validation_errors": validation.errors},
            )

    # Check if tool has script content
    if tool.executor_type == "python" and not tool.script_content:
        raise HTTPException(
            status_code=400,
            detail=f"Tool '{request.tool_name}' has no script content",
        )

    # Create execution record
    execution = ToolExecution(
        tool_id=tool.id,
        version=str(tool.version),
        input_data=request.arguments,
        status=ExecutionStatus.RUNNING,
    )
    session.add(execution)
    await session.flush()

    # Execute the script synchronously
    exec_result = execute_script(
        script_content=tool.script_content or "",
        input_data=request.arguments,
    )

    # Update execution record
    execution.status = ExecutionStatus.SUCCESS if exec_result.success else ExecutionStatus.FAILED
    execution.output_data = exec_result.result
    execution.error_message = exec_result.error
    execution.duration_ms = exec_result.duration_ms
    await session.flush()

    return ToolInvokeResponse(
        success=exec_result.success,
        result=exec_result.result,
        error=exec_result.error,
        duration_ms=exec_result.duration_ms,
    )
