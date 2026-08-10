"""LLM factory: OpenAI-compatible chat endpoints.

Default is Gemini's free tier. Groq is included as an alternative (free, no
credit card, open-weight US models, ~14,400 requests/day vs Gemini's ~20).
Any other OpenAI-compatible endpoint — NERSC, ALCF, a local vLLM/Ollama —
works the same way: one more entry in PROVIDERS.
"""

import os

from langchain_openai import ChatOpenAI

PROVIDERS = {
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key_env": "GOOGLE_API_KEY",
        # rolling alias: some pinned models (e.g. gemini-2.5-flash) are closed
        # to new API accounts and 404 for them
        "default_model": "gemini-flash-latest",
        "key_url": "https://aistudio.google.com/apikey",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "default_model": "openai/gpt-oss-120b",
        "key_url": "https://console.groq.com/keys",
    },
}


def make_llm(provider: str = "gemini", model: str | None = None,
             temperature: float = 0.0) -> ChatOpenAI:
    cfg = PROVIDERS[provider]
    api_key = os.environ.get(cfg["key_env"])
    if not api_key:
        raise RuntimeError(
            f"{cfg['key_env']} is not set. Get a free key at {cfg['key_url']} "
            "and put it in a .env file (see .env.example), then call "
            "load_dotenv() before make_llm()."
        )
    return ChatOpenAI(
        model=model or cfg["default_model"],
        base_url=cfg["base_url"],
        api_key=api_key,
        temperature=temperature,
    )
