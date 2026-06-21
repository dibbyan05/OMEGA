"""
╔══════════════════════════════════════════════════════╗
║       voice/wakeword.py  —  Wake-word Detector       ║
║   Runs two daemons:                                  ║
║     • wake_loop()  — detects "Omega" / "Hey Omega" ║
║     • stop_loop()  — detects "Omega stop"           ║
╚══════════════════════════════════════════════════════╝
"""

import os
import sys
import threading
import time
import speech_recognition as sr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# ─────────────────────────────────────────────────────
#  Shared event objects
# ─────────────────────────────────────────────────────
wake_event = threading.Event()   # set when wake word detected
stop_event = threading.Event()   # set when "omega stop" detected

# Separate recogniser for each background listener thread
_wake_recognizer = sr.Recognizer()
_stop_recognizer = sr.Recognizer()

_wake_recognizer.energy_threshold         = config.SR_ENERGY_THRESHOLD
_wake_recognizer.dynamic_energy_threshold = config.SR_DYNAMIC_ENERGY
_wake_recognizer.pause_threshold          = config.SR_PAUSE_THRESHOLD

_stop_recognizer.energy_threshold         = config.SR_ENERGY_THRESHOLD
_stop_recognizer.dynamic_energy_threshold = config.SR_DYNAMIC_ENERGY
_stop_recognizer.pause_threshold          = config.SR_PAUSE_THRESHOLD


# ─────────────────────────────────────────────────────
#  Inline wake-word check
# ─────────────────────────────────────────────────────
def heard_wake(text: str) -> bool:
    return any(w in text for w in config.WAKE_WORDS)


def strip_wake(text: str) -> str:
    """Remove the wake-word prefix and return the remainder."""
    for w in sorted(config.WAKE_WORDS, key=len, reverse=True):
        if w in text:
            idx = text.find(w)
            return text[idx + len(w):].strip(" ,.!?")
    return text


# ─────────────────────────────────────────────────────
#  Background: stop-word listener
#  Continuously monitors mic for "Omega stop" and sets
#  stop_event + calls tts.stop_speaking() immediately.
# ─────────────────────────────────────────────────────
def _stop_listener_loop():
    while True:
        try:
            with sr.Microphone() as source:
                audio = _stop_recognizer.listen(source, timeout=2, phrase_time_limit=3)
            said = _stop_recognizer.recognize_google(audio).lower()
            if any(sw in said for sw in config.STOP_WORDS):
                stop_event.set()
                try:
                    from voice.tts import stop_speaking
                    stop_speaking()
                except Exception:
                    pass
                print("[WakeWord] STOP detected.")
        except Exception:
            time.sleep(0.5)  # Prevent CPU burn on timeout or mic noise


def start_stop_listener() -> threading.Thread:
    """Start the background stop-word listener daemon thread."""
    t = threading.Thread(target=_stop_listener_loop, daemon=True, name="StopListener")
    t.start()
    return t
