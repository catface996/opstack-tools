"""Database tools for query and schema operations.

Tools:
- db_execute_query: Execute read-only SQL queries
- db_list_tables: List database tables
- db_describe_table: Get table schema information
"""

DATABASE_TOOLS = [
    "db_execute_query",
    "db_list_tables",
    "db_describe_table",
]

__all__ = ["DATABASE_TOOLS"]
