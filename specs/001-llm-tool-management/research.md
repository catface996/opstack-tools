# Research: LLM Tool Management System

**Feature**: 001-llm-tool-management
**Date**: 2025-12-26

## Research Topics

### 1. LLM Tool Format (OpenAI Function Calling)

**Decision**: Use OpenAI function calling format as the standard for LLM-compatible tool queries

**Rationale**:
- OpenAI's function calling format is the de facto industry standard
- Compatible with Claude, GPT, and most other LLM providers
- Well-documented JSON Schema-based parameter definition
- Supports tool descriptions, parameter types, and required fields

**Format Structure**:
```json
{
  "type": "function",
  "function": {
    "name": "tool_name",
    "description": "Tool description",
    "parameters": {
      "type": "object",
      "properties": {
        "param1": {
          "type": "string",
          "description": "Parameter description"
        }
      },
      "required": ["param1"]
    }
  }
}
```

**Alternatives Considered**:
- MCP (Model Context Protocol): Newer, less widely adopted
- Custom format: Would require documentation and adapter code
- Anthropic Claude format: Similar to OpenAI, easily mapped

---

### 2. Python Script Execution Strategy

**Decision**: Use subprocess with RestrictedPython for sandboxed execution

**Rationale**:
- subprocess provides process isolation (separate memory space, timeout capability)
- 30-second timeout enforced via subprocess timeout parameter
- Full network access allowed per spec clarification
- Captures stdout/stderr for result and error reporting

**Implementation Approach**:
```python
import subprocess
import tempfile

def execute_script(script_content: str, params: dict, timeout: int = 30) -> dict:
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
        f.write(script_content.encode())
        f.flush()
        result = subprocess.run(
            ['python', f.name],
            input=json.dumps(params).encode(),
            capture_output=True,
            timeout=timeout
        )
    return {
        'stdout': result.stdout.decode(),
        'stderr': result.stderr.decode(),
        'returncode': result.returncode
    }
```

**Alternatives Considered**:
- exec() in same process: Security risk, no isolation
- Docker containers: Overhead too high for 100 concurrent executions
- AWS Lambda / serverless: Added complexity, external dependency
- RestrictedPython: Limited functionality, blocks many useful operations

---

### 3. Python Libraries for Tool Scripts

**Decision**: Provide a curated set of common libraries pre-installed

**Rationale**:
- Users expect common data processing libraries available
- Network access confirmed, so HTTP clients needed
- JSON handling is essential for LLM integration

**Pre-installed Libraries**:
- **Standard library**: json, os, sys, datetime, re, urllib, math
- **HTTP/Network**: requests, httpx
- **Data processing**: pandas (optional), numpy (optional)
- **JSON/Schema**: jsonschema

**Alternatives Considered**:
- Allow pip install in scripts: Security/performance concerns
- Docker with custom images: Overhead for simple scripts
- Virtual environments per tool: Resource intensive

---

### 4. Frontend Technology

**Decision**: React with TypeScript and Ant Design

**Rationale**:
- React is widely adopted with strong ecosystem
- TypeScript provides type safety for API integration
- Ant Design provides enterprise-ready form components (essential for tool configuration)
- Monaco Editor available for Python script editing with syntax highlighting

**Key Components Needed**:
- Tool list with search and pagination
- Tool detail/edit form with:
  - Monaco editor for Python script
  - JSON Schema builder for parameters
  - Status toggle
- Tool execution test panel

**Alternatives Considered**:
- Vue.js: Good option, but React has broader component ecosystem
- Plain JavaScript: Lacks type safety for complex schemas
- Server-rendered (Jinja2): Limited interactivity for code editor

---

### 5. Version Auto-increment Strategy

**Decision**: Simple integer increment stored in Tool.version field

**Rationale**:
- Spec clarified version auto-increments on each save
- Integer is simpler than semantic versioning for this use case
- ToolVersion table already exists for version history snapshots

**Implementation**:
```python
# On tool update
tool.version = tool.version + 1
# Create version snapshot
version = ToolVersion(
    tool_id=tool.id,
    version=str(tool.version),
    input_schema=tool.input_schema,
    executor_config=tool.executor_config
)
```

**Alternatives Considered**:
- Semantic versioning: Overkill for auto-increment
- UUID versions: Loses ordering information
- Timestamp versions: Less intuitive

---

### 6. Tool Input/Output Contract

**Decision**: JSON in, JSON out via stdin/stdout

**Rationale**:
- Simple, universal interface
- Easy to test and debug
- LLM can easily parse JSON responses
- Consistent with existing executor_config pattern

**Script Contract**:
```python
# Tool script template
import json
import sys

# Read input from stdin
input_data = json.load(sys.stdin)

# Process
result = {"output": "value"}

# Write output to stdout
print(json.dumps(result))
```

**Alternatives Considered**:
- Function return values: Requires code injection/modification
- File-based I/O: More complex, harder to stream
- Custom protocol: Unnecessary complexity

---

## Summary of Decisions

| Topic | Decision | Key Benefit |
|-------|----------|-------------|
| LLM Format | OpenAI function calling | Industry standard, wide compatibility |
| Execution | subprocess + timeout | Process isolation, timeout support |
| Libraries | Curated pre-installed set | Balance of capability and security |
| Frontend | React + TypeScript + Ant Design | Rich form/editor components |
| Versioning | Integer auto-increment | Simple, matches spec |
| I/O Contract | JSON stdin/stdout | Universal, LLM-friendly |
