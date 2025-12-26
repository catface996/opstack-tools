# Data Model: LLM Tool Management System

**Feature**: 001-llm-tool-management
**Date**: 2025-12-26

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│  ToolCategory   │       │      Tool       │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ category_id (FK)│
│ name            │   1:N │ id (PK)         │
│ description     │       │ name (unique)   │
│ parent_id (FK)  │───┐   │ display_name    │
│ created_at      │   │   │ description     │
│ updated_at      │   │   │ status          │
└─────────────────┘   │   │ tags            │
        ▲             │   │ input_schema    │
        │             │   │ output_schema   │
        └─────────────┘   │ script_content* │
       (self-reference)   │ executor_type   │
                          │ executor_config │
                          │ version         │
                          │ created_at      │
                          │ updated_at      │
                          └────────┬────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼ 1:N          ▼ 1:N          │
          ┌─────────────────┐  ┌─────────────────┐│
          │   ToolVersion   │  │  ToolExecution  ││
          ├─────────────────┤  ├─────────────────┤│
          │ id (PK)         │  │ id (PK)         ││
          │ tool_id (FK)    │  │ tool_id (FK)    ││
          │ version         │  │ version         ││
          │ changelog       │  │ status          ││
          │ input_schema    │  │ input_data      ││
          │ output_schema   │  │ output_data     ││
          │ executor_config │  │ error_message   ││
          │ script_content* │  │ started_at      ││
          │ is_latest       │  │ completed_at    ││
          │ created_at      │  │ duration_ms     ││
          │ updated_at      │  │ caller_id       ││
          └─────────────────┘  │ trace_id        ││
                               │ created_at      ││
                               │ updated_at      ││
                               └─────────────────┘│
                                                  │
* = NEW field to be added                         │
```

## Entities

### Tool (Existing - Modified)

Primary entity representing a callable tool.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| name | string(100) | unique, indexed, not null | Tool identifier (snake_case, used in API) |
| display_name | string(200) | not null | Human-readable name |
| description | text | not null | Tool description for users and LLMs |
| status | enum | default: DRAFT | DRAFT, ACTIVE, DEPRECATED, DISABLED |
| category_id | UUID | FK → ToolCategory, nullable | Optional category reference |
| tags | string[] | JSONB, default: [] | Searchable tags |
| input_schema | JSON | JSONB, not null | JSON Schema for input parameters |
| output_schema | JSON | JSONB, default: {} | JSON Schema for expected output |
| **script_content** | text | **NEW**, nullable | Python script source code |
| executor_type | string | default: "python" | Executor type (python, http, shell, mcp) |
| executor_config | JSON | JSONB, default: {} | Executor-specific configuration |
| version | integer | default: 1, auto-increment | Current version number |
| created_at | datetime | auto, not null | Creation timestamp |
| updated_at | datetime | auto, not null | Last modification timestamp |

**Validation Rules**:
- `name` must be unique, lowercase alphanumeric with underscores
- `input_schema` must be valid JSON Schema (draft-07)
- `script_content` is required when `executor_type` is "python"
- `version` auto-increments on every update

**State Transitions**:
```
DRAFT → ACTIVE (activate)
ACTIVE → DISABLED (deactivate)
ACTIVE → DEPRECATED (deprecate)
DISABLED → ACTIVE (reactivate)
DEPRECATED → ACTIVE (undeprecate)
Any → (delete)
```

### ToolCategory (Existing)

Hierarchical category for organizing tools.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| name | string | unique, indexed, not null | Category name |
| description | text | nullable | Category description |
| parent_id | UUID | FK → ToolCategory (self), nullable | Parent category for hierarchy |
| created_at | datetime | auto, not null | Creation timestamp |
| updated_at | datetime | auto, not null | Last modification timestamp |

### ToolVersion (Existing - Modified)

Snapshot of tool configuration at a specific version.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| tool_id | UUID | FK → Tool, not null | Parent tool reference |
| version | string | not null | Version number as string |
| changelog | text | nullable | Description of changes |
| input_schema | JSON | JSONB | Snapshot of input_schema |
| output_schema | JSON | JSONB | Snapshot of output_schema |
| executor_config | JSON | JSONB | Snapshot of executor_config |
| **script_content** | text | **NEW**, nullable | Snapshot of script_content |
| is_latest | boolean | default: true | Whether this is the latest version |
| created_at | datetime | auto, not null | Creation timestamp |
| updated_at | datetime | auto, not null | Last modification timestamp |

### ToolExecution (Existing)

Record of a tool invocation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| tool_id | UUID | FK → Tool, not null | Executed tool reference |
| version | string | not null | Tool version at execution time |
| status | enum | default: PENDING | PENDING, RUNNING, SUCCESS, FAILED, TIMEOUT, CANCELLED |
| input_data | JSON | JSONB, not null | Input parameters provided |
| output_data | JSON | JSONB, nullable | Execution result (if success) |
| error_message | text | nullable | Error details (if failed) |
| started_at | datetime | nullable | Execution start time |
| completed_at | datetime | nullable | Execution completion time |
| duration_ms | integer | nullable | Execution duration in milliseconds |
| caller_id | string | nullable | Identifier of caller (LLM agent, user) |
| trace_id | string | nullable | Distributed tracing ID |
| created_at | datetime | auto, not null | Record creation timestamp |
| updated_at | datetime | auto, not null | Last modification timestamp |

**Execution Status Transitions**:
```
PENDING → RUNNING (started)
RUNNING → SUCCESS (completed successfully)
RUNNING → FAILED (error occurred)
RUNNING → TIMEOUT (exceeded 30s limit)
PENDING → CANCELLED (user cancelled)
RUNNING → CANCELLED (user cancelled)
```

## Database Migrations Required

### Migration 1: Add script_content to Tool

```sql
ALTER TABLE tools ADD COLUMN script_content TEXT;
```

### Migration 2: Add script_content to ToolVersion

```sql
ALTER TABLE tool_versions ADD COLUMN script_content TEXT;
```

### Migration 3: Change version from string to integer (Tool)

```sql
-- Note: Existing data uses "1.0.0" format, need to convert
ALTER TABLE tools ALTER COLUMN current_version TYPE INTEGER
  USING (split_part(current_version, '.', 1)::INTEGER);
ALTER TABLE tools RENAME COLUMN current_version TO version;
ALTER TABLE tools ALTER COLUMN version SET DEFAULT 1;
```

## Indexes

Existing indexes are sufficient. Consider adding:

```sql
-- For LLM query performance (filter by status)
CREATE INDEX idx_tools_status ON tools(status) WHERE status = 'ACTIVE';

-- For search performance
CREATE INDEX idx_tools_name_trgm ON tools USING gin(name gin_trgm_ops);
CREATE INDEX idx_tools_display_name_trgm ON tools USING gin(display_name gin_trgm_ops);
```

## JSON Schema Examples

### Tool Input Schema Example

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query"
    },
    "limit": {
      "type": "integer",
      "default": 10,
      "minimum": 1,
      "maximum": 100
    }
  },
  "required": ["query"]
}
```

### Tool Output Schema Example

```json
{
  "type": "object",
  "properties": {
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "url": {"type": "string"}
        }
      }
    },
    "total": {"type": "integer"}
  }
}
```
