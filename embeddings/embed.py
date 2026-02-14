import os
import numpy as np
from typing import List, Union
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load from project root
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass

# Lazy load OpenAI client only when needed
_client = None


def _get_client():
    """Get or initialize OpenAI client."""
    global _client
    if _client is None:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please set your OpenAI API key to use embedding functions."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def _fallback_embedding(texts, model="text-embedding-3-large"):
    """
    Fallback to direct HTTP call to OpenAI embeddings endpoint.
    """
    import requests
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set for fallback embedding call.")
    url = "https://api.openai.com/v1/embeddings"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    # Accept either single string or list
    if isinstance(texts, str):
        payload = {"model": model, "input": texts}
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["embedding"]
    else:
        payload = {"model": model, "input": texts}
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in data.get("data", [])]


def embed_text(text: str) -> np.ndarray:
    """
    Embed a single text string.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector as numpy array
    """
    try:
        client = _get_client()
        resp = client.embeddings.create(model="text-embedding-3-large", input=text)
        return np.array(resp.data[0].embedding)
    except Exception as e:
        msg = str(e)
        if isinstance(e, TypeError) or "proxies" in msg.lower():
            emb = _fallback_embedding(text)
            return np.array(emb)
        raise


def embed_texts(texts: Union[List[str], str]) -> np.ndarray:
    """
    Embed one or more texts.
    
    Args:
        texts: Single text string or list of texts
        
    Returns:
        Embedding vector(s) as numpy array of shape (n, embedding_dim)
    """
    try:
        client = _get_client()
        # Handle single string
        if isinstance(texts, str):
            texts = [texts]

        vectors = []
        for text in texts:
            resp = client.embeddings.create(model="text-embedding-3-large", input=text)
            vectors.append(resp.data[0].embedding)

        return np.array(vectors)
    except Exception as e:
        msg = str(e)
        if isinstance(e, TypeError) or "proxies" in msg.lower():
            emb = _fallback_embedding(texts)
            return np.array(emb)
        raise


