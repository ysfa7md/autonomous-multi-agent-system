import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

HAS_KEY = bool(os.environ.get("GROQ_API_KEY"))


def get_llm(model: str = "llama-3.3-70b-versatile", temperature: float = 0.2):
    """Return a configured ChatGroq instance, or None if no API key is set."""
    if not HAS_KEY:
        return None
    return ChatGroq(model=model, temperature=temperature)


def extract_tokens(response) -> int:
    """
    Best-effort token extraction across LangChain/Groq response shapes.
    Never raises — returns 0 if usage metadata isn't available.
    """
    try:
        usage = getattr(response, "usage_metadata", None)
        if usage:
            return int(usage.get("total_tokens", 0))
    except Exception:
        pass

    try:
        meta = getattr(response, "response_metadata", {}) or {}
        usage = meta.get("token_usage", {}) or {}
        if usage:
            return int(usage.get("total_tokens", 0))
    except Exception:
        pass

    return 0
