import logging
from openai import OpenAI
from config import get_openai_key

# Initialize OpenAI client with API key from config
client_openai = OpenAI(api_key=get_openai_key())

def get_gpt_response(query):
    """
    Sends a query to GPT-4 and returns the response.
    """
    try:
        system_message = {
            "role": "system",
            "content": "You are an AI assistant that helps answer questions about a Kubernetes cluster."
        }
        user_message = {"role": "user", "content": query}

        response = client_openai.chat.completions.create(
            model="gpt-4",
            messages=[system_message, user_message],
            max_tokens=150,
            temperature=0.5
        )

        gpt_answer = response.choices[0].message.content.strip()
        logging.debug(f"GPT-4 response: {gpt_answer}")
        return gpt_answer

    except Exception as e:
        logging.error(f"Error generating GPT-4 response: {e}", exc_info=True)
        return "I'm sorry, I couldn't process your request at the moment."
