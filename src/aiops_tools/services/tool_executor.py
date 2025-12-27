"""Tool execution service using subprocess."""

import json
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from aiops_tools.core.config import settings


@dataclass
class ExecutionResult:
    """Result of a tool execution."""

    success: bool
    result: dict | None = None
    error: str | None = None
    duration_ms: int = 0
    stdout: str = ""
    stderr: str = ""


def execute_script(
    script_content: str,
    input_data: dict,
    timeout: int | None = None,
) -> ExecutionResult:
    """Execute a Python script with input data.

    The script receives input via stdin as JSON and should output
    result as JSON to stdout.

    Args:
        script_content: Python source code to execute.
        input_data: Input parameters to pass via stdin.
        timeout: Execution timeout in seconds (default: from settings).

    Returns:
        ExecutionResult with success status and result or error.
    """
    if timeout is None:
        timeout = settings.tool_execution_timeout

    start_time = time.time()

    # Wrap user script with IO handling
    wrapper_script = f'''
import sys
import json

# User-defined script
{script_content}

# Read input from stdin and execute main()
if __name__ == "__main__":
    input_data = json.loads(sys.stdin.read())
    result = main(input_data)
    print(json.dumps(result))
'''

    # Create temporary file for the script
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8",
    ) as f:
        f.write(wrapper_script)
        script_path = Path(f.name)

    try:
        # Execute the script with input via stdin
        result = subprocess.run(
            ["python", str(script_path)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        duration_ms = int((time.time() - start_time) * 1000)

        if result.returncode == 0:
            # Try to parse stdout as JSON
            try:
                output = json.loads(result.stdout) if result.stdout.strip() else {}
                return ExecutionResult(
                    success=True,
                    result=output,
                    duration_ms=duration_ms,
                    stdout=result.stdout,
                    stderr=result.stderr,
                )
            except json.JSONDecodeError:
                # If output is not JSON, wrap it
                return ExecutionResult(
                    success=True,
                    result={"output": result.stdout},
                    duration_ms=duration_ms,
                    stdout=result.stdout,
                    stderr=result.stderr,
                )
        else:
            # Script returned non-zero exit code
            error_msg = result.stderr or result.stdout or "Unknown error"
            return ExecutionResult(
                success=False,
                error=error_msg.strip(),
                duration_ms=duration_ms,
                stdout=result.stdout,
                stderr=result.stderr,
            )

    except subprocess.TimeoutExpired:
        duration_ms = int((time.time() - start_time) * 1000)
        return ExecutionResult(
            success=False,
            error=f"Execution timeout after {timeout} seconds",
            duration_ms=duration_ms,
        )
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ExecutionResult(
            success=False,
            error=f"Execution error: {e!s}",
            duration_ms=duration_ms,
        )
    finally:
        # Clean up temporary file
        try:
            script_path.unlink()
        except OSError:
            pass


async def execute_script_async(
    script_content: str,
    input_data: dict,
    timeout: int | None = None,
) -> ExecutionResult:
    """Async wrapper for execute_script.

    In production, this would use asyncio.create_subprocess_exec.
    For simplicity, this currently wraps the sync version.
    """
    import asyncio

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: execute_script(script_content, input_data, timeout),
    )
