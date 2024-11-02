import logging
import json
from openai import OpenAI
from config import get_openai_key
import time

client_openai = OpenAI(api_key=get_openai_key())

def interpret_query_with_gpt(query, variant=1, error_feedback=None):
    """
    Sends a query to GPT to interpret and return a structured response with a kubectl command.
    Accepts a variant parameter to specify which prompt variant to use and an optional error_feedback parameter.
    """
    # Define base prompt variations
    base_message_content = (
        "You are an AI assistant that interprets Kubernetes-related queries and returns structured JSON responses.\n"
        "Your goal is to generate accurate 'kubectl' commands for Kubernetes clusters when possible. Each command should directly retrieve the requested data if available.\n"
        "If a query does not require a Kubernetes command, provide a general response in JSON format.\n\n"
        
        "Return responses in this JSON format:\n"
        "- 'kubectl_command': The kubectl command to run to satisfy the query.\n\n"
        
        "If no command is possible, respond instead with:\n"
        "- 'general_response': A concise answer to the question or helpful guidance.\n\n"
        
        "Guidelines for generating commands:\n"
        "1. **Counting Resources**:\n"
        "   - Avoid using `wc -l` for counting, as it can be inaccurate. Instead, retrieve JSON output and count items programmatically.\n"
        "   - Example: For 'How many pods are there?', respond with:\n"
        "     {\"kubectl_command\": \"kubectl get pods --all-namespaces -o json --kubeconfig ~/.kube/config\"}\n\n"
        
        "2. **Querying Resource Status**:\n"
        "   - Use `-o=jsonpath` to query specific fields like `.status`, `.spec`, or `.metadata`. For instance, to get the status of a service or pod, target `.status.phase` or `.status.loadBalancer` as appropriate.\n"
        "   - Example: For 'What is the status of harbor registry?', respond with:\n"
        "     {\"kubectl_command\": \"kubectl get svc harbor-registry -o=jsonpath='{.status}' --kubeconfig ~/.kube/config\"}\n\n"
        
        "3. **Accessing IPs and Ports**:\n"
        "   - To get a pod or service's IP, use `.status.podIP` or `.status.loadBalancer.ingress[0].ip`.\n"
        "   - For container or service ports, access `.spec.ports[]` and look for `targetPort` or `containerPort`.\n"
        "   - Example: For 'What is the container port for harbor-core?', respond with:\n"
        "     {\"kubectl_command\": \"kubectl get pods -l app=harbor-core -o=jsonpath='{.items[0].spec.containers[0].ports[0].containerPort}' --kubeconfig ~/.kube/config\"}\n\n"

        "4. **Handling Probes (Readiness/Liveness)**:\n"
        "   - Use `.spec.containers[].readinessProbe` or `.livenessProbe` for probe paths, often located under `httpGet.path`.\n"
        "   - Example: For 'What is the readiness probe path for the harbor core?', respond with:\n"
        "     {\"kubectl_command\": \"kubectl get pods -l app=harbor-core -o=jsonpath='{.items[0].spec.containers[0].readinessProbe.httpGet.path}' --kubeconfig ~/.kube/config\"}\n\n"

        "5. **Accessing PostgreSQL Configuration Data**:\n"
        "   - For questions requiring data outside of kubectl commands (e.g., environment variables or database configuration), use `kubectl exec` to access pods directly.\n"
        "   - Example: For 'What is the name of the database in PostgreSQL used by harbor?', respond with:\n"
        "     {\"kubectl_command\": \"kubectl exec -n harbor $(kubectl get pod -n harbor -l app=harbor-database -o jsonpath='{.items[0].metadata.name}' --kubeconfig ~/.kube/config) --kubeconfig ~/.kube/config -- printenv POSTGRES_DB\"}\n\n"
        
        "Respond only with the JSON response without extra commentary. Ensure the JSON is valid and parsable."
    )

    # Modify prompt based on variant
    if variant == 2:
        system_message_content = base_message_content + (
            "\n\nEnsure each command includes `--kubeconfig ~/.kube/config` for specificity in environment handling.\n"
            "Be concise, and validate JSON paths to ensure data accuracy."
        )
    elif variant == 3:
        system_message_content = base_message_content + (
            "\n\nFor cases where errors occur, double-check JSON path accuracy or consider alternative commands."
        )
    else:
        system_message_content = base_message_content  # Default variant

    # Include error feedback in the user message if available
    user_message_content = f"Interpret this query: {query}"
    if error_feedback:
        user_message_content += f"\n\nNote: The previous command attempt failed with the following error:\n{error_feedback}"

    system_message = {"role": "system", "content": system_message_content}
    user_message = {"role": "user", "content": user_message_content}

    try:
        response = client_openai.chat.completions.create(
            model="gpt-4",
            messages=[system_message, user_message],
            max_tokens=200,
            temperature=0.3
        )

        gpt_answer = response.choices[0].message.content.strip()
        logging.debug(f"GPT-4 response (variant {variant}): {gpt_answer}")

        # Try parsing the GPT response as JSON
        try:
            structured_response = json.loads(gpt_answer)
            if 'kubectl_command' in structured_response or 'general_response' in structured_response:
                return structured_response  # Return if valid response
            else:
                logging.error("Parsed JSON does not contain expected keys.")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse GPT response as JSON: {e}")

    except Exception as e:
        logging.error(f"Error generating GPT-4 response with variant {variant}: {e}", exc_info=True)

    return None
