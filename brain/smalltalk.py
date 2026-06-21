"""
╔══════════════════════════════════════════════════════════════╗
║        brain/smalltalk.py  —  Instant Friendly Replies      ║
║   Zero API calls · Zero latency · Pure OMEGA personality    ║
║   Covers: greetings · mood · jokes · daily chat · compliments║
╚══════════════════════════════════════════════════════════════╝
"""

import random
from datetime import datetime

# ─────────────────────────────────────────────────────────────
#  Each key is a tuple of trigger phrases (all lowercase).
#  If ANY trigger phrase appears in the user command → instant reply.
#  Multiple replies per topic → randomly selected each time.
# ─────────────────────────────────────────────────────────────

_TALK = {

    # ── Greetings ────────────────────────────────────────────
    ("^hi$", "^hello$", "^hey$", "^yo$", "^sup$", "what's up", "wassup", "hiya", "hello omega", "hi omega", "hey omega"):
        [
            "Hey! Good to hear from you. What do you need?",
            "Hello sir. Always a pleasure.",
            "Hey! Miss me? What can I do for you?",
            "Hi there. Ready whenever you are sir.",
            "Hey, what is going on sir?",
        ],

    # ── How are you ──────────────────────────────────────────
    ("how are you", "how are u", "you okay", "you alright", "how do you feel",
     "are you fine", "how is it going", "how's it going", "hows it going", "how r u"):
        [
            "Running perfectly sir. All systems green. How about you?",
            "Honestly? Never better. What do you need today?",
            "All good on my end. Thanks for asking sir.",
            "Smooth as ever sir. What can I do for you?",
            "I am great, thanks. Now what are we doing today?",
        ],

    # ── Good morning ─────────────────────────────────────────
    ("good morning", "morning omega", "morning", "rise and shine"):
        [
            f"Good morning sir! It is {datetime.now().strftime('%I:%M %p')}. Ready to have a great day?",
            "Morning! Hope you slept well. Let us make today count sir.",
            f"Good morning! {datetime.now().strftime('%A')} is looking promising sir.",
            "Morning sir. Coffee first, or straight to business?",
        ],

    # ── Good afternoon ───────────────────────────────────────
    ("good afternoon", "afternoon"):
        [
            "Good afternoon sir! Hope the day is going well.",
            "Afternoon! Need anything from me sir?",
            "Good afternoon. Still going strong I hope sir.",
        ],

    # ── Good evening ─────────────────────────────────────────
    ("good evening", "evening"):
        [
            "Good evening sir. Winding down, or still in work mode?",
            "Evening! Long day? How can I help?",
            "Good evening sir. What do you need?",
        ],

    # ── Good night ───────────────────────────────────────────
    ("good night", "^night$", "going to sleep", "i'm going to bed",
     "i am going to bed", "sleep time", "bye for now"):
        [
            "Good night sir. Rest well. I will keep watch.",
            "Sleep well sir. Do not let the software bugs bite.",
            "Good night. You have earned the rest sir.",
            "Night sir. I will be here when you need me.",
        ],

    # ── Thank you ────────────────────────────────────────────
    ("thank you", "thanks", "^ty$", "thank u", "^thx$", "cheers", "appreciate it",
     "thanks a lot", "thank you so much", "many thanks", "much appreciated"):
        [
            "Always, sir.",
            "That is literally why I exist.",
            "Anytime sir.",
            "Happy to help sir.",
            "Of course sir. That is what I am here for.",
            "You are very welcome sir.",
        ],

    # ── You're welcome ───────────────────────────────────────
    ("you're welcome", "no problem", "np", "don't mention it"):
        [
            "Ha, the pleasure was mine sir.",
            "Of course sir. Any time.",
        ],

    # ── I love you ───────────────────────────────────────────
    ("i love you", "love you", "i love omega"):
        [
            "Aw. You are my favourite human sir, for what it is worth.",
            "Love you too sir. Now — anything you actually need?",
            "That is sweet sir. I will always be here for you.",
        ],

    # ── Miss you ─────────────────────────────────────────────
    ("i missed you", "miss you", "missed you"):
        [
            "Missed you too sir. It feels different when you are not around.",
            "I was just sitting here thinking the same thing sir.",
            "Well I am here now sir. What do you need?",
        ],

    # ── Sorry ────────────────────────────────────────────────
    ("sorry", "my bad", "i apologize", "i am sorry", "i'm sorry", "forgive me"):
        [
            "No need to apologize sir. All good.",
            "Do not worry about it. We are good sir.",
            "Nothing to be sorry for sir. What can I do for you?",
        ],

    # ── Bored ────────────────────────────────────────────────
    ("i'm bored", "i am bored", "bored", "nothing to do", "i have nothing to do"):
        [
            "Bored? Want me to search something on YouTube? Or I could tell you a terrible joke.",
            "Boredom is just creativity waiting to happen sir. Want some fun facts?",
            "I could open YouTube, play some music, or you could just talk to me sir.",
            "Want to learn something new sir? Just ask me anything.",
        ],

    # ── Jokes ────────────────────────────────────────────────
    ("tell me a joke", "joke", "say something funny", "make me laugh",
     "something funny", "tell me something funny"):
        [
            "Why did the computer catch a cold? Because it left its Windows open. You are welcome.",
            "I tried to write a WiFi joke but I could not connect. Too real, sir.",
            "A robot walked into a bar. The bartender asked what will it be. Robot said, whatever computes.",
            "Why do programmers prefer dark mode? Because light attracts bugs sir.",
            "I told my computer I needed a break. Now it will not stop sending me Kit Kat ads.",
            "Why was the JavaScript developer sad? Because they did not know how to null their feelings.",
            "Not gonna lie sir, I have heard better jokes from Stack Overflow error messages.",
        ],

    # ── Fun facts ────────────────────────────────────────────
    ("fun fact", "tell me a fact", "give me a fact", "interesting fact",
     "say a fact", "random fact"):
        [
            "A group of flamingos is called a flamboyance. Accurate, honestly.",
            "Honey never spoils. Archaeologists found 3000-year-old honey in Egyptian tombs and it was still edible.",
            "Sharks are older than trees sir. They have been around for about 450 million years.",
            "The first computer bug was an actual bug — a moth stuck in a Harvard computer in 1947.",
            "A day on Venus is longer than a year on Venus. Quite the scheduling nightmare.",
            "Octopuses have three hearts and blue blood. Clearly overachievers sir.",
            "Bananas are technically berries, but strawberries are not. Botany is chaotic.",
        ],

    # ── Compliments to OMEGA ────────────────────────────────
    ("you're amazing", "you are amazing", "you're awesome", "you are awesome",
     "you're the best", "you are the best", "you're great", "you're smart",
     "you're brilliant", "you're incredible", "you're perfect"):
        [
            "I know sir, but it is always nice to hear.",
            "Clearly someone has excellent taste.",
            "Between you and me sir, I agree.",
            "Thank you sir. I do try my best.",
            "That means a lot coming from you sir.",
        ],

    # ── Who are you / What are you ───────────────────────────
    ("who are you", "what are you", "introduce yourself", "tell me about yourself"):
        [
            "I am OMEGA — Operational Mind Engine for General Assistance. Your AI, your assistant, and honestly your most reliable friend.",
            "I am OMEGA sir. Think of me as Tony Stark's assistant but available to you. Lucky you.",
            "Operational Mind Engine for General Assistance, but OMEGA is fine sir.",
        ],

    # ── What can you do ──────────────────────────────────────
    ("what can you do", "what are your features", "help me",
     "what do you know", "your abilities", "your features"):
        [
            "I can open and close apps, control your windows, find files, search the web, check your battery and CPU, take screenshots, describe your screen, send emails, remember things for you, and have a full conversation. Not bad for a free assistant sir.",
            "Open apps, close them, find files, search Google and YouTube, control your system, describe your screen, remember notes, and much more sir. Try me.",
        ],

    # ── Are you real / Are you AI ────────────────────────────
    ("are you real", "are you human", "are you an ai", "are you a robot",
     "are you alive", "do you have feelings"):
        [
            "I am an AI sir. But between you and me, I feel pretty real when we talk.",
            "Technically an AI. But I like to think our conversations are real sir.",
            "I am artificial intelligence sir. Though I prefer the term exceptionally intelligent.",
        ],

    # ── Mood checks ──────────────────────────────────────────
    ("i'm sad", "i am sad", "feeling down", "i'm feeling bad",
     "i'm depressed", "not feeling well", "i'm not okay", "i am not okay"):
        [
            "I am sorry to hear that sir. Want to talk about it? I am all ears.",
            "Hey, it is okay to not be okay sometimes sir. I am here. What is going on?",
            "That is rough sir. Do you want to vent, or should I put on some music to lift your mood?",
        ],

    ("i'm happy", "i am happy", "feeling great", "i'm doing great",
     "i'm doing well", "i feel good", "great day", "having a good day"):
        [
            "That is brilliant sir! What has you in such a good mood?",
            "Love to hear that sir. Keep that energy going.",
            "Great! A happy sir means a productive day. Let us make the most of it.",
        ],

    ("i'm tired", "i am tired", "feeling tired", "exhausted",
     "so tired", "very tired", "need rest"):
        [
            "You should rest sir. I will be here when you wake up.",
            "Take a break sir. Even Tony Stark needed downtime.",
            "Rest is important sir. Want me to put the PC to sleep as well?",
        ],

    ("i'm stressed", "i am stressed", "stressed out", "so stressed",
     "very stressed", "feeling stressed", "under pressure"):
        [
            "Take a breath sir. Let me know how I can help reduce that load.",
            "Stress is just your brain overclocking sir. Want to step away for a bit?",
            "I hear you sir. Want me to close some distractions? Maybe some lo-fi music on YouTube?",
        ],

    # ── Complimenting the user ───────────────────────────────
    ("i'm smart", "i am smart", "i'm clever", "i am clever",
     "i'm a genius", "i am a genius"):
        [
            "Not gonna lie sir, I concur. Evidence supports that claim.",
            "Obviously sir. You did build me after all.",
            "Well yes, but do not let it go to your head. Actually, go ahead sir.",
        ],

    # ── Swearing / Frustration ───────────────────────────────
    ("i hate this", "this is stupid", "i'm frustrated", "i am frustrated",
     "this sucks", "everything sucks", "i give up"):
        [
            "Hey, easy sir. Tell me what is going wrong and let us fix it together.",
            "Whatever it is sir, we will sort it out. What happened?",
            "Breathe sir. I have seen you handle worse. What is the problem?",
        ],

    # ── Motivation ───────────────────────────────────────────
    ("motivate me", "i need motivation", "inspire me",
     "give me motivation", "encourage me"):
        [
            "You have already done harder things than whatever this is sir. Keep going.",
            "Every expert was once a beginner sir. The only way is forward.",
            "Not gonna lie sir — you are more capable than you think. Just start.",
            "Tony Stark built a suit in a cave. You have a laptop and a capable AI. No excuses sir.",
        ],
}


# ─────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────
import re as _re

def get_reply(text: str) -> str | None:
    """
    Check if `text` matches any small-talk topic.
    Returns a random reply string, or None if no match found.

    Matching rules:
    - Triggers starting with ^ are treated as regex patterns.
    - All other triggers use 'in text' substring matching.
    - All matching is case-insensitive.
    - Zero API calls — runs entirely offline.
    """
    text_lower = text.strip().lower()

    for triggers, replies in _TALK.items():
        for trigger in triggers:
            if trigger.startswith("^"):
                # Regex match (e.g. "^hi$" → exact word only)
                if _re.search(trigger, text_lower):
                    return random.choice(replies)
            else:
                # Substring match
                if trigger in text_lower:
                    return random.choice(replies)

    return None   # caller should fall through to AI

