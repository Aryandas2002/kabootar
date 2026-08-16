"""Offline text-to-speech via pyttsx3 (Windows SAPI5) — no API key or network needed."""

import threading

import pyttsx3

_lock = threading.Lock()


def speak(text: str) -> None:
    """Speak text out loud, blocking until finished. Safe to call from a background thread."""
    if not text:
        return
    with _lock:
        # A fresh engine per call avoids pyttsx3's flaky behavior when reused
        # across threads/calls on Windows (runAndWait can hang otherwise).
        engine = pyttsx3.init()
        try:
            engine.setProperty("rate", 180)
            engine.say(text)
            engine.runAndWait()
        finally:
            engine.stop()
