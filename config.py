from kubernetes import config
from kubernetes.config.config_exception import ConfigException
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def load_kubernetes_config():
    """
    Loads the Kubernetes configuration from the kubeconfig file.
    """
    try:
        config.load_kube_config()
        logging.info("Success loading kubeconfig.")
    except ConfigException as e:
        logging.error(f"Failed to load kubeconfig: {e}")
        raise e

def get_openai_key():
    """
    Retrieves the OpenAI API key from environment variables.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("OPENAI_API_KEY not found in environment variables.")
        raise EnvironmentError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")
    return api_key
