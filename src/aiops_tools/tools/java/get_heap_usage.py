"""Get JVM heap memory usage via JMX/Jolokia."""

TOOL_DEFINITION = {
    "name": "java_get_heap_usage",
    "display_name": "Get JVM Heap Usage",
    "description": "Retrieve current heap memory usage from a Java application via JMX. Returns used, committed, max, and initial heap sizes.",
    "tags": ["java", "jmx", "memory", "heap"],
    "input_schema": {
        "type": "object",
        "properties": {
            "jmx_url": {
                "type": "string",
                "description": "JMX service URL or Jolokia endpoint. Examples: http://localhost:8080/jolokia or service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi",
            },
            "username": {
                "type": "string",
                "description": "JMX authentication username (if required)",
            },
            "password": {
                "type": "string",
                "description": "JMX authentication password (if required)",
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
                    "heap": {
                        "type": "object",
                        "properties": {
                            "used_bytes": {"type": "integer"},
                            "committed_bytes": {"type": "integer"},
                            "max_bytes": {"type": "integer"},
                            "init_bytes": {"type": "integer"},
                            "used_percent": {"type": "number"},
                        },
                    },
                    "non_heap": {
                        "type": "object",
                        "properties": {
                            "used_bytes": {"type": "integer"},
                            "committed_bytes": {"type": "integer"},
                            "max_bytes": {"type": "integer"},
                        },
                    },
                    "timestamp": {"type": "string"},
                },
            },
        },
    },
}


def main(input_data: dict) -> dict:
    """Get JVM heap memory usage.

    Args:
        input_data: Dictionary with jmx_url, optional username/password

    Returns:
        Dictionary with success status and memory data or error
    """
    from datetime import datetime, timezone

    jmx_url = input_data.get("jmx_url")
    username = input_data.get("username")
    password = input_data.get("password")

    if not jmx_url:
        return {
            "success": False,
            "error": {
                "code": "JMX_INVALID_INPUT",
                "message": "jmx_url is required",
            },
        }

    # Determine if this is a Jolokia REST endpoint or JMX RMI
    if jmx_url.startswith("http"):
        return _get_heap_via_jolokia(jmx_url, username, password)
    else:
        return {
            "success": False,
            "error": {
                "code": "JMX_NOT_SUPPORTED",
                "message": "Direct JMX RMI connection not supported. Use Jolokia HTTP endpoint instead.",
            },
        }


def _get_heap_via_jolokia(base_url: str, username: str | None, password: str | None) -> dict:
    """Get heap usage via Jolokia REST API."""
    try:
        import httpx
    except ImportError:
        return {
            "success": False,
            "error": {
                "code": "JMX_IMPORT_ERROR",
                "message": "httpx package not installed. Run: pip install httpx",
            },
        }

    from datetime import datetime, timezone

    # Normalize URL
    base_url = base_url.rstrip("/")
    if not base_url.endswith("/jolokia"):
        if "/jolokia" not in base_url:
            base_url = f"{base_url}/jolokia"

    # Build auth if provided
    auth = None
    if username and password:
        auth = (username, password)

    try:
        # Get heap memory
        heap_url = f"{base_url}/read/java.lang:type=Memory/HeapMemoryUsage"
        response = httpx.get(heap_url, auth=auth, timeout=30)

        if response.status_code == 401:
            return {
                "success": False,
                "error": {
                    "code": "JMX_AUTH_ERROR",
                    "message": "Authentication failed. Check username and password.",
                },
            }

        if response.status_code != 200:
            return {
                "success": False,
                "error": {
                    "code": "JMX_CONNECTION_ERROR",
                    "message": f"Jolokia returned status {response.status_code}",
                },
            }

        heap_data = response.json()
        if heap_data.get("status") != 200:
            return {
                "success": False,
                "error": {
                    "code": "JMX_ERROR",
                    "message": heap_data.get("error", "Unknown Jolokia error"),
                },
            }

        heap_value = heap_data.get("value", {})

        # Get non-heap memory
        non_heap_url = f"{base_url}/read/java.lang:type=Memory/NonHeapMemoryUsage"
        non_heap_response = httpx.get(non_heap_url, auth=auth, timeout=30)
        non_heap_data = non_heap_response.json() if non_heap_response.status_code == 200 else {}
        non_heap_value = non_heap_data.get("value", {})

        # Calculate heap percentage
        max_heap = heap_value.get("max", 0)
        used_heap = heap_value.get("used", 0)
        used_percent = (used_heap / max_heap * 100) if max_heap > 0 else 0

        return {
            "success": True,
            "data": {
                "heap": {
                    "used_bytes": heap_value.get("used", 0),
                    "committed_bytes": heap_value.get("committed", 0),
                    "max_bytes": heap_value.get("max", 0),
                    "init_bytes": heap_value.get("init", 0),
                    "used_percent": round(used_percent, 2),
                },
                "non_heap": {
                    "used_bytes": non_heap_value.get("used", 0),
                    "committed_bytes": non_heap_value.get("committed", 0),
                    "max_bytes": non_heap_value.get("max", -1),
                },
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
