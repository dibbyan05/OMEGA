# 🤖 O.M.E.G.A — Operational Mind Engine for General Assistance

> *"I am fully operational and all systems are functional, sir."*

A next-generation local desktop AI voice assistant inspired by Tony Stark's OMEGA.
Runs **100% free** — no paid APIs, no subscriptions.

---

## 📋 Table of Contents

- [Tech Stack](#-tech-stack--100-free)
- [Project Structure](#-project-structure)
- [Step 1 — Get Your Free API Key](#-step-1--get-your-free-openrouter-api-key)
- [Step 2 — Paste Your API Key](#-step-2--paste-your-api-key-into-configpy)
- [Step 3 — Install Dependencies](#-step-3--install-dependencies)
- [Step 4 — Run OMEGA](#-step-4--run-omega)
- [Wake Word & Commands](#-wake-word--commands)
- [Custom Modes](#-custom-modes)
- [Memory System](#-memory-system)
- [Troubleshooting](#-troubleshooting)

---

## ⚡ Tech Stack — 100% Free

| Component | Tool | Cost |
|-----------|------|------|
| 🧠 AI Brain | `google/gemma-4-31b-it:free` via OpenRouter | FREE |
| 👁️ Screen Vision | `meta-llama/llama-3.2-11b-vision-instruct:free` via OpenRouter | FREE |
| 🔊 Text-to-Speech | `pyttsx3` (offline Windows SAPI5) + `gTTS` fallback | FREE |
| 🎤 Speech Recognition | `SpeechRecognition` + Google free Speech API | FREE |
| 🖥️ Window Control | `pygetwindow` + `pyautogui` | FREE |
| 📊 System Stats | `psutil` | FREE |

---

## 📁 Project Structure

```
OMEGA/
│
├── main.py                ← ▶ Run this to start OMEGA
├── config.py              ← ⚙️ PASTE YOUR API KEY HERE
├── requirements.txt       ← 📦 All dependencies
│
├── brain/
│   ├── llm.py             ← OpenRouter API client
│   ├── intent.py          ← Command classifier
│   └── planner.py         ← Action executor
│
├── voice/
│   ├── tts.py             ← Text-to-Speech (pyttsx3 + gTTS)
│   ├── listen.py          ← Microphone input
│   └── wakeword.py        ← Wake word detector
│
├── computer/
│   ├── apps.py            ← Open / close applications
│   ├── windows.py         ← Window maximize/minimize/close
│   ├── files.py           ← File find/create/move/delete
│   └── system.py          ← Shutdown/sleep/lock/volume/battery
│
├── vision/
│   └── screen.py          ← Screenshot + AI screen description
│
├── memory/
│   ├── memory.py          ← Remember/recall notes
│   └── memory.json        ← Persistent storage (auto-created)
│
└── commands/
    └── custom.json        ← Study/Gaming/Work mode configs
```

---

## 🔑 Step 1 — Get Your Free OpenRouter API Key

OpenRouter gives you **free access** to Gemma 4, Llama Vision, and more.

1. Go to **[https://openrouter.ai](https://openrouter.ai)**
2. Click **"Sign In"** → create a free account (Google sign-in works)
3. Once logged in, click your profile icon → **"API Keys"**
4. Click **"Create Key"** → give it a name like `omega`
5. **Copy the key** — it starts with `sk-or-v1-...`

> ⚠️ **Keep your API key private.** Do not share it publicly or commit it to GitHub.

---

## 🔧 Step 2 — Paste Your API Key into `config.py`

Open the file:

```
OMEGA/config.py
```

Find this section near the **top of the file** (around line 10):

```python
# ─────────────────────────────────────────────────────────────
#  OPENROUTER  —  FREE MODELS ONLY
# ─────────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    "sk-or-v1-PASTE_YOUR_KEY_HERE"       # ← REPLACE THIS
)
```

Replace `sk-or-v1-PASTE_YOUR_KEY_HERE` with your actual key:

```python
OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    "sk-or-v1-abc123yourrealkeygoeshere"  # ← your real key
)
```

### ✅ That's it — that's the only place you need to paste anything.

> 💡 **Alternatively**, you can set it as a system environment variable:
> ```
> Windows: setx OPENROUTER_API_KEY "sk-or-v1-your-key-here"
> ```
> Then you don't need to touch `config.py` at all.

---

## 📦 Step 3 — Install Dependencies

Open a terminal in the `OMEGA/` folder and run:

```bash
pip install -r requirements.txt
```

This installs everything:

| Package | Purpose |
|---------|---------|
| `SpeechRecognition` | Microphone input |
| `PyAudio` | Audio driver for microphone |
| `pyttsx3` | Offline text-to-speech (primary) |
| `gTTS` | Google free TTS (fallback) |
| `playsound` | Plays the gTTS audio file |
| `requests` | OpenRouter API calls |
| `Pillow` | Screenshots |
| `pyautogui` | Keyboard/mouse automation |
| `pygetwindow` | Window control |
| `psutil` | CPU / battery / RAM stats |

> ⚠️ If `PyAudio` fails to install:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

---

## ▶️ Step 4 — Run OMEGA

```bash
python main.py
```

You should see the boot banner:

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        O.M.E.G.A  v5.0                               ║
║              Operational Mind Engine for General Assistance                       ║
╚══════════════════════════════════════════════════════════════════════════╝

⏳  Waiting for wake word  ('Omega' / 'Hey Omega') ...
```

OMEGA will say:
> *"Systems online. Hello sir, O.M.E.G.A version five is up and ready. What do you need?"*

---

## 🎤 Wake Word & Commands

### Activate OMEGA
Say any of these:
- **"Omega"**
- **"Hey Omega"**
- **"O.M.E.G.A"**

### Stop Speaking
Say **"Omega stop"** at any time to interrupt speech immediately.

### Shut Down OMEGA
Say **"Goodbye Omega"** or **"Exit"**.

---

## 💬 Example Commands

### 🖥️ Apps
| Say | Action |
|-----|--------|
| `"Open Chrome"` | Launches Chrome |
| `"Open VS Code"` | Launches Visual Studio Code |
| `"Close Spotify"` | Kills Spotify process |
| `"Launch Discord"` | Opens Discord |

### 🪟 Windows
| Say | Action |
|-----|--------|
| `"Maximize Chrome"` | Maximizes Chrome window |
| `"Minimize this window"` | Minimizes active window |
| `"Switch window"` | Alt+Tab |
| `"Close this window"` | Closes active window |

### 📁 Files
| Say | Action |
|-----|--------|
| `"Find my physics notes"` | Searches & opens the file |
| `"Create file homework.txt"` | Creates file on Desktop |
| `"Create folder Projects"` | Creates folder on Desktop |
| `"Open Downloads folder"` | Opens Downloads |

### 🔋 System
| Say | Action |
|-----|--------|
| `"Battery status"` | Reports battery % |
| `"CPU usage"` | Reports CPU & RAM |
| `"Lock computer"` | Locks the PC |
| `"Shutdown"` | Asks for confirmation, then shuts down |
| `"Restart"` | Asks for confirmation, then restarts |
| `"Sleep"` | Puts PC to sleep |

### 🔊 Volume
| Say | Action |
|-----|--------|
| `"Volume up"` | Increases volume |
| `"Volume down"` | Decreases volume |
| `"Set volume to 60"` | Sets volume to 60% |

### 🌐 Web
| Say | Action |
|-----|--------|
| `"Search quantum physics"` | Google search |
| `"Search YouTube for lo-fi music"` | YouTube search |
| `"Open youtube"` | Opens YouTube |

### 📸 Screen Vision
| Say | Action |
|-----|--------|
| `"Look at my screen"` | Takes screenshot, AI describes it |
| `"Take a screenshot"` | Saves screenshot to Desktop |

### 🧠 Memory
| Say | Action |
|-----|--------|
| `"Remember my project is OMEGA"` | Stores the note |
| `"What did you remember?"` | Recalls stored notes |

### 📧 Email
| Say | Action |
|-----|--------|
| `"Send an email"` | OMEGA asks for recipient, subject, and message → opens mailto draft |

### 🤖 AI Chat
Anything not matched above gets sent directly to Gemma 4 for a conversational answer:
- `"How does quantum entanglement work?"`
- `"Write me a Python function to sort a list"`
- `"Tell me a joke"`

---

## 🎮 Custom Modes

Say `"Activate [mode] mode"`:

| Mode | What it does |
|------|-------------|
| `"Study mode"` | Closes Discord & Spotify, opens VS Code + Notion |
| `"Gaming mode"` | Opens Discord + Spotify, sets volume to 70% |
| `"Work mode"` | Opens Chrome + VS Code + Gmail, sets volume to 40% |
| `"Night mode"` | Lowers volume to 20%, opens Quick Settings |
| `"Presentation mode"` | Closes distractions, opens PowerPoint, sets volume to 60% |

### Adding Custom Modes

Edit `commands/custom.json` to add your own:

```json
{
  "my_mode": {
    "greeting": "My custom mode activated sir.",
    "steps": [
      { "type": "open_app", "value": "chrome" },
      { "type": "open_url", "value": "https://example.com" },
      { "type": "volume",   "value": "50" },
      { "type": "speak",    "value": "All set sir." }
    ]
  }
}
```

**Available step types:**

| Type | Value | Example |
|------|-------|---------|
| `open_app` | app name | `"chrome"`, `"vscode"` |
| `close_app` | app name | `"discord"` |
| `open_url` | full URL | `"https://notion.so"` |
| `volume` | 0–100 | `"60"` |
| `speak` | text to say | `"Done sir."` |
| `sleep` | seconds | `"1.5"` |
| `key` | hotkey combo | `"win+d"` |

---

## 🧠 Memory System

Memory is stored in `memory/memory.json` — it persists between sessions.

```json
{
  "notes": [
    { "text": "my project is OMEGA", "when": "2026-06-10T17:00:00" }
  ],
  "facts_about_user": {
    "project": "OMEGA"
  },
  "reminders": []
}
```

To clear all memory, delete `memory/memory.json` — it will be recreated automatically.

---

## 🛠️ Troubleshooting

### ❌ "No module named 'pyaudio'"
```bash
pip install pipwin
pipwin install pyaudio
```

### ❌ OMEGA doesn't hear me
- Make sure your microphone is set as the **default recording device** in Windows Sound Settings.
- Try speaking louder or adjusting `SR_ENERGY_THRESHOLD` in `config.py` (lower = more sensitive):
  ```python
  SR_ENERGY_THRESHOLD = 200   # default is 300
  ```

### ❌ API errors / no AI response
- Check that your API key in `config.py` is correct.
- Visit [openrouter.ai/activity](https://openrouter.ai/activity) to verify your key is active.
- Free models may occasionally hit rate limits — wait a few seconds and try again.

### ❌ TTS voice sounds wrong
Change the preferred voice in `config.py`:
```python
TTS_VOICE_PREFERENCES = ["david", "mark", "george", "zira"]
```
`david` = male US English · `zira` = female US English

### ❌ "Look at my screen" does not work
The vision model requires an internet connection (it's a free OpenRouter model).
Make sure `meta-llama/llama-3.2-11b-vision-instruct:free` is available on your OpenRouter account.

---

## 🔒 Keeping Your API Key Safe

- **Never** paste your key into a public GitHub repo.
- Use the **environment variable** method for production:
  ```bash
  # Run once in terminal (permanent):
  setx OPENROUTER_API_KEY "sk-or-v1-your-key-here"
  ```
- Or create a `.env` file (never commit it) and load with `python-dotenv`.

---

## 📝 Quick Reference Card

```
🔑 API Key     →  config.py  line ~14  (OPENROUTER_API_KEY)
▶️  Start       →  python main.py
🎤 Wake        →  Say "Omega" or "Hey Omega"
🛑 Stop        →  Say "Omega stop"
🚪 Exit        →  Say "Goodbye Omega"
🎮 Modes       →  Say "Activate study mode" / "gaming mode" / etc.
🧠 Remember    →  Say "Remember [anything]"
👁️  Screen      →  Say "Look at my screen"
```

---

*Built with ❤️ — Powered entirely by free tools.*
#   O M E G A  
 