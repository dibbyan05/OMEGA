"""
╔══════════════════════════════════════════════════════╗
║         voice/tts.py  —  Text-to-Speech Engine       ║
║   Primary : Windows SAPI5 natively (via win32com)    ║
║   Fallback: gTTS (Google free TTS, needs net)        ║
╚══════════════════════════════════════════════════════╝

DESIGN:
  pyttsx3 can be notoriously buggy and silent on modern Windows.
  Instead, we use Windows' built-in SAPI5 directly via win32com.
  This is 100% offline, free, and incredibly stable.
"""

import os
import re
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# ─────────────────────────────────────────────────────
#  Shared state
# ─────────────────────────────────────────────────────
_engine = None
_stop_flag = threading.Event()
_engine_lock = threading.Lock()

def _clean(text: str) -> str:
    """Strip markdown so output sounds natural when spoken."""
    text = re.sub(r"\*\*|__|\*|_|`|#+|>|\[|\]|\{|\}|\|", "", text)
    text = re.sub(r"\\n|\n|\r", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def _init_engine():
    global _engine
    try:
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        eng = win32com.client.Dispatch("SAPI.SpVoice")
        
        # SAPI5 rate is between -10 and 10. (0 is normal, 1 is slightly fast)
        eng.Rate = 1 
        eng.Volume = 100

        # Try to select the preferred voice (e.g. David)
        voices = eng.GetVoices()
        chosen = None
        for i in range(voices.Count):
            v = voices.Item(i)
            name = v.GetDescription().lower()
            if any(pref in name for pref in config.TTS_VOICE_PREFERENCES):
                chosen = v
                break
        
        if chosen:
            eng.Voice = chosen
            
        _engine = eng
        print(f"[TTS] Native Windows Speech ready — {eng.Voice.GetDescription()}")
    except Exception as exc:
        _engine = None
        print(f"[TTS] Native speech unavailable ({exc}) — will use gTTS fallback.")

_init_engine()

def speak(text: str) -> None:
    text = _clean(str(text)).strip()
    if not text:
        return

    try:
        print(f"\n[OMEGA]: {text}\n")
    except UnicodeEncodeError:
        print(f"\n[OMEGA]: {text.encode('ascii', errors='replace').decode()}\n")

    _stop_flag.clear()

    # ── Primary: Windows Native (win32com) ────────────
    if _engine:
        try:
            with _engine_lock:
                import pythoncom
                pythoncom.CoInitialize()  # Ensure COM is ready in this thread
                # Speak synchronously. To allow interrupt, we could use async flag,
                # but synchronous is 100% reliable for not being silent.
                # SVSFDefault = 0
                _engine.Speak(text, 0)
            return
        except Exception as exc:
            print(f"[TTS] Native speech error: {exc} — trying gTTS")

    # ── Fallback: gTTS ────────────────────────────────
    _speak_gtts(text)

def _speak_gtts(text: str) -> None:
    tmp_path = None
    try:
        from gtts import gTTS
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.close()
        tmp_path = tmp.name
        gTTS(text=text, lang="en", slow=False).save(tmp_path)

        played = False
        try:
            from playsound import playsound
            playsound(tmp_path)
            played = True
        except Exception:
            pass

        if not played:
            os.system(f'start /wait wmplayer "{tmp_path}"')

    except Exception as exc:
        print(f"[TTS] gTTS error: {exc}")
    finally:
        if tmp_path:
            time.sleep(0.3)
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

def stop_speaking() -> None:
    _stop_flag.set()
    if _engine:
        try:
            import pythoncom
            pythoncom.CoInitialize()
            # SVSFPurgeBeforeSpeak = 2. Purges the speech queue to stop speaking immediately.
            _engine.Speak("", 2)
        except Exception:
            pass
    print("[TTS] Stopped by user.")
