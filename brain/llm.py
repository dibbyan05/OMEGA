"""
╔══════════════════════════════════════════════════════╗
║           brain/llm.py  —  OpenRouter Client         ║
║   ALL FREE: gemma-4-31b-it + llama-3.2-vision:free   ║
╚══════════════════════════════════════════════════════╝
"""

import base64
import json
import re
import sys
import os

import requests

# Allow running standalone for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# ─────────────────────────────────────────────────────
#  Conversation history  (multi-turn context)
# ─────────────────────────────────────────────────────
_history: list[dict] = []


def _clean(text: str) -> str:
    """Strip markdown symbols so speech sounds natural."""
    text = re.sub(r"\*\*|__|\*|_|`|#+|>|\[|\]|\{|\}|\|", "", text)
    text = re.sub(r"\\n|\n|\r", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def _post(messages: list[dict], model: str, max_tokens: int = None) -> str:
    """Low-level POST to OpenRouter; returns assistant reply text."""
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type":  "application/json",
        "HTTP-Referer":  "https://omega-local",
        "X-Title":       "OMEGA",
    }
    payload = {
        "model":      model,
        "messages":   messages,
        "max_tokens": max_tokens or config.MAX_TOKENS,
    }
    resp = requests.post(config.OPENROUTER_URL, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


# ─────────────────────────────────────────────────────
#  Public: text chat
# ─────────────────────────────────────────────────────
def chat(user_message: str, extra_context: str = "") -> str:
    """
    Send a user message to the free Gemma model.
    Maintains rolling conversation history.
    Returns the cleaned assistant reply.
    """
    global _history

    content = user_message
    if extra_context:
        content = f"[Web context: {extra_context}]\n\nUser: {user_message}"

    _history.append({"role": "user", "content": content})

    # Keep history within token budget
    max_pairs = config.MAX_HISTORY_TURNS * 2
    if len(_history) > max_pairs:
        _history = _history[-max_pairs:]

    messages = [{"role": "system", "content": config.OMEGA_PERSONA}] + _history

    try:
        reply = _post(messages, config.TEXT_MODEL)
        reply = _clean(reply)
        _history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as exc:
        print(f"[LLM] chat error: {exc}")
        return _fallback(user_message)


# ─────────────────────────────────────────────────────
#  Public: intent classification
# ─────────────────────────────────────────────────────
def classify_intent(user_command: str) -> dict:
    """
    Ask the free Gemma model to classify the user command
    into a structured JSON intent object.
    Returns a dict; on parse failure returns {"action":"chat","query": <command>}.
    """
    messages = [
        {"role": "system", "content": config.INTENT_SYSTEM_PROMPT},
        {"role": "user",   "content": user_command},
    ]
    try:
        raw = _post(messages, config.TEXT_MODEL, max_tokens=120)
        # Extract JSON even if the model wraps it in markdown fences
        match = re.search(r"\{.*?\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(raw.strip())
    except Exception as exc:
        print(f"[LLM] intent parse error: {exc} | raw: {raw!r}")
        return {"action": "chat", "query": user_command}


# ─────────────────────────────────────────────────────
#  Public: vision — describe a screenshot
# ─────────────────────────────────────────────────────
def describe_screen(image_path: str) -> str:
    """
    Encode a screenshot and send it to the free Llama 3.2 Vision model.
    Returns a natural-language description of the screen.
    FREE model: meta-llama/llama-3.2-11b-vision-instruct:free
    """
    try:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are OMEGA, a smart AI assistant. "
                    "Describe what is visible on this screenshot in 2-3 natural sentences. "
                    "Be specific about open apps, windows, or content. "
                    "Speak like a helpful friend, not a robot."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    },
                    {
                        "type": "text",
                        "text": "What do you see on my screen right now?",
                    },
                ],
            },
        ]

        reply = _post(messages, config.VISION_MODEL, max_tokens=200)
        return _clean(reply)

    except Exception as exc:
        print(f"[LLM] vision error: {exc}")
        return "Sorry sir, I had trouble analysing the screen. Let me try again in a moment."


# ─────────────────────────────────────────────────────
#  Offline fallback when API is unreachable
# ─────────────────────────────────────────────────────
def _fallback(query: str) -> str:
    from datetime import datetime
    q = query.lower()
    if any(w in q for w in ["time", "clock"]):
        return f"It is {datetime.now().strftime('%I:%M %p')}, sir."
    if "date" in q:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
    return (
        "My connection seems a bit slow right now, sir. "
        "Give me a second and try again."
    )


def reset_history():
    """Clear conversation history (e.g. on new session)."""
    global _history
    _history = []
