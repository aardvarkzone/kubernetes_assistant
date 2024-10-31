# gpt_client.py

import logging
import json
from openai import OpenAI
from config import get_openai_key

client_openai = OpenAI(api_key=get_openai_key())

def interpret_query_with_gpt(query):
    """
    Sends a query to GPT to interpret and return a structured response with a kubectl command.
    Attempts up to three prompt variants if needed.
    """
    def gpt_request(prompt_variant):
        """
        Attempts to generate a command or general response from GPT-4 using a specific prompt variant.
        """
        try:
            # Define different prompt variations, all with the full set of detailed instructions
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
                "     {\"kubectl_command\": \"kubectl get pods --all-namespaces -o json --kubeconfig ~/.kube/config | jq '.items | length'\"}\n\n"
                
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
                
                "Respond only with the JSON response without extra commentary. If the query is a general question unrelated to specific Kubernetes commands, respond with a 'general_response' JSON field instead of 'kubectl_command'."
            )

            # Modify instructions slightly based on variant
            if prompt_variant == 2:
                system_message_content = base_message_content + (
                    "\n\nEnsure each command includes `--kubeconfig ~/.kube/config` for specificity in environment handling.\n"
                    "Be concise, and validate JSON paths to ensure data accuracy."
                )
            elif prompt_variant == 3:
                system_message_content = base_message_content + (
                    "\n\nFor cases where errors occur, double-check JSON path accuracy or consider alternative commands."
                )
            else:
                system_message_content = base_message_content  # Default

            system_message = {"role": "system", "content": system_message_content}
            user_message = {"role": "user", "content": f"Interpret this query: {query}"}

            response = client_openai.chat.completions.create(
                model="gpt-4",
                messages=[system_message, user_message],
                max_tokens=100,
                temperature=0.3
            )

            gpt_answer = response.choices[0].message.content.strip()
            logging.debug(f"GPT-4 response (variant {prompt_variant}): {gpt_answer}")

            structured_response = json.loads(gpt_answer)
            if 'kubectl_command' in structured_response or 'general_response' in structured_response:
                return structured_response  # Return if valid response

        except json.JSONDecodeError:
            logging.error("Failed to parse GPT response as JSON.")
        except Exception as e:
            logging.error(f"Error generating GPT-4 response with variant {prompt_variant}: {e}", exc_info=True)
        return None

    # Try up to three prompt variants
    for variant in range(1, 4):
        result = gpt_request(variant)
        if result:
            return result  # Exit loop on first valid response

    # If all attempts fail
    return {"general_response": "Could not generate a specific command. Please refine your question or try a different query."}
