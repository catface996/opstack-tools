"""Tool validation service with detailed error messages."""

import ast
import re
from dataclasses import dataclass

import jsonschema

from aiops_tools.core.errors import ErrorCode, ErrorDetail, get_error_template


@dataclass
class ValidationResult:
    """Result of a validation check."""

    valid: bool
    errors: list[ErrorDetail]


def validate_python_syntax(script_content: str) -> ValidationResult:
    """Validate Python script syntax.

    Args:
        script_content: Python source code to validate.

    Returns:
        ValidationResult with valid=True if syntax is correct,
        or valid=False with detailed error information.
    """
    if not script_content or not script_content.strip():
        template = get_error_template("script_content_empty")
        return ValidationResult(
            valid=False,
            errors=[
                ErrorDetail(
                    code=template.get("code", ErrorCode.INVALID_FIELD).value,
                    field="script_content",
                    message=template.get("message", "Script content is empty"),
                    suggestion=template.get("suggestion"),
                )
            ],
        )

    try:
        tree = ast.parse(script_content)

        # Check if main function exists
        has_main = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                has_main = True
                break

        if not has_main:
            return ValidationResult(
                valid=False,
                errors=[
                    ErrorDetail(
                        code=ErrorCode.VALIDATION_ERROR.value,
                        field="script_content",
                        message="Script must define a 'main' function",
                        suggestion="Add a 'main(input_data: dict) -> dict' function to your script. "
                        "This function will be called when the tool is executed.",
                        details={
                            "example": 'def main(input_data):\n    # Your code here\n    return {"success": True, "data": {}}'
                        },
                    )
                ],
            )

        return ValidationResult(valid=True, errors=[])

    except SyntaxError as e:
        template = get_error_template("script_syntax_error")
        # Build detailed syntax error message
        error_location = f"line {e.lineno}" if e.lineno else "unknown location"
        if e.offset:
            error_location += f", column {e.offset}"

        error_context = ""
        if e.text:
            error_context = f"\n  Code: {e.text.strip()}"
            if e.offset:
                error_context += f"\n  {' ' * (e.offset + 7)}^"

        return ValidationResult(
            valid=False,
            errors=[
                ErrorDetail(
                    code=template.get("code", ErrorCode.SCRIPT_SYNTAX_ERROR).value,
                    field="script_content",
                    message=f"Python syntax error at {error_location}: {e.msg}{error_context}",
                    suggestion=template.get("suggestion"),
                    details={
                        "line": e.lineno,
                        "column": e.offset,
                        "error_type": "SyntaxError",
                        "error_message": e.msg,
                    },
                )
            ],
        )


def validate_json_schema(schema: dict, field_name: str = "input_schema") -> ValidationResult:
    """Validate that a dictionary is a valid JSON Schema.

    Args:
        schema: Dictionary to validate as JSON Schema.
        field_name: Name of the field being validated (for error messages).

    Returns:
        ValidationResult with valid=True if schema is valid,
        or valid=False with detailed error information.
    """
    if not schema:
        # Empty schema is valid (no parameters)
        return ValidationResult(valid=True, errors=[])

    try:
        # Validate the schema itself by checking it against the meta-schema
        jsonschema.Draft7Validator.check_schema(schema)
        return ValidationResult(valid=True, errors=[])
    except jsonschema.SchemaError as e:
        template = get_error_template("invalid_json_schema")

        # Build path to the error location in the schema
        error_path = " -> ".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"

        return ValidationResult(
            valid=False,
            errors=[
                ErrorDetail(
                    code=template.get("code", ErrorCode.INVALID_JSON_SCHEMA).value,
                    field=field_name,
                    message=f"Invalid JSON Schema at '{error_path}': {e.message}",
                    suggestion=template.get("suggestion"),
                    details={
                        "schema_path": list(e.absolute_path) if e.absolute_path else [],
                        "validator": e.validator,
                        "validator_value": str(e.validator_value)[:100],  # Truncate for safety
                    },
                )
            ],
        )


def validate_input_against_schema(
    input_data: dict, input_schema: dict
) -> ValidationResult:
    """Validate input data against a JSON Schema.

    Args:
        input_data: Input data to validate.
        input_schema: JSON Schema to validate against.

    Returns:
        ValidationResult with valid=True if input matches schema,
        or valid=False with detailed error information.
    """
    if not input_schema:
        # No schema means any input is valid
        return ValidationResult(valid=True, errors=[])

    try:
        jsonschema.validate(instance=input_data, schema=input_schema)
        return ValidationResult(valid=True, errors=[])
    except jsonschema.ValidationError as e:
        # Build path to the error location
        error_path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"

        return ValidationResult(
            valid=False,
            errors=[
                ErrorDetail(
                    code=ErrorCode.VALIDATION_ERROR.value,
                    field=f"input_data.{error_path}" if error_path != "root" else "input_data",
                    message=e.message,
                    suggestion=f"Check the value at '{error_path}' in your input data.",
                    details={
                        "path": list(e.absolute_path) if e.absolute_path else [],
                        "validator": e.validator,
                        "expected": str(e.validator_value)[:100] if e.validator_value else None,
                        "actual": str(e.instance)[:100] if e.instance else None,
                    },
                )
            ],
        )


def validate_tool_name(name: str) -> ValidationResult:
    """Validate tool name format.

    Args:
        name: Tool name to validate.

    Returns:
        ValidationResult with validation status and errors if any.
    """
    errors = []

    if not name:
        errors.append(
            ErrorDetail(
                code=ErrorCode.MISSING_REQUIRED_FIELD.value,
                field="name",
                message="Tool name is required",
                suggestion="Please provide a unique tool name.",
            )
        )
    elif len(name) > 100:
        template = get_error_template("tool_name_too_long")
        errors.append(
            ErrorDetail(
                code=template.get("code", ErrorCode.INVALID_FIELD).value,
                field="name",
                message=template.get("message", f"Tool name is too long ({len(name)} characters)"),
                suggestion=template.get("suggestion"),
                details={"current_length": len(name), "max_length": 100},
            )
        )
    elif not re.match(r"^[a-z][a-z0-9_]*$", name):
        template = get_error_template("invalid_tool_name")
        errors.append(
            ErrorDetail(
                code=template.get("code", ErrorCode.INVALID_FORMAT).value,
                field="name",
                message=template.get("message", "Invalid tool name format"),
                suggestion=template.get("suggestion"),
                details={
                    "provided_name": name,
                    "valid_pattern": "^[a-z][a-z0-9_]*$",
                    "examples": ["my_tool", "k8s_list_pods", "db_query"],
                },
            )
        )

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def validate_tool(
    script_content: str | None,
    input_schema: dict | None,
    executor_type: str,
    name: str | None = None,
) -> ValidationResult:
    """Validate a complete tool definition.

    Args:
        script_content: Python script content (required for python executor).
        input_schema: JSON Schema for input parameters.
        executor_type: Type of executor (python, http, etc.).
        name: Tool name (optional, validated if provided).

    Returns:
        ValidationResult with combined validation results.
    """
    errors: list[ErrorDetail] = []

    # Validate tool name if provided
    if name is not None:
        name_result = validate_tool_name(name)
        if not name_result.valid:
            errors.extend(name_result.errors)

    # Validate script content for python executor
    if executor_type == "python":
        if not script_content:
            template = get_error_template("script_content_required")
            errors.append(
                ErrorDetail(
                    code=template.get("code", ErrorCode.MISSING_REQUIRED_FIELD).value,
                    field="script_content",
                    message=template.get("message", "Script content is required for Python executor"),
                    suggestion=template.get("suggestion"),
                    details={
                        "executor_type": executor_type,
                        "example": template.get("example"),
                    },
                )
            )
        else:
            syntax_result = validate_python_syntax(script_content)
            if not syntax_result.valid:
                errors.extend(syntax_result.errors)

    # Validate input schema if provided
    if input_schema:
        schema_result = validate_json_schema(input_schema, "input_schema")
        if not schema_result.valid:
            errors.extend(schema_result.errors)

    return ValidationResult(valid=len(errors) == 0, errors=errors)
