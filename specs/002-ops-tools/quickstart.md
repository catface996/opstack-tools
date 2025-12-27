# Quickstart: Operations Tools Collection

**Feature**: 002-ops-tools
**Date**: 2025-12-27

## Overview

This guide explains how to create and test operations tools in the AIOps Tools platform.

## Prerequisites

1. **Running API Server**
   ```bash
   cd /path/to/op-stack-tools
   uv run uvicorn aiops_tools.main:app --reload
   ```

2. **Database with migrations applied**
   ```bash
   uv run alembic upgrade head
   ```

3. **Required Python packages** (for tool scripts)
   ```bash
   uv add kubernetes psycopg2-binary mysql-connector-python boto3
   ```

## Creating a Tool

### Step 1: Create a Category

```bash
curl -X POST http://localhost:8000/api/v1/tools/categories/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "kubernetes",
    "description": "Kubernetes cluster operations"
  }'
```

### Step 2: Create a Tool

```bash
curl -X POST http://localhost:8000/api/v1/tools/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "k8s_list_namespaces",
    "display_name": "List Kubernetes Namespaces",
    "description": "List all namespaces in a Kubernetes cluster",
    "category_id": "<category-uuid>",
    "tags": ["kubernetes", "namespaces"],
    "input_schema": {
      "type": "object",
      "properties": {
        "kubeconfig": {
          "type": "string",
          "description": "Path to kubeconfig file"
        }
      }
    },
    "script_content": "from kubernetes import client, config\n\ndef main(input_data):\n    try:\n        if kubeconfig := input_data.get(\"kubeconfig\"):\n            config.load_kube_config(kubeconfig)\n        else:\n            config.load_incluster_config()\n        v1 = client.CoreV1Api()\n        namespaces = v1.list_namespace()\n        return {\n            \"success\": True,\n            \"data\": {\n                \"namespaces\": [\n                    {\"name\": ns.metadata.name, \"status\": ns.status.phase}\n                    for ns in namespaces.items\n                ]\n            }\n        }\n    except Exception as e:\n        return {\"success\": False, \"error\": {\"code\": \"K8S_ERROR\", \"message\": str(e)}}"
  }'
```

### Step 3: Activate the Tool

```bash
curl -X POST http://localhost:8000/api/v1/tools/activate \
  -H "Content-Type: application/json" \
  -d '{"tool_id": "<tool-uuid>"}'
```

### Step 4: Invoke the Tool

```bash
curl -X POST http://localhost:8000/api/v1/llm/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "<tool-uuid>",
    "input_data": {
      "kubeconfig": "~/.kube/config"
    }
  }'
```

## Tool Script Pattern

All tool scripts must define a `main(input_data)` function:

```python
def main(input_data: dict) -> dict:
    """Execute the tool.

    Args:
        input_data: Dictionary with input parameters from JSON schema

    Returns:
        Dictionary with either:
        - {"success": True, "data": {...}} on success
        - {"success": False, "error": {"code": "...", "message": "..."}} on failure
    """
    try:
        # 1. Extract parameters
        param = input_data.get("param_name", "default")

        # 2. Execute operation
        result = do_something(param)

        # 3. Return structured result
        return {
            "success": True,
            "data": result
        }
    except SomeException as e:
        return {
            "success": False,
            "error": {
                "code": "ERROR_CODE",
                "message": str(e),
                "details": {"param": param}
            }
        }
```

## Testing Tools

### Unit Testing

```python
# tests/unit/tools/test_k8s_tools.py
import pytest
from unittest.mock import patch, MagicMock

def test_k8s_list_namespaces():
    """Test namespace listing."""
    # Import the tool script
    from aiops_tools.tools.k8s.list_namespaces import main

    # Mock the kubernetes client
    with patch('kubernetes.client.CoreV1Api') as mock_api:
        mock_ns = MagicMock()
        mock_ns.metadata.name = "default"
        mock_ns.status.phase = "Active"
        mock_api.return_value.list_namespace.return_value.items = [mock_ns]

        result = main({"kubeconfig": "/fake/path"})

        assert result["success"] is True
        assert len(result["data"]["namespaces"]) == 1
        assert result["data"]["namespaces"][0]["name"] == "default"
```

### Integration Testing

```python
# tests/integration/test_tool_execution.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_invoke_tool(client: AsyncClient, created_tool_id: str):
    """Test tool invocation through API."""
    response = await client.post(
        "/api/v1/llm/tools/invoke",
        json={
            "tool_id": created_tool_id,
            "input_data": {"namespace": "default"}
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] in ["success", "failed"]
```

## Error Handling

### Standard Error Codes

| Category | Code | Description |
|----------|------|-------------|
| K8S | `K8S_CONNECTION_ERROR` | Cannot connect to cluster |
| K8S | `K8S_AUTH_ERROR` | Authentication failed |
| K8S | `K8S_NOT_FOUND` | Resource not found |
| DB | `DB_CONNECTION_ERROR` | Cannot connect to database |
| DB | `DB_QUERY_ERROR` | Query execution failed |
| DB | `DB_REJECTED` | Non-SELECT query rejected |
| Java | `JMX_CONNECTION_ERROR` | Cannot connect to JMX |
| AWS | `AWS_AUTH_ERROR` | Invalid credentials |
| AWS | `AWS_ACCESS_DENIED` | Insufficient permissions |

### Error Response Example

```json
{
    "success": false,
    "error": {
        "code": "K8S_CONNECTION_ERROR",
        "message": "Failed to connect to Kubernetes cluster",
        "details": {
            "host": "https://k8s.example.com",
            "timeout": 30
        }
    }
}
```

## LLM Integration

Tools are exposed to LLM agents via:

1. **List Tools**: `POST /api/v1/llm/tools/list`
   - Returns tool names, descriptions, and input schemas
   - LLM uses this to understand available capabilities

2. **Invoke Tool**: `POST /api/v1/llm/tools/invoke`
   - LLM calls this with tool_id and input_data
   - Returns execution result

### Example LLM Workflow

```
User: "What pods are running in the production namespace?"

LLM:
1. Calls /llm/tools/list to find k8s_list_pods tool
2. Calls /llm/tools/invoke with:
   {"tool_id": "...", "input_data": {"namespace": "production"}}
3. Formats response for user
```

## Deployment Checklist

- [ ] Add required dependencies to `pyproject.toml`
- [ ] Create tool categories via API or seed script
- [ ] Create and activate all tools
- [ ] Configure credentials/access for target systems
- [ ] Test each tool category in target environment
- [ ] Monitor tool executions via execution records
