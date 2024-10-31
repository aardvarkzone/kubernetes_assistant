# gpt_client.py

import logging
import json
from openai import OpenAI
from config import get_openai_key

# Initialize OpenAI client with API key from config
client_openai = OpenAI(api_key=get_openai_key())

def interpret_query_with_gpt(query):
    """
    Sends a query to GPT-4 to interpret and return a structured response.
    """
    try:
        system_message = {
            "role": "system",
            "content": (
                "You are an AI assistant that interprets Kubernetes-related queries and returns structured JSON responses. "
                "Your responses must strictly follow this JSON format:\n\n"
                
                "Fields:\n"
                "- 'intent': Main action type, such as 'count', 'list', 'status', 'ip', 'logs', 'age', 'restarts', 'environmentvariable', 'mountpath', 'port', or 'readinessprobe'.\n"
                "- 'resource_type': The Kubernetes resource type being queried (e.g., 'pod', 'service', 'namespace', 'node'). When the target is clear from the question (e.g., asking for a 'namespace'), use this to clarify the main context.\n"
                "- 'resource_name': The exact name of the resource if specified, preserving spacing and case from the query.\n"
                "- 'namespace': The namespace specified in the query; default to 'default' if no namespace is explicitly mentioned.\n"
                "- 'action': The specific action aligned with the query's primary task, based on intent (e.g., 'count', 'getstatus', 'list').\n\n"
                
                "Guidelines:\n"
                "- Use these mappings to interpret intents:\n"
                "  * 'count' for totals (e.g., 'how many pods').\n"
                "  * 'list' for queries about retrieval (e.g., 'list all', 'retrieve').\n"
                "  * 'status' for health/state checks.\n"
                "  * 'ip' for IP address requests.\n"
                "  * 'logs' for log data.\n"
                "  * 'age' for queries about creation time.\n"
                "  * 'restarts' for restart counts.\n"
                "  * 'environmentvariable' for environment variable values.\n"
                "  * 'mountpath' for persistent volume paths.\n"
                "  * 'port' for container or service port information.\n"
                "  * 'readinessprobe' for health checks or readiness probe information.\n\n"

                "Target-Specific Context:\n"
                "- Clearly identify a target in 'resource_type' when apparent (e.g., 'namespace' in 'Which namespace is the harbor service deployed to?'). Use 'resource_name' for specific resource identifiers (e.g., 'harbor').\n"
                
                "Namespace and Action:\n"
                "- Use the exact namespace if specified in the query; otherwise, set 'default'.\n"
                "- Ensure every query has an 'action' field that best represents its main purpose.\n\n"
                
                "Examples:\n"
                "- Query: 'How many pods are running?'\n"
                "  Response: {'intent': 'count', 'resource_type': 'pod', 'namespace': 'default', 'action': 'count'}\n"
                
                "- Query: 'What is the IP of pod abc in the monitoring namespace?'\n"
                "  Response: {'intent': 'ip', 'resource_type': 'pod', 'resource_name': 'abc', 'namespace': 'monitoring', 'action': 'ip'}\n"
                
                "- Query: 'Which namespace is the harbor service deployed to?'\n"
                "  Response: {'intent': 'list', 'resource_type': 'namespace', 'resource_name': 'harbor', 'action': 'list'}\n"
                
                "- Query: 'What is the container port for pod my-pod in the dev namespace?'\n"
                "  Response: {'intent': 'port', 'resource_type': 'pod', 'resource_name': 'my-pod', 'namespace': 'dev', 'action': 'port'}\n"
                
                "- Query: 'How old is the pod example-pod in the default namespace?'\n"
                "  Response: {'intent': 'age', 'resource_type': 'pod', 'resource_name': 'example-pod', 'namespace': 'default', 'action': 'age'}\n"
                
                "- Query: 'Show logs for pod nginx-pod in the web namespace'\n"
                "  Response: {'intent': 'logs', 'resource_type': 'pod', 'resource_name': 'nginx-pod', 'namespace': 'web', 'action': 'logs'}\n"
                
                "- Query: 'What is the value of the environment variable DATABASE_URL in pod backend-pod?'\n"
                "  Response: {'intent': 'environmentvariable', 'resource_type': 'pod', 'resource_name': 'backend-pod', 'namespace': 'default', 'action': 'environmentvariable', 'env_var_name': 'DATABASE_URL'}\n"
                
                "- Query: 'Which port does the redis service use in the staging namespace?'\n"
                "  Response: {'intent': 'port', 'resource_type': 'service', 'resource_name': 'redis', 'namespace': 'staging', 'action': 'port'}\n"
                
                "- Query: 'What is the readiness probe path for the app-server pod?'\n"
                "  Response: {'intent': 'readinessprobe', 'resource_type': 'pod', 'resource_name': 'app-server', 'namespace': 'default', 'action': 'readinessprobe'}\n\n"
                
                "Always follow these mappings and return JSON only, without additional text or commentary."
            )
        }



        user_message = {"role": "user", "content": f"Interpret this query: {query}"}

        response = client_openai.chat.completions.create(
            model="gpt-4",
            messages=[system_message, user_message],
            max_tokens=150,
            temperature=0.5
        )

        gpt_answer = response.choices[0].message.content.strip()
        logging.debug(f"GPT-4 response: {gpt_answer}")

        # Attempt to parse the GPT-4 response as JSON
        try:
            structured_response = json.loads(gpt_answer)
            logging.info(f"Parsed structured response: {structured_response}")
            return structured_response
        except json.JSONDecodeError:
            logging.error("Failed to parse GPT response as JSON.")
            return {
                "error": "Failed to interpret query as JSON.",
                "raw_response": gpt_answer
            }

    except Exception as e:
        logging.error(f"Error generating GPT-4 response: {e}", exc_info=True)
        return {
            "error": "An error occurred while querying GPT.",
            "details": str(e)
        }
