# k8s_client.py
import logging
from kubernetes import client
from kubernetes.client.exceptions import ApiException
from utils import extract_resource_name, get_generic_name
from datetime import datetime, timezone

def handle_k8s_query(query_lower, original_query):
    """
    Handles Kubernetes-related queries by parsing the query and calling appropriate functions.
    """
    if "how many pods" in query_lower or "pod count" in query_lower:
        return get_pod_count()

    if "node count" in query_lower or "how many nodes" in query_lower:
        return get_node_count()

    if "status of the node" in query_lower:
        node_name = extract_resource_name(original_query, "node")
        if node_name:
            return get_node_status(node_name)
        return "Could not extract node name."

    if "pod" in query_lower and "status" in query_lower:
        pod_name = extract_resource_name(original_query, "pod")
        if pod_name:
            return get_pod_status(pod_name)
        return "Could not extract pod name."

    if "pods running under the deployment" in query_lower or "which pod is spawned by the deployment" in query_lower:
        deployment_name = extract_resource_name(original_query, "deployment")
        if deployment_name:
            return get_pods(deployment=deployment_name)
        return "Could not extract deployment name."

    if "list of running pods" in query_lower or "list running pods" in query_lower:
        return get_pods(status_filter="Running")

    if "pod" in query_lower and "age" in query_lower:
        pod_name = extract_resource_name(original_query, "pod")
        if pod_name:
            return get_pod_age(pod_name)
        return "Could not extract pod name."

    if "pod" in query_lower and "restarts" in query_lower:
        pod_name = extract_resource_name(original_query, "pod")
        if pod_name:
            return get_pod_restarts(pod_name)
        return "Could not extract pod name."

    if "pod" in query_lower and "ip" in query_lower:
        pod_name = extract_resource_name(original_query, "pod")
        if pod_name:
            return get_pod_ip(pod_name)
        return "Could not extract pod name."

    if "pod" in query_lower and "logs" in query_lower:
        pod_name = extract_resource_name(original_query, "pod")
        if pod_name:
            return get_pod_logs(pod_name)
        return "Could not extract pod name."

    if "list all namespaces" in query_lower or "how many namespaces" in query_lower:
        return get_namespaces()

    if "how many services" in query_lower or "service count" in query_lower:
        return get_service_count()

    if "list all services" in query_lower or "services in" in query_lower:
        return list_services()

    if "details of service" in query_lower:
        service_name = extract_resource_name(original_query, "service")
        if service_name:
            return get_service_details(service_name)
        return "Could not extract service name."

    return "Query not recognized."

def get_pod_count(namespace='default'):
    """
    Returns the number of pods in the specified namespace.
    """
    try:
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace=namespace)
        return len(pods.items)
    except ApiException as e:
        logging.error(f"Error fetching pods: {e.status} - {e.reason}")
        return "Error fetching pods."

def get_pods(namespace='default', status_filter=None, deployment=None):
    """
    Returns a list of pod names in the specified namespace, optionally filtered by status or deployment.
    """
    try:
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace=namespace)
        filtered_pods = pods.items

        if status_filter:
            filtered_pods = [pod for pod in filtered_pods if pod.status.phase.lower() == status_filter.lower()]

        if deployment:
            filtered_pods = [pod for pod in filtered_pods if deployment in pod.metadata.name]

        pod_names = [get_generic_name(pod.metadata.name) for pod in filtered_pods]
        return pod_names
    except ApiException as e:
        logging.error(f"Error fetching pods: {e.status} - {e.reason}")
        return "Error fetching pods."

def get_pod_status(pod_name, namespace='default'):
    """
    Returns the status of a specific pod.
    """
    try:
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        return pod.status.phase
    except ApiException as e:
        logging.error(f"Error fetching pod status: {e.status} - {e.reason}")
        return "Error fetching pod status."

def get_pod_age(pod_name, namespace='default'):
    """
    Returns the age of a specific pod.
    """
    try:
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        start_time = pod.status.start_time
        if start_time:
            age = datetime.now(timezone.utc) - start_time.replace(tzinfo=timezone.utc)
            return str(age).split('.')[0]
        return "Unknown"
    except ApiException as e:
        logging.error(f"Error fetching pod age: {e.status} - {e.reason}")
        return "Error fetching pod age."

def get_pod_restarts(pod_name, namespace='default'):
    """
    Returns the total number of restarts for a specific pod.
    """
    try:
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        return sum(container.restart_count for container in pod.status.container_statuses) if pod.status.container_statuses else 0
    except ApiException as e:
        logging.error(f"Error fetching pod restarts: {e.status} - {e.reason}")
        return "Error fetching pod restarts."

def get_pod_ip(pod_name, namespace='default'):
    """
    Returns the IP address of a specific pod.
    """
    try:
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        return pod.status.pod_ip
    except ApiException as e:
        logging.error(f"Error fetching pod IP: {e.status} - {e.reason}")
        return "Error fetching pod IP."

def get_pod_logs(pod_name, namespace='default', container_name=None, tail_lines=100):
    """
    Returns the logs of a specific pod. Optionally, logs from a specific container can be fetched.
    """
    try:
        v1 = client.CoreV1Api()
        return v1.read_namespaced_pod_log(name=pod_name, namespace=namespace, container=container_name, tail_lines=tail_lines)
    except ApiException as e:
        logging.error(f"Error fetching pod logs: {e.status} - {e.reason}")
        return "Error fetching pod logs."

def get_node_count():
    """
    Returns the number of nodes in the cluster.
    """
    try:
        v1 = client.CoreV1Api()
        nodes = v1.list_node()
        return len(nodes.items)
    except ApiException as e:
        logging.error(f"Error fetching nodes: {e.status} - {e.reason}")
        return "Error fetching node count."

def get_node_status(node_name):
    """
    Returns the status of a specific node.
    """
    try:
        v1 = client.CoreV1Api()
        node = v1.read_node(name=node_name)
        conditions = node.status.conditions
        for condition in conditions:
            if condition.type == "Ready":
                return condition.status
        return "Unknown"
    except ApiException as e:
        logging.error(f"Error fetching node status: {e.status} - {e.reason}")
        return "Error fetching node status."

def get_namespaces():
    """
    Returns a list of all namespaces in the cluster.
    """
    try:
        v1 = client.CoreV1Api()
        namespaces = v1.list_namespace()
        return [ns.metadata.name for ns in namespaces.items]
    except ApiException as e:
        logging.error(f"Error fetching namespaces: {e.status} - {e.reason}")
        return "Error fetching namespaces."

def get_service_count(namespace='default'):
    """
    Returns the number of services in the specified namespace.
    """
    try:
        v1 = client.CoreV1Api()
        services = v1.list_namespaced_service(namespace=namespace)
        return len(services.items)
    except ApiException as e:
        logging.error(f"Error fetching services: {e.status} - {e.reason}")
        return "Error fetching services."

def list_services(namespace='default'):
    """
    Returns a list of service names in the specified namespace.
    """
    try:
        v1 = client.CoreV1Api()
        services = v1.list_namespaced_service(namespace=namespace)
        return [get_generic_name(svc.metadata.name) for svc in services.items]
    except ApiException as e:
        logging.error(f"Error fetching services: {e.status} - {e.reason}")
        return "Error fetching services."

def get_service_details(service_name, namespace='default'):
    """
    Returns the details of a specific service.
    """
    try:
        v1 = client.CoreV1Api()
        service = v1.read_namespaced_service(name=service_name, namespace=namespace)
        service_type = service.spec.type
        ports = [port.port for port in service.spec.ports]
        details = {
            "name": get_generic_name(service.metadata.name),
            "type": service_type,
            "ports": ports
        }
        return details
    except ApiException as e:
        logging.error(f"Error fetching service details: {e.status} - {e.reason}")
        return "Error fetching service details."
