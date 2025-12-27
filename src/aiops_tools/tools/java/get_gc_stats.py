"""Get JVM garbage collection statistics via JMX/Jolokia."""

TOOL_DEFINITION = {
    "name": "java_get_gc_stats",
    "display_name": "Get GC Statistics",
    "description": "Retrieve garbage collection statistics from a Java application. Shows collection counts and times for each GC collector.",
    "tags": ["java", "jmx", "gc", "memory"],
    "input_schema": {
        "type": "object",
        "properties": {
            "jmx_url": {
                "type": "string",
                "description": "JMX service URL or Jolokia endpoint",
            },
            "username": {"type": "string"},
            "password": {"type": "string"},
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
                    "collectors": {"type": "array"},
                    "memory_pools": {"type": "array"},
                    "timestamp": {"type": "string"},
                },
            },
        },
    },
}


def main(input_data: dict) -> dict:
    """Get JVM garbage collection statistics.

    Args:
        input_data: Dictionary with jmx_url, optional username/password

    Returns:
        Dictionary with success status and GC data or error
    """
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

    if jmx_url.startswith("http"):
        return _get_gc_via_jolokia(jmx_url, username, password)
    else:
        return {
            "success": False,
            "error": {
                "code": "JMX_NOT_SUPPORTED",
                "message": "Direct JMX RMI connection not supported. Use Jolokia HTTP endpoint instead.",
            },
        }


def _get_gc_via_jolokia(base_url: str, username: str | None, password: str | None) -> dict:
    """Get GC stats via Jolokia REST API."""
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
        # Search for GC MBeans
        search_url = f"{base_url}/search/java.lang:type=GarbageCollector,*"
        search_response = httpx.get(search_url, auth=auth, timeout=30)

        if search_response.status_code == 401:
            return {
                "success": False,
                "error": {
                    "code": "JMX_AUTH_ERROR",
                    "message": "Authentication failed",
                },
            }

        search_data = search_response.json()
        gc_mbeans = search_data.get("value", [])

        collectors = []
        for mbean in gc_mbeans:
            # Get GC attributes
            # URL encode the mbean name (replace special chars)
            encoded_mbean = mbean.replace(":", "%3A").replace(",", "%2C").replace("=", "%3D")
            gc_url = f"{base_url}/read/{encoded_mbean}"
            gc_response = httpx.get(gc_url, auth=auth, timeout=30)

            if gc_response.status_code == 200:
                gc_data = gc_response.json().get("value", {})

                # Extract collector name from MBean name
                name = "Unknown"
                if "name=" in mbean:
                    name = mbean.split("name=")[1].split(",")[0]

                collectors.append({
                    "name": name,
                    "collection_count": gc_data.get("CollectionCount", 0),
                    "collection_time_ms": gc_data.get("CollectionTime", 0),
                    "memory_pools": gc_data.get("MemoryPoolNames", []),
                })

        # Get memory pools
        pool_search_url = f"{base_url}/search/java.lang:type=MemoryPool,*"
        pool_response = httpx.get(pool_search_url, auth=auth, timeout=30)
        pool_mbeans = pool_response.json().get("value", []) if pool_response.status_code == 200 else []

        memory_pools = []
        for mbean in pool_mbeans:
            encoded_mbean = mbean.replace(":", "%3A").replace(",", "%2C").replace("=", "%3D")
            pool_url = f"{base_url}/read/{encoded_mbean}"
            pool_data_response = httpx.get(pool_url, auth=auth, timeout=30)

            if pool_data_response.status_code == 200:
                pool_data = pool_data_response.json().get("value", {})

                name = "Unknown"
                if "name=" in mbean:
                    name = mbean.split("name=")[1].split(",")[0]

                usage = pool_data.get("Usage", {})
                peak = pool_data.get("PeakUsage", {})

                memory_pools.append({
                    "name": name,
                    "type": pool_data.get("Type", "UNKNOWN"),
                    "used_bytes": usage.get("used", 0),
                    "max_bytes": usage.get("max", -1),
                    "peak_used_bytes": peak.get("used", 0),
                })

        return {
            "success": True,
            "data": {
                "collectors": collectors,
                "memory_pools": memory_pools,
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
