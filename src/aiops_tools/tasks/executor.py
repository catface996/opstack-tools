"""Celery task for tool execution."""

from datetime import datetime
from uuid import UUID

from celery import Celery

from aiops_tools.core.config import settings
from aiops_tools.services.tool_executor import execute_script

# Create Celery app
celery_app = Celery(
    "aiops_tools",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.tool_execution_timeout + 10,  # Extra buffer
    task_soft_time_limit=settings.tool_execution_timeout,
)


@celery_app.task(bind=True, name="execute_tool")
def execute_tool_task(
    self,
    execution_id: str,
    script_content: str,
    input_data: dict,
) -> dict:
    """Execute a tool script as a Celery task.

    Args:
        execution_id: UUID of the ToolExecution record.
        script_content: Python script to execute.
        input_data: Input parameters for the script.

    Returns:
        Dictionary with execution results.
    """
    # Execute the script
    result = execute_script(
        script_content=script_content,
        input_data=input_data,
        timeout=settings.tool_execution_timeout,
    )

    return {
        "execution_id": execution_id,
        "success": result.success,
        "result": result.result,
        "error": result.error,
        "duration_ms": result.duration_ms,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def update_execution_status(
    execution_id: UUID,
    status: str,
    output_data: dict | None = None,
    error_message: str | None = None,
    duration_ms: int | None = None,
) -> None:
    """Update ToolExecution record status.

    This should be called from the task result callback
    or from the API endpoint that polls for results.

    Note: This requires a database session, which should be
    handled by the caller in an async context.
    """
    # This is a placeholder - actual DB update should be done
    # by the API layer with proper session management
    pass
