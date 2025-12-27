"""List Kubernetes namespaces."""

from datetime import datetime, timezone

TOOL_DEFINITION = {
    "name": "k8s_list_namespaces",
    "display_name": "List Namespaces",
    "description": "List all namespaces in the Kubernetes cluster with their status.",
    "tags": ["kubernetes", "namespaces", "list"],
    "input_schema": {
        "type": "object",
        "properties": {
            "kubeconfig": {"type": "string"},
            "context": {"type": "string"},
        },
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "namespaces": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "status": {"type": "string"},
                                "age": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
    },
}


def _get_age(creation_timestamp: datetime) -> str:
    """Calculate human-readable age from creation timestamp."""
    now = datetime.now(timezone.utc)
    delta = now - creation_timestamp

    if delta.days > 0:
        return f"{delta.days}d"
    hours = delta.seconds // 3600
    if hours > 0:
        return f"{hours}h"
    minutes = (delta.seconds % 3600) // 60
    return f"{minutes}m"


def main(input_data: dict) -> dict:
    """List all namespaces in the Kubernetes cluster.

    Args:
        input_data: Dictionary with optional kubeconfig, context

    Returns:
        Dictionary with success status and namespace list or error
    """
    try:
        from kubernetes import client, config

        kubeconfig = input_data.get("kubeconfig")
        context = input_data.get("context")

        # Load kubernetes configuration
        try:
            if kubeconfig:
                config.load_kube_config(config_file=kubeconfig, context=context)
            else:
                try:
                    config.load_incluster_config()
                except config.ConfigException:
                    config.load_kube_config(context=context)
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "K8S_CONFIG_ERROR",
                    "message": f"Failed to load Kubernetes configuration: {e}",
                },
            }

        v1 = client.CoreV1Api()

        # List namespaces
        namespaces = v1.list_namespace()

        namespace_list = []
        for ns in namespaces.items:
            namespace_list.append({
                "name": ns.metadata.name,
                "status": ns.status.phase,
                "age": _get_age(ns.metadata.creation_timestamp),
            })

        return {
            "success": True,
            "data": {
                "namespaces": namespace_list,
            },
        }

    except ImportError:
        return {
            "success": False,
            "error": {
                "code": "K8S_IMPORT_ERROR",
                "message": "kubernetes package not installed. Run: pip install kubernetes",
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "K8S_ERROR",
                "message": str(e),
            },
        }
