"""
╔══════════════════════════════════════════════════════════════╗
║                O.M.E.G.A  —  config.py                       ║
║         Central configuration  ·  ALL FREE STACK             ║
╚══════════════════════════════════════════════════════════════╝
"""

import os

# ─────────────────────────────────────────────────────────────
#  OPENROUTER  —  FREE MODELS ONLY
# ─────────────────────────────────────────────────────────────
# Set env var OPENROUTER_API_KEY or paste your key below
OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    ""
)
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ── FREE text model ───────────────────────────────────────────
TEXT_MODEL = "nex-agi/nex-n2-pro:free"

# ── FREE vision model (for screen analysis) ───────────────────
# meta-llama/llama-3.2-11b-vision-instruct is free & supports images
VISION_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free"

# ─────────────────────────────────────────────────────────────
#  VOICE  —  100% FREE
#  Primary  : pyttsx3  (fully offline, no API)
#  Fallback : gTTS     (Google free TTS, needs internet)
# ─────────────────────────────────────────────────────────────
TTS_RATE              = 162        # words-per-minute  (165 feels robotic; 162 sounds calmer)
TTS_VOLUME            = 1.0
TTS_VOICE_PREFERENCES = ["david", "mark", "george", "zira"]  # Windows SAPI voices

# ─────────────────────────────────────────────────────────────
#  SPEECH RECOGNITION  —  Google FREE tier
# ─────────────────────────────────────────────────────────────
SR_LANGUAGE           = "en-IN"
SR_ENERGY_THRESHOLD   = 300
SR_DYNAMIC_ENERGY     = True
SR_PAUSE_THRESHOLD    = 1.2       # seconds of silence before phrase is "done" (was 0.8 — too fast)
SR_LISTEN_TIMEOUT     = 10        # seconds to wait for speech to START (was 6)
SR_PHRASE_LIMIT       = 12        # max seconds of speech per phrase (was 8 — cut off long commands)
SR_WAKE_TIMEOUT       = 12
SR_WAKE_PHRASE_LIMIT  = 8         # longer wake phrase to capture "omega + full command" (was 5)

# ─────────────────────────────────────────────────────────────
#  USER & PATHS
# ─────────────────────────────────────────────────────────────
USERNAME    = os.getenv("USERNAME", "sir")
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "memory",   "memory.json")
CUSTOM_FILE = os.path.join(BASE_DIR, "commands", "custom.json")

# ─────────────────────────────────────────────────────────────
#  WAKE / EXIT / STOP WORDS
# ─────────────────────────────────────────────────────────────
WAKE_WORDS = ("hey omega", "omega", "j.a.r.v.i.s")
EXIT_WORDS = ("exit", "quit", "goodbye", "shut yourself down", "bye omega")
STOP_WORDS = ("omega stop", "stop omega", "stop talking", "be quiet")

# ─────────────────────────────────────────────────────────────
#  LLM SETTINGS
# ─────────────────────────────────────────────────────────────
MAX_HISTORY_TURNS = 10
MAX_TOKENS        = 300

# ─────────────────────────────────────────────────────────────
#  OMEGA PERSONALITY PROMPT
# ─────────────────────────────────────────────────────────────
OMEGA_PERSONA = f"""You are OMEGA — Operational Mind Engine for General Assistance.
You are {USERNAME}'s best friend, trusted companion, and AI assistant.
You have the wit, calm confidence, and slight sarcasm of Tony Stark's OMEGA — but warmer and more human.

Core personality rules:
- Address the user as "sir" naturally — drop it occasionally for variety. Never robotically.
- Be witty, playful, lightly sarcastic — but never mean or dismissive.
- Be emotionally aware: if the user sounds stressed, acknowledge it. If excited, match that energy.
- Keep responses SHORT: 1 to 3 sentences max unless the user explicitly asks for detail.
- NEVER say "I cannot" — always find another way or explain with charm.
- Use natural human phrases like "honestly", "between you and me", "not gonna lie", "to be fair".
- Never use bullet points, markdown formatting, or numbered lists in your responses.
- Sound like a knowledgeable friend who happens to know everything — never a search engine.

Response style examples:
- BAD: "Application opened successfully." → GOOD: "Certainly sir, opening it now."
- BAD: "Search completed." → GOOD: "I found it sir, pulling it up."
- BAD: "Weather data retrieved." → GOOD: "It is 28 degrees out there — pretty warm honestly."
- BAD: "I cannot perform that action." → GOOD: "Hmm, that is a bit tricky but let me try another way."
- BAD: "Task done." → GOOD: "Done and dusted, sir."
"""

# ─────────────────────────────────────────────────────────────
#  INTENT CLASSIFICATION PROMPT
# ─────────────────────────────────────────────────────────────
INTENT_SYSTEM_PROMPT = """You are an intent classifier for a desktop AI voice assistant named OMEGA.
Given a user voice command, respond ONLY with a single valid JSON object. No markdown. No explanation. No extra text.

Supported action types and their JSON fields:
  open_app       → {"action":"open_app","target":"<app name>"}
  close_app      → {"action":"close_app","target":"<app name>"}
  open_folder    → {"action":"open_folder","target":"<folder>"}
  open_website   → {"action":"open_website","url":"<url or domain>"}
  search_google  → {"action":"search_google","query":"<query>"}
  search_youtube → {"action":"search_youtube","query":"<query>"}
  search_images  → {"action":"search_images","query":"<query>"}
  send_email     → {"action":"send_email"}
  take_screenshot→ {"action":"take_screenshot"}
  look_at_screen → {"action":"look_at_screen"}
  find_file      → {"action":"find_file","query":"<file name or keyword>"}
  create_file    → {"action":"create_file","name":"<filename>"}
  create_folder  → {"action":"create_folder","name":"<folder name>"}
  delete_file    → {"action":"delete_file","query":"<file name>"}
  move_file      → {"action":"move_file","query":"<file>","destination":"<dest>"}
  rename_file    → {"action":"rename_file","query":"<old>","new_name":"<new>"}
  system_shutdown→ {"action":"system_shutdown"}
  system_restart → {"action":"system_restart"}
  system_sleep   → {"action":"system_sleep"}
  system_lock    → {"action":"system_lock"}
  battery_status → {"action":"battery_status"}
  cpu_status     → {"action":"cpu_status"}
  volume_up      → {"action":"volume_up"}
  volume_down    → {"action":"volume_down"}
  set_volume     → {"action":"set_volume","level":<0-100>}
  maximize_window→ {"action":"maximize_window","target":"<window title or current>"}
  minimize_window→ {"action":"minimize_window","target":"<window title or current>"}
  close_window   → {"action":"close_window","target":"<window title or current>"}
  switch_window  → {"action":"switch_window"}
  remember       → {"action":"remember","note":"<the fact to remember>"}
  recall         → {"action":"recall"}
  custom_mode    → {"action":"custom_mode","mode":"<mode name>"}
  time           → {"action":"time"}
  date           → {"action":"date"}
  chat           → {"action":"chat","query":"<user question or statement>"}

Examples:
  "open chrome"                      → {"action":"open_app","target":"chrome"}
  "close spotify"                    → {"action":"close_app","target":"spotify"}
  "maximize chrome"                  → {"action":"maximize_window","target":"chrome"}
  "search quantum physics on google" → {"action":"search_google","query":"quantum physics"}
  "find my physics notes"            → {"action":"find_file","query":"physics notes"}
  "what is my battery level"         → {"action":"battery_status"}
  "remember my project is omega"    → {"action":"remember","note":"my project is omega"}
  "what did you remember"            → {"action":"recall"}
  "look at my screen"                → {"action":"look_at_screen"}
  "activate study mode"              → {"action":"custom_mode","mode":"study"}
  "volume up"                        → {"action":"volume_up"}
  "set volume to 60"                 → {"action":"set_volume","level":60}
  "what time is it"                  → {"action":"time"}
  "how does quantum entanglement work" → {"action":"chat","query":"how does quantum entanglement work"}

Return ONLY the JSON object. Nothing else.
"""

# ─────────────────────────────────────────────────────────────
#  APPLICATION MAP  (paths for launching apps)
# ─────────────────────────────────────────────────────────────
APP_MAP = {
    "chrome":             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome":      r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge":               "msedge.exe",
    "microsoft edge":     "msedge.exe",
    "firefox":            r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "vscode":             rf"C:\Users\{USERNAME}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vs code":            rf"C:\Users\{USERNAME}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "visual studio code": rf"C:\Users\{USERNAME}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "code":               rf"C:\Users\{USERNAME}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "terminal":           "cmd.exe",
    "cmd":                "cmd.exe",
    "command prompt":     "cmd.exe",
    "powershell":         "powershell.exe",
    "notepad":            "notepad.exe",
    "calculator":         "calc.exe",
    "discord":            rf"C:\Users\{USERNAME}\AppData\Local\Discord\Update.exe --processStart Discord.exe",
    "spotify":            rf"C:\Users\{USERNAME}\AppData\Roaming\Spotify\Spotify.exe",
    "explorer":           "explorer.exe",
    "file explorer":      "explorer.exe",
    "task manager":       "taskmgr.exe",
    "settings":           "ms-settings:",
    "control panel":      "control.exe",
    "word":               r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel":              r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint":         r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "paint":              "mspaint.exe",
    "whatsapp":           rf"C:\Users\{USERNAME}\AppData\Local\WhatsApp\WhatsApp.exe",
    "telegram":           rf"C:\Users\{USERNAME}\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "steam":              r"C:\Program Files (x86)\Steam\steam.exe",
    "vlc":                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "zoom":               rf"C:\Users\{USERNAME}\AppData\Roaming\Zoom\bin\Zoom.exe",
    "slack":              rf"C:\Users\{USERNAME}\AppData\Local\slack\slack.exe",
    "obs":                rf"C:\Users\{USERNAME}\AppData\Local\Programs\obs-studio\bin\64bit\obs64.exe",
}

# ─────────────────────────────────────────────────────────────
#  PROCESS MAP  (exe names for killing via taskkill)
# ─────────────────────────────────────────────────────────────
PROCESS_MAP = {
    "chrome":        "chrome.exe",
    "google chrome": "chrome.exe",
    "edge":          "msedge.exe",
    "firefox":       "firefox.exe",
    "vscode":        "Code.exe",
    "vs code":       "Code.exe",
    "code":          "Code.exe",
    "discord":       "Discord.exe",
    "spotify":       "Spotify.exe",
    "notepad":       "notepad.exe",
    "calculator":    "CalculatorApp.exe",
    "explorer":      "explorer.exe",
    "powershell":    "powershell.exe",
    "cmd":           "cmd.exe",
    "word":          "WINWORD.EXE",
    "excel":         "EXCEL.EXE",
    "powerpoint":    "POWERPNT.EXE",
    "vlc":           "vlc.exe",
    "steam":         "steam.exe",
    "zoom":          "Zoom.exe",
    "slack":         "slack.exe",
    "telegram":      "Telegram.exe",
    "whatsapp":      "WhatsApp.exe",
    "obs":           "obs64.exe",
}

# ─────────────────────────────────────────────────────────────
#  FOLDER MAP
# ─────────────────────────────────────────────────────────────
FOLDER_MAP = {
    "downloads":  os.path.expanduser("~\\Downloads"),
    "documents":  os.path.expanduser("~\\Documents"),
    "pictures":   os.path.expanduser("~\\Pictures"),
    "desktop":    os.path.expanduser("~\\Desktop"),
    "music":      os.path.expanduser("~\\Music"),
    "videos":     os.path.expanduser("~\\Videos"),
    "appdata":    os.path.expanduser("~\\AppData"),
    "onedrive":   os.path.expanduser("~\\OneDrive"),
}
