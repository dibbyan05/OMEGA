"""
╔══════════════════════════════════════════════════════╗
║       vision/screen.py  —  Screen Vision             ║
║   Screenshot via PIL + free vision LLM description   ║
╚══════════════════════════════════════════════════════╝
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from PIL import ImageGrab
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False
    print("[Vision] Pillow not installed — screenshots unavailable.")


# ─────────────────────────────────────────────────────
#  Screenshot capture
# ─────────────────────────────────────────────────────
def take_screenshot(save_dir: str = None) -> str | None:
    """
    Capture the full screen and save it as a PNG.
    Saves to Desktop by default.
    Returns the full file path on success, None on failure.
    """
    if not _PIL_AVAILABLE:
        print("[Vision] Pillow unavailable — cannot take screenshot.")
        return None

    try:
        save_dir = save_dir or os.path.expanduser("~\\Desktop")
        os.makedirs(save_dir, exist_ok=True)

        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"omega_screenshot_{ts}.png"
        path     = os.path.join(save_dir, filename)

        img = ImageGrab.grab()
        img.save(path)
        print(f"[Vision] Screenshot saved: {path}")
        return path

    except Exception as exc:
        print(f"[Vision] Screenshot error: {exc}")
        return None


# ─────────────────────────────────────────────────────
#  Screen description via free vision LLM
# ─────────────────────────────────────────────────────
def describe(image_path: str) -> str:
    """
    Send the screenshot to the free Llama 3.2 Vision model on OpenRouter
    and return a natural-language description of what is on screen.
    """
    if not image_path or not os.path.exists(image_path):
        return "I could not find the screenshot to analyse, sir."

    try:
        from brain.llm import describe_screen
        return describe_screen(image_path)
    except Exception as exc:
        print(f"[Vision] describe error: {exc}")
        return "Sorry sir, I had trouble reading the screen. Let me try again."


# ─────────────────────────────────────────────────────
#  Convenience: capture + describe in one call
# ─────────────────────────────────────────────────────
def look_at_screen() -> str:
    """
    Take a screenshot and return a vision-model description.
    Convenience wrapper for the planner.
    """
    path = take_screenshot()
    if not path:
        return "I was unable to capture your screen sir. Make sure Pillow is installed."
    return describe(path)
