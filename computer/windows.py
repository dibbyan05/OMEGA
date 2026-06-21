"""
╔══════════════════════════════════════════════════════╗
║      computer/windows.py  —  Window Management       ║
║   Uses pygetwindow + pyautogui                       ║
╚══════════════════════════════════════════════════════╝
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import pygetwindow as gw
    _GW_AVAILABLE = True
except ImportError:
    _GW_AVAILABLE = False
    print("[Windows] pygetwindow not found — window control limited.")

try:
    import pyautogui
    pyautogui.FAILSAFE = False   # prevent FailSafeException on corner moves
    _PAG_AVAILABLE = True
except ImportError:
    _PAG_AVAILABLE = False
    print("[Windows] pyautogui not found — hotkeys unavailable.")


# ─────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────
def _find_window(target: str):
    """Return the first window whose title contains target (case-insensitive)."""
    if not _GW_AVAILABLE:
        return None
    if target.lower() in ("current", "this", ""):
        wins = gw.getActiveWindow()
        return wins
    matches = gw.getWindowsWithTitle(target)
    if not matches:
        # fuzzy: any window containing any word of target
        tl = target.lower()
        for w in gw.getAllWindows():
            if tl in w.title.lower():
                return w
    return matches[0] if matches else None


# ─────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────
def maximize_window(target: str = "current") -> bool:
    w = _find_window(target)
    if w:
        try:
            w.maximize()
            print(f"[Windows] Maximized: {w.title!r}")
            return True
        except Exception as exc:
            print(f"[Windows] Maximize error: {exc}")
    elif _PAG_AVAILABLE:
        # fallback: Win+Up
        pyautogui.hotkey("win", "up")
        return True
    return False


def minimize_window(target: str = "current") -> bool:
    w = _find_window(target)
    if w:
        try:
            w.minimize()
            print(f"[Windows] Minimized: {w.title!r}")
            return True
        except Exception as exc:
            print(f"[Windows] Minimize error: {exc}")
    elif _PAG_AVAILABLE:
        pyautogui.hotkey("win", "down")
        return True
    return False


def close_window(target: str = "current") -> bool:
    w = _find_window(target)
    if w:
        try:
            w.close()
            print(f"[Windows] Closed: {w.title!r}")
            return True
        except Exception as exc:
            print(f"[Windows] Close error: {exc}")
    elif _PAG_AVAILABLE:
        pyautogui.hotkey("alt", "f4")
        return True
    return False


def switch_window() -> None:
    """Alt-Tab to the next window."""
    if _PAG_AVAILABLE:
        pyautogui.hotkey("alt", "tab")
        time.sleep(0.2)


def list_open_windows() -> list[str]:
    """Return titles of all visible windows."""
    if not _GW_AVAILABLE:
        return []
    return [w.title for w in gw.getAllWindows() if w.title.strip()]
