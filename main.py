# main.py

import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from gpt_client import interpret_query_with_gpt
from k8s_client import handle_k8s_query
from utils import ensure_string

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("agent.log"), logging.StreamHandler()]
)

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def create_query():
    """
    Handles POST requests to the /query endpoint.
    Extracts the user's query, interprets it, and returns the output of the kubectl command.
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
        
        # Get structured response from GPT with kubectl command
        structured_query = interpret_query_with_gpt(query)
        if not structured_query or "error" in structured_query:
            return jsonify(structured_query), 500

        # Execute kubectl command based on GPT's response
        answer = handle_k8s_query(structured_query)
        logging.info(f"Generated answer: {answer}")

        return jsonify({"query": query, "answer": ensure_string(answer)})

    except Exception as e:
        logging.error(f"Error processing query: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
