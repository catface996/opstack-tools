#!/usr/bin/env python3
"""Seed script for creating tool categories."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aiops_tools.core.database import get_session
from aiops_tools.models.tool import ToolCategory


CATEGORIES = [
    {
        "name": "kubernetes",
        "description": "Kubernetes cluster operations - list pods, get logs, restart deployments",
    },
    {
        "name": "database",
        "description": "Database query and schema operations - execute queries, list tables, describe schemas",
    },
    {
        "name": "java",
        "description": "JVM application monitoring - heap usage, thread dumps, GC statistics",
    },
    {
        "name": "aws",
        "description": "AWS cloud resource management - EC2, S3, RDS, CloudWatch",
    },
]


async def seed_categories() -> dict[str, str]:
    """Create tool categories and return mapping of name to ID.

    Returns:
        Dict mapping category name to UUID string
    """
    category_ids = {}

    async for session in get_session():
        for cat_data in CATEGORIES:
            # Check if category already exists
            result = await session.execute(
                select(ToolCategory).where(ToolCategory.name == cat_data["name"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"Category '{cat_data['name']}' already exists (id: {existing.id})")
                category_ids[cat_data["name"]] = str(existing.id)
            else:
                category = ToolCategory(**cat_data)
                session.add(category)
                await session.flush()
                await session.refresh(category)
                print(f"Created category '{cat_data['name']}' (id: {category.id})")
                category_ids[cat_data["name"]] = str(category.id)

        await session.commit()

    return category_ids


async def main():
    """Run the seed script."""
    print("Seeding tool categories...")
    print("-" * 40)

    category_ids = await seed_categories()

    print("-" * 40)
    print("Category IDs:")
    for name, cat_id in category_ids.items():
        print(f"  {name}: {cat_id}")

    print("\nDone!")
    return category_ids


if __name__ == "__main__":
    asyncio.run(main())
