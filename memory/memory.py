"""
╔══════════════════════════════════════════════════════╗
║       memory/memory.py  —  Persistent Memory         ║
║   Reads/writes memory.json for user facts & notes    ║
╚══════════════════════════════════════════════════════╝
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# ─────────────────────────────────────────────────────
#  Internal state
# ─────────────────────────────────────────────────────
_EMPTY = {
    "notes":          [],   # list of {"text": str, "when": ISO-string}
    "facts_about_user": {},   # key → value  e.g. {"project": "OMEGA"}
    "reminders":      [],   # future use
}

_data: dict = {}   # loaded on first access


# ─────────────────────────────────────────────────────
#  Load / Save
# ─────────────────────────────────────────────────────
def _load() -> dict:
    """Load memory.json, or return an empty structure if missing/corrupt."""
    global _data
    if _data:
        return _data
    path = config.MEMORY_FILE
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                _data = json.load(f)
                # Ensure all expected keys exist
                for key, default in _EMPTY.items():
                    _data.setdefault(key, type(default)())
                return _data
        except Exception as exc:
            print(f"[Memory] Load error: {exc} — starting fresh.")
    _data = {k: (list() if isinstance(v, list) else dict()) for k, v in _EMPTY.items()}
    return _data


def _save() -> None:
    """Persist current in-memory state to memory.json."""
    try:
        os.makedirs(os.path.dirname(config.MEMORY_FILE), exist_ok=True)
        with open(config.MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(_data, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        print(f"[Memory] Save error: {exc}")


# ─────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────
def remember(note: str) -> None:
    """Store a plain-text note with a timestamp."""
    data = _load()
    data["notes"].append({
        "text": note,
        "when": datetime.now().isoformat(),
    })
    _save()
    print(f"[Memory] Remembered: {note!r}")


def recall_notes(n: int = 5) -> str:
    """Return the last `n` notes as a readable string."""
    data  = _load()
    notes = data.get("notes", [])
    if not notes:
        return "You have not asked me to remember anything yet sir."
    recent = notes[-n:]
    items  = "; ".join(entry["text"] for entry in recent)
    return f"Here is what I have got: {items}."


def set_fact(key: str, value: str) -> None:
    """Store a key-value fact about the user (e.g. project='OMEGA')."""
    data = _load()
    data["facts_about_user"][key.lower()] = value
    _save()
    print(f"[Memory] Fact: {key} = {value}")


def get_fact(key: str) -> str | None:
    """Retrieve a stored user fact by key, or None."""
    data = _load()
    return data.get("facts_about_user", {}).get(key.lower())


def all_facts() -> dict:
    """Return all stored user facts."""
    return _load().get("facts_about_user", {})


def forget(keyword: str) -> bool:
    """Remove notes that contain `keyword`. Returns True if anything was removed."""
    data   = _load()
    before = len(data["notes"])
    data["notes"] = [
        n for n in data["notes"] if keyword.lower() not in n["text"].lower()
    ]
    changed = len(data["notes"]) < before
    if changed:
        _save()
    return changed
