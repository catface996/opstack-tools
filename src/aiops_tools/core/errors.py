"""Standardized error handling for AIOps Tools API."""

from enum import Enum
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorCode(str, Enum):
    """Standard error codes for the API."""

    # Validation errors (422)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FIELD = "INVALID_FIELD"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    SCRIPT_SYNTAX_ERROR = "SCRIPT_SYNTAX_ERROR"
    INVALID_JSON_SCHEMA = "INVALID_JSON_SCHEMA"

    # Business logic errors (400)
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    INVALID_STATE = "INVALID_STATE"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"

    # Not found errors (404)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    CATEGORY_NOT_FOUND = "CATEGORY_NOT_FOUND"

    # Execution errors (500)
    EXECUTION_FAILED = "EXECUTION_FAILED"
    EXECUTION_TIMEOUT = "EXECUTION_TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorDetail(BaseModel):
    """Detailed error information for a single error."""

    code: str
    field: str | None = None
    message: str
    suggestion: str | None = None
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """Standardized error response format."""

    success: bool = False
    error: ErrorDetail
    errors: list[ErrorDetail] | None = None  # For multiple validation errors


class APIError(HTTPException):
    """Custom API exception with structured error details."""

    def __init__(
        self,
        status_code: int,
        code: ErrorCode | str,
        message: str,
        field: str | None = None,
        suggestion: str | None = None,
        details: dict[str, Any] | None = None,
        errors: list[ErrorDetail] | None = None,
    ):
        self.code = code if isinstance(code, str) else code.value
        self.field = field
        self.message = message
        self.suggestion = suggestion
        self.details = details
        self.errors = errors

        error_detail = ErrorDetail(
            code=self.code,
            field=field,
            message=message,
            suggestion=suggestion,
            details=details,
        )

        response = ErrorResponse(
            error=error_detail,
            errors=errors,
        )

        super().__init__(status_code=status_code, detail=response.model_dump())


class ValidationError(APIError):
    """Validation error with helpful suggestions."""

    def __init__(
        self,
        field: str,
        message: str,
        suggestion: str | None = None,
        details: dict[str, Any] | None = None,
        code: ErrorCode = ErrorCode.VALIDATION_ERROR,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=code,
            field=field,
            message=message,
            suggestion=suggestion,
            details=details,
        )


class MultiValidationError(APIError):
    """Multiple validation errors."""

    def __init__(self, errors: list[ErrorDetail]):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=ErrorCode.VALIDATION_ERROR,
            message=f"Validation failed with {len(errors)} error(s)",
            errors=errors,
        )


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(
        self,
        resource: str,
        identifier: str | None = None,
        suggestion: str | None = None,
    ):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with ID '{identifier}' not found"

        code_map = {
            "Tool": ErrorCode.TOOL_NOT_FOUND,
            "Category": ErrorCode.CATEGORY_NOT_FOUND,
        }

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code=code_map.get(resource, ErrorCode.RESOURCE_NOT_FOUND),
            message=message,
            suggestion=suggestion or f"Please check the {resource.lower()} ID and try again",
        )


class DuplicateError(APIError):
    """Duplicate resource error."""

    def __init__(
        self,
        resource: str,
        field: str,
        value: str,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.DUPLICATE_RESOURCE,
            field=field,
            message=f"{resource} with {field}='{value}' already exists",
            suggestion=f"Please use a different {field} value",
        )


# Error message templates for common validation scenarios
ERROR_MESSAGES = {
    "script_content_required": {
        "code": ErrorCode.MISSING_REQUIRED_FIELD,
        "message": "Script content is required when executor_type is 'python'",
        "suggestion": "Please provide a valid Python script in the 'script_content' field. "
        "The script must define a 'main(input_data: dict) -> dict' function.",
        "example": 'def main(input_data):\n    return {"success": True, "data": {}}',
    },
    "script_content_empty": {
        "code": ErrorCode.INVALID_FIELD,
        "message": "Script content cannot be empty",
        "suggestion": "Please provide a non-empty Python script with a 'main' function.",
    },
    "script_syntax_error": {
        "code": ErrorCode.SCRIPT_SYNTAX_ERROR,
        "message": "Python script contains syntax errors",
        "suggestion": "Please check the Python syntax and ensure the script is valid.",
    },
    "invalid_json_schema": {
        "code": ErrorCode.INVALID_JSON_SCHEMA,
        "message": "Invalid JSON Schema format",
        "suggestion": "Please ensure the schema follows JSON Schema Draft 7 specification. "
        "See https://json-schema.org/ for reference.",
    },
    "invalid_tool_name": {
        "code": ErrorCode.INVALID_FORMAT,
        "message": "Tool name must start with a lowercase letter and contain only lowercase letters, numbers, and underscores",
        "suggestion": "Example valid names: 'my_tool', 'k8s_list_pods', 'db_query'",
    },
    "tool_name_too_long": {
        "code": ErrorCode.INVALID_FIELD,
        "message": "Tool name exceeds maximum length of 100 characters",
        "suggestion": "Please use a shorter, more concise tool name.",
    },
    "display_name_required": {
        "code": ErrorCode.MISSING_REQUIRED_FIELD,
        "message": "Display name is required",
        "suggestion": "Please provide a human-readable display name for the tool.",
    },
    "description_required": {
        "code": ErrorCode.MISSING_REQUIRED_FIELD,
        "message": "Description is required",
        "suggestion": "Please provide a description that explains what the tool does. "
        "This helps LLM agents understand when to use this tool.",
    },
    "invalid_uuid": {
        "code": ErrorCode.INVALID_FORMAT,
        "message": "Invalid UUID format",
        "suggestion": "Please provide a valid UUID in the format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    },
    "category_not_found": {
        "code": ErrorCode.CATEGORY_NOT_FOUND,
        "message": "The specified category does not exist",
        "suggestion": "Please use POST /api/tools/v1/categories/list to see available categories, "
        "or create a new category first.",
    },
}


def get_error_template(key: str) -> dict:
    """Get error message template by key."""
    return ERROR_MESSAGES.get(key, {})


async def api_exception_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle APIError exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


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


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle Pydantic validation errors."""
    from pydantic import ValidationError as PydanticValidationError

    if isinstance(exc, PydanticValidationError):
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            msg = error["msg"]

            # Map common Pydantic errors to helpful messages
            suggestion = None
            if "string_pattern_mismatch" in error["type"]:
                template = get_error_template("invalid_tool_name")
                suggestion = template.get("suggestion")
            elif "missing" in error["type"]:
                suggestion = f"The field '{field}' is required. Please provide a value."
            elif "uuid" in error["type"].lower():
                template = get_error_template("invalid_uuid")
                suggestion = template.get("suggestion")

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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.model_dump(),
        )

    # Fallback for other exceptions
    error_detail = ErrorDetail(
        code=ErrorCode.INTERNAL_ERROR.value,
        message=str(exc),
    )
    response = ErrorResponse(error=error_detail)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(),
    )
