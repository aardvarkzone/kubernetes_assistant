# k8s_client.py

import logging
import subprocess

def execute_kubectl_command(kubectl_command):
    """
    Executes the provided kubectl command and returns the output.
    """
    try:
        result = subprocess.run(
            kubectl_command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        logging.debug(f"kubectl command output: {result.stdout}")
        return result.stdout.strip() or "No output available"
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing kubectl command: {e}")
        return f"Error executing kubectl command: {e}"

def handle_k8s_query(structured_query):
    """
    Handles Kubernetes-related queries by executing the kubectl command provided in the structured response.
    """
    if "general_response" in structured_query:
        # Return a general response if no specific Kubernetes command is provided
        return structured_query["general_response"]

    kubectl_command = structured_query.get("kubectl_command", "")
    if not kubectl_command:
        return "No kubectl command provided in the structured query."

    logging.info(f"Executing kubectl command: {kubectl_command}")
    return execute_kubectl_command(kubectl_command)
