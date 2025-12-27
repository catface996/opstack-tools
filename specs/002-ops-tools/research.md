# Research: Operations Tools Collection

**Feature**: 002-ops-tools
**Date**: 2025-12-27

## Overview

This document captures technology decisions and best practices research for implementing the Operations Tools Collection feature.

---

## 1. Kubernetes Client Library

### Decision
Use the official **kubernetes** Python client library.

### Rationale
- Official client maintained by Kubernetes SIG
- Supports all K8S API versions with auto-generated clients
- Handles authentication via kubeconfig, in-cluster config, or explicit credentials
- Well-documented with extensive examples
- Mature library with stable API

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| kubectl subprocess calls | Less reliable, parsing text output is fragile, no structured errors |
| kr8s (lightweight client) | Newer library, smaller community, fewer features |
| pykube-ng | Less active maintenance, fewer features than official client |

### Implementation Notes
- Use `kubernetes.client.CoreV1Api` for pod operations
- Use `kubernetes.client.AppsV1Api` for deployment operations
- Support both kubeconfig file and in-cluster authentication
- Handle `ApiException` for structured error responses

---

## 2. Database Connectivity

### Decision
Use **psycopg2** for PostgreSQL and **mysql-connector-python** for MySQL.

### Rationale
- psycopg2 is the most mature PostgreSQL adapter for Python
- mysql-connector-python is Oracle's official MySQL driver
- Both support parameterized queries to prevent SQL injection
- Both support connection pooling and timeouts
- Wide adoption means good community support and documentation

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| asyncpg (PostgreSQL) | Already used for FastAPI DB, but tool scripts run sync in subprocess |
| SQLAlchemy | Over-engineered for simple query execution, adds unnecessary abstraction |
| PyMySQL | Pure Python, slower than mysql-connector for large result sets |

### Implementation Notes
- Enforce read-only mode by parsing SQL and rejecting non-SELECT statements
- Use `cursor.description` for schema introspection
- Set `connect_timeout` and `query_timeout` parameters
- Limit result rows with configurable `max_rows` parameter
- Use parameterized queries even though we control inputs (defense in depth)

### SQL Validation Strategy
```python
# Simple validation approach
ALLOWED_STATEMENTS = {'SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN'}
def validate_sql(sql: str) -> bool:
    first_word = sql.strip().split()[0].upper()
    return first_word in ALLOWED_STATEMENTS
```

---

## 3. JMX Connectivity for Java Tools

### Decision
Use **py4j** or **jmxquery** for JMX connectivity, with fallback to **jolokia** REST API.

### Rationale
- JMX is the standard way to monitor Java applications
- Multiple approaches provide flexibility for different deployment scenarios
- Jolokia REST approach is firewall-friendly and widely deployed

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| jmxterm (subprocess) | Text parsing is fragile, requires Java installation |
| Direct JMX RMI | Requires complex networking setup, firewall issues |

### Implementation Notes
- Primary approach: Use Jolokia REST API if available (most common in production)
- Fallback: Direct JMX connection via py4j gateway
- MBean paths for common metrics:
  - Heap: `java.lang:type=Memory` → `HeapMemoryUsage`
  - GC: `java.lang:type=GarbageCollector,name=*` → `CollectionCount`, `CollectionTime`
  - Threads: `java.lang:type=Threading` → `ThreadCount`, `dumpAllThreads()`

### Jolokia REST Pattern
```python
# GET /jolokia/read/java.lang:type=Memory/HeapMemoryUsage
response = {
    "value": {
        "committed": 1073741824,
        "init": 268435456,
        "max": 4294967296,
        "used": 536870912
    }
}
```

---

## 4. AWS SDK

### Decision
Use **boto3** (official AWS SDK for Python).

### Rationale
- Official AWS SDK with full service coverage
- Automatic credential discovery (env vars, config files, IAM roles)
- Pagination helpers for large result sets
- Well-documented with extensive examples
- Active development and support

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| aiobotocore | Tool scripts run synchronously in subprocess |
| AWS CLI subprocess | Text parsing is fragile, no structured errors |
| localstack (for testing) | Good for testing, but production uses real boto3 |

### Implementation Notes
- Support multiple credential sources:
  1. Explicit credentials in tool input (for multi-tenant)
  2. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
  3. AWS config file (`~/.aws/credentials`)
  4. IAM instance role (for EC2/ECS deployment)
- Handle `ClientError` exceptions for structured error responses
- Use pagination for EC2 instances and S3 objects
- Region should be required parameter for all tools

### Credential Priority
```python
def get_boto_session(input_data: dict):
    if 'aws_access_key_id' in input_data:
        return boto3.Session(
            aws_access_key_id=input_data['aws_access_key_id'],
            aws_secret_access_key=input_data['aws_secret_access_key'],
            region_name=input_data['region']
        )
    return boto3.Session(region_name=input_data['region'])
```

---

## 5. Error Handling Strategy

### Decision
Standardize error responses across all tool categories.

### Error Response Schema
```json
{
    "success": false,
    "error": {
        "code": "CONNECTION_TIMEOUT",
        "message": "Failed to connect to Kubernetes cluster",
        "details": {
            "host": "https://k8s.example.com",
            "timeout_seconds": 30
        }
    }
}
```

### Error Codes by Category

**K8S Errors**:
- `K8S_CONNECTION_ERROR` - Cannot connect to cluster
- `K8S_AUTH_ERROR` - Authentication failed
- `K8S_NOT_FOUND` - Resource not found
- `K8S_FORBIDDEN` - Insufficient permissions

**Database Errors**:
- `DB_CONNECTION_ERROR` - Cannot connect to database
- `DB_AUTH_ERROR` - Authentication failed
- `DB_QUERY_ERROR` - Query execution failed
- `DB_TIMEOUT` - Query timeout
- `DB_REJECTED` - Non-SELECT query rejected

**Java Errors**:
- `JMX_CONNECTION_ERROR` - Cannot connect to JMX endpoint
- `JMX_AUTH_ERROR` - JMX authentication failed
- `JMX_MBEAN_NOT_FOUND` - MBean not found

**AWS Errors**:
- `AWS_AUTH_ERROR` - Invalid credentials
- `AWS_ACCESS_DENIED` - Insufficient permissions
- `AWS_NOT_FOUND` - Resource not found
- `AWS_RATE_LIMITED` - Rate limit exceeded

---

## 6. Tool Script Pattern

### Decision
All tool scripts follow the same pattern for consistency.

### Standard Script Structure
```python
"""Tool description for LLM understanding."""

def main(input_data: dict) -> dict:
    """Execute the tool.

    Args:
        input_data: Dictionary with tool parameters

    Returns:
        Dictionary with results or error
    """
    try:
        # 1. Validate required parameters
        # 2. Execute operation
        # 3. Return structured result
        return {
            "success": True,
            "data": {...}
        }
    except SpecificException as e:
        return {
            "success": False,
            "error": {
                "code": "ERROR_CODE",
                "message": str(e),
                "details": {...}
            }
        }
```

---

## 7. Dependencies to Add

### Required Dependencies (pyproject.toml)
```toml
# K8S
"kubernetes>=28.1.0",

# Database
"psycopg2-binary>=2.9.9",
"mysql-connector-python>=8.3.0",

# AWS
"boto3>=1.34.0",

# Java/JMX (optional, for direct JMX)
"py4j>=0.10.9",
```

### Optional Dependencies (for testing)
```toml
[project.optional-dependencies]
ops-tools = [
    "moto>=5.0.0",  # AWS mocking
    "kubernetes-mock>=1.0.0",  # K8S mocking (if available)
]
```

---

## Summary

All research items resolved. No NEEDS CLARIFICATION items remain.

| Area | Decision | Key Library |
|------|----------|-------------|
| K8S | Official Python client | kubernetes |
| PostgreSQL | Standard adapter | psycopg2 |
| MySQL | Official connector | mysql-connector-python |
| Java/JMX | Jolokia REST + py4j fallback | requests, py4j |
| AWS | Official SDK | boto3 |
| Errors | Standardized schema | N/A |
