"""
╔══════════════════════════════════════════════════════╗
║         brain/intent.py  —  Intent Classifier        ║
║   Wraps llm.classify_intent with fallback matching   ║
╚══════════════════════════════════════════════════════╝
"""

import json
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# ─────────────────────────────────────────────────────
#  Fast local keyword patterns
#  These are checked BEFORE hitting the API to save
#  latency for common, unambiguous commands.
# ─────────────────────────────────────────────────────
_LOCAL_PATTERNS = [
    # ── system ──────────────────────────────────────
    (r"\b(shutdown|shut down|power off)\b",            lambda _: {"action": "system_shutdown"}),
    (r"\b(restart|reboot)\b",                          lambda _: {"action": "system_restart"}),
    (r"\b(sleep|hibernate|sleep mode)\b",              lambda _: {"action": "system_sleep"}),
    (r"\b(lock|lock screen|lock computer|lock pc)\b",  lambda _: {"action": "system_lock"}),
    (r"\bbattery\b",                                   lambda _: {"action": "battery_status"}),
    (r"\bcpu\b|\bprocessor\b|\bram usage\b",           lambda _: {"action": "cpu_status"}),

    # ── time / date ──────────────────────────────────
    (r"\bwhat.?s the time\b|\bwhat time\b|\bcurrent time\b|\btell me the time\b",
                                                       lambda _: {"action": "time"}),
    (r"\bwhat.?s the date\b|\bwhat date\b|\btoday.?s date\b|\bwhat day is it\b",
                                                       lambda _: {"action": "date"}),

    # ── volume ───────────────────────────────────────
    (r"\bvolume up\b|\bincrease volume\b|\blouder\b",  lambda _: {"action": "volume_up"}),
    (r"\bvolume down\b|\bdecrease volume\b|\blower.*volume\b|\bmute\b",
                                                       lambda _: {"action": "volume_down"}),
    (r"\bset volume\b.*?(\d+)",
     lambda m: {"action": "set_volume", "level": int(m.group(1))}),

    # ── windows ──────────────────────────────────────
    (r"\bswitch window\b|\balt.?tab\b|\bnext window\b", lambda _: {"action": "switch_window"}),
    (r"\bmaximize\b\s*(.*)",
     lambda m: {"action": "maximize_window", "target": m.group(1).strip() or "current"}),
    (r"\bminimize\b\s*(.*)",
     lambda m: {"action": "minimize_window", "target": m.group(1).strip() or "current"}),

    # ── compound commands ("open chrome and search X") ─
    (r"^(?:open|launch|start)\s+\w+\s+and\s+(?:search|google|look up|find)\s+(.+?)(?:\s+on\s+(?:google|youtube))?$",
     lambda m: {"action": "search_google", "query": m.group(1).strip()}),
    (r"^(?:open|launch|start)\s+\w+\s+and\s+(?:play|watch)\s+(.+?)(?:\s+on\s+youtube)?$",
     lambda m: {"action": "search_youtube", "query": m.group(1).strip()}),

    # ── apps ─────────────────────────────────────────
    (r"^(?:open|launch|start)\s+(.+?)(?:\s+and\s+.+)?$",
     lambda m: {"action": "open_app", "target": m.group(1).strip()}),
    (r"^(?:close|exit|kill)\s+(.+)",
     lambda m: {"action": "close_app", "target": m.group(1).strip()}),

    # ── folders ──────────────────────────────────────
    (r"open (?:my\s+)?(downloads|documents|pictures|desktop|music|videos|appdata|onedrive)(?: folder)?",
     lambda m: {"action": "open_folder", "target": m.group(1)}),

    # ── web ──────────────────────────────────────────
    (r"(?:search|look up|google)\s+(.+?)(?:\s+on google)?$",
     lambda m: {"action": "search_google", "query": m.group(1).strip()}),
    (r"(?:search|find|play|watch)\s+(.+?)(?:\s+on youtube)?$",
     lambda m: {"action": "search_youtube", "query": m.group(1).strip()}),
    (r"open youtube",                                  lambda _: {"action": "open_website", "url": "https://www.youtube.com"}),

    # ── browser navigation ───────────────────────────
    (r"\bclick(?: the)? (1st|first|2nd|second|3rd|third|4th|fourth) link(?:\s+and\s+scroll)?",
     lambda m: {"action": "click_link", "target": m.group(1), "scroll": "scroll" in m.group(0).lower()}),
    (r"\b(?:scroll down|scroll through the page|scroll)\b", lambda _: {"action": "scroll_page", "direction": "down"}),
    (r"\bscroll up\b", lambda _: {"action": "scroll_page", "direction": "up"}),
    (r"\b(?:open (?:a )?(?:new|another) tab|new tab)\b", lambda _: {"action": "new_tab"}),

    # ── screenshot ───────────────────────────────────
    (r"\bscreenshot\b|\bcapture screen\b|\bsnapshot\b", lambda _: {"action": "take_screenshot"}),
    (r"\blook at (?:my )?screen\b|\bwhat.?s on (?:my )?screen\b",
                                                        lambda _: {"action": "look_at_screen"}),

    # ── memory ───────────────────────────────────────
    (r"^remember\s+(.+)",
     lambda m: {"action": "remember", "note": m.group(1).strip()}),
    (r"\brecall\b|\bwhat did you remember\b|\bshow (?:my\s+)?notes\b|\bwhat do you know\b",
                                                       lambda _: {"action": "recall"}),

    # ── files ────────────────────────────────────────
    (r"(?:find|locate|search for)\s+(?:file\s+)?(.+)",
     lambda m: {"action": "find_file", "query": m.group(1).strip()}),
    (r"(?:create|make)\s+file\s+(?:named|called)?\s*(.+)",
     lambda m: {"action": "create_file", "name": m.group(1).strip()}),
    (r"(?:create|make|new)\s+folder\s+(?:named|called)?\s*(.+)",
     lambda m: {"action": "create_folder", "name": m.group(1).strip()}),

    # ── email ────────────────────────────────────────
    (r"\b(?:send|write|compose|draft)\s+(?:an?\s+)?email\b",
                                                       lambda _: {"action": "send_email"}),

    # ── modes ────────────────────────────────────────
    (r"(?:activate|enable|start|switch to)\s+(\w+)\s+mode",
     lambda m: {"action": "custom_mode", "mode": m.group(1).lower()}),
    (r"^(\w+)\s+mode$",
     lambda m: {"action": "custom_mode", "mode": m.group(1).lower()}),
]

_CUSTOM_MODE_CACHE = {
    "path": None,
    "mtime": None,
    "names": (),
}


def _load_custom_mode_names() -> tuple[str, ...]:
    """Load custom mode names from commands/custom.json."""
    path = config.CUSTOM_FILE
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return ()

    if _CUSTOM_MODE_CACHE["path"] == path and _CUSTOM_MODE_CACHE["mtime"] == mtime:
        return _CUSTOM_MODE_CACHE["names"]

    names: tuple[str, ...] = ()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f) or {}
        if isinstance(data, dict):
            names = tuple(
                sorted({
                    str(name).strip().lower()
                    for name in data.keys()
                    if str(name).strip()
                })
            )
    except Exception as exc:
        print(f"[Intent] custom.json load error: {exc}")

    _CUSTOM_MODE_CACHE.update({
        "path": path,
        "mtime": mtime,
        "names": names,
    })
    return names


def get_custom_mode_intent(command: str) -> dict | None:
    """Return a custom-mode intent when the command targets a configured mode."""
    text = command.strip().lower()
    if not text:
        return None

    for mode in _load_custom_mode_names():
        escaped = re.escape(mode)
        if text == mode or text == f"{mode} mode":
            return {"action": "custom_mode", "mode": mode}
        if re.fullmatch(rf"(?:activate|enable|start|switch to)\s+{escaped}(?:\s+mode)?", text):
            return {"action": "custom_mode", "mode": mode}

    return None


def get_intent(command: str) -> dict:
    """
    Classify the user command into a structured intent dict.

    Strategy:
    1. Try fast local regex patterns (zero latency, no API call).
    2. If no match → call LLM (free Gemma model via OpenRouter).
    3. On any failure → default to {"action": "chat", "query": command}.
    """
    text = command.strip().lower()

    # ── Step 1: Local regex fast-path ─────────────────
    custom_mode = get_custom_mode_intent(command)
    if custom_mode:
        print(f"[Intent] Custom mode match -> {custom_mode}")
        return custom_mode

    for pattern, builder in _LOCAL_PATTERNS:
        m = re.search(pattern, text)
        if m:
            try:
                result = builder(m)
                if result:
                    print(f"[Intent] Local match -> {result}")
                    return result
            except Exception as e:
                print(f"[Intent] Local builder error: {e}")

    # ── Step 2: LLM classification ────────────────────
    print(f"[Intent] Sending to LLM: {text!r}")
    try:
        from brain import llm
        result = llm.classify_intent(command)
        print(f"[Intent] LLM result -> {result}")
        return result
    except Exception as exc:
        print(f"[Intent] LLM error: {exc}")

    # ── Step 3: Fallback ──────────────────────────────
    return {"action": "chat", "query": command}
