# Implementation Plan: LLM Tool Management System

**Branch**: `001-llm-tool-management` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-llm-tool-management/spec.md`

## Summary

Build an LLM Tool Management System that enables users to create, configure, query, and execute Python-based tools through a web interface and LLM-compatible API endpoints. The system provides dual query formats (frontend-friendly and OpenAI function calling compatible) and executes Python scripts with full network access in an isolated environment with 30-second timeout.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLModel, SQLAlchemy, asyncpg, Celery, Redis, Pydantic
**Storage**: PostgreSQL (via asyncpg), Redis (caching & task queue)
**Testing**: pytest, pytest-asyncio, pytest-cov
**Target Platform**: Linux server (containerized)
**Project Type**: Web application (backend API + frontend TBD)
**Performance Goals**: 100 concurrent tool invocations, <1s API response time
**Constraints**: 30-second Python script timeout, no authentication required
**Scale/Scope**: Internal/development tool platform, expected <1000 tools

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution is not yet configured (template only). Proceeding with standard best practices:

- [x] **Testability**: All endpoints and services will have unit and integration tests
- [x] **Simplicity**: Leveraging existing codebase structure, no over-engineering
- [x] **Observability**: Logging tool invocations (FR-015), audit trail maintained

## Project Structure

### Documentation (this feature)

```text
specs/001-llm-tool-management/
├── plan.md              # This file
├── research.md          # Phase 0 output - technology decisions
├── data-model.md        # Phase 1 output - entity definitions
├── quickstart.md        # Phase 1 output - setup guide
├── contracts/           # Phase 1 output - API schemas
│   ├── openapi-llm.yaml # LLM-compatible tool query endpoints
│   └── openapi-tools.yaml # Tool management endpoints
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
src/aiops_tools/
├── models/
│   ├── base.py          # Existing - base model
│   └── tool.py          # Existing - Tool, ToolVersion, ToolExecution, ToolCategory
├── schemas/
│   ├── __init__.py      # Existing
│   ├── tool.py          # Existing - Pydantic schemas
│   └── llm.py           # NEW - LLM-compatible tool schemas (OpenAI format)
├── services/
│   ├── __init__.py      # Existing
│   ├── tool_executor.py # NEW - Python script execution service
│   └── tool_validator.py # NEW - Tool validation (syntax, schema)
├── api/v1/
│   ├── router.py        # Existing
│   └── endpoints/
│       ├── tools.py     # Existing - CRUD endpoints
│       ├── executions.py # Existing - Execution endpoints
│       └── llm.py       # NEW - LLM query endpoint
├── core/
│   ├── config.py        # Existing
│   ├── database.py      # Existing
│   └── redis.py         # Existing
├── tasks/
│   └── executor.py      # NEW - Celery task for script execution
└── main.py              # Existing

tests/
├── unit/
│   ├── test_tool_executor.py
│   └── test_tool_validator.py
├── integration/
│   ├── test_tools_api.py
│   └── test_llm_api.py
└── conftest.py

frontend/                # NEW - Web UI (TBD: React/Vue)
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: Web application structure selected. Backend already exists with FastAPI/PostgreSQL stack. Frontend will be added as a separate directory. The existing API provides most CRUD operations; this feature adds LLM-compatible endpoints and Python script execution.

## Complexity Tracking

No constitution violations identified. The implementation extends the existing codebase with minimal new components:

| Component | Justification |
|-----------|--------------|
| LLM endpoint | Core requirement for LLM integration (SC-003) |
| Script executor | Core requirement for tool invocation (FR-007) |
| Frontend | Core requirement for web interface (FR-001) |

## Gap Analysis

Comparing spec requirements against existing implementation:

| Requirement | Status | Gap |
|-------------|--------|-----|
| FR-001: Web interface | Missing | Need frontend |
| FR-002: Create tools | Partial | Missing Python script field in UI |
| FR-003: Validate tools | Missing | Need syntax validation service |
| FR-004: LLM query endpoint | Missing | Need new endpoint |
| FR-005: JSON schema in LLM response | Missing | Need schema transformation |
| FR-006: Tool invocation | Partial | Endpoint exists, execution not implemented |
| FR-007: Isolated execution | Missing | Need execution service |
| FR-008: Return results | Partial | Schema exists, executor missing |
| FR-009: Edit tools | Exists | PATCH endpoint available |
| FR-010: Delete tools | Exists | DELETE endpoint available |
| FR-011: Dual query formats | Missing | Need LLM format endpoint |
| FR-012: Pagination | Exists | List endpoint supports pagination |
| FR-013: Search | Exists | Search parameter in list endpoint |
| FR-014: 30s timeout | Missing | Config has 300s, need adjustment |
| FR-015: Audit logging | Partial | ToolExecution records exist |

## Implementation Priorities

Based on gap analysis and user story priorities:

1. **P1 - LLM Query Endpoint** (US-3): Add `/api/v1/llm/tools` endpoint returning OpenAI function calling format
2. **P1 - Python Script Field**: Add `script_content` field to Tool model and schemas
3. **P2 - Tool Executor Service**: Implement isolated Python script execution with 30s timeout
4. **P2 - Celery Task Integration**: Connect executor to Celery for async execution
5. **P3 - Frontend**: Build web UI for tool management
6. **P3 - Validation Service**: Add Python syntax validation on tool save
