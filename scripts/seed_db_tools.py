#!/usr/bin/env python3
"""Seed script for creating Database tools."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import select

from aiops_tools.core.database import get_session
from aiops_tools.models.tool import Tool, ToolCategory, ToolStatus
from aiops_tools.services.tool_loader import get_tool_definition, get_tool_script


DATABASE_TOOLS = [
    "execute_query",
    "list_tables",
    "describe_table",
]


async def get_category_id(session, name: str) -> str | None:
    """Get category ID by name."""
    result = await session.execute(
        select(ToolCategory).where(ToolCategory.name == name)
    )
    category = result.scalar_one_or_none()
    return str(category.id) if category else None


async def seed_db_tools() -> list[str]:
    """Create Database tools and return list of created tool IDs."""
    created_tools = []

    async for session in get_session():
        # Get database category
        category_id = await get_category_id(session, "database")
        if not category_id:
            print("ERROR: 'database' category not found. Run seed_categories.py first.")
            return []

        for tool_name in DATABASE_TOOLS:
            # Get tool definition
            definition = get_tool_definition("database", tool_name)
            if not definition:
                print(f"WARNING: No definition found for {tool_name}")
                continue

            # Check if tool already exists
            full_name = definition.get("name", f"db_{tool_name}")
            result = await session.execute(
                select(Tool).where(Tool.name == full_name)
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"Tool '{full_name}' already exists (id: {existing.id})")
                created_tools.append(str(existing.id))
                continue

            # Get script content
            script = get_tool_script("database", tool_name)
            if not script:
                print(f"WARNING: No script found for {tool_name}")
                continue

            # Create tool
            tool = Tool(
                name=full_name,
                display_name=definition.get("display_name", tool_name.replace("_", " ").title()),
                description=definition.get("description", ""),
                status=ToolStatus.ACTIVE,
                category_id=category_id,
                tags=definition.get("tags", ["database"]),
                input_schema=definition.get("input_schema", {}),
                output_schema=definition.get("output_schema", {}),
                script_content=script,
                executor_type="python",
            )
            session.add(tool)
            await session.flush()
            await session.refresh(tool)
            print(f"Created tool '{full_name}' (id: {tool.id})")
            created_tools.append(str(tool.id))

        await session.commit()

    return created_tools


async def main():
    """Run the seed script."""
    print("Seeding Database tools...")
    print("-" * 40)

    tool_ids = await seed_db_tools()

    print("-" * 40)
    print(f"Created {len(tool_ids)} Database tools")
    print("\nDone!")
    return tool_ids


if __name__ == "__main__":
    asyncio.run(main())
