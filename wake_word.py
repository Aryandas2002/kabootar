"""Always-on microphone listening: spot the word "Kabootar", then capture the command that follows.

Uses SpeechRecognition's free Google Web Speech API for recognition (needs internet, no API key).
"""

import threading
from difflib import SequenceMatcher

import speech_recognition as sr

from config import COMMAND_PHRASE_TIME_LIMIT, COMMAND_TIMEOUT, WAKE_WORDS


def _matches_wake_word(text: str) -> bool:
    text = text.lower().strip()
    if not text:
        return False
    for word in WAKE_WORDS:
        if word in text:
            return True
        if SequenceMatcher(None, text, word).ratio() > 0.72:
            return True
    return False


class KabootarEar:
    """Wraps a microphone + recognizer with wake-word spotting and command capture."""

    def __init__(self, on_status=None):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.mic = sr.Microphone()
        self._on_status = on_status or (lambda *_: None)
        print(f"Using microphone: {sr.Microphone.list_microphone_names()[self.mic.device_index] if self.mic.device_index is not None else '(system default)'}")
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
        print(f"Calibrated. Energy threshold: {self.recognizer.energy_threshold:.1f}")

    def wait_for_wake_word(self, stop_event: threading.Event) -> bool:
        """Blocks, listening in short bursts, until "Kabootar" is heard or stop_event is set.

        Returns True on wake-word detection, False if stopped.
        """
        while not stop_event.is_set():
            try:
                with self.mic as source:
                    audio = self.recognizer.listen(
                        source, timeout=3, phrase_time_limit=3
                    )
            except sr.WaitTimeoutError:
                continue

            try:
                text = self.recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                print("[heard audio, couldn't make out words]")
                continue
            except sr.RequestError as exc:
                print(f"[speech recognition service error] {exc}")
                continue

            print(f"[heard] {text!r}")
            if _matches_wake_word(text):
                return True
        return False

    def listen_command(self) -> str:
        """Captures one spoken command and returns the transcribed text (empty on failure)."""
        try:
            with self.mic as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=COMMAND_TIMEOUT,
                    phrase_time_limit=COMMAND_PHRASE_TIME_LIMIT,
                )
        except sr.WaitTimeoutError:
            return ""

        try:
            return self.recognizer.recognize_google(audio)
        except (sr.UnknownValueError, sr.RequestError):
            return ""
