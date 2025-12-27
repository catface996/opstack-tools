"""Restart a Kubernetes deployment."""

from datetime import datetime, timezone

TOOL_DEFINITION = {
    "name": "k8s_restart_deployment",
    "display_name": "Restart Deployment",
    "description": "Perform a rolling restart of a deployment by updating its pod template annotation. This triggers a gradual replacement of all pods.",
    "tags": ["kubernetes", "deployments", "restart"],
    "input_schema": {
        "type": "object",
        "properties": {
            "namespace": {
                "type": "string",
                "default": "default",
            },
            "deployment_name": {
                "type": "string",
                "description": "Name of the deployment to restart",
            },
            "kubeconfig": {"type": "string"},
            "context": {"type": "string"},
        },
        "required": ["deployment_name"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "deployment_name": {"type": "string"},
                    "namespace": {"type": "string"},
                    "message": {"type": "string"},
                    "restart_time": {"type": "string"},
                },
            },
        },
    },
}


def main(input_data: dict) -> dict:
    """Restart a Kubernetes deployment.

    Args:
        input_data: Dictionary with deployment_name, optional namespace, kubeconfig, context

    Returns:
        Dictionary with success status and restart confirmation or error
    """
    try:
        from kubernetes import client, config
        from kubernetes.client.rest import ApiException

        deployment_name = input_data.get("deployment_name")
        if not deployment_name:
            return {
                "success": False,
                "error": {
                    "code": "K8S_INVALID_INPUT",
                    "message": "deployment_name is required",
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

        apps_v1 = client.AppsV1Api()

        # Get current deployment to verify it exists
        try:
            deployment = apps_v1.read_namespaced_deployment(deployment_name, namespace)
        except ApiException as e:
            if e.status == 404:
                return {
                    "success": False,
                    "error": {
                        "code": "K8S_NOT_FOUND",
                        "message": f"Deployment '{deployment_name}' not found in namespace '{namespace}'",
                    },
                }
            elif e.status == 403:
                return {
                    "success": False,
                    "error": {
                        "code": "K8S_FORBIDDEN",
                        "message": f"Access denied to deployment '{deployment_name}'",
                    },
                }
            raise

        # Perform rollout restart by updating annotation
        restart_time = datetime.now(timezone.utc).isoformat()

        # Ensure annotations exist
        if deployment.spec.template.metadata.annotations is None:
            deployment.spec.template.metadata.annotations = {}

        deployment.spec.template.metadata.annotations["kubectl.kubernetes.io/restartedAt"] = restart_time

        try:
            apps_v1.patch_namespaced_deployment(
                deployment_name,
                namespace,
                deployment,
            )
        except ApiException as e:
            return {
                "success": False,
                "error": {
                    "code": "K8S_PATCH_ERROR",
                    "message": f"Failed to restart deployment: {e.reason}",
                },
            }

        return {
            "success": True,
            "data": {
                "deployment_name": deployment_name,
                "namespace": namespace,
                "message": "Rollout restart initiated successfully",
                "restart_time": restart_time,
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
