#k8s_client.py
import logging
from gpt_client import interpret_query_with_gpt
import subprocess
import json

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
        output = result.stdout.strip()
        logging.debug(f"kubectl command output: {output}")
        return output or "No output available"
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.strip() or e.stdout.strip()
        logging.error(f"Error executing kubectl command: {error_output}")
        return f"Error executing kubectl command: {error_output}"

def handle_k8s_query(structured_query, query):
    """
    Handles Kubernetes-related queries by executing the kubectl command provided in the structured response.
    Retries with next prompt variant if command execution fails and includes error feedback.
    """
    attempt = 0  # Track attempts for retry logic
    error_feedback = None  # Track the error message for feedback

    while attempt < 3:  # Limit to three prompt variants
        if not structured_query:
            logging.error("Structured query is None.")
            break  # Exit the loop if no structured query is returned

        # Check if a kubectl command was provided
        kubectl_command = structured_query.get("kubectl_command")
        if kubectl_command:
            logging.info(f"Executing kubectl command: {kubectl_command}")
            answer = execute_kubectl_command(kubectl_command)

            # If the command succeeds, return the result
            if "Error executing kubectl command" not in answer:
                # Attempt to parse JSON output if expected
                if "-o json" in kubectl_command or "-o=json" in kubectl_command:
                    try:
                        json_output = json.loads(answer)
                        # Process the JSON output as needed
                        logging.debug(f"Parsed JSON output: {json_output}")
                        # Return processed information or the raw JSON
                        return json_output
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to parse kubectl JSON output: {e}")
                        # Return the raw output if parsing fails
                        return answer
                else:
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
        if not structured_query:
            logging.error("Failed to get a structured query from GPT.")
            break  # Exit the loop if GPT fails to provide a response

    # If all retries fail
    return "Could not generate a successful command. Please refine your question or try a different query."
