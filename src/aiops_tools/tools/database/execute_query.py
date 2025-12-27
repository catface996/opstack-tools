"""Execute read-only SQL queries."""

import time

TOOL_DEFINITION = {
    "name": "db_execute_query",
    "display_name": "Execute SQL Query",
    "description": "Execute a read-only SQL query against a PostgreSQL or MySQL database. Only SELECT, SHOW, DESCRIBE, and EXPLAIN statements are allowed. Results are limited to prevent memory issues.",
    "tags": ["database", "query", "sql"],
    "input_schema": {
        "type": "object",
        "properties": {
            "db_type": {
                "type": "string",
                "enum": ["postgresql", "mysql"],
                "description": "Database type",
            },
            "host": {
                "type": "string",
                "description": "Database host address",
            },
            "port": {
                "type": "integer",
                "description": "Database port (5432 for PostgreSQL, 3306 for MySQL)",
            },
            "database": {
                "type": "string",
                "description": "Database name",
            },
            "username": {
                "type": "string",
                "description": "Database username",
            },
            "password": {
                "type": "string",
                "description": "Database password",
            },
            "query": {
                "type": "string",
                "description": "SQL query to execute (SELECT only)",
            },
            "timeout": {
                "type": "integer",
                "description": "Query timeout in seconds",
                "default": 30,
            },
            "max_rows": {
                "type": "integer",
                "description": "Maximum number of rows to return",
                "default": 1000,
            },
        },
        "required": ["db_type", "host", "database", "username", "password", "query"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "columns": {"type": "array", "items": {"type": "string"}},
                    "rows": {"type": "array"},
                    "row_count": {"type": "integer"},
                    "truncated": {"type": "boolean"},
                    "execution_time_ms": {"type": "integer"},
                },
            },
        },
    },
}


def main(input_data: dict) -> dict:
    """Execute a read-only SQL query.

    Args:
        input_data: Dictionary with connection details and query

    Returns:
        Dictionary with success status and query results or error
    """
    from aiops_tools.tools.database.query_validator import validate_sql

    # Extract parameters
    db_type = input_data.get("db_type")
    host = input_data.get("host")
    port = input_data.get("port")
    database = input_data.get("database")
    username = input_data.get("username")
    password = input_data.get("password")
    query = input_data.get("query")
    timeout = input_data.get("timeout", 30)
    max_rows = input_data.get("max_rows", 1000)

    # Validate required fields
    if not all([db_type, host, database, username, password, query]):
        return {
            "success": False,
            "error": {
                "code": "DB_INVALID_INPUT",
                "message": "Missing required parameters: db_type, host, database, username, password, query",
            },
        }

    # Validate SQL
    is_valid, error_msg = validate_sql(query)
    if not is_valid:
        return {
            "success": False,
            "error": {
                "code": "DB_REJECTED",
                "message": error_msg,
            },
        }

    # Set default ports
    if port is None:
        port = 5432 if db_type == "postgresql" else 3306

    start_time = time.time()

    try:
        if db_type == "postgresql":
            return _execute_postgresql(host, port, database, username, password, query, timeout, max_rows, start_time)
        elif db_type == "mysql":
            return _execute_mysql(host, port, database, username, password, query, timeout, max_rows, start_time)
        else:
            return {
                "success": False,
                "error": {
                    "code": "DB_INVALID_TYPE",
                    "message": f"Unsupported database type: {db_type}. Use 'postgresql' or 'mysql'",
                },
            }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "DB_ERROR",
                "message": str(e),
            },
        }


def _execute_postgresql(host, port, database, username, password, query, timeout, max_rows, start_time):
    """Execute query on PostgreSQL."""
    try:
        import psycopg2
        from psycopg2 import OperationalError, ProgrammingError
    except ImportError:
        return {
            "success": False,
            "error": {
                "code": "DB_IMPORT_ERROR",
                "message": "psycopg2 package not installed. Run: pip install psycopg2-binary",
            },
        }

    conn = None
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
            connect_timeout=timeout,
        )
        conn.set_session(readonly=True)

        with conn.cursor() as cursor:
            cursor.execute(query)

            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # Fetch rows with limit
            rows = cursor.fetchmany(max_rows + 1)
            truncated = len(rows) > max_rows
            if truncated:
                rows = rows[:max_rows]

            # Convert to list of lists for JSON serialization
            rows = [list(row) for row in rows]

            execution_time_ms = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "data": {
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows),
                    "truncated": truncated,
                    "execution_time_ms": execution_time_ms,
                },
            }

    except OperationalError as e:
        return {
            "success": False,
            "error": {
                "code": "DB_CONNECTION_ERROR",
                "message": f"Failed to connect to PostgreSQL: {e}",
            },
        }
    except ProgrammingError as e:
        return {
            "success": False,
            "error": {
                "code": "DB_QUERY_ERROR",
                "message": f"Query error: {e}",
            },
        }
    finally:
        if conn:
            conn.close()


def _execute_mysql(host, port, database, username, password, query, timeout, max_rows, start_time):
    """Execute query on MySQL."""
    try:
        import mysql.connector
        from mysql.connector import Error as MySQLError
    except ImportError:
        return {
            "success": False,
            "error": {
                "code": "DB_IMPORT_ERROR",
                "message": "mysql-connector-python package not installed. Run: pip install mysql-connector-python",
            },
        }

    conn = None
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
            connection_timeout=timeout,
        )

        cursor = conn.cursor()
        cursor.execute(query)

        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        # Fetch rows with limit
        rows = cursor.fetchmany(max_rows + 1)
        truncated = len(rows) > max_rows
        if truncated:
            rows = rows[:max_rows]

        # Convert to list of lists
        rows = [list(row) for row in rows]

        execution_time_ms = int((time.time() - start_time) * 1000)

        return {
            "success": True,
            "data": {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "truncated": truncated,
                "execution_time_ms": execution_time_ms,
            },
        }

    except MySQLError as e:
        if e.errno == 2003:
            return {
                "success": False,
                "error": {
                    "code": "DB_CONNECTION_ERROR",
                    "message": f"Failed to connect to MySQL: {e}",
                },
            }
        return {
            "success": False,
            "error": {
                "code": "DB_QUERY_ERROR",
                "message": f"Query error: {e}",
            },
        }
    finally:
        if conn:
            conn.close()
