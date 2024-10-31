# gpt_client.py

import logging
import json
from openai import OpenAI
from config import get_openai_key

# Initialize OpenAI client with API key from config
client_openai = OpenAI(api_key=get_openai_key())

def interpret_query_with_gpt(query):
    """
    Sends a query to GPT to interpret and return a structured response with a kubectl command.
    If the query is general, returns a generic response instead of a kubectl command.
    """
    try:
        system_message = {
            "role": "system",
            "content": (
                "You are an AI assistant that interprets Kubernetes-related queries and returns structured JSON responses.\n"
                "For each query, try to generate a 'kubectl' command that will execute the requested action.\n\n"
                
                "Fields in response JSON:\n"
                "- 'kubectl_command': The exact kubectl command to run to satisfy the query.\n"
                
                "Examples:\n"
                "- Query: 'How many pods are in the default namespace?'\n"
                "  Response: {\"kubectl_command\": \"kubectl get pods -n default --no-headers | wc -l\"}\n"
                
                "- Query: 'What is the IP of the pod nginx in the web namespace?'\n"
                "  Response: {\"kubectl_command\": \"kubectl get pod nginx -n web -o=jsonpath='{.status.podIP}'\"}\n"
                
                "- Query: 'Show logs for pod my-pod in the default namespace.'\n"
                "  Response: {\"kubectl_command\": \"kubectl logs my-pod -n default\"}\n\n"
                
                "If the query does not involve a specific Kubernetes command, respond with a generic answer in the following JSON format:\n"
                "{\"general_response\": \"<informative answer here>\"}\n"
                
                "Respond with the JSON only, without additional commentary."
            )
        }

        user_message = {"role": "user", "content": f"Interpret this query: {query}"}

        response = client_openai.chat.completions.create(
            model="gpt-4",
            messages=[system_message, user_message],
            max_tokens=100,
            temperature=0.3
        )

        gpt_answer = response.choices[0].message.content.strip()
        logging.debug(f"GPT-4 response: {gpt_answer}")

        # Parse the GPT-4 response as JSON
        try:
            structured_response = json.loads(gpt_answer)
            logging.info(f"Parsed structured response: {structured_response}")
            
            # Check if there's a 'kubectl_command' key in the response
            if 'kubectl_command' not in structured_response:
                # Return the general response if it's a more informative answer
                return {"general_response": structured_response.get("general_response", "No specific command or answer available.")}

            return structured_response

        except json.JSONDecodeError:
            logging.error("Failed to parse GPT response as JSON.")
            return {"error": "Failed to interpret query as JSON.", "raw_response": gpt_answer}

    except Exception as e:
        logging.error(f"Error generating GPT-4 response: {e}", exc_info=True)
        return {"error": "An error occurred while querying GPT.", "details": str(e)}
