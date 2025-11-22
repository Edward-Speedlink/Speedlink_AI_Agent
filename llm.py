import requests

OLLAMA_API = "http://localhost:11434/api/generate"

def query_deepseek(prompt: str, model: str = "deepseek-r1:7b") -> str:
    """
    Send a prompt to the local Ollama DeepSeek model and return the response.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except Exception as e:
        return f"Error querying DeepSeek: {e}"
