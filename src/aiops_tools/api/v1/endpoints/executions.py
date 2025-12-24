"""Tool execution API endpoints."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aiops_tools.core.database import get_session
from aiops_tools.models import ExecutionStatus, Tool, ToolExecution, ToolStatus
from aiops_tools.schemas import ToolExecutionRequest, ToolExecutionResponse

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/{tool_id}/execute", response_model=ToolExecutionResponse, status_code=status.HTTP_202_ACCEPTED)
async def execute_tool(
    session: SessionDep, tool_id: UUID, request: ToolExecutionRequest
) -> ToolExecution:
    """Execute a tool asynchronously."""
    # Get the tool
    tool = await session.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    if tool.status != ToolStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Tool is not active")

    # Create execution record
    execution = ToolExecution(
        tool_id=tool_id,
        version=tool.current_version,
        status=ExecutionStatus.PENDING,
        input_data=request.input_data,
        caller_id=request.caller_id,
        trace_id=request.trace_id,
    )
    session.add(execution)
    await session.flush()
    await session.refresh(execution)

    # TODO: Dispatch to Celery task for actual execution
    # For now, we just mark it as pending

    return execution


@router.get("/{tool_id}/executions", response_model=list[ToolExecutionResponse])
async def list_tool_executions(
    session: SessionDep,
    tool_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    status_filter: ExecutionStatus | None = Query(None, alias="status"),
) -> list[ToolExecution]:
    """List executions for a specific tool."""
    query = select(ToolExecution).where(ToolExecution.tool_id == tool_id)

    if status_filter:
        query = query.where(ToolExecution.status == status_filter)

    query = query.order_by(ToolExecution.created_at.desc()).limit(limit)
    result = await session.execute(query)
    return list(result.scalars().all())


@router.get("/executions/{execution_id}", response_model=ToolExecutionResponse)
async def get_execution(session: SessionDep, execution_id: UUID) -> ToolExecution:
    """Get an execution by ID."""
    execution = await session.get(ToolExecution, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.post("/executions/{execution_id}/cancel", response_model=ToolExecutionResponse)
async def cancel_execution(session: SessionDep, execution_id: UUID) -> ToolExecution:
    """Cancel a pending or running execution."""
    execution = await session.get(ToolExecution, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    if execution.status not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
        raise HTTPException(status_code=400, detail="Execution cannot be cancelled")

    execution.status = ExecutionStatus.CANCELLED
    execution.completed_at = datetime.utcnow()
    await session.flush()
    await session.refresh(execution)

    # TODO: Actually cancel the Celery task if running

    return execution
