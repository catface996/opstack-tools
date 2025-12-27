"""SQL query validator for read-only operations."""

import re

# Allowed SQL statement types (read-only operations)
ALLOWED_STATEMENTS = {"SELECT", "SHOW", "DESCRIBE", "EXPLAIN", "DESC"}

# Dangerous patterns that should be rejected
DANGEROUS_PATTERNS = [
    r";\s*(?:INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|GRANT|REVOKE)",
    r"INTO\s+OUTFILE",
    r"INTO\s+DUMPFILE",
    r"LOAD_FILE\s*\(",
    r"--",  # SQL comments that might hide malicious code
]


def validate_sql(sql: str) -> tuple[bool, str | None]:
    """Validate that SQL is a read-only statement.

    Args:
        sql: SQL query string to validate

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if valid
        - (False, "error message") if invalid
    """
    if not sql or not sql.strip():
        return False, "Empty SQL query"

    # Normalize whitespace and get first word
    normalized = sql.strip()
    first_word = normalized.split()[0].upper()

    # Check if statement type is allowed
    if first_word not in ALLOWED_STATEMENTS:
        return False, f"Only {', '.join(sorted(ALLOWED_STATEMENTS))} statements are allowed. Got: {first_word}"

    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return False, f"Query contains potentially dangerous pattern"

    # Check for multiple statements (semicolon followed by another statement)
    # Allow semicolon at end, but not multiple statements
    statements = [s.strip() for s in normalized.rstrip(";").split(";") if s.strip()]
    if len(statements) > 1:
        return False, "Multiple SQL statements are not allowed"

    return True, None


def sanitize_identifier(identifier: str) -> str:
    """Sanitize a database identifier (table name, column name).

    Args:
        identifier: Database identifier to sanitize

    Returns:
        Sanitized identifier safe for use in queries

    Raises:
        ValueError: If identifier contains invalid characters
    """
    # Only allow alphanumeric, underscore, and dot (for schema.table)
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$", identifier):
        raise ValueError(f"Invalid identifier: {identifier}")
    return identifier
