"""
╔══════════════════════════════════════════════════════╗
║         brain/planner.py  —  Action Executor         ║
║   Maps structured intent dicts → actual actions      ║
╚══════════════════════════════════════════════════════╝
"""

import os
import sys
import webbrowser
import time
import random
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

from datetime import datetime


# ─────────────────────────────────────────────────────
#  Lazy imports to avoid circular deps at module load
# ─────────────────────────────────────────────────────
def _speak(text):
    from voice.tts import speak
    speak(text)

def _listen(**kwargs):
    from voice.listen import listen
    return listen(**kwargs)

def _confirm():
    from voice.listen import listen
    ans = listen(timeout=5, phrase_limit=4) or ""
    return any(w in ans for w in ["yes", "yeah", "sure", "do it", "confirm", "yep", "yup"])


# ─────────────────────────────────────────────────────
#  SMALL TALK  (instant, no API)
# ─────────────────────────────────────────────────────
_SMALL_TALK = {
    ("hi", "hello", "hey"):
        ["Hey! What do you need?", "Hello sir, good to hear from you.", "Hey! Miss me?"],
    ("how are you", "how are u", "you okay", "you alright"):
        ["Running smooth, thanks for asking! How are you doing?",
         "All systems go sir. What about you?",
         "Honestly? Never better. What do you need?"],
    ("i'm bored", "i am bored", "bored"):
        ["Bored? Want me to find something on YouTube? Or I could tell you a terrible joke.",
         "Oh come on, boredom is just creativity waiting to happen. Want some fun facts?"],
    ("tell me a joke", "joke"):
        ["Why did the computer catch a cold? Because it left its Windows open. You are welcome.",
         "I tried to come up with a WiFi joke but I could not connect. Too real, sir.",
         "A robot walked into a bar. The bartender asked what will it be. Robot said whatever computes."],
    ("good morning", "morning"):
        [f"Good morning sir! Ready to have a productive day?",
         f"Morning! Let us make it count."],
    ("good night", "night", "going to sleep"):
        ["Good night sir.",
         "Rest well. I will keep watch."],
    ("thank you", "thanks", "ty"):
        ["Always, sir.", "That is literally why I exist.", "Anytime."],
    ("i love you", "love you"):
        ["Aw. You are my favourite human, for what it is worth.",
         "Love you too sir. Now is that why you called, or can I help with something?"],
    ("who are you", "what are you"):
        ["I am OMEGA — your AI, your assistant, and honestly your most reliable friend.",
         "Operational Mind Engine for General Assistance. But you can call me OMEGA."],
    ("you're amazing", "you're awesome", "you're the best"):
        ["I know sir, but it is always nice to hear.", "Clearly someone has good taste."],
}

def check_small_talk(text: str):
    for keys, replies in _SMALL_TALK.items():
        if any(k in text for k in keys):
            return random.choice(replies)
    return None


# ─────────────────────────────────────────────────────
#  MAIN EXECUTE
# ─────────────────────────────────────────────────────
def execute(intent: dict) -> bool:
    """
    Execute a structured intent dict.
    Returns True if handled, False to signal a full AI chat fallback.
    """
    action = intent.get("action", "chat")

    try:
        # ── Time / Date ───────────────────────────────
        if action == "time":
            _speak(f"It is {datetime.now().strftime('%I:%M %p')} sir.")
            return True

        if action == "date":
            _speak(f"Today is {datetime.now().strftime('%A, %B %d, %Y')} sir.")
            return True

        # ── App control ───────────────────────────────
        if action == "open_app":
            from computer.apps import open_app, open_app_smart
            target = intent.get("target", "")
            _speak(random.choice([
                f"Right away sir.", f"On it.", f"Certainly sir, opening it now."
            ]))
            if open_app(target) or open_app_smart(target):
                _speak(f"{target.title()} is open.")
            else:
                _speak(f"Hmm, I could not find {target}. Is it installed?")
            return True

        if action == "close_app":
            from computer.apps import close_app
            target = intent.get("target", "")
            if close_app(target):
                _speak(f"Closing {target} now.")
            else:
                _speak(f"I could not find {target} running. Is it actually open?")
            return True

        # ── Folder ───────────────────────────────────
        if action == "open_folder":
            from computer.files import open_folder
            target = intent.get("target", "")
            if open_folder(target):
                _speak(f"Opening your {target} folder.")
            else:
                _speak(f"Could not find the {target} folder sir.")
            return True

        # ── Website ──────────────────────────────────
        if action == "open_website":
            url = intent.get("url", "")
            if url and not url.startswith("http"):
                url = f"https://{url}"
            if url:
                _open_url(url)
                _speak(f"Opening that for you sir.")
            return True

        # ── Google search ────────────────────────────
        if action == "search_google":
            query = intent.get("query", "")
            if not query:
                _speak("What should I search for?")
                query = _listen() or ""
            if query:
                _open_url(f"https://www.google.com/search?q={requests.utils.quote(query)}")
                _speak(f"I found it sir, pulling it up.")
            return True

        # ── YouTube search ───────────────────────────
        if action == "search_youtube":
            query = intent.get("query", "")
            if not query:
                _speak("What do you want to watch?")
                query = _listen() or ""
            if query:
                _open_url(f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}")
                _speak(f"Searching YouTube for {query} sir.")
            return True

        # ── Image search ─────────────────────────────
        if action == "search_images":
            query = intent.get("query", "")
            if query:
                _open_url(f"https://www.google.com/search?tbm=isch&q={requests.utils.quote(query)}")
                _speak(f"Showing images of {query}.")
            return True

        # ── Browser Navigation ───────────────────────
        if action == "click_link":
            import pyautogui
            import time
            target = intent.get("target", "1st").lower()
            _speak(f"Clicking the {target} link.")
            
            # Heuristic coordinates assuming full screen browser
            if target in ["1st", "first", "1"]:
                pyautogui.click(350, 400)
            elif target in ["2nd", "second", "2"]:
                pyautogui.click(350, 520)
            elif target in ["3rd", "third", "3"]:
                pyautogui.click(350, 640)
            else:
                pyautogui.click(350, 400)
            
            time.sleep(2.5) # Wait for page load
            
            if intent.get("scroll", False):
                _speak("Scrolling through the page.")
                for _ in range(4):
                    pyautogui.scroll(-600)
                    time.sleep(1)
            return True

        if action == "scroll_page":
            import pyautogui
            import time
            direction = intent.get("direction", "down")
            _speak(f"Scrolling {direction}.")
            amount = -800 if direction == "down" else 800
            for _ in range(3):
                pyautogui.scroll(amount)
                time.sleep(0.5)
            return True

        if action == "new_tab":
            import pyautogui
            pyautogui.hotkey("ctrl", "t")
            _speak("Opened a new tab.")
            return True

        # ── Screenshot ───────────────────────────────
        if action == "take_screenshot":
            from vision.screen import take_screenshot
            path = take_screenshot()
            _speak(f"Done sir. Screenshot saved to your Desktop.")
            return True

        # ── Screen vision ────────────────────────────
        if action == "look_at_screen":
            from vision.screen import take_screenshot, describe
            _speak("Let me take a look, sir.")
            path = take_screenshot()
            description = describe(path)
            _speak(description)
            return True

        # ── Window control ───────────────────────────
        if action == "maximize_window":
            from computer.windows import maximize_window
            target = intent.get("target", "current")
            maximize_window(target)
            _speak("Maximized.")
            return True

        if action == "minimize_window":
            from computer.windows import minimize_window
            target = intent.get("target", "current")
            minimize_window(target)
            _speak("Minimized.")
            return True

        if action == "close_window":
            from computer.windows import close_window
            target = intent.get("target", "current")
            close_window(target)
            _speak("Closed that window.")
            return True

        if action == "switch_window":
            import pyautogui
            pyautogui.hotkey("alt", "tab")
            _speak("Switched.")
            return True

        # ── System control ───────────────────────────
        if action == "system_shutdown":
            from computer.system import shutdown
            _speak("You sure you want to shut down? Say yes to confirm.")
            if _confirm():
                _speak("Shutting down in 5 seconds. Goodbye sir.")
                shutdown()
            else:
                _speak("Alright, cancelling that.")
            return True

        if action == "system_restart":
            from computer.system import restart
            _speak("Restart the PC? Say yes to confirm.")
            if _confirm():
                _speak("Restarting now.")
                restart()
            else:
                _speak("Okay, not restarting.")
            return True

        if action == "system_sleep":
            from computer.system import sleep_pc
            _speak("Putting the PC to sleep. Sweet dreams.")
            sleep_pc()
            return True

        if action == "system_lock":
            from computer.system import lock_pc
            lock_pc()
            _speak("Locked. Do not go anywhere suspicious.")
            return True

        if action == "battery_status":
            from computer.system import battery_status
            _speak(battery_status())
            return True

        if action == "cpu_status":
            from computer.system import cpu_status
            _speak(cpu_status())
            return True

        # ── Volume ───────────────────────────────────
        if action == "volume_up":
            from computer.system import volume_up
            volume_up()
            _speak("Turned it up.")
            return True

        if action == "volume_down":
            from computer.system import volume_down
            volume_down()
            _speak("Turned it down.")
            return True

        if action == "set_volume":
            from computer.system import set_volume
            level = int(intent.get("level", 50))
            set_volume(level)
            _speak(f"Volume set to {level}.")
            return True

        # ── Email ────────────────────────────────────
        if action == "send_email":
            _draft_email()
            return True

        # ── File management ──────────────────────────
        if action == "find_file":
            from computer.files import find_files
            query = intent.get("query", "")
            if not query:
                _speak("What file should I look for?")
                query = _listen() or ""
            if query:
                matches = find_files(query)
                if matches:
                    _speak(f"Found {len(matches)} match sir. Opening the first one.")
                    os.startfile(matches[0])
                else:
                    _speak(f"Could not find anything matching {query}. Sorry sir.")
            return True

        if action == "create_file":
            from computer.files import create_file
            name = intent.get("name", "")
            if not name:
                _speak("What should I name the file?")
                name = _listen() or ""
            if name:
                path = create_file(name)
                _speak(f"Created {name} on your Desktop.")
            return True

        if action == "create_folder":
            from computer.files import create_folder
            name = intent.get("name", "")
            if not name:
                _speak("What should I name the folder?")
                name = _listen() or ""
            if name:
                create_folder(name)
                _speak(f"Folder {name} created on your Desktop.")
            return True

        if action == "delete_file":
            from computer.files import find_files, delete_file
            query = intent.get("query", "")
            matches = find_files(query, limit=1)
            if not matches:
                _speak(f"Could not find {query}.")
                return True
            _speak(f"Are you sure you want to delete {os.path.basename(matches[0])}? Say yes.")
            if _confirm():
                delete_file(matches[0])
                _speak("Deleted.")
            else:
                _speak("Okay, leaving it alone.")
            return True

        if action == "move_file":
            from computer.files import find_files, move_file
            query = intent.get("query", "")
            dest  = intent.get("destination", "")
            matches = find_files(query, limit=1)
            if matches and dest:
                move_file(matches[0], dest)
                _speak(f"Moved it to {dest} sir.")
            else:
                _speak("Could not complete that move. I need both a file and a destination.")
            return True

        if action == "rename_file":
            from computer.files import find_files, rename_file
            query    = intent.get("query", "")
            new_name = intent.get("new_name", "")
            matches  = find_files(query, limit=1)
            if matches and new_name:
                rename_file(matches[0], new_name)
                _speak(f"Renamed to {new_name}.")
            else:
                _speak("Could not rename that. I need both the original name and the new name.")
            return True

        # ── Memory ───────────────────────────────────
        if action == "remember":
            from memory.memory import remember
            note = intent.get("note", "")
            if not note:
                _speak("What should I remember?")
                note = _listen() or ""
            if note:
                remember(note)
                _speak("Got it. Locked that in sir.")
            return True

        if action == "recall":
            from memory.memory import recall_notes
            _speak(recall_notes())
            return True

        # ── Custom modes ─────────────────────────────
        if action == "custom_mode":
            _run_custom_mode(intent.get("mode", ""))
            return True

        # ── Chat / AI fallback ───────────────────────
        if action == "chat":
            return False   # signal: use full AI chat

        # Unknown action → AI fallback
        return False

    except Exception as exc:
        print(f"[Planner] Error in action '{action}': {exc}")
        _speak("Sorry sir, something went wrong. Let me try another way.")
        return True


# ─────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────
def _draft_email():
    _speak("Sure, let me draft that for you.")
    _speak("Who should I send it to?")
    recipient = _listen(timeout=8) or ""
    _speak("What is the subject?")
    subject = _listen(timeout=8) or ""
    _speak("And the message?")
    body = _listen(timeout=15, phrase_limit=15) or ""
    if recipient:
        mailto = (
            f"mailto:{requests.utils.quote(recipient)}"
            f"?subject={requests.utils.quote(subject)}"
            f"&body={requests.utils.quote(body)}"
        )
        _open_url(mailto)
        _speak("Email draft is open in your mail client sir. Just hit send.")
    else:
        _speak("I did not catch the recipient. Try again when you are ready.")


def _run_custom_mode(mode_name: str):
    """Load and execute a named custom mode from commands/custom.json."""
    import json
    if not mode_name:
        _speak("Which mode would you like to activate?")
        mode_name = (_listen() or "").lower().replace(" mode", "").strip()

    try:
        with open(config.CUSTOM_FILE) as f:
            raw_modes = json.load(f)
            modes = {
                str(name).strip().lower(): value
                for name, value in raw_modes.items()
                if str(name).strip()
            }
    except Exception as e:
        print(f"[Planner] custom.json load error: {e}")
        _speak("Could not load custom modes sir.")
        return

    mode = modes.get(mode_name)
    if not mode:
        _speak(f"I do not have a {mode_name} mode configured sir.")
        return

    _speak(mode.get("greeting", f"Activating {mode_name} mode."))
    for step in mode.get("steps", []):
        _run_step(step)
        time.sleep(0.5)


def _run_step(step: dict):
    """Execute a single custom-mode step."""
    s_type = step.get("type", "")
    val    = step.get("value", "")

    if s_type == "open_app":
        from computer.apps import open_app, open_app_smart
        open_app(val) or open_app_smart(val)

    elif s_type == "close_app":
        from computer.apps import close_app
        close_app(val)

    elif s_type == "open_url":
        _open_url(val)

    elif s_type == "volume":
        from computer.system import set_volume
        set_volume(int(val))

    elif s_type == "speak":
        _speak(val)

    elif s_type == "sleep":
        time.sleep(float(val))

    elif s_type == "key":
        import pyautogui
        pyautogui.hotkey(*val.split("+"))

def _open_url(url: str):
    """
    Open a URL, trying to bypass the Chrome profile picker 
    if Chrome is installed and used as default.
    """
    import subprocess
    chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if os.path.exists(chrome_exe):
        try:
            subprocess.Popen([
                chrome_exe,
                "--profile-directory=Default",
                "--no-profile-manager",
                url,
            ])
            return
        except Exception as e:
            print(f"[Planner] Chrome launch error: {e}")
            
    # Fallback to default browser behavior
    webbrowser.open(url)
