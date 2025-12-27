"""List Kubernetes pods in a namespace."""

from datetime import datetime, timezone

TOOL_DEFINITION = {
    "name": "k8s_list_pods",
    "display_name": "List Kubernetes Pods",
    "description": "List all pods in a specified namespace with their status information. Returns pod names, status, restart count, and age.",
    "tags": ["kubernetes", "pods", "list"],
    "input_schema": {
        "type": "object",
        "properties": {
            "namespace": {
                "type": "string",
                "description": "Kubernetes namespace to list pods from",
                "default": "default",
            },
            "kubeconfig": {
                "type": "string",
                "description": "Path to kubeconfig file (optional, uses default if not specified)",
            },
            "context": {
                "type": "string",
                "description": "Kubernetes context to use (optional)",
            },
            "label_selector": {
                "type": "string",
                "description": "Label selector to filter pods (e.g., 'app=nginx')",
            },
        },
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "namespace": {"type": "string"},
                    "pods": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "status": {"type": "string"},
                                "ready": {"type": "string"},
                                "restarts": {"type": "integer"},
                                "age": {"type": "string"},
                                "node": {"type": "string"},
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


def _get_ready_count(container_statuses: list | None) -> str:
    """Get ready/total container count string."""
    if not container_statuses:
        return "0/0"
    ready = sum(1 for cs in container_statuses if cs.ready)
    total = len(container_statuses)
    return f"{ready}/{total}"


def _get_restart_count(container_statuses: list | None) -> int:
    """Get total restart count across all containers."""
    if not container_statuses:
        return 0
    return sum(cs.restart_count for cs in container_statuses)


def main(input_data: dict) -> dict:
    """List pods in a Kubernetes namespace.

    Args:
        input_data: Dictionary with optional namespace, kubeconfig, context, label_selector

    Returns:
        Dictionary with success status and pod list or error
    """
    try:
        from kubernetes import client, config
        from kubernetes.client.rest import ApiException

        namespace = input_data.get("namespace", "default")
        kubeconfig = input_data.get("kubeconfig")
        context = input_data.get("context")
        label_selector = input_data.get("label_selector")

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

        # List pods
        try:
            if label_selector:
                pods = v1.list_namespaced_pod(namespace, label_selector=label_selector)
            else:
                pods = v1.list_namespaced_pod(namespace)
        except ApiException as e:
            if e.status == 404:
                return {
                    "success": False,
                    "error": {
                        "code": "K8S_NOT_FOUND",
                        "message": f"Namespace '{namespace}' not found",
                    },
                }
            elif e.status == 403:
                return {
                    "success": False,
                    "error": {
                        "code": "K8S_FORBIDDEN",
                        "message": f"Access denied to namespace '{namespace}'",
                    },
                }
            raise

        pod_list = []
        for pod in pods.items:
            pod_list.append({
                "name": pod.metadata.name,
                "status": pod.status.phase,
                "ready": _get_ready_count(pod.status.container_statuses),
                "restarts": _get_restart_count(pod.status.container_statuses),
                "age": _get_age(pod.metadata.creation_timestamp),
                "node": pod.spec.node_name or "N/A",
            })

        return {
            "success": True,
            "data": {
                "namespace": namespace,
                "pods": pod_list,
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
