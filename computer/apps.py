"""
╔══════════════════════════════════════════════════════╗
║       computer/apps.py  —  Application Control       ║
║   Open, close, and auto-detect installed apps        ║
╚══════════════════════════════════════════════════════╝
"""

import os
import re
import sys
import subprocess
import winreg
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# ─────────────────────────────────────────────────────
#  Open app by name (using hardcoded APP_MAP)
# ─────────────────────────────────────────────────────
def open_app(name: str) -> bool:
    """
    Try to open an application by name using the APP_MAP in config.
    Returns True on success, False if not found.
    """
    name = name.lower().strip()

    # Direct match
    path = config.APP_MAP.get(name)

    # Fuzzy match
    if not path:
        for key, val in config.APP_MAP.items():
            if key in name or name in key:
                path = val
                break

    if not path:
        return False

    try:
        # Chrome special handling: use list-based Popen to avoid
        # shell splitting on spaces in "Program Files", and add
        # flags to bypass the profile picker.
        if "chrome.exe" in path.lower() and os.path.exists(path):
            subprocess.Popen([
                path,
                "--profile-directory=Default",
                "--no-profile-manager",
            ])
        else:
            subprocess.Popen(path, shell=True)
        print(f"[Apps] Opened: {name} -> {path}")
        return True
    except Exception as exc:
        print(f"[Apps] Open error ({name}): {exc}")
        return False


# ─────────────────────────────────────────────────────
#  Smart open — scans registry + Start Menu shortcuts
# ─────────────────────────────────────────────────────
_registry_cache: dict[str, str] = {}   # name -> exe path


def _build_registry_cache():
    """Scan Windows Uninstall registry keys for installed app paths."""
    global _registry_cache
    if _registry_cache:
        return   # already built

    hives = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]

    for hive, subkey in hives:
        try:
            reg = winreg.OpenKey(hive, subkey)
            for i in range(winreg.QueryInfoKey(reg)[0]):
                try:
                    sub_name = winreg.EnumKey(reg, i)
                    sub_key  = winreg.OpenKey(reg, sub_name)
                    try:
                        disp = winreg.QueryValueEx(sub_key, "DisplayName")[0].lower()
                        loc  = winreg.QueryValueEx(sub_key, "InstallLocation")[0]
                        if disp and loc and os.path.isdir(loc):
                            # Try to find the main exe in the install folder
                            exes = list(Path(loc).glob("*.exe"))
                            if exes:
                                _registry_cache[disp] = str(exes[0])
                    except Exception:
                        pass
                    finally:
                        winreg.CloseKey(sub_key)
                except Exception:
                    pass
            winreg.CloseKey(reg)
        except Exception:
            pass

    print(f"[Apps] Registry cache built: {len(_registry_cache)} entries")


def _search_start_menu(name: str) -> str | None:
    """Search Start Menu .lnk shortcuts for an app matching name."""
    start_dirs = [
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs"),
    ]
    name_lower = name.lower()
    for start_dir in start_dirs:
        for root, dirs, files in os.walk(start_dir):
            for f in files:
                if f.lower().endswith(".lnk") and name_lower in f.lower():
                    return os.path.join(root, f)
    return None


def open_app_smart(name: str) -> bool:
    """
    Intelligent app launcher:
    1. Registry scan for installed apps.
    2. Start Menu .lnk shortcuts.
    3. Direct PATH lookup.
    Returns True on success.
    """
    name_lower = name.lower().strip()

    # ── Registry ──────────────────────────────────────
    _build_registry_cache()
    for key, path in _registry_cache.items():
        if name_lower in key or key in name_lower:
            try:
                subprocess.Popen(path, shell=True)
                print(f"[Apps] Smart open (registry): {name} -> {path}")
                return True
            except Exception as exc:
                print(f"[Apps] Registry launch error: {exc}")

    # ── Start Menu ────────────────────────────────────
    lnk = _search_start_menu(name_lower)
    if lnk:
        try:
            os.startfile(lnk)
            print(f"[Apps] Smart open (Start Menu): {lnk}")
            return True
        except Exception as exc:
            print(f"[Apps] Start Menu launch error: {exc}")

    # ── Direct PATH ───────────────────────────────────
    exe_guess = name_lower.replace(" ", "") + ".exe"
    try:
        subprocess.Popen(exe_guess, shell=True)
        print(f"[Apps] Smart open (PATH): {exe_guess}")
        return True
    except Exception:
        pass

    print(f"[Apps] Could not find: {name}")
    return False


# ─────────────────────────────────────────────────────
#  Close app
# ─────────────────────────────────────────────────────
def close_app(name: str) -> bool:
    """Kill a running application by name using PROCESS_MAP."""
    name_lower = name.lower().strip()

    # Direct match
    target = config.PROCESS_MAP.get(name_lower)

    # Fuzzy match
    if not target:
        for key, val in config.PROCESS_MAP.items():
            if key in name_lower or name_lower in key:
                target = val
                break

    # Last resort: try raw exe name
    if not target:
        target = name_lower.replace(" ", "") + ".exe"

    result = subprocess.run(
        ["taskkill", "/f", "/im", target],
        capture_output=True,
        text=True,
    )
    success = result.returncode == 0
    print(f"[Apps] Close '{target}': {'OK' if success else 'NOT FOUND'}")
    return success
