"""Tool validation service."""

import ast
from dataclasses import dataclass

import jsonschema


@dataclass
class ValidationResult:
    """Result of a validation check."""

    valid: bool
    errors: list[dict[str, str]]


def validate_python_syntax(script_content: str) -> ValidationResult:
    """Validate Python script syntax.

    Args:
        script_content: Python source code to validate.

    Returns:
        ValidationResult with valid=True if syntax is correct,
        or valid=False with error details.
    """
    if not script_content or not script_content.strip():
        return ValidationResult(
            valid=False,
            errors=[{"field": "script_content", "message": "Script content is empty"}],
        )

    try:
        ast.parse(script_content)
        return ValidationResult(valid=True, errors=[])
    except SyntaxError as e:
        return ValidationResult(
            valid=False,
            errors=[
                {
                    "field": "script_content",
                    "message": f"Syntax error at line {e.lineno}: {e.msg}",
                }
            ],
        )


def validate_json_schema(schema: dict) -> ValidationResult:
    """Validate that a dictionary is a valid JSON Schema.

    Args:
        schema: Dictionary to validate as JSON Schema.

    Returns:
        ValidationResult with valid=True if schema is valid,
        or valid=False with error details.
    """
    if not schema:
        # Empty schema is valid (no parameters)
        return ValidationResult(valid=True, errors=[])

    try:
        # Validate the schema itself by checking it against the meta-schema
        jsonschema.Draft7Validator.check_schema(schema)
        return ValidationResult(valid=True, errors=[])
    except jsonschema.SchemaError as e:
        return ValidationResult(
            valid=False,
            errors=[{"field": "input_schema", "message": str(e.message)}],
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
        or valid=False with error details.
    """
    if not input_schema:
        # No schema means any input is valid
        return ValidationResult(valid=True, errors=[])

    try:
        jsonschema.validate(instance=input_data, schema=input_schema)
        return ValidationResult(valid=True, errors=[])
    except jsonschema.ValidationError as e:
        return ValidationResult(
            valid=False,
            errors=[{"field": "input_data", "message": e.message}],
        )


def validate_tool(
    script_content: str | None,
    input_schema: dict | None,
    executor_type: str,
) -> ValidationResult:
    """Validate a complete tool definition.

    Args:
        script_content: Python script content (required for python executor).
        input_schema: JSON Schema for input parameters.
        executor_type: Type of executor (python, http, etc.).

    Returns:
        ValidationResult with combined validation results.
    """
    errors: list[dict[str, str]] = []

    # Validate script content for python executor
    if executor_type == "python":
        if not script_content:
            errors.append(
                {
                    "field": "script_content",
                    "message": "Script content is required for Python executor",
                }
            )
        else:
            syntax_result = validate_python_syntax(script_content)
            if not syntax_result.valid:
                errors.extend(syntax_result.errors)

    # Validate input schema if provided
    if input_schema:
        schema_result = validate_json_schema(input_schema)
        if not schema_result.valid:
            errors.extend(schema_result.errors)

    return ValidationResult(valid=len(errors) == 0, errors=errors)
