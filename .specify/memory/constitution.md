<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0 (Initial constitution)
- Added principles:
  - I. URL Convention
  - II. POST-Only API
  - III. Tool Execution Safety
  - IV. LLM Compatibility
- Added sections:
  - Technology Stack
  - API Standards
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (Constitution Check section exists)
  - .specify/templates/spec-template.md ✅ (No constitution-specific updates needed)
- Follow-up TODOs: None
-->

# AIOps Tools Constitution

## Core Principles

### I. URL Convention

All business-related HTTP endpoints MUST follow this URL structure:

```
/api/tools/{version}/{path}
```

**Rules**:
- Base prefix: `/api/tools/`
- Version segment: `v1`, `v2`, etc.
- Business path: specific operation path

**Examples**:
- `/api/tools/v1/tools/list` - List tools
- `/api/tools/v1/tools/create` - Create tool
- `/api/tools/v1/categories/list` - List categories
- `/api/tools/v1/llm/list` - LLM tool list
- `/api/tools/v1/llm/invoke` - Invoke tool

**Exceptions** (not under `/api/tools/`):
- `/health` - Health check endpoint
- `/docs` - Swagger UI documentation
- `/redoc` - ReDoc documentation
- `/` - Root endpoint with API info

**Rationale**: Consistent URL structure improves API discoverability, versioning management, and client integration.

### II. POST-Only API

All business API endpoints MUST use HTTP POST method.

**Rules**:
- All CRUD operations use POST (not GET/PUT/DELETE)
- Request body MUST be JSON format
- Response body MUST be JSON format

**Examples**:
- `POST /api/tools/v1/list` with `{"page_size": 20}` (not GET with query params)
- `POST /api/tools/v1/delete` with `{"tool_id": "xxx"}` (not DELETE)

**Rationale**: POST-only simplifies client implementation, avoids URL length limits, enables complex query parameters, and provides consistent request/response patterns.

### III. Tool Execution Safety

Tool script execution MUST be safe and bounded.

**Rules**:
- Execution timeout: 30 seconds maximum
- Scripts run in isolated subprocess
- Input/output via JSON (stdin/stdout)
- All tools MUST have `main(input_data: dict) -> dict` entry point
- Return format: `{"success": bool, "data": {...}}` or `{"success": false, "error": {"code": "...", "message": "..."}}`

**Rationale**: Prevents runaway scripts, ensures predictable resource usage, and provides consistent error handling.

### IV. LLM Compatibility

Tool definitions MUST be compatible with OpenAI function calling format.

**Rules**:
- Tools expose `input_schema` following JSON Schema
- LLM endpoint returns tools in OpenAI function format
- Tool names use snake_case (e.g., `k8s_list_pods`)
- Descriptions are clear and actionable for LLM consumption

**Rationale**: Enables seamless integration with LLM agents and maintains compatibility with industry standards.

## Technology Stack

**Core Technologies**:
- Language: Python 3.11+
- Framework: FastAPI with async support
- ORM: SQLModel + SQLAlchemy
- Database: PostgreSQL 15+
- Cache/Queue: Redis 7+
- Task Queue: Celery (optional)

**Operations Tools Dependencies**:
- Kubernetes: `kubernetes` client library
- Database: `psycopg2` (PostgreSQL), `mysql-connector-python` (MySQL)
- AWS: `boto3`
- Java/JMX: Jolokia REST API

## API Standards

**Request/Response Format**:
- Content-Type: `application/json`
- All timestamps in ISO 8601 format
- UUIDs for entity identifiers

**Pagination**:
- Default page size: 20
- Maximum page size: 100
- Parameters: `page`, `page_size`

**Error Response Format**:
```json
{
  "detail": "Error message"
}
```

Or for validation errors:
```json
{
  "detail": {
    "validation_errors": [...]
  }
}
```

## Governance

- This constitution supersedes all other development practices
- Amendments require documentation and version increment
- All code reviews MUST verify compliance with these principles
- Use `CLAUDE.md` for runtime development guidance

**Version**: 1.0.0 | **Ratified**: 2025-12-27 | **Last Amended**: 2025-12-27
