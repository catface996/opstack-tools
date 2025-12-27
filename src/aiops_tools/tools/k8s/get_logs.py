"""Get logs from a Kubernetes pod."""

TOOL_DEFINITION = {
    "name": "k8s_get_logs",
    "display_name": "Get Pod Logs",
    "description": "Retrieve logs from a specific pod. Supports tail lines limit and container selection for multi-container pods.",
    "tags": ["kubernetes", "pods", "logs"],
    "input_schema": {
        "type": "object",
        "properties": {
            "namespace": {
                "type": "string",
                "description": "Kubernetes namespace",
                "default": "default",
            },
            "pod_name": {
                "type": "string",
                "description": "Name of the pod to get logs from",
            },
            "container": {
                "type": "string",
                "description": "Container name (required for multi-container pods)",
            },
            "tail_lines": {
                "type": "integer",
                "description": "Number of lines to return from end of logs",
                "default": 100,
            },
            "kubeconfig": {
                "type": "string",
                "description": "Path to kubeconfig file",
            },
            "context": {
                "type": "string",
                "description": "Kubernetes context to use",
            },
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
                    "pod_name": {"type": "string"},
                    "container": {"type": "string"},
                    "logs": {"type": "string"},
                    "line_count": {"type": "integer"},
                },
            },
        },
    },
}


def main(input_data: dict) -> dict:
    """Get logs from a Kubernetes pod.

    Args:
        input_data: Dictionary with pod_name, optional namespace, container, tail_lines

    Returns:
        Dictionary with success status and logs or error
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
        container = input_data.get("container")
        tail_lines = input_data.get("tail_lines", 100)
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

        # Get pod logs
        try:
            kwargs = {
                "name": pod_name,
                "namespace": namespace,
                "tail_lines": tail_lines,
            }
            if container:
                kwargs["container"] = container

            logs = v1.read_namespaced_pod_log(**kwargs)

        except ApiException as e:
            if e.status == 404:
                return {
                    "success": False,
                    "error": {
                        "code": "K8S_NOT_FOUND",
                        "message": f"Pod '{pod_name}' not found in namespace '{namespace}'",
                    },
                }
            elif e.status == 400 and "container" in str(e.body).lower():
                return {
                    "success": False,
                    "error": {
                        "code": "K8S_CONTAINER_ERROR",
                        "message": "Pod has multiple containers. Please specify 'container' parameter.",
                    },
                }
            raise

        line_count = len(logs.splitlines()) if logs else 0

        return {
            "success": True,
            "data": {
                "pod_name": pod_name,
                "container": container or "default",
                "logs": logs,
                "line_count": line_count,
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
