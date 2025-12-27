# Implementation Plan: Operations Tools Collection

**Branch**: `002-ops-tools` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-ops-tools/spec.md`

## Summary

Add a collection of 16+ pre-built operational tools across four categories (K8S, Database, Java, AWS) to enable LLM agents to perform common DevOps and SRE tasks. Tools follow the existing tool execution framework using Python scripts with JSON input/output via stdin/stdout.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, SQLModel, kubernetes (k8s client), psycopg2/mysql-connector (DB), boto3 (AWS)
**Storage**: PostgreSQL (existing), tool definitions stored in `tools` table
**Testing**: pytest, pytest-asyncio
**Target Platform**: Linux server (Docker)
**Project Type**: Single backend API (existing)
**Performance Goals**: Tool execution completes within 30 seconds for standard operations
**Constraints**: Query timeout configurable, result row limits to prevent memory issues
**Scale/Scope**: 16+ tools across 4 categories, serving multiple LLM agent instances

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution is not yet customized (contains template placeholders). Proceeding with standard best practices:

- [x] **Single responsibility**: Each tool performs one specific operation
- [x] **Testability**: Tools are independently testable via the execute endpoint
- [x] **Simplicity**: Tools use existing framework, no new infrastructure required
- [x] **Observability**: Tool executions are logged with timing and trace IDs

## Project Structure

### Documentation (this feature)

```text
specs/002-ops-tools/
├── plan.md              # This file
├── research.md          # Phase 0 output - technology decisions
├── data-model.md        # Phase 1 output - no new models needed
├── quickstart.md        # Phase 1 output - tool creation guide
├── contracts/           # Phase 1 output - tool schemas
│   ├── k8s-tools.yaml
│   ├── db-tools.yaml
│   ├── java-tools.yaml
│   └── aws-tools.yaml
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/aiops_tools/
├── tools/                    # NEW: Pre-built tool scripts
│   ├── __init__.py
│   ├── k8s/
│   │   ├── __init__.py
│   │   ├── list_pods.py
│   │   ├── get_logs.py
│   │   ├── describe_pod.py
│   │   ├── restart_deployment.py
│   │   ├── list_namespaces.py
│   │   └── get_deployment_status.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── execute_query.py
│   │   ├── list_tables.py
│   │   ├── describe_table.py
│   │   └── query_validator.py
│   ├── java/
│   │   ├── __init__.py
│   │   ├── get_heap_usage.py
│   │   ├── get_thread_dump.py
│   │   ├── get_gc_stats.py
│   │   └── list_mbeans.py
│   └── aws/
│       ├── __init__.py
│       ├── list_ec2_instances.py
│       ├── describe_instance.py
│       ├── list_s3_buckets.py
│       ├── list_s3_objects.py
│       ├── describe_rds.py
│       └── get_cloudwatch_metrics.py
├── services/
│   └── tool_loader.py        # NEW: Load and register pre-built tools
└── api/v1/endpoints/
    └── tools.py              # EXISTING: Already has CRUD + invoke

tests/
├── unit/
│   └── tools/
│       ├── test_k8s_tools.py
│       ├── test_db_tools.py
│       ├── test_java_tools.py
│       └── test_aws_tools.py
└── integration/
    └── test_tool_execution.py
```

**Structure Decision**: Extend existing single-project structure. New tool scripts are added under `src/aiops_tools/tools/` organized by category. No new API endpoints needed - tools use existing CRUD and invoke endpoints.

## Complexity Tracking

No constitution violations. The implementation:
- Uses existing tool execution framework
- Adds no new database models (tools stored in existing `tools` table)
- Requires no new API endpoints
- Follows existing patterns for tool definition and execution
