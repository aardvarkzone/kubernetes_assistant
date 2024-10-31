# Kubernetes Query Assistant

This project is an AI-powered assistant that interprets and responds to Kubernetes-related queries using a combination of Kubernetes `kubectl` commands and OpenAI's GPT-4 model. The assistant interacts with a local Kubernetes cluster (via Minikube) to answer queries about the cluster's resources such as pods, nodes, namespaces, and services.

## Project Structure

### `main.py`

The main entry point of the application, responsible for initializing the Flask API and processing user queries.

- **`/query`** (POST): Processes the user's query, sends it to GPT-4 for interpretation, and executes the response if it involves a Kubernetes command.
- **Error Handling**: If a query doesn't involve a specific Kubernetes command, a general response is provided by GPT-4.

### `gpt_client.py`

Handles communication with GPT-4 using the OpenAI API and returns structured responses.

- **`interpret_query_with_gpt(query)`**: Interprets a query and generates a `kubectl` command if relevant. If no specific command is appropriate, it provides a general response.

### `k8s_client.py`

Handles execution of Kubernetes-related queries.

- **`execute_kubectl_command(kubectl_command)`**: Executes provided `kubectl` commands and returns their output.
- **`handle_k8s_query(structured_query)`**: Processes structured queries, either executing a Kubernetes command or returning a general response.

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

At the beginning of this project, my experience with Kubernetes was limited. To ensure I could accurately interact with Kubernetes resources such as pods, services, nodes, and namespaces, I dedicated time to learning about each concept. Initially, I misunderstood the assignment and began setting up the program within a Kubernetes cluster itself. After revisiting the project requirements, I realized the intended setup was to run the program locally and interact with a local Kubernetes (Minikube) cluster via the Kubernetes API. This realization allowed me to shift focus from in-cluster setup to managing local API interactions effectively.

### Evolving My Approach to Query Interpretation with GPT-4

My initial approach for handling user queries involved creating a detailed intent and action mapping. I aimed to "train" GPT-4 myself by setting up a strict structure where each type of Kubernetes question (e.g., counting pods, checking node status) would be mapped to specific intents and corresponding actions. For each query type, I predefined the necessary actions and conditions, aiming to guide GPT-4 on what Kubernetes information to extract and how to interpret each query.

As I experimented, I realized that GPT-4 could handle these interpretations much more flexibly and accurately if it was allowed to generate specific `kubectl` commands on its own. I adapted my approach to let GPT-4 generate appropriate commands dynamically, removing the need for manually defined mappings. This change streamlined the process, allowing GPT-4 to handle a broader variety of questions naturally. Now, if the query requires a general Kubernetes explanation (like "What is Kubernetes?"), GPT-4 provides an informative response instead of generating a `kubectl` command, ensuring the assistant remains helpful across a range of question types.

### Leveraging GPT-4 for Comprehensive Query Handling

GPT-4 has been instrumental in brainstorming potential queries and structuring informative responses. Working with GPT-4 to anticipate possible user questions—from specific resource checks to general Kubernetes inquiries—helped me deepen my understanding of Kubernetes API interactions and the resources it manages. Additionally, GPT-4 provided insights into improving code readability, commenting, and this README file, making the overall project more comprehensive and user-friendly.
