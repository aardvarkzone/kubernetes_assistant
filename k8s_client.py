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
    # Check if the response includes a general response instead of a command
    if "general_response" in structured_query:
        general_response = structured_query["general_response"]
        logging.info(f"General response provided: {general_response}")
        return general_response
    
    # Check if a kubectl command was provided
    kubectl_command = structured_query.get("kubectl_command")
    if not kubectl_command:
        logging.warning("No kubectl command or general response provided in the structured query.")
        return "No kubectl command or general response available for this query."

    # Execute the provided kubectl command
    logging.info(f"Executing kubectl command: {kubectl_command}")
    return execute_kubectl_command(kubectl_command)
