"""LLM factory: OpenAI-compatible chat endpoints.

Default is Gemini's free tier. Groq is included as an alternative (free, no
credit card, open-weight US models, ~14,400 requests/day vs Gemini's ~20).
Any other OpenAI-compatible endpoint — NERSC, ALCF, a local vLLM/Ollama —
works the same way: one more entry in PROVIDERS.
"""

import os

from langchain_openai import ChatOpenAI

# Gemini 3 models reject replayed tool calls that lack a "thought signature"
# (HTTP 400). The real signature is dropped by the OpenAI-compat round trip,
# but Google documents a dummy value that skips validation for exactly this
# case: https://ai.google.dev/gemini-api/docs/thinking#signatures
_DUMMY_THOUGHT_SIGNATURE = "context_engineering_is_the_way_to_go"


class _GeminiChat(ChatOpenAI):
    """ChatOpenAI that stamps the documented dummy thought signature onto
    every replayed assistant tool call, so multi-turn tool use works against
    Gemini 3 models through the OpenAI-compatible endpoint."""

    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        for message in payload.get("messages", []):
            if message.get("role") == "assistant":
                for tool_call in message.get("tool_calls") or []:
                    tool_call.setdefault(
                        "extra_content",
                        {"google": {"thought_signature": _DUMMY_THOUGHT_SIGNATURE}},
                    )
        return payload


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
    chat_class = _GeminiChat if provider == "gemini" else ChatOpenAI
    return chat_class(
        model=model or cfg["default_model"],
        base_url=cfg["base_url"],
        api_key=api_key,
        temperature=temperature,
    )
