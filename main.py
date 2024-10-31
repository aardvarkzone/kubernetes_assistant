# main.py

import logging
from flask import Flask, request, jsonify
from pydantic import ValidationError
from dotenv import load_dotenv

from config import load_kubernetes_config
from gpt_client import interpret_query_with_gpt
from k8s_client import handle_k8s_query
from models import QueryResponse
from utils import ensure_string

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("agent.log")]
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
    Sends the query to GPT for interpretation and then dynamically calls Kubernetes functions based on GPT's response.
    """
    # Interpret the query using GPT to get structured response
    structured_query = interpret_query_with_gpt(query)
    if not structured_query:
        return "Could not understand the query."

    # Pass structured query to Kubernetes handler
    answer = handle_k8s_query(structured_query)
    return ensure_string(answer)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
