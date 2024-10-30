# Kubernetes Query Assistant

This project is an AI-powered assistant that interacts with a Kubernetes cluster (via Minikube) to answer queries about the cluster's resources such as pods, nodes, namespaces, and services. It processes queries by either querying the Kubernetes API or using OpenAI's GPT-4 for more general questions.

## Project Structure

### `main.py`

The main entry point of the application, responsible for initializing the Flask API and processing user queries.

- **`/query`** (POST): Processes the user's query and routes it either to the Kubernetes API or GPT-4 woth `create_query(query)`.
- **`process_query(query)`**: Determines if the query is related to Kubernetes and handles it accordingly.

### `config.py`

- **`load_kubernetes_config()`**: Loads the Kubernetes configuration (e.g., `kubeconfig`) for local development.
- **`get_openai_key()`**: Retrieves the OpenAI API key from environment variables.

### `gpt_client.py`

Handles communication with GPT-4 using the OpenAI API.

### `k8s_client.py`

Handles queries to the Kubernetes API, such as:

- Counting pods, nodes, services.
- Getting the status of nodes or pods.
- Listing namespaces and services.

### `logs.py`

Configures logging, writing logs to `agent.log`.

### `models.py`

Defines the `QueryResponse` Pydantic model for validating query responses.

### `utils.py`

- **`extract_resource_name(query, resource_type)`**: Extracts the name of Kubernetes resources (e.g., pod, node) from a query.
- **`get_generic_name(resource_name)`**: Strips unique identifiers from resource names.
- **`ensure_string(answer)`**: Ensures responses are returned as strings for compatibility.

## Requirements

- Python 3.10
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Environment Variables

Create a `.env` file at the project root with the following:

```bash
OPENAI_API_KEY=your-openai-api-key
```

## Setup Instructions

### 1. Install Dependencies

Install the necessary Python packages:

```bash
pip install -r requirements.txt
```

Ensure `requirements.txt` includes:

```
requests
Flask
pydantic
kubernetes
openai
python-dotenv
datetime
logging
os
dotenv
```

### 2. Start Minikube

Start a local Kubernetes cluster with:

```bash
minikube start
```

### 3. Test Kubernetes Setup

Verify that Minikube is running correctly:

```bash
kubectl get nodes
kubectl get pods -A
```

### 4. Run the Application

Start the Flask app:

```bash
python main.py
```

The application will run on `localhost:8000`.

### 5. Example Queries

You can send queries to the `/query` endpoint. Some examples:

- **Pods Query**:
  ```json
  {
      "query": "How many pods are there?"
  }
  ```

- **Node Count Query**:
  ```json
  {
      "query": "How many nodes are in the cluster?"
  }
  ```

- **Namespace Query**:
  ```json
  {
      "query": "List all namespaces."
  }
  ```

- **Service Query**:
  ```json
  {
      "query": "How many services are running?"
  }
  ```

Use a tool like [Postman](https://www.postman.com/) or `curl` to test the API:

```bash
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query": "How many nodes are in the cluster?"}'
```

## Logging

Logs are written to `agent.log` in the project root.

---

## My Process

### Understanding Kubernetes and Revising My Approach

At the beginning of this project, my experience with Kubernetes was limited. I took time to familiarize myself with Kubernetes concepts, such as pods, services, nodes, and namespaces, to ensure I could accurately query these resources. Initially, I misunderstood the assignment, and my initial attempt involved setting up the program within a Kubernetes cluster itself. After revisiting the assignment requirements, I realized that running the program locally was the intended setup, and I shifted my approach to executing everything via local Kubernetes (Minikube) and the Kubernetes API.

### Leveraging GPT-4

I also used GPT-4 to assist me in creating a list of potential queries. This step was vital in ensuring my program could answer a wide range of Kubernetes-related questions. GPT-4 helped me brainstorm various possible user queries that could be sent to the API, covering aspects like pod status, node count, service details, and namespace information. Trying to cover the scope of potential questions also gave me deeper knowledge about Kubernetes, as I worked to understand how to interact with its resources—such as pods, nodes, services, and namespaces—in a meaningful way. This process enhanced my understanding of Kubernetes' API and the resources it manages. I also used GPT-4 to assist in writing comments and this readme file. 

---
