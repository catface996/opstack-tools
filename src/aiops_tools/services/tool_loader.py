"""Tool loader service for registering pre-built tools."""

import importlib
import inspect
from pathlib import Path
from typing import Any

from aiops_tools.models.tool import ToolStatus


def get_tool_script(category: str, tool_name: str) -> str | None:
    """Get the script content for a tool.

    Args:
        category: Tool category (k8s, database, java, aws)
        tool_name: Tool name without category prefix

    Returns:
        Script content as string, or None if not found
    """
    try:
        module_name = f"aiops_tools.tools.{category}.{tool_name}"
        module = importlib.import_module(module_name)

        # Get the source code of the module
        source_file = inspect.getfile(module)
        with open(source_file, encoding="utf-8") as f:
            return f.read()
    except (ImportError, OSError):
        return None


def get_tool_definition(category: str, tool_name: str) -> dict[str, Any] | None:
    """Get the tool definition for a tool.

    Args:
        category: Tool category (k8s, database, java, aws)
        tool_name: Tool name without category prefix

    Returns:
        Tool definition dict, or None if not found
    """
    try:
        module_name = f"aiops_tools.tools.{category}.{tool_name}"
        module = importlib.import_module(module_name)

        if hasattr(module, "TOOL_DEFINITION"):
            return module.TOOL_DEFINITION
        return None
    except ImportError:
        return None


def build_tool_record(
    category: str,
    tool_name: str,
    category_id: str | None = None,
) -> dict[str, Any] | None:
    """Build a complete tool record for database insertion.

    Args:
        category: Tool category (k8s, database, java, aws)
        tool_name: Tool name without category prefix
        category_id: Optional category UUID

    Returns:
        Complete tool record dict, or None if tool not found
    """
    definition = get_tool_definition(category, tool_name)
    if not definition:
        return None

    script = get_tool_script(category, tool_name)
    if not script:
        return None

    return {
        "name": definition.get("name", f"{category}_{tool_name}"),
        "display_name": definition.get("display_name", tool_name.replace("_", " ").title()),
        "description": definition.get("description", ""),
        "status": ToolStatus.DRAFT,
        "category_id": category_id,
        "tags": definition.get("tags", [category]),
        "input_schema": definition.get("input_schema", {}),
        "output_schema": definition.get("output_schema", {}),
        "script_content": script,
        "executor_type": "python",
        "executor_config": definition.get("executor_config", {}),
    }


def list_available_tools() -> dict[str, list[str]]:
    """List all available pre-built tools by category.

    Returns:
        Dict mapping category names to list of tool names
    """
    from aiops_tools.tools.k8s import K8S_TOOLS
    from aiops_tools.tools.database import DATABASE_TOOLS
    from aiops_tools.tools.java import JAVA_TOOLS
    from aiops_tools.tools.aws import AWS_TOOLS

    return {
        "k8s": K8S_TOOLS,
        "database": DATABASE_TOOLS,
        "java": JAVA_TOOLS,
        "aws": AWS_TOOLS,
    }
