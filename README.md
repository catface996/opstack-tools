# AIOps Tools

LLM Tool Management System - Create, manage, and execute tools for LLM function calling.

## Features

- **Tool Management**: Create, update, and delete tools via web interface
- **LLM-Compatible API**: OpenAI function calling format for tool discovery and invocation
- **Python Script Execution**: Execute Python scripts as tools with 30-second timeout
- **Version Control**: Auto-increment version on each tool update

## Quick Start

### Using Docker Compose

```bash
# Start all services (API, PostgreSQL, Redis, Celery)
docker-compose up -d

# View logs
docker-compose logs -f api
```

### Access Points

- **API**: http://localhost:6060
- **Swagger UI**: http://localhost:6060/docs
- **ReDoc**: http://localhost:6060/redoc
- **Frontend**: http://localhost:3000 (when running separately)

### API Endpoints

#### Tool Management
- `GET /api/v1/tools` - List tools with pagination
- `POST /api/v1/tools` - Create new tool
- `GET /api/v1/tools/{id}` - Get tool details
- `PATCH /api/v1/tools/{id}` - Update tool
- `DELETE /api/v1/tools/{id}` - Delete tool

#### LLM API (OpenAI Function Calling Format)
- `GET /api/v1/llm/tools` - List tools in LLM format
- `GET /api/v1/llm/tools/{name}` - Get single tool
- `POST /api/v1/llm/tools/{name}/invoke` - Execute tool

## Development

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Node.js 18+ (for frontend)

### Local Development

```bash
# Install Python dependencies
pip install -e .

# Start backend (requires PostgreSQL and Redis)
uvicorn aiops_tools.main:app --host 0.0.0.0 --port 6060 --reload

# Start frontend
cd frontend
npm install
npm run dev
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 6060 | API server port |
| `DATABASE_URL` | postgresql+asyncpg://... | PostgreSQL connection URL |
| `REDIS_URL` | redis://localhost:6379/0 | Redis connection URL |
| `DEBUG` | false | Enable debug mode |

## License

MIT
