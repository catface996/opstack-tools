# Quickstart: LLM Tool Management System

**Feature**: 001-llm-tool-management
**Date**: 2025-12-26

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Node.js 18+ (for frontend)

## Backend Setup

### 1. Clone and Install Dependencies

```bash
cd op-stack-tools

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Install dependencies
pip install -e ".[dev]"
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# Application
APP_NAME=AIOps Tools
APP_VERSION=0.1.0
DEBUG=true
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/aiops_tools

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Tool Execution
TOOL_EXECUTION_TIMEOUT=30
MAX_CONCURRENT_EXECUTIONS=10
```

### 3. Start Services

```bash
# Start PostgreSQL and Redis (using Docker)
docker run -d --name postgres -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=aiops_tools \
  postgres:14

docker run -d --name redis -p 6379:6379 redis:6

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn aiops_tools.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker
celery -A aiops_tools.tasks worker --loglevel=info
```

### 4. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/api/v1/docs
```

## Quick Usage Guide

### Create a Tool

```bash
curl -X POST http://localhost:8000/api/v1/tools \
  -H "Content-Type: application/json" \
  -d '{
    "name": "hello_world",
    "display_name": "Hello World",
    "description": "A simple greeting tool",
    "input_schema": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "Name to greet"
        }
      },
      "required": ["name"]
    },
    "script_content": "import json\nimport sys\n\ndata = json.load(sys.stdin)\nprint(json.dumps({\"message\": f\"Hello, {data[\"name\"]}!\"}))"
  }'
```

### Activate the Tool

```bash
curl -X POST http://localhost:8000/api/v1/tools/{tool_id}/activate
```

### Query Tools for LLM

```bash
# Get all active tools in OpenAI function calling format
curl http://localhost:8000/api/v1/llm/tools
```

Response:
```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "hello_world",
        "description": "A simple greeting tool",
        "parameters": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string",
              "description": "Name to greet"
            }
          },
          "required": ["name"]
        }
      }
    }
  ]
}
```

### Invoke a Tool

```bash
# Via LLM endpoint (synchronous, waits for result)
curl -X POST http://localhost:8000/api/v1/llm/tools/hello_world/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {"name": "World"},
    "caller_id": "test-agent"
  }'
```

Response:
```json
{
  "success": true,
  "result": {
    "message": "Hello, World!"
  },
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "duration_ms": 123
}
```

## Tool Script Template

Python scripts should follow this pattern:

```python
import json
import sys

# Read input from stdin
input_data = json.load(sys.stdin)

# Your logic here
result = {
    "output": "value"
}

# Write output to stdout (must be valid JSON)
print(json.dumps(result))
```

### Available Libraries

Scripts have access to:
- Standard library: json, os, sys, datetime, re, urllib, math
- HTTP: requests, httpx
- Data processing: json, csv
- Schema validation: jsonschema

### Error Handling

```python
import json
import sys

try:
    input_data = json.load(sys.stdin)
    # Process...
    result = {"success": True, "data": "..."}
    print(json.dumps(result))
except Exception as e:
    # Errors to stderr are captured as error_message
    print(json.dumps({"error": str(e)}), file=sys.stderr)
    sys.exit(1)
```

## Frontend Setup (Coming Soon)

```bash
cd frontend
npm install
npm run dev
```

Access at http://localhost:3000

## Development

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=aiops_tools

# Specific test file
pytest tests/integration/test_llm_api.py -v
```

### Code Quality

```bash
# Lint
ruff check src/

# Type check
mypy src/

# Format
ruff format src/
```

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tools` | List tools (paginated) |
| POST | `/api/v1/tools` | Create tool |
| GET | `/api/v1/tools/{id}` | Get tool |
| PATCH | `/api/v1/tools/{id}` | Update tool |
| DELETE | `/api/v1/tools/{id}` | Delete tool |
| POST | `/api/v1/tools/{id}/activate` | Activate tool |
| POST | `/api/v1/tools/{id}/deactivate` | Deactivate tool |
| POST | `/api/v1/tools/{id}/execute` | Execute tool (async) |
| GET | `/api/v1/llm/tools` | List tools (LLM format) |
| GET | `/api/v1/llm/tools/{name}` | Get tool (LLM format) |
| POST | `/api/v1/llm/tools/{name}/invoke` | Invoke tool (sync) |

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection
psql -h localhost -U postgres -d aiops_tools
```

### Celery Not Processing Tasks

```bash
# Check Redis is running
docker ps | grep redis

# Check Celery worker logs
celery -A aiops_tools.tasks worker --loglevel=debug
```

### Tool Execution Timeout

- Default timeout is 30 seconds
- Check script for infinite loops or long-running operations
- Consider optimizing or breaking into smaller tools
