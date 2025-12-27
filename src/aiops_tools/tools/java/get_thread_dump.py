"""Get JVM thread dump via JMX/Jolokia."""

TOOL_DEFINITION = {
    "name": "java_get_thread_dump",
    "display_name": "Get Thread Dump",
    "description": "Generate a thread dump from a running Java application. Shows all threads with their stack traces and states.",
    "tags": ["java", "jmx", "threads", "dump"],
    "input_schema": {
        "type": "object",
        "properties": {
            "jmx_url": {
                "type": "string",
                "description": "JMX service URL or Jolokia endpoint",
            },
            "username": {"type": "string"},
            "password": {"type": "string"},
            "max_depth": {
                "type": "integer",
                "description": "Maximum stack trace depth per thread",
                "default": 50,
            },
        },
        "required": ["jmx_url"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "thread_count": {"type": "integer"},
                    "daemon_count": {"type": "integer"},
                    "peak_count": {"type": "integer"},
                    "threads": {"type": "array"},
                    "deadlocked_threads": {"type": "array"},
                    "timestamp": {"type": "string"},
                },
            },
        },
    },
}


def main(input_data: dict) -> dict:
    """Get JVM thread dump.

    Args:
        input_data: Dictionary with jmx_url, optional username/password/max_depth

    Returns:
        Dictionary with success status and thread data or error
    """
    jmx_url = input_data.get("jmx_url")
    username = input_data.get("username")
    password = input_data.get("password")
    max_depth = input_data.get("max_depth", 50)

    if not jmx_url:
        return {
            "success": False,
            "error": {
                "code": "JMX_INVALID_INPUT",
                "message": "jmx_url is required",
            },
        }

    if jmx_url.startswith("http"):
        return _get_threads_via_jolokia(jmx_url, username, password, max_depth)
    else:
        return {
            "success": False,
            "error": {
                "code": "JMX_NOT_SUPPORTED",
                "message": "Direct JMX RMI connection not supported. Use Jolokia HTTP endpoint instead.",
            },
        }


def _get_threads_via_jolokia(base_url: str, username: str | None, password: str | None, max_depth: int) -> dict:
    """Get thread dump via Jolokia REST API."""
    try:
        import httpx
    except ImportError:
        return {
            "success": False,
            "error": {
                "code": "JMX_IMPORT_ERROR",
                "message": "httpx package not installed",
            },
        }

    from datetime import datetime, timezone

    base_url = base_url.rstrip("/")
    if not base_url.endswith("/jolokia"):
        if "/jolokia" not in base_url:
            base_url = f"{base_url}/jolokia"

    auth = None
    if username and password:
        auth = (username, password)

    try:
        # Get thread count info
        thread_mbean = "java.lang:type=Threading"
        count_url = f"{base_url}/read/{thread_mbean}/ThreadCount,DaemonThreadCount,PeakThreadCount"
        count_response = httpx.get(count_url, auth=auth, timeout=30)

        if count_response.status_code == 401:
            return {
                "success": False,
                "error": {
                    "code": "JMX_AUTH_ERROR",
                    "message": "Authentication failed",
                },
            }

        count_data = count_response.json().get("value", {})

        # Get all thread IDs
        thread_ids_url = f"{base_url}/read/{thread_mbean}/AllThreadIds"
        ids_response = httpx.get(thread_ids_url, auth=auth, timeout=30)
        thread_ids = ids_response.json().get("value", [])

        # Get thread info for all threads (using exec operation)
        # Jolokia exec format: /exec/mbean/operation/arg1/arg2...
        threads = []

        # Get thread info in batches to avoid URL length issues
        for thread_id in thread_ids[:100]:  # Limit to first 100 threads
            try:
                # Get basic thread info
                info_url = f"{base_url}/exec/{thread_mbean}/getThreadInfo(long)/{thread_id}"
                info_response = httpx.get(info_url, auth=auth, timeout=10)
                if info_response.status_code == 200:
                    info_data = info_response.json().get("value", {})
                    if info_data:
                        stack_trace = []
                        if info_data.get("stackTrace"):
                            for frame in info_data["stackTrace"][:max_depth]:
                                class_name = frame.get("className", "")
                                method_name = frame.get("methodName", "")
                                line_number = frame.get("lineNumber", -1)
                                file_name = frame.get("fileName", "")
                                stack_trace.append(f"{class_name}.{method_name}({file_name}:{line_number})")

                        threads.append({
                            "name": info_data.get("threadName", "Unknown"),
                            "id": info_data.get("threadId", thread_id),
                            "state": info_data.get("threadState", "UNKNOWN"),
                            "daemon": info_data.get("daemon", False),
                            "priority": info_data.get("priority", 5),
                            "stack_trace": stack_trace,
                            "locked_monitors": [],
                            "locked_synchronizers": [],
                        })
            except Exception:
                continue

        # Check for deadlocked threads
        deadlocked = []
        try:
            deadlock_url = f"{base_url}/exec/{thread_mbean}/findDeadlockedThreads()"
            deadlock_response = httpx.get(deadlock_url, auth=auth, timeout=10)
            deadlock_data = deadlock_response.json().get("value")
            if deadlock_data:
                deadlocked = list(deadlock_data)
        except Exception:
            pass

        return {
            "success": True,
            "data": {
                "thread_count": count_data.get("ThreadCount", len(threads)),
                "daemon_count": count_data.get("DaemonThreadCount", 0),
                "peak_count": count_data.get("PeakThreadCount", 0),
                "threads": threads,
                "deadlocked_threads": deadlocked,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }

    except httpx.ConnectError as e:
        return {
            "success": False,
            "error": {
                "code": "JMX_CONNECTION_ERROR",
                "message": f"Failed to connect to Jolokia endpoint: {e}",
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "JMX_ERROR",
                "message": str(e),
            },
        }
