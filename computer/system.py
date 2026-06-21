"""
╔══════════════════════════════════════════════════════╗
║       computer/system.py  —  System Control          ║
║   shutdown · restart · sleep · lock · battery · cpu  ║
║   volume via Windows API (no nircmd required)        ║
╚══════════════════════════════════════════════════════╝
"""

import os
import sys
import subprocess
from ctypes import POINTER, byref, c_float, c_int, c_void_p, cast, wintypes

try:
    import comtypes
    from comtypes import CLSCTX_ALL, COMMETHOD, GUID, HRESULT, IUnknown
    from comtypes.client import CreateObject

    _COMTYPES_AVAILABLE = True

    CLSID_MMDeviceEnumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")

    class IAudioEndpointVolume(IUnknown):
        _iid_ = GUID("{5CDF2C82-841E-4546-9722-0CF74078229A}")
        _methods_ = [
            COMMETHOD([], HRESULT, "SetMasterVolumeLevelScalar",
                      (["in"], c_float, "fLevel"),
                      (["in"], c_void_p, "pguidEventContext")),
            COMMETHOD([], HRESULT, "GetMasterVolumeLevelScalar",
                      (["out"], POINTER(c_float), "pfLevel")),
            COMMETHOD([], HRESULT, "SetMute",
                      (["in"], wintypes.BOOL, "bMute"),
                      (["in"], c_void_p, "pguidEventContext")),
            COMMETHOD([], HRESULT, "GetMute",
                      (["out"], POINTER(wintypes.BOOL), "pbMute")),
        ]

    class IMMDevice(IUnknown):
        _iid_ = GUID("{D666063F-1587-4E43-81F1-B948E807363F}")
        _methods_ = [
            COMMETHOD([], HRESULT, "Activate",
                      (["in"], POINTER(GUID), "iid"),
                      (["in"], wintypes.DWORD, "dwClsCtx"),
                      (["in"], c_void_p, "pActivationParams"),
                      (["out"], POINTER(c_void_p), "ppInterface")),
        ]

    class IMMDeviceEnumerator(IUnknown):
        _iid_ = GUID("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
        _methods_ = [
            COMMETHOD([], HRESULT, "GetDefaultAudioEndpoint",
                      (["in"], c_int, "dataFlow"),
                      (["in"], c_int, "role"),
                      (["out"], POINTER(POINTER(IMMDevice)), "ppDevice")),
        ]
except Exception:
    _COMTYPES_AVAILABLE = False

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False
    print("[System] psutil not found — battery/CPU info unavailable.")


# ─────────────────────────────────────────────────────
#  Power control
# ─────────────────────────────────────────────────────
def shutdown() -> None:
    """Shut the PC down in 5 seconds."""
    os.system("shutdown /s /t 5")

def restart() -> None:
    """Restart the PC immediately."""
    os.system("shutdown /r /t 1")

def sleep_pc() -> None:
    """Put the PC into sleep/suspend mode."""
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def lock_pc() -> None:
    """Lock the workstation."""
    os.system("rundll32.exe user32.dll,LockWorkStation")


# ─────────────────────────────────────────────────────
#  Status
# ─────────────────────────────────────────────────────
def battery_status() -> str:
    """Return a human-friendly battery status string."""
    if not _PSUTIL:
        return "I do not have access to battery info right now sir."
    try:
        batt = psutil.sensors_battery()
        if batt is None:
            return "This machine does not appear to have a battery sir — probably a desktop."
        pct    = int(batt.percent)
        plugin = batt.power_plugged
        if plugin:
            status = "plugged in and charging" if pct < 100 else "fully charged"
        else:
            status = "running on battery"
        if pct <= 15 and not plugin:
            warn = " You might want to plug in soon sir."
        else:
            warn = ""
        return f"Battery is at {pct} percent, {status}.{warn}"
    except Exception as exc:
        return f"Could not read battery status sir: {exc}"


def cpu_status() -> str:
    """Return CPU and RAM usage as a human-friendly string."""
    if not _PSUTIL:
        return "I cannot check system stats right now sir."
    try:
        cpu  = psutil.cpu_percent(interval=1)
        ram  = psutil.virtual_memory()
        used = ram.used  // (1024**3)
        tot  = ram.total // (1024**3)
        pct  = int(ram.percent)

        if cpu > 85:
            cpu_comment = "— that is quite high honestly."
        elif cpu > 50:
            cpu_comment = "— moderate load."
        else:
            cpu_comment = "— looking healthy."

        return (
            f"CPU is at {cpu:.0f} percent {cpu_comment} "
            f"RAM is using {used} of {tot} gigabytes, that is {pct} percent."
        )
    except Exception as exc:
        return f"Could not read system stats sir: {exc}"


# ─────────────────────────────────────────────────────
#  Volume  (Windows Core Audio via PowerShell — no nircmd needed)
# ─────────────────────────────────────────────────────
def _ps_volume(command: str) -> None:
    """Run a PowerShell command to control Windows audio."""
    subprocess.run(
        ["powershell", "-Command", command],
        capture_output=True,
        timeout=5,
    )


def set_volume(level: int) -> None:
    """Set master volume to a percentage 0-100 using Windows Audio."""
    level = max(0, min(100, int(level)))
    if _COMTYPES_AVAILABLE:
        try:
            comtypes.CoInitialize()
            enumerator = CreateObject(
                CLSID_MMDeviceEnumerator,
                interface=IMMDeviceEnumerator,
            )
            device = enumerator.GetDefaultAudioEndpoint(0, 1)

            endpoint_ptr = device.Activate(
                byref(IAudioEndpointVolume._iid_),
                CLSCTX_ALL,
                None,
            )
            endpoint = cast(endpoint_ptr, POINTER(IAudioEndpointVolume))

            endpoint.SetMute(False, None)
            endpoint.SetMasterVolumeLevelScalar(level / 100.0, None)
            print(f"[System] Volume set to {level}%")
            return
        except Exception as exc:
            print(f"[System] Volume COM error: {exc}")
        finally:
            try:
                comtypes.CoUninitialize()
            except Exception:
                pass

    # Fallback: nudge volume keys if COM is unavailable.
    try:
        import pyautogui
        for _ in range(10):
            pyautogui.press("volumeup")
    except Exception:
        _ps_volume("(New-Object -ComObject WScript.Shell).SendKeys([char]175) " * 5)
    print(f"[System] Volume fallback used for target {level}%")


def volume_up() -> None:
    """Increase volume by ~10 steps using keyboard simulation."""
    try:
        import pyautogui
        for _ in range(10):
            pyautogui.press("volumeup")
    except Exception:
        _ps_volume("(New-Object -ComObject WScript.Shell).SendKeys([char]175) " * 5)
    print("[System] Volume up")


def volume_down() -> None:
    """Decrease volume by ~10 steps using keyboard simulation."""
    try:
        import pyautogui
        for _ in range(10):
            pyautogui.press("volumedown")
    except Exception:
        _ps_volume("(New-Object -ComObject WScript.Shell).SendKeys([char]174) " * 5)
    print("[System] Volume down")
