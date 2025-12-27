"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from aiops_tools.api.v1.router import api_router
from aiops_tools.core.config import settings
from aiops_tools.core.database import init_db
from aiops_tools.core.errors import (
    APIError,
    ErrorCode,
    ErrorDetail,
    ErrorResponse,
)
from aiops_tools.core.redis import close_redis, get_redis


# API Description in Markdown format (matching Spring version style)
API_DESCRIPTION = """
AIOps Tools API 文档 - LLM 工具管理平台

## 功能模块

### 工具管理
- **分类管理**: 工具分类 CRUD、层级分类支持
- **工具管理**: 工具 CRUD、版本控制、状态管理
- **工具执行**: Python 脚本安全执行、30秒超时保护

### LLM 集成
- **工具发现**: OpenAI function calling 格式的工具列表
- **工具调用**: 统一的工具调用接口，支持 JSON 输入输出

## 认证方式

需要认证的接口需在请求头中携带 JWT Token：
```
Authorization: Bearer <token>
```

## API 规范

- 所有业务接口使用 POST 方法
- 请求/响应均为 JSON 格式
- URL 格式: `/api/tools/v1/{module}/{action}`
"""

# OpenAPI tags metadata for better documentation organization
tags_metadata = [
    {
        "name": "Categories",
        "description": "分类管理 - 创建和管理工具分类",
    },
    {
        "name": "Tools",
        "description": "工具管理 - 工具的增删改查、启用/禁用",
    },
    {
        "name": "LLM",
        "description": "LLM 接口 - OpenAI function calling 格式的工具发现和调用",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    await init_db()
    await get_redis()
    yield
    # Shutdown
    await close_redis()


def custom_openapi():
    """Generate custom OpenAPI schema matching Spring version protocol."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AIOps Tools API",
        version="1.0.0",
        description=API_DESCRIPTION,
        routes=app.routes,
        tags=tags_metadata,
    )

    # Add servers (matching Spring version)
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:6060",
            "description": "本地开发环境",
        },
        {
            "url": "https://api.aiops-tools.example.com",
            "description": "生产环境",
        },
    ]

    # Add contact info (matching Spring version)
    openapi_schema["info"]["contact"] = {
        "name": "AIOps Team",
        "email": "aiops@example.com",
    }

    # Add license (matching Spring version - Apache 2.0)
    openapi_schema["info"]["license"] = {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0",
    }

    # Add security scheme (Bearer JWT - matching Spring version)
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Authentication": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT 认证，请在登录接口获取 Token 后填入",
        }
    }

    # Add global security requirement
    openapi_schema["security"] = [{"Bearer Authentication": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(
    title="AIOps Tools API",
    version="1.0.0",
    description=API_DESCRIPTION,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=None,  # Disable default docs, we'll add custom routes
    redoc_url=None,  # Disable default redoc
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

# Override the openapi method with custom implementation
app.openapi = custom_openapi


# Swagger UI at /swagger-ui.html (matching Spring version URL)
@app.get("/swagger-ui.html", include_in_schema=False)
async def swagger_ui_html():
    """Swagger UI documentation (Spring-compatible URL)."""
    return get_swagger_ui_html(
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        title="AIOps Tools API - Swagger UI",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


# Also available at /docs for convenience
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Swagger UI documentation."""
    return get_swagger_ui_html(
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        title="AIOps Tools API - Swagger UI",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


# OpenAPI JSON at /v3/api-docs (matching Spring version URL)
@app.get("/v3/api-docs", include_in_schema=False)
async def openapi_json():
    """OpenAPI JSON specification (Spring-compatible URL)."""
    return app.openapi()


# OpenAPI YAML at /v3/api-docs.yaml (matching Spring version URL)
@app.get("/v3/api-docs.yaml", include_in_schema=False)
async def openapi_yaml():
    """OpenAPI YAML specification (Spring-compatible URL)."""
    import yaml
    return yaml.dump(app.openapi(), allow_unicode=True, default_flow_style=False)


# ReDoc at /redoc
@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    """ReDoc documentation."""
    return get_redoc_html(
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        title="AIOps Tools API - ReDoc",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers for consistent error responses
@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle custom APIError exceptions with structured response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTPException with consistent format."""
    # If it's already in our format, return as-is
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    # Convert to standard format
    error_detail = ErrorDetail(
        code=ErrorCode.INTERNAL_ERROR.value if exc.status_code >= 500 else "HTTP_ERROR",
        message=str(exc.detail) if exc.detail else "An error occurred",
    )
    response = ErrorResponse(error=error_detail)
    return JSONResponse(status_code=exc.status_code, content=response.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic/FastAPI validation errors with helpful messages."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        msg = error["msg"]
        error_type = error.get("type", "")

        # Map common error types to helpful suggestions
        suggestion = None
        if "string_pattern_mismatch" in error_type:
            suggestion = "Tool name must start with a lowercase letter and contain only lowercase letters, numbers, and underscores. Example: 'my_tool', 'k8s_list_pods'"
        elif "missing" in error_type:
            suggestion = f"The field '{field}' is required. Please provide a value."
        elif "uuid" in error_type.lower():
            suggestion = "Please provide a valid UUID in format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        elif "string_too_short" in error_type:
            suggestion = f"The field '{field}' is too short. Please provide a longer value."
        elif "string_too_long" in error_type:
            suggestion = f"The field '{field}' is too long. Please provide a shorter value."
        elif "json_invalid" in error_type:
            suggestion = "Please provide valid JSON in the request body."

        errors.append(
            ErrorDetail(
                code=ErrorCode.INVALID_FIELD.value,
                field=field,
                message=msg,
                suggestion=suggestion,
            )
        )

    response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.VALIDATION_ERROR.value,
            message=f"Request validation failed with {len(errors)} error(s)",
        ),
        errors=errors,
    )
    return JSONResponse(
        status_code=422,
        content=response.model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    error_detail = ErrorDetail(
        code=ErrorCode.INTERNAL_ERROR.value,
        message="An unexpected error occurred. Please try again later.",
        details={"error_type": type(exc).__name__} if settings.debug else None,
    )
    response = ErrorResponse(error=error_detail)
    return JSONResponse(
        status_code=500,
        content=response.model_dump(),
    )


# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {
        "name": "AIOps Tools API",
        "version": "1.0.0",
        "docs": "/docs",
        "swagger-ui": "/swagger-ui.html",
        "redoc": "/redoc",
        "openapi-json": "/v3/api-docs",
        "openapi-yaml": "/v3/api-docs.yaml",
        "openapi": f"{settings.api_v1_prefix}/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "aiops_tools.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
