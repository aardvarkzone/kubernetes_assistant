# utils.py
import re
import logging

def extract_resource_name(query, resource_type):
    """
    Extracts the name of a Kubernetes resource (node, pod, service, etc.) from the user's query.
    """
    patterns = {
        "node": r"node\s+(?:named|with name)\s+['\"]?([\w\-]+)['\"]?",
        "deployment": r"deployment\s+(?:named|with name)\s+['\"]?([\w\-]+)['\"]?",
        "pod": r"pod\s+(?:named|with name)\s+['\"]?([\w\-]+)['\"]?",
        "service": r"service\s+(?:named|with name)\s+['\"]?([\w\-]+)['\"]?",
        "namespace": r"namespace\s+(?:named|with name)\s+['\"]?([\w\-]+)['\"]?"
    }

    if resource_type in patterns:
        match = re.search(patterns[resource_type], query, re.IGNORECASE)
        if match:
            return match.group(1)
        logging.debug(f"No {resource_type} name found in the query.")
        return None
    else:
        logging.error(f"Invalid resource type: {resource_type}")
        return None

def get_generic_name(resource_name):
    """
    Generalizes the resource name by removing unique identifiers (e.g., hashes) from the name.
    """
    return re.split(r"-[a-z0-9]{8,10}$", resource_name)[0]

def ensure_string(answer):
    """
    Ensures the answer is a string. If it's not, it converts it to a string.
    """
    if not isinstance(answer, str):
        return str(answer)
    return answer
