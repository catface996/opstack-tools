"""List available MBeans via JMX/Jolokia."""

TOOL_DEFINITION = {
    "name": "java_list_mbeans",
    "display_name": "List MBeans",
    "description": "List all MBeans available on a JMX endpoint. Useful for discovering available metrics and operations.",
    "tags": ["java", "jmx", "mbeans", "discovery"],
    "input_schema": {
        "type": "object",
        "properties": {
            "jmx_url": {
                "type": "string",
                "description": "JMX service URL or Jolokia endpoint",
            },
            "username": {"type": "string"},
            "password": {"type": "string"},
            "domain": {
                "type": "string",
                "description": "Filter by MBean domain (e.g., 'java.lang', 'com.example')",
            },
            "pattern": {
                "type": "string",
                "description": "Object name pattern to filter MBeans",
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
                    "total_count": {"type": "integer"},
                    "domains": {"type": "array", "items": {"type": "string"}},
                    "mbeans": {"type": "array"},
                },
            },
        },
    },
}


def main(input_data: dict) -> dict:
    """List available MBeans.

    Args:
        input_data: Dictionary with jmx_url, optional username/password/domain/pattern

    Returns:
        Dictionary with success status and MBean list or error
    """
    jmx_url = input_data.get("jmx_url")
    username = input_data.get("username")
    password = input_data.get("password")
    domain = input_data.get("domain")
    pattern = input_data.get("pattern")

    if not jmx_url:
        return {
            "success": False,
            "error": {
                "code": "JMX_INVALID_INPUT",
                "message": "jmx_url is required",
            },
        }

    if jmx_url.startswith("http"):
        return _list_mbeans_via_jolokia(jmx_url, username, password, domain, pattern)
    else:
        return {
            "success": False,
            "error": {
                "code": "JMX_NOT_SUPPORTED",
                "message": "Direct JMX RMI connection not supported. Use Jolokia HTTP endpoint instead.",
            },
        }


def _list_mbeans_via_jolokia(base_url: str, username: str | None, password: str | None,
                              domain: str | None, pattern: str | None) -> dict:
    """List MBeans via Jolokia REST API."""
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

    base_url = base_url.rstrip("/")
    if not base_url.endswith("/jolokia"):
        if "/jolokia" not in base_url:
            base_url = f"{base_url}/jolokia"

    auth = None
    if username and password:
        auth = (username, password)

    try:
        # Build search pattern
        if pattern:
            search_pattern = pattern
        elif domain:
            search_pattern = f"{domain}:*"
        else:
            search_pattern = "*:*"

        # Search for MBeans
        search_url = f"{base_url}/search/{search_pattern}"
        search_response = httpx.get(search_url, auth=auth, timeout=30)

        if search_response.status_code == 401:
            return {
                "success": False,
                "error": {
                    "code": "JMX_AUTH_ERROR",
                    "message": "Authentication failed",
                },
            }

        if search_response.status_code != 200:
            return {
                "success": False,
                "error": {
                    "code": "JMX_CONNECTION_ERROR",
                    "message": f"Jolokia returned status {search_response.status_code}",
                },
            }

        search_data = search_response.json()
        mbean_names = search_data.get("value", [])

        # Extract unique domains
        domains = set()
        mbeans = []

        for mbean_name in mbean_names[:200]:  # Limit to 200 MBeans
            # Parse domain from mbean name (format: domain:key=value,...)
            if ":" in mbean_name:
                mbean_domain = mbean_name.split(":")[0]
                domains.add(mbean_domain)

                # Extract type if present
                mbean_type = None
                if "type=" in mbean_name:
                    type_part = mbean_name.split("type=")[1]
                    mbean_type = type_part.split(",")[0]

                mbeans.append({
                    "object_name": mbean_name,
                    "domain": mbean_domain,
                    "type": mbean_type,
                    "attributes": [],  # Could fetch with another call, but expensive
                    "operations": [],
                })

        return {
            "success": True,
            "data": {
                "total_count": len(mbean_names),
                "domains": sorted(list(domains)),
                "mbeans": mbeans,
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
