<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0
- Added principles:
  - V. Pagination Standards
  - VI. Response Format
- Updated sections:
  - API Standards (pagination request/response format)
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (Constitution Check section exists)
  - .specify/templates/spec-template.md ✅ (No constitution-specific updates needed)
- Follow-up TODOs:
  - Update existing list endpoints to use new pagination format
  - Update response format to include code/message/success wrapper
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

### V. Pagination Standards

All list endpoints MUST use standardized pagination request and response formats.

**Pagination Request Format**:
```json
{
  "page": 1,
  "size": 20,
  "tenantId": null,
  "traceId": null,
  "userId": null
}
```

**Rules**:
- `page`: Page number, starts from 1, default 1, minimum 1
- `size`: Page size, default 20, range 1-100
- `tenantId`, `traceId`, `userId`: Gateway-injected fields (hidden from user input)

**Pagination Response Format**:
```json
{
  "code": 0,
  "message": "success",
  "success": true,
  "data": {
    "content": [],
    "page": 1,
    "size": 10,
    "totalElements": 100,
    "totalPages": 10,
    "first": true,
    "last": false
  }
}
```

**Response Fields**:
- `content`: Data list for current page
- `page`: Current page number (starts from 1)
- `size`: Page size
- `totalElements`: Total record count
- `totalPages`: Total page count
- `first`: Whether this is the first page
- `last`: Whether this is the last page

**Rationale**: Standardized pagination format ensures consistent client implementation and predictable API behavior across all list endpoints.

### VI. Response Format

All API responses MUST follow a standardized wrapper format.

**Success Response**:
```json
{
  "code": 0,
  "message": "success",
  "success": true,
  "data": { ... }
}
```

**Error Response**:
```json
{
  "code": <error_code>,
  "message": "<error_message>",
  "success": false,
  "data": null,
  "error": {
    "code": "<ERROR_CODE>",
    "field": "<field_name>",
    "message": "<detailed_message>",
    "suggestion": "<how_to_fix>"
  }
}
```

**Rules**:
- `code`: 0 for success, non-zero for errors
- `message`: Human-readable message
- `success`: Boolean indicating success/failure
- `data`: Response payload (null on error)
- `error`: Detailed error information (only on error)

**Rationale**: Consistent response format enables standardized error handling and simplifies client-side parsing.

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

**Pagination** (see Principle V for detailed format):
- Default page size: 20
- Maximum page size: 100
- Request parameters: `page` (from 1), `size`
- Response includes: `content`, `page`, `size`, `totalElements`, `totalPages`, `first`, `last`

**Response Wrapper** (see Principle VI for detailed format):
- All responses wrapped with `code`, `message`, `success`, `data`
- Error responses include additional `error` object with details

## Governance

- This constitution supersedes all other development practices
- Amendments require documentation and version increment
- All code reviews MUST verify compliance with these principles
- Use `CLAUDE.md` for runtime development guidance

**Version**: 1.0.0 | **Ratified**: 2025-12-27 | **Last Amended**: 2025-12-27
