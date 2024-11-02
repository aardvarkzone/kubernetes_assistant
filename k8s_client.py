# k8s_client.py

import logging
from gpt_client import interpret_query_with_gpt
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

from gpt_client import interpret_query_with_gpt

def handle_k8s_query(structured_query, query):
    """
    Handles Kubernetes-related queries by executing the kubectl command provided in the structured response.
    Retries with next prompt variant if command execution fails and includes error feedback.
    """
    attempt = 0  # Track attempts for retry logic
    error_feedback = None  # Track the error message for feedback

    while attempt < 3:  # Limit to three prompt variants
        # Check if a kubectl command was provided
        kubectl_command = structured_query.get("kubectl_command")
        if kubectl_command:
            logging.info(f"Executing kubectl command: {kubectl_command}")
            answer = execute_kubectl_command(kubectl_command)

            # If the command succeeds, return the result
            if not answer.startswith("Error executing kubectl command"):
                return answer

            # Capture error feedback for next attempt
            error_feedback = answer
            logging.warning(f"Command failed with error: {error_feedback}. Retrying with next variant.")

        else:
            # If no kubectl command, check for a general response
            general_response = structured_query.get("general_response")
            if general_response:
                logging.info(f"General response provided: {general_response}")
                return general_response

        # If command execution fails, try the next GPT prompt variant with error feedback
        attempt += 1
        structured_query = interpret_query_with_gpt(query, variant=attempt+1, error_feedback=error_feedback)

    # If all retries fail
    return "Could not generate a successful command. Please refine your question or try a different query."
