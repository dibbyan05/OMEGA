"""
╔══════════════════════════════════════════════════════╗
║      voice/listen.py  —  Speech Recognition          ║
║   Uses SpeechRecognition + Google FREE speech API    ║
╚══════════════════════════════════════════════════════╝
"""

import os
import sys
import speech_recognition as sr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# ─────────────────────────────────────────────────────
#  Single shared recogniser instance
# ─────────────────────────────────────────────────────
_recognizer = sr.Recognizer()
_recognizer.energy_threshold         = config.SR_ENERGY_THRESHOLD
_recognizer.dynamic_energy_threshold = config.SR_DYNAMIC_ENERGY
_recognizer.pause_threshold          = config.SR_PAUSE_THRESHOLD


# ─────────────────────────────────────────────────────
#  Public: listen
# ─────────────────────────────────────────────────────
def listen(
    timeout:      int  = None,
    phrase_limit: int  = None,
    silent:       bool = False,
) -> str | None:
    """
    Record from the microphone and return lowercased transcription, or None.

    Args:
        timeout      – seconds to wait for speech before returning None
        phrase_limit – max seconds of speech to capture in one phrase
        silent       – if True, do not speak error messages (used during wake-word polling)
    """
    timeout      = timeout      or config.SR_LISTEN_TIMEOUT
    phrase_limit = phrase_limit or config.SR_PHRASE_LIMIT

    try:
        with sr.Microphone() as source:
            # Longer calibration = better noise filtering = fewer mishears
            _recognizer.adjust_for_ambient_noise(source, duration=0.6)
            print("🎤  [Listening...]")
            try:
                audio = _recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit,
                )
            except sr.WaitTimeoutError:
                return None

        # Get the best transcription from Google
        # Try with show_all to pick the highest-confidence result
        try:
            results = _recognizer.recognize_google(
                audio, language=config.SR_LANGUAGE, show_all=True
            )
            if results and isinstance(results, dict):
                alts = results.get("alternative", [])
                if alts:
                    text = alts[0].get("transcript", "").lower()
                    confidence = alts[0].get("confidence", "n/a")
                    print(f"👤 YOU: {text}  (confidence: {confidence})")
                    return text
        except Exception:
            pass

        # Fallback: standard single-result recognition
        text = _recognizer.recognize_google(audio, language=config.SR_LANGUAGE).lower()
        print(f"👤 YOU: {text}")
        return text

    except sr.UnknownValueError:
        if not silent:
            _safe_speak("Didn't quite catch that, sir — say it again?")
        return None

    except sr.RequestError as exc:
        print(f"[Listen] Google Speech API error: {exc}")
        if not silent:
            _safe_speak("Connection hiccup — try again.")
        return None

    except Exception as exc:
        print(f"[Listen] Unexpected error: {exc}")
        return None


# ─────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────
def _safe_speak(text: str) -> None:
    """Speak without importing at module level (avoids circular imports)."""
    try:
        from voice.tts import speak
        speak(text)
    except Exception:
        print(f"[Listen] (would say): {text}")
