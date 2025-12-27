"""Get Kubernetes deployment status."""

TOOL_DEFINITION = {
    "name": "k8s_get_deployment_status",
    "display_name": "Get Deployment Status",
    "description": "Get the status of a deployment including replica counts, conditions, and rollout status.",
    "tags": ["kubernetes", "deployments", "status"],
    "input_schema": {
        "type": "object",
        "properties": {
            "namespace": {
                "type": "string",
                "default": "default",
            },
            "deployment_name": {
                "type": "string",
                "description": "Name of the deployment",
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
                    "name": {"type": "string"},
                    "namespace": {"type": "string"},
                    "replicas": {
                        "type": "object",
                        "properties": {
                            "desired": {"type": "integer"},
                            "ready": {"type": "integer"},
                            "available": {"type": "integer"},
                            "updated": {"type": "integer"},
                        },
                    },
                    "conditions": {"type": "array"},
                    "strategy": {"type": "string"},
                },
            },
        },
    },
}


def main(input_data: dict) -> dict:
    """Get deployment status.

    Args:
        input_data: Dictionary with deployment_name, optional namespace, kubeconfig, context

    Returns:
        Dictionary with success status and deployment details or error
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

        # Get deployment
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
            raise

        # Build conditions list
        conditions = []
        if deployment.status.conditions:
            for cond in deployment.status.conditions:
                conditions.append({
                    "type": cond.type,
                    "status": cond.status,
                    "reason": cond.reason,
                    "message": cond.message,
                })

        # Get strategy type
        strategy = "Unknown"
        if deployment.spec.strategy:
            strategy = deployment.spec.strategy.type

        return {
            "success": True,
            "data": {
                "name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "replicas": {
                    "desired": deployment.spec.replicas or 0,
                    "ready": deployment.status.ready_replicas or 0,
                    "available": deployment.status.available_replicas or 0,
                    "updated": deployment.status.updated_replicas or 0,
                },
                "conditions": conditions,
                "strategy": strategy,
                "labels": dict(deployment.metadata.labels) if deployment.metadata.labels else {},
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
