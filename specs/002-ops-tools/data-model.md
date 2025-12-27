# Data Model: Operations Tools Collection

**Feature**: 002-ops-tools
**Date**: 2025-12-27

## Overview

This feature **does not introduce new database models**. All tools are stored in the existing `tools` table and organized using existing `tool_categories` table.

## Existing Models Used

### ToolCategory (existing)

Used to organize the 4 tool categories.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | string | Category name (e.g., "kubernetes", "database") |
| description | string | Category description |
| parent_id | UUID | Optional parent category |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

**Categories to Create**:
- `kubernetes` - Kubernetes cluster operations
- `database` - Database query and schema operations
- `java` - JVM application monitoring
- `aws` - AWS cloud resource management

### Tool (existing)

Each operational tool is stored as a Tool record.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | string | Tool identifier (e.g., "k8s_list_pods") |
| display_name | string | Human-readable name |
| description | string | Tool description for LLM understanding |
| status | enum | draft, active, deprecated, disabled |
| category_id | UUID | Foreign key to tool_categories |
| tags | array | Tool tags for filtering |
| input_schema | JSON | JSON Schema for input parameters |
| output_schema | JSON | JSON Schema for output format |
| script_content | text | Python script source code |
| executor_type | string | Always "python" for these tools |
| executor_config | JSON | Execution configuration |
| version | int | Auto-incremented version |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

### ToolExecution (existing)

Each tool invocation creates an execution record.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tool_id | UUID | Foreign key to tools |
| version | string | Tool version at execution time |
| status | enum | pending, running, success, failed, timeout, cancelled |
| input_data | JSON | Input parameters |
| output_data | JSON | Execution result |
| error_message | string | Error description if failed |
| started_at | datetime | Execution start time |
| completed_at | datetime | Execution end time |
| duration_ms | int | Execution duration |
| caller_id | string | Agent or user identifier |
| trace_id | string | Distributed tracing ID |

## Tool Input Schemas

### K8S Tools Input Patterns

**Common K8S Fields**:
```json
{
  "kubeconfig": "string (optional) - Path to kubeconfig file",
  "context": "string (optional) - Kubernetes context name",
  "namespace": "string - Target namespace"
}
```

### Database Tools Input Patterns

**Common Database Fields**:
```json
{
  "db_type": "string - 'postgresql' or 'mysql'",
  "host": "string - Database host",
  "port": "integer - Database port",
  "database": "string - Database name",
  "username": "string - Database user",
  "password": "string - Database password",
  "timeout": "integer (optional) - Query timeout in seconds"
}
```

### Java Tools Input Patterns

**Common JMX Fields**:
```json
{
  "jmx_url": "string - JMX service URL or Jolokia endpoint",
  "username": "string (optional) - JMX username",
  "password": "string (optional) - JMX password"
}
```

### AWS Tools Input Patterns

**Common AWS Fields**:
```json
{
  "region": "string - AWS region",
  "aws_access_key_id": "string (optional) - AWS access key",
  "aws_secret_access_key": "string (optional) - AWS secret key"
}
```

## Tool Output Schema

All tools follow a standard output format:

**Success Response**:
```json
{
  "success": true,
  "data": {
    "...tool-specific data..."
  }
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "...additional context..."
    }
  }
}
```

## Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│ LLM Agent   │────▶│ /tools/invoke │────▶│ Tool Executor  │
│             │     │              │     │ (subprocess)   │
└─────────────┘     └──────────────┘     └────────────────┘
                           │                     │
                           ▼                     ▼
                    ┌──────────────┐     ┌────────────────┐
                    │ tools table  │     │ External System│
                    │ (get script) │     │ (K8S/DB/AWS)   │
                    └──────────────┘     └────────────────┘
                           │                     │
                           ▼                     │
                    ┌──────────────┐             │
                    │ executions   │◀────────────┘
                    │ table (log)  │
                    └──────────────┘
```

## Migration Notes

No database migrations required. This feature only:
1. Creates 4 new category records
2. Creates 16+ tool records
3. Uses existing tables with existing schema

Tool data can be seeded via:
- API calls to `/api/v1/tools/categories/create` and `/api/v1/tools/create`
- Database seed script (recommended for initial deployment)
- Tool loader service that reads from Python files
