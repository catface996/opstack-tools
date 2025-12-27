"""Describe a Kubernetes pod with detailed information."""

from datetime import datetime, timezone

TOOL_DEFINITION = {
    "name": "k8s_describe_pod",
    "display_name": "Describe Pod",
    "description": "Get detailed information about a pod including events, conditions, container statuses, and resource usage.",
    "tags": ["kubernetes", "pods", "describe"],
    "input_schema": {
        "type": "object",
        "properties": {
            "namespace": {
                "type": "string",
                "default": "default",
            },
            "pod_name": {
                "type": "string",
                "description": "Name of the pod to describe",
            },
            "kubeconfig": {"type": "string"},
            "context": {"type": "string"},
        },
        "required": ["pod_name"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "namespace": {"type": "string"},
                    "status": {"type": "string"},
                    "node": {"type": "string"},
                    "ip": {"type": "string"},
                    "containers": {"type": "array"},
                    "events": {"type": "array"},
                },
            },
        },
    },
}


def _format_age(timestamp: datetime | None) -> str:
    """Format timestamp as age string."""
    if not timestamp:
        return "N/A"
    now = datetime.now(timezone.utc)
    delta = now - timestamp
    if delta.days > 0:
        return f"{delta.days}d ago"
    hours = delta.seconds // 3600
    if hours > 0:
        return f"{hours}h ago"
    minutes = (delta.seconds % 3600) // 60
    return f"{minutes}m ago"


def main(input_data: dict) -> dict:
    """Describe a Kubernetes pod.

    Args:
        input_data: Dictionary with pod_name, optional namespace, kubeconfig, context

    Returns:
        Dictionary with success status and pod details or error
    """
    try:
        from kubernetes import client, config
        from kubernetes.client.rest import ApiException

        pod_name = input_data.get("pod_name")
        if not pod_name:
            return {
                "success": False,
                "error": {
                    "code": "K8S_INVALID_INPUT",
                    "message": "pod_name is required",
                },
            }

        namespace = input_data.get("namespace", "default")
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

        # Get pod details
        try:
            pod = v1.read_namespaced_pod(pod_name, namespace)
        except ApiException as e:
            if e.status == 404:
                return {
                    "success": False,
                    "error": {
                        "code": "K8S_NOT_FOUND",
                        "message": f"Pod '{pod_name}' not found in namespace '{namespace}'",
                    },
                }
            raise

        # Get pod events
        events = []
        try:
            field_selector = f"involvedObject.name={pod_name},involvedObject.namespace={namespace}"
            event_list = v1.list_namespaced_event(namespace, field_selector=field_selector)
            for event in event_list.items[-10:]:  # Last 10 events
                events.append({
                    "type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "age": _format_age(event.last_timestamp or event.first_timestamp),
                })
        except Exception:
            pass  # Events are optional

        # Build container info
        containers = []
        if pod.status.container_statuses:
            for cs in pod.status.container_statuses:
                state = "Unknown"
                if cs.state.running:
                    state = "Running"
                elif cs.state.waiting:
                    state = f"Waiting ({cs.state.waiting.reason})"
                elif cs.state.terminated:
                    state = f"Terminated ({cs.state.terminated.reason})"

                containers.append({
                    "name": cs.name,
                    "image": cs.image,
                    "state": state,
                    "ready": cs.ready,
                    "restart_count": cs.restart_count,
                })

        return {
            "success": True,
            "data": {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "node": pod.spec.node_name or "N/A",
                "ip": pod.status.pod_ip or "N/A",
                "host_ip": pod.status.host_ip or "N/A",
                "start_time": pod.status.start_time.isoformat() if pod.status.start_time else None,
                "labels": dict(pod.metadata.labels) if pod.metadata.labels else {},
                "containers": containers,
                "events": events,
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
