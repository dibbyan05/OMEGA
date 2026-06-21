import os
import sys
import io
import random

# ── Force UTF-8 output so banner / emoji don't crash Windows terminal ───
# Works for Python 3.7+ on Windows (cp1252 is the default, which breaks Unicode)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

os.environ["PYTHONIOENCODING"] = "utf-8"   # also affects child processes

# ── Make sure all sub-packages can resolve imports ──────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from voice.tts      import speak
from voice.listen   import listen
from voice.wakeword import heard_wake, strip_wake, start_stop_listener
from brain.intent     import get_intent, get_custom_mode_intent
from brain.planner    import execute
from brain.smalltalk  import get_reply as small_talk_reply
from brain.llm        import chat, reset_history


# ─────────────────────────────────────────────────────────────────────────
#  Boot banner
# ─────────────────────────────────────────────────────────────────────────
_BANNER = r"""
╔══════════════════════════════════════════════════════════════════════════╗
║                        Ω.M.E.G.A    v5.0                                 ║  
║              Operational Mind Engine for General Assistance              ║
║──────────────────────────────────────────────────────────────────────────║
║              ██████╗  ███╗   ███╗███████╗ ██████╗  █████╗                ║
║             ██╔═══██╗ ████╗ ████║██╔════╝██╔════╝ ██╔══██╗               ║
║             ██║   ██║ ██╔████╔██║█████╗  ██║  ███╗███████║               ║
║             ██║   ██║ ██║╚██╔╝██║██╔══╝  ██║   ██║██╔══██║               ║
║             ╚██████╔╝ ██║ ╚═╝ ██║███████╗╚██████╔╝██║  ██║               ║
║              ╚═════╝  ╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝               ║ 
║──────────────────────────────────────────────────────────────────────────║
║                     DIBBYAN GHOSH : ECE/25/07 : CEMK                     ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

_WAKE_RESPONSES = [
   "At your service, sir.",
    "Online and ready, sir.",
    "Systems activated. How may I assist you?",
    "I am listening, sir.",
    "All systems are standing by.",
    "Ready for your command.",
    "Good to hear from you, sir.",
    "Omega is online. Awaiting instructions.",
    "Voice interface connected. Proceed.",
    "Standing by, sir.",
]

_EXIT_WORDS = set(config.EXIT_WORDS)


# ─────────────────────────────────────────────────────────────────────────
#  Command handler
# ─────────────────────────────────────────────────────────────────────────
def handle_command(command: str) -> str | bool:
    """
    Process a voice command:
    1. Check for exit signal.
    2. Check small-talk (instant, no API).
    3. Classify intent (local regex first, then LLM).
    4. Execute via planner.
    5. Fall through to full LLM chat.

    Returns "exit" to terminate, True if handled, False if unknown.
    """
    c = command.strip().lower()

    # ── Exit ──────────────────────────────────────────────────────────────
    if any(w in c for w in _EXIT_WORDS):
        return "exit"
    
    custom = get_custom_mode_intent(command)
    if custom:
        return execute(custom)

    # ── Small talk (zero latency, no API) ──────────────────────────────────
    # Checked FIRST — instant offline reply for greetings, jokes, mood, etc.
    small = small_talk_reply(c)
    if small:
        speak(small)
        return True

    # ── Intent → Action ───────────────────────────────────────────────────
    intent  = get_intent(command)
    handled = execute(intent)

    if handled:
        return True

    # ── AI fallback: full conversation ────────────────────────────────────
    speak("Let me think about that for a second...")
    reply = chat(command)
    speak(reply)
    return True


# ─────────────────────────────────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────────────────────────────────
def run():
    print(_BANNER)

    # Start background stop-word listener (DISABLED: causes PyAudio C-level crashes)
    # start_stop_listener()

    # Boot greeting
    speak(
        f"Systems online. Hello sir, OMEGA version five is up and ready. "
        f"What can I do for you?"
    )

    while True:
        # ── Waiting for wake word ──────────────────────────────────────────
        print("⏳  Waiting for wake word  ('Omega' / 'Hey Omega') ...")
        raw = listen(
            timeout      = 86400,
            phrase_limit = config.SR_WAKE_PHRASE_LIMIT,
            silent       = True,   # don't speak errors during idle polling
        )
        if not raw:
            continue
        if not heard_wake(raw):
            continue

        # ── Wake word detected ─────────────────────────────────────────────
        command = strip_wake(raw).strip()

        # Wake word only — ask what they want
        if not command or len(command) < 2:
            speak(random.choice(_WAKE_RESPONSES))
            command = listen(
                timeout      = config.SR_LISTEN_TIMEOUT,
                phrase_limit = config.SR_PHRASE_LIMIT,
            ) or ""
            if not command:
                speak("Did not catch that. I am here whenever you need me sir.")
                continue

        print(f"\n[CMD] {command}\n")

        # ── Process ────────────────────────────────────────────────────────
        result = handle_command(command)

        if result == "exit":
            speak(random.choice([
                "Alright, shutting down. Take care of yourself sir.",
                "Going offline. You know where to find me.",
                "Goodbye sir. Always a pleasure, signing off.",
            ]))
            break


# ─────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n[OMEGA] Interrupted by user. Shutting down.")
        speak("Shutting down sir. Goodbye.")
    except Exception as exc:
        print(f"[OMEGA] Fatal error: {exc}")
        speak("Something went quite wrong sir. Check the terminal for details.")
        raise
