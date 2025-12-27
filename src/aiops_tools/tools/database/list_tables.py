"""List database tables."""

TOOL_DEFINITION = {
    "name": "db_list_tables",
    "display_name": "List Database Tables",
    "description": "List all tables in a database with their row counts and sizes.",
    "tags": ["database", "schema", "tables"],
    "input_schema": {
        "type": "object",
        "properties": {
            "db_type": {
                "type": "string",
                "enum": ["postgresql", "mysql"],
            },
            "host": {"type": "string"},
            "port": {"type": "integer"},
            "database": {"type": "string"},
            "username": {"type": "string"},
            "password": {"type": "string"},
            "schema": {
                "type": "string",
                "description": "Schema name (PostgreSQL only)",
                "default": "public",
            },
        },
        "required": ["db_type", "host", "database", "username", "password"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "database": {"type": "string"},
                    "schema": {"type": "string"},
                    "tables": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "row_count": {"type": "integer"},
                                "size_bytes": {"type": "integer"},
                            },
                        },
                    },
                },
            },
        },
    },
}


def main(input_data: dict) -> dict:
    """List tables in a database.

    Args:
        input_data: Dictionary with connection details

    Returns:
        Dictionary with success status and table list or error
    """
    db_type = input_data.get("db_type")
    host = input_data.get("host")
    port = input_data.get("port")
    database = input_data.get("database")
    username = input_data.get("username")
    password = input_data.get("password")
    schema = input_data.get("schema", "public")

    if not all([db_type, host, database, username, password]):
        return {
            "success": False,
            "error": {
                "code": "DB_INVALID_INPUT",
                "message": "Missing required parameters",
            },
        }

    if port is None:
        port = 5432 if db_type == "postgresql" else 3306

    try:
        if db_type == "postgresql":
            return _list_postgresql_tables(host, port, database, username, password, schema)
        elif db_type == "mysql":
            return _list_mysql_tables(host, port, database, username, password)
        else:
            return {
                "success": False,
                "error": {
                    "code": "DB_INVALID_TYPE",
                    "message": f"Unsupported database type: {db_type}",
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


def _list_postgresql_tables(host, port, database, username, password, schema):
    """List tables in PostgreSQL."""
    try:
        import psycopg2
    except ImportError:
        return {
            "success": False,
            "error": {
                "code": "DB_IMPORT_ERROR",
                "message": "psycopg2 package not installed",
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
        )

        query = """
            SELECT
                t.table_name,
                t.table_type,
                COALESCE(s.n_live_tup, 0) as row_count,
                COALESCE(pg_total_relation_size(quote_ident(t.table_schema) || '.' || quote_ident(t.table_name)), 0) as size_bytes
            FROM information_schema.tables t
            LEFT JOIN pg_stat_user_tables s ON t.table_name = s.relname AND t.table_schema = s.schemaname
            WHERE t.table_schema = %s
            ORDER BY t.table_name
        """

        with conn.cursor() as cursor:
            cursor.execute(query, (schema,))
            rows = cursor.fetchall()

        tables = []
        for row in rows:
            tables.append({
                "name": row[0],
                "type": "view" if row[1] == "VIEW" else "table",
                "row_count": row[2],
                "size_bytes": row[3],
            })

        return {
            "success": True,
            "data": {
                "database": database,
                "schema": schema,
                "tables": tables,
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "DB_CONNECTION_ERROR",
                "message": str(e),
            },
        }
    finally:
        if conn:
            conn.close()


def _list_mysql_tables(host, port, database, username, password):
    """List tables in MySQL."""
    try:
        import mysql.connector
    except ImportError:
        return {
            "success": False,
            "error": {
                "code": "DB_IMPORT_ERROR",
                "message": "mysql-connector-python package not installed",
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
        )

        query = """
            SELECT
                TABLE_NAME,
                TABLE_TYPE,
                TABLE_ROWS,
                DATA_LENGTH + INDEX_LENGTH as size_bytes
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME
        """

        cursor = conn.cursor()
        cursor.execute(query, (database,))
        rows = cursor.fetchall()

        tables = []
        for row in rows:
            tables.append({
                "name": row[0],
                "type": "view" if row[1] == "VIEW" else "table",
                "row_count": row[2] or 0,
                "size_bytes": row[3] or 0,
            })

        return {
            "success": True,
            "data": {
                "database": database,
                "schema": database,
                "tables": tables,
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "DB_CONNECTION_ERROR",
                "message": str(e),
            },
        }
    finally:
        if conn:
            conn.close()
