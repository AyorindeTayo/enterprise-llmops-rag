"""LLM service for generating answers using context."""

import os
import requests
from typing import Optional
from pathlib import Path
from datetime import datetime

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
                "Please set your OpenAI API key to use LLM functions."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def _fallback_chat_completion(messages, model="gpt-4o", temperature=0.7, max_tokens=1000):
    """
    Fallback to direct HTTP call to OpenAI REST API if client instantiation fails.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set for fallback HTTP call.")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # backwards-compatible extraction
    if "choices" in data and len(data["choices"]) > 0:
        # support both new and old shapes
        choice = data["choices"][0]
        if isinstance(choice.get("message"), dict):
            return choice["message"].get("content", "")
        return choice.get("text", "")
    return ""


def _get_demo_answer(question: str, context: str) -> str:
    """Generate a demo answer for testing without API calls."""
    # Check for common questions
    if "date" in question.lower():
        return f"Based on the context provided ({context}), the current date is February 13, 2026."
    elif "time" in question.lower():
        return f"The current time is {datetime.now().strftime('%H:%M:%S')}."
    else:
        return f"Based on the provided context: '{context}', I can help answer your question about '{question}'."


def generate_answer(question: str, context: str, model: str = "gpt-4o", temperature: float = 0.7, use_demo: bool = False) -> str:
    """
    Generate answer to a question using provided context.
    
    Args:
        question: User's question
        context: Retrieved context to base the answer on
        model: OpenAI model to use (default: gpt-4o)
        temperature: Temperature for generation (0-1, default: 0.7)
        use_demo: Use demo mode (no API calls) for testing
        
    Returns:
        Generated answer string
    """
    try:
        # Use demo mode if requested (useful for testing without API quota)
        if use_demo:
            return _get_demo_answer(question, context)
        
        client = _get_client()
        
        system_prompt = """You are a helpful assistant that answers questions based on provided context.
Always use the context provided to answer the question accurately. 
If the context doesn't contain relevant information, say so clearly.
Provide clear, concise, and accurate answers."""

        user_message = f"""Context:
{context}

Question: {question}

Based on the context above, please answer the question."""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        return answer
        
    except Exception as e:
        msg = str(e)
        if isinstance(e, TypeError) or "proxies" in msg.lower():
            try:
                # build prompts here in case _get_client() failed before they were defined
                system_prompt = """You are a helpful assistant that answers questions based on provided context.
Always use the context provided to answer the question accurately. 
If the context doesn't contain relevant information, say so clearly.
Provide clear, concise, and accurate answers."""

                user_message = f"""Context:
{context}

Question: {question}

Based on the context above, please answer the question."""

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ]
                return _fallback_chat_completion(messages, model=model, temperature=temperature)
            except Exception as e2:
                return f"Error generating answer: {str(e2)}"
        return f"Error generating answer: {msg}"


def generate_summary(text: str, model: str = "gpt-4o", use_demo: bool = False) -> str:
    """
    Generate a summary of the provided text.
    
    Args:
        text: Text to summarize
        model: OpenAI model to use
        use_demo: Use demo mode for testing
        
    Returns:
        Summary string
    """
    try:
        if use_demo:
            return f"Summary: {text[:200]}..." if len(text) > 200 else f"Summary: {text}"
        
        client = _get_client()
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                {"role": "user", "content": f"Please provide a concise summary of the following text:\n\n{text}"}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        msg = str(e)
        if isinstance(e, TypeError) or "proxies" in msg.lower():
            try:
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                    {"role": "user", "content": f"Please provide a concise summary of the following text:\n\n{text}"}
                ]
                return _fallback_chat_completion(messages, model=model)
            except Exception as e2:
                return f"Error generating summary: {str(e2)}"
        return f"Error generating summary: {msg}"


def rephrase_question(question: str, model: str = "gpt-4o", use_demo: bool = False) -> str:
    """
    Rephrase a question for better retrieval.
    
    Args:
        question: Original question
        model: OpenAI model to use
        use_demo: Use demo mode for testing
        
    Returns:
        Rephrased question
    """
    try:
        if use_demo:
            return question  # In demo mode, return original
        
        client = _get_client()
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that rephrases questions to be clearer and more specific for document retrieval."},
                {"role": "user", "content": f"Rephrase the following question to make it clearer and more specific:\n{question}"}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        msg = str(e)
        if isinstance(e, TypeError) or "proxies" in msg.lower():
            try:
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that rephrases questions to be clearer and more specific for document retrieval."},
                    {"role": "user", "content": f"Rephrase the following question to make it clearer and more specific:\n{question}"}
                ]
                return _fallback_chat_completion(messages, model=model, temperature=0.3)
            except Exception:
                return question
        return question  # Return original if rephrasing fails


def extract_keywords(text: str, model: str = "gpt-4o", use_demo: bool = False) -> list:
    """
    Extract keywords from text.
    
    Args:
        text: Text to extract keywords from
        model: OpenAI model to use
        use_demo: Use demo mode for testing
        
    Returns:
        List of keywords
    """
    try:
        if use_demo:
            # Simple keyword extraction in demo mode
            words = text.lower().split()
            return [w.strip('.,!?;:') for w in words if len(w) > 3][:5]
        
        client = _get_client()
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Extract the main keywords from the text and return them as a comma-separated list."},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        keywords_text = response.choices[0].message.content
        keywords = [kw.strip() for kw in keywords_text.split(",")]
        return keywords
        
    except Exception as e:
        msg = str(e)
        if isinstance(e, TypeError) or "proxies" in msg.lower():
            try:
                messages = [
                    {"role": "system", "content": "Extract the main keywords from the text and return them as a comma-separated list."},
                    {"role": "user", "content": text}
                ]
                resp = _fallback_chat_completion(messages, model=model, temperature=0.3)
                return [kw.strip() for kw in resp.split(",") if kw.strip()]
            except Exception:
                return []
        return []


