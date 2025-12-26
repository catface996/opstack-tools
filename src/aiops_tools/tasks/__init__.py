"""Celery tasks package."""

from aiops_tools.tasks.executor import execute_tool_task

__all__ = ["execute_tool_task"]
