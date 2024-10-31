# k8s_client.py

import logging
from kubernetes import client
from kubernetes.client.exceptions import ApiException
from datetime import datetime, timezone
import subprocess

def handle_k8s_query(structured_query):
    """
    Handles Kubernetes-related queries based on the structured response from GPT.
    """
    # Normalize and standardize inputs
    intent = structured_query.get("intent", "").strip().lower()
    resource_type = structured_query.get("resource_type", "").strip().lower()
    resource_name = structured_query.get("resource_name", "").strip() if structured_query.get("resource_name") else ""
    namespace = structured_query.get("namespace", "default").strip().lower() if structured_query.get("namespace") else "default"
    action = structured_query.get("action", "").strip().lower()

    # Synonym mapping for common intents and actions
    action_map = {
        "count": ["count", "getcount", "total", "howmany", "quantity"],
        "list": ["list", "getinformation", "retrieve", "describe", "showall"],
        "status": ["status", "getstatus", "health", "condition"],
        "ip": ["ip", "getip", "address"],
        "logs": ["logs", "getlogs", "output"],
        "age": ["age", "getage", "uptime", "creationtime", "howold"],
        "restarts": ["restarts", "getrestarts", "restartcount"],
        "environmentvariable": ["environmentvariable", "getenvironmentvariable", "env", "envvar"],
        "mountpath": ["mountpath", "getmountpath", "volumemount", "volume"],
        "port": ["port", "getport", "containerport"],
        "readinessprobe": ["readinessprobe", "getreadinessprobe", "healthcheck"]
    }

    # Helper function to map actions and intents to standardized values
    def normalize_action(action):
        for key, synonyms in action_map.items():
            if action in synonyms:
                return key
        return action  # return action as-is if no match found

    # Normalize action and intent based on synonyms
    normalized_action = normalize_action(action)
    normalized_intent = normalize_action(intent)
    logging.info(f"Normalized intent: {normalized_intent}, action: {normalized_action}")    

    # Pods
    if resource_type in ["pod", "pods"]:
        if normalized_intent == "count" or normalized_action == "count":
            return get_pod_count(namespace)
        elif normalized_intent == "status" and resource_name:
            return get_pod_status(resource_name, namespace)
        elif normalized_intent == "ip" and resource_name:
            return get_pod_ip(resource_name, namespace)
        elif normalized_intent == "logs" and resource_name:
            return get_pod_logs(resource_name, namespace)
        elif normalized_intent == "age" and resource_name:
            return get_pod_age(resource_name, namespace)
        elif normalized_intent == "restarts" and resource_name:
            return get_pod_restarts(resource_name, namespace)
        elif normalized_intent == "environmentvariable" and resource_name:
            env_var_name = structured_query.get("env_var_name", "").strip()
            return get_pod_environment_variable(resource_name, env_var_name, namespace)
        elif normalized_intent == "mountpath" and resource_name:
            return get_pod_mount_paths(resource_name, namespace)
        elif normalized_intent == "port" and resource_name:
            return get_container_ports(resource_name, namespace)
        elif normalized_intent == "readinessprobe" and resource_name:
            return get_readiness_probe(resource_name, namespace)

    # Nodes
    elif resource_type in ["node", "nodes"]:
        if normalized_intent == "count":
            return get_node_count()
        elif normalized_intent == "status" and resource_name:
            return get_node_status(resource_name)

    # Services
    elif resource_type in ["service", "services"]:
        if normalized_intent == "count":
            return get_service_count(namespace)
        elif normalized_intent in ["list", "retrieve"]:
            return list_services(namespace)
        elif normalized_intent == "status" and resource_name:
            return get_service_status(resource_name, namespace)
        elif normalized_intent == "port" and resource_name:
            return get_service_ports(resource_name, namespace)

    # Deployments
    elif resource_type in ["deployment", "deployments"]:
        if normalized_intent == "list" and resource_name:
            return get_pods(deployment=resource_name, namespace=namespace)

    # Namespaces
    elif resource_type in ["namespace", "namespaces"]:
        if normalized_intent in ["list", "retrieve"]:
            return get_namespaces()
        elif normalized_intent == "count":
            return get_namespace_count()

    # Fallback if no recognized action or intent
    return "Action or resource type not recognized."




# Kubernetes functions

def get_pod_count(namespace='default'):
    try:
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace=namespace)
        return len(pods.items)
    except ApiException as e:
        logging.error(f"Error fetching pod count: {e.status} - {e.reason}")
        return "Error fetching pod count."

def get_pod_status(pod_name, namespace='default'):
    try:
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        return pod.status.phase
    except ApiException as e:
        logging.error(f"Error fetching pod status: {e.status} - {e.reason}")
        return "Error fetching pod status."

def get_pod_ip(pod_name, namespace='default'):
    try:
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        return pod.status.pod_ip
    except ApiException as e:
        logging.error(f"Error fetching pod IP: {e.status} - {e.reason}")
        return "Error fetching pod IP."

def get_pod_logs(pod_name, namespace='default', container_name=None, tail_lines=100):
    try:
        v1 = client.CoreV1Api()
        return v1.read_namespaced_pod_log(name=pod_name, namespace=namespace, container=container_name, tail_lines=tail_lines)
    except ApiException as e:
        logging.error(f"Error fetching pod logs: {e.status} - {e.reason}")
        return "Error fetching pod logs."

def get_pod_age(pod_name, namespace='default'):
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
    try:
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        return sum(container.restart_count for container in pod.status.container_statuses) if pod.status.container_statuses else 0
    except ApiException as e:
        logging.error(f"Error fetching pod restarts: {e.status} - {e.reason}")
        return "Error fetching pod restarts."

def get_pod_environment_variable(pod_name, env_var_name, namespace='default'):
    try:
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        for container in pod.spec.containers:
            for env in container.env or []:
                if env.name == env_var_name:
                    return env.value
        return f"Environment variable '{env_var_name}' not found."
    except ApiException as e:
        logging.error(f"Error fetching environment variable: {e.status} - {e.reason}")
        return "Error fetching environment variable."

def get_pod_mount_paths(pod_name, namespace='default'):
    try:
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        mount_paths = {}
        for container in pod.spec.containers:
            mount_paths[container.name] = [mount.mount_path for mount in container.volume_mounts or []]
        return mount_paths if mount_paths else "No volume mounts found."
    except ApiException as e:
        logging.error(f"Error fetching pod mount paths: {e.status} - {e.reason}")
        return "Error fetching pod mount paths."

def get_node_count():
    try:
        v1 = client.CoreV1Api()
        nodes = v1.list_node()
        return len(nodes.items)
    except ApiException as e:
        logging.error(f"Error fetching node count: {e.status} - {e.reason}")
        return "Error fetching node count."

def get_node_status(node_name):
    try:
        v1 = client.CoreV1Api()
        node = v1.read_node(name=node_name)
        for condition in node.status.conditions:
            if condition.type == "Ready":
                return condition.status
        return "Unknown"
    except ApiException as e:
        logging.error(f"Error fetching node status: {e.status} - {e.reason}")
        return "Error fetching node status."

def get_service_count(namespace='default'):
    try:
        v1 = client.CoreV1Api()
        services = v1.list_namespaced_service(namespace=namespace)
        return len(services.items)
    except ApiException as e:
        logging.error(f"Error fetching service count: {e.status} - {e.reason}")
        return "Error fetching service count."

def list_services(namespace='default'):
    try:
        v1 = client.CoreV1Api()
        services = v1.list_namespaced_service(namespace=namespace)
        return [svc.metadata.name for svc in services.items]
    except ApiException as e:
        logging.error(f"Error fetching services: {e.status} - {e.reason}")
        return "Error fetching services."

def get_service_namespace(service_name):
    try:
        v1 = client.CoreV1Api()
        services = v1.list_service_for_all_namespaces()
        for svc in services.items:
            if svc.metadata.name == service_name:
                return svc.metadata.namespace
        return f"Service '{service_name}' not found."
    except ApiException as e:
        logging.error(f"Error fetching service namespace: {e.status} - {e.reason}")
        return "Error fetching service namespace."

def get_service_details(service_name, namespace='default'):
    try:
        v1 = client.CoreV1Api()
        service = v1.read_namespaced_service(name=service_name, namespace=namespace)
        details = {
            "name": service.metadata.name,
            "type": service.spec.type,
            "ports": [port.port for port in service.spec.ports]
        }
        return details
    except ApiException as e:
        logging.error(f"Error fetching service details: {e.status} - {e.reason}")
        return "Error fetching service details."

def get_service_ports(service_name, namespace='default'):
    try:
        v1 = client.CoreV1Api()
        service = v1.read_namespaced_service(name=service_name, namespace=namespace)
        return [port.target_port for port in service.spec.ports]
    except ApiException as e:
        logging.error(f"Error fetching service ports: {e.status} - {e.reason}")
        return "Error fetching service ports."

def get_pods(namespace='default', deployment=None):
    try:
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace=namespace)
        if deployment:
            return [pod.metadata.name for pod in pods.items if deployment in pod.metadata.name]
        return [pod.metadata.name for pod in pods.items]
    except ApiException as e:
        logging.error(f"Error fetching pods: {e.status} - {e.reason}")
        return "Error fetching pods."

def get_namespaces():
    try:
        v1 = client.CoreV1Api()
        namespaces = v1.list_namespace()
        return [ns.metadata.name for ns in namespaces.items]
    except ApiException as e:
        logging.error(f"Error fetching namespaces: {e.status} - {e.reason}")
        return "Error fetching namespaces."

def get_namespace_count():
    try:
        v1 = client.CoreV1Api()
        namespaces = v1.list_namespace()
        return len(namespaces.items)
    except ApiException as e:
        logging.error(f"Error fetching namespace count: {e.status} - {e.reason}")
        return "Error fetching namespace count."


def get_container_ports(pod_name, namespace="default"):
    """Fetches container ports for a specific pod in a namespace."""
    try:
        result = subprocess.run(
            ["kubectl", "get", "pod", pod_name, "-n", namespace, "-o", "json"],
            check=True,
            capture_output=True,
            text=True
        )
        pod_data = json.loads(result.stdout)
        ports = []
        for container in pod_data.get("spec", {}).get("containers", []):
            for port in container.get("ports", []):
                ports.append(port.get("containerPort"))
        return ports if ports else "No ports found"
    except subprocess.CalledProcessError as e:
        return f"Error fetching container ports: {e}"

def get_readiness_probe(pod_name, namespace="default"):
    """Fetches the readiness probe path for a specific pod in a namespace."""
    try:
        result = subprocess.run(
            ["kubectl", "get", "pod", pod_name, "-n", namespace, "-o", "json"],
            check=True,
            capture_output=True,
            text=True
        )
        pod_data = json.loads(result.stdout)
        readiness_probe_paths = []
        for container in pod_data.get("spec", {}).get("containers", []):
            readiness_probe = container.get("readinessProbe", {})
            http_get = readiness_probe.get("httpGet", {})
            path = http_get.get("path")
            if path:
                readiness_probe_paths.append(path)
        return readiness_probe_paths if readiness_probe_paths else "No readiness probe found"
    except subprocess.CalledProcessError as e:
        return f"Error fetching readiness probe: {e}"
    