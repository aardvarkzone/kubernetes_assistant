# main.py
import logging
from flask import Flask, request, jsonify
from pydantic import ValidationError
from dotenv import load_dotenv

from config import load_kubernetes_config
from gpt_client import get_gpt_response
from k8s_client import handle_k8s_query
from models import QueryResponse
from utils import ensure_string

load_dotenv()

# Configure loggings
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent.log"),
    ]
)

app = Flask(__name__)

# Load Kubernetes configuration
try:
    load_kubernetes_config()
    logging.info("Kubernetes configuration loaded successfully.")
except Exception as e:
    logging.error(f"Failed to load Kubernetes configuration: {e}")
    raise e

@app.route('/query', methods=['POST'])
def create_query():
    """
    Handles POST requests to the /query endpoint.
    Extracts the user's query, processes it, and returns the appropriate answer.
    """
    try:
        # Extract the query from the request data
        request_data = request.json
        if not request_data or 'query' not in request_data:
            logging.warning("Invalid request: 'query' field is missing.")
            return jsonify({"error": "Invalid request. 'query' field is required."}), 400

        query = request_data.get('query').strip()
        if not query:
            logging.warning("Empty query received.")
            return jsonify({"error": "Query cannot be empty."}), 400

        logging.info(f"Received query: {query}")
        answer = process_query(query)
        logging.info(f"Generated answer: {answer}")

        # Use Pydantic's validation for the response
        try:
            response = QueryResponse(query=query, answer=answer)
            return jsonify(response.model_dump())
        except ValidationError as e:
            logging.error(f"Validation error: {e}")
            return jsonify({"error": "Invalid data format.", "details": e.errors()}), 400

    except Exception as e:
        logging.error(f"Error processing query: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error."}), 500

def process_query(query):
    """
    Determines if the query is related to Kubernetes or requires GPT-4 assistance.
    Routes the query to the appropriate handler.
    """
    query_lower = query.lower()

    # Define keywords for K8s queries
    k8s_keywords = [
        "pod", "pods", "node", "nodes", "service", "services",
        "deployment", "deployments", "namespace", "namespaces"
    ]

    # Check if any K8s keyword is in the query
    if any(keyword in query_lower for keyword in k8s_keywords):
        logging.info("Kubernetes query detected.")
        answer = handle_k8s_query(query_lower, query)
    else:
        logging.info("Non-Kubernetes query detected, using GPT-4.")
        answer = get_gpt_response(query)

    # Use the utility function to ensure the answer is a string
    return ensure_string(answer)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
