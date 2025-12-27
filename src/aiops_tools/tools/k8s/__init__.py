"""Kubernetes tools for cluster operations.

Tools:
- k8s_list_pods: List pods in a namespace
- k8s_get_logs: Get pod logs
- k8s_describe_pod: Get detailed pod information
- k8s_restart_deployment: Restart a deployment
- k8s_list_namespaces: List all namespaces
- k8s_get_deployment_status: Get deployment status
"""

K8S_TOOLS = [
    "k8s_list_pods",
    "k8s_get_logs",
    "k8s_describe_pod",
    "k8s_restart_deployment",
    "k8s_list_namespaces",
    "k8s_get_deployment_status",
]

__all__ = ["K8S_TOOLS"]
