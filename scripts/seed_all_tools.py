#!/usr/bin/env python3
"""Master seed script that creates all categories and tools."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def main():
    """Run all seed scripts in order."""
    print("=" * 60)
    print("Seeding ALL Operations Tools")
    print("=" * 60)
    print()

    # Import seed functions
    from seed_categories import seed_categories
    from seed_k8s_tools import seed_k8s_tools
    from seed_db_tools import seed_db_tools
    from seed_java_tools import seed_java_tools
    from seed_aws_tools import seed_aws_tools

    # Step 1: Create categories
    print("Step 1: Creating categories...")
    print("-" * 40)
    category_ids = await seed_categories()
    print()

    # Step 2: Create K8S tools
    print("Step 2: Creating K8S tools...")
    print("-" * 40)
    k8s_tools = await seed_k8s_tools()
    print()

    # Step 3: Create Database tools
    print("Step 3: Creating Database tools...")
    print("-" * 40)
    db_tools = await seed_db_tools()
    print()

    # Step 4: Create Java tools
    print("Step 4: Creating Java tools...")
    print("-" * 40)
    java_tools = await seed_java_tools()
    print()

    # Step 5: Create AWS tools
    print("Step 5: Creating AWS tools...")
    print("-" * 40)
    aws_tools = await seed_aws_tools()
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Categories created: {len(category_ids)}")
    print(f"K8S tools created:  {len(k8s_tools)}")
    print(f"DB tools created:   {len(db_tools)}")
    print(f"Java tools created: {len(java_tools)}")
    print(f"AWS tools created:  {len(aws_tools)}")
    print("-" * 40)
    total = len(k8s_tools) + len(db_tools) + len(java_tools) + len(aws_tools)
    print(f"TOTAL TOOLS: {total}")
    print()
    print("All tools are now ACTIVE and ready to use via:")
    print("  POST /api/v1/llm/tools/list")
    print("  POST /api/v1/llm/tools/invoke")
    print()


if __name__ == "__main__":
    asyncio.run(main())
