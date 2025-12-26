"""LLM-compatible schemas for OpenAI function calling format."""

from pydantic import BaseModel, Field

from aiops_tools.models import Tool


class LLMToolParameter(BaseModel):
    """Parameter definition in OpenAI function format."""

    type: str = "object"
    properties: dict = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)


class LLMToolFunction(BaseModel):
    """Function definition in OpenAI function format."""

    name: str
    description: str
    parameters: LLMToolParameter


class LLMTool(BaseModel):
    """Tool in OpenAI function calling format."""

    type: str = "function"
    function: LLMToolFunction


class LLMToolListResponse(BaseModel):
    """Response containing list of tools in LLM format."""

    tools: list[LLMTool]


class LLMToolGetRequest(BaseModel):
    """Request to get a tool by name."""

    tool_name: str


class ToolInvokeRequest(BaseModel):
    """Request to invoke a tool."""

    tool_name: str
    arguments: dict = Field(default_factory=dict)


class ToolInvokeResponse(BaseModel):
    """Response from tool invocation."""

    success: bool
    result: dict | None = None
    error: str | None = None
    duration_ms: int = 0


def transform_to_llm_format(tool: Tool) -> LLMTool:
    """Transform a Tool model to OpenAI function calling format.

    Args:
        tool: Tool database model.

    Returns:
        LLMTool in OpenAI function calling format.
    """
    # Build parameters from input_schema or use empty object
    input_schema = tool.input_schema or {}
    parameters = LLMToolParameter(
        type=input_schema.get("type", "object"),
        properties=input_schema.get("properties", {}),
        required=input_schema.get("required", []),
    )

    function = LLMToolFunction(
        name=tool.name,
        description=tool.description or f"Tool: {tool.name}",
        parameters=parameters,
    )

    return LLMTool(type="function", function=function)
