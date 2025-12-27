"""Describe database table schema."""

TOOL_DEFINITION = {
    "name": "db_describe_table",
    "display_name": "Describe Table Schema",
    "description": "Get detailed schema information for a table including columns, data types, constraints, and indexes.",
    "tags": ["database", "schema", "describe"],
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
            "table_name": {
                "type": "string",
                "description": "Name of the table to describe",
            },
            "schema": {
                "type": "string",
                "default": "public",
            },
        },
        "required": ["db_type", "host", "database", "username", "password", "table_name"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"},
                    "schema": {"type": "string"},
                    "columns": {"type": "array"},
                    "indexes": {"type": "array"},
                    "foreign_keys": {"type": "array"},
                },
            },
        },
    },
}


def main(input_data: dict) -> dict:
    """Describe a database table.

    Args:
        input_data: Dictionary with connection details and table name

    Returns:
        Dictionary with success status and table schema or error
    """
    db_type = input_data.get("db_type")
    host = input_data.get("host")
    port = input_data.get("port")
    database = input_data.get("database")
    username = input_data.get("username")
    password = input_data.get("password")
    table_name = input_data.get("table_name")
    schema = input_data.get("schema", "public")

    if not all([db_type, host, database, username, password, table_name]):
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
            return _describe_postgresql_table(host, port, database, username, password, table_name, schema)
        elif db_type == "mysql":
            return _describe_mysql_table(host, port, database, username, password, table_name)
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


def _describe_postgresql_table(host, port, database, username, password, table_name, schema):
    """Describe a PostgreSQL table."""
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

        # Get columns
        column_query = """
            SELECT
                c.column_name,
                c.data_type,
                c.is_nullable = 'YES' as nullable,
                c.column_default,
                CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as primary_key
            FROM information_schema.columns c
            LEFT JOIN (
                SELECT ku.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage ku
                    ON tc.constraint_name = ku.constraint_name
                WHERE tc.table_schema = %s AND tc.table_name = %s AND tc.constraint_type = 'PRIMARY KEY'
            ) pk ON c.column_name = pk.column_name
            WHERE c.table_schema = %s AND c.table_name = %s
            ORDER BY c.ordinal_position
        """

        with conn.cursor() as cursor:
            cursor.execute(column_query, (schema, table_name, schema, table_name))
            column_rows = cursor.fetchall()

            if not column_rows:
                return {
                    "success": False,
                    "error": {
                        "code": "DB_NOT_FOUND",
                        "message": f"Table '{table_name}' not found in schema '{schema}'",
                    },
                }

        columns = []
        for row in column_rows:
            columns.append({
                "name": row[0],
                "data_type": row[1],
                "nullable": row[2],
                "default": row[3],
                "primary_key": row[4],
            })

        # Get indexes
        index_query = """
            SELECT
                i.relname as index_name,
                array_agg(a.attname ORDER BY array_position(ix.indkey, a.attnum)) as columns,
                ix.indisunique as is_unique
            FROM pg_index ix
            JOIN pg_class t ON t.oid = ix.indrelid
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE n.nspname = %s AND t.relname = %s
            GROUP BY i.relname, ix.indisunique
        """

        with conn.cursor() as cursor:
            cursor.execute(index_query, (schema, table_name))
            index_rows = cursor.fetchall()

        indexes = []
        for row in index_rows:
            indexes.append({
                "name": row[0],
                "columns": row[1],
                "unique": row[2],
            })

        # Get foreign keys
        fk_query = """
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS references_table,
                ccu.column_name AS references_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_schema = %s AND tc.table_name = %s AND tc.constraint_type = 'FOREIGN KEY'
        """

        with conn.cursor() as cursor:
            cursor.execute(fk_query, (schema, table_name))
            fk_rows = cursor.fetchall()

        foreign_keys = []
        for row in fk_rows:
            foreign_keys.append({
                "name": row[0],
                "column": row[1],
                "references_table": row[2],
                "references_column": row[3],
            })

        return {
            "success": True,
            "data": {
                "table_name": table_name,
                "schema": schema,
                "columns": columns,
                "indexes": indexes,
                "foreign_keys": foreign_keys,
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
    finally:
        if conn:
            conn.close()


def _describe_mysql_table(host, port, database, username, password, table_name):
    """Describe a MySQL table."""
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

        # Get columns
        column_query = """
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE = 'YES' as nullable,
                COLUMN_DEFAULT,
                COLUMN_KEY = 'PRI' as primary_key
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """

        cursor = conn.cursor()
        cursor.execute(column_query, (database, table_name))
        column_rows = cursor.fetchall()

        if not column_rows:
            return {
                "success": False,
                "error": {
                    "code": "DB_NOT_FOUND",
                    "message": f"Table '{table_name}' not found",
                },
            }

        columns = []
        for row in column_rows:
            columns.append({
                "name": row[0],
                "data_type": row[1],
                "nullable": bool(row[2]),
                "default": row[3],
                "primary_key": bool(row[4]),
            })

        # Get indexes
        index_query = """
            SELECT
                INDEX_NAME,
                GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) as columns,
                NOT NON_UNIQUE as is_unique
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            GROUP BY INDEX_NAME, NON_UNIQUE
        """

        cursor.execute(index_query, (database, table_name))
        index_rows = cursor.fetchall()

        indexes = []
        for row in index_rows:
            indexes.append({
                "name": row[0],
                "columns": row[1].split(",") if row[1] else [],
                "unique": bool(row[2]),
            })

        # Get foreign keys
        fk_query = """
            SELECT
                CONSTRAINT_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND REFERENCED_TABLE_NAME IS NOT NULL
        """

        cursor.execute(fk_query, (database, table_name))
        fk_rows = cursor.fetchall()

        foreign_keys = []
        for row in fk_rows:
            foreign_keys.append({
                "name": row[0],
                "column": row[1],
                "references_table": row[2],
                "references_column": row[3],
            })

        return {
            "success": True,
            "data": {
                "table_name": table_name,
                "schema": database,
                "columns": columns,
                "indexes": indexes,
                "foreign_keys": foreign_keys,
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
    finally:
        if conn:
            conn.close()
