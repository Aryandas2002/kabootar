"""Kabootar — a Jarvis-style voice assistant. Say "Kabootar" to wake it, then speak a command.

Run:  python kabootar.py
Quit: right-click the tray icon -> Quit, or close the little status widget.
"""

import os
import sys
import threading

from dotenv import load_dotenv

load_dotenv()

if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
    print(
        "GEMINI_API_KEY is not set.\n"
        "Get a free key at https://aistudio.google.com/apikey and either:\n"
        "  - copy .env.example to .env and paste it in, or\n"
        "  - set it for this session:  $env:GEMINI_API_KEY = 'AIza...'\n"
    )
    sys.exit(1)

import brain
import tts
from overlay import Overlay
from wake_word import KabootarEar

stop_event = threading.Event()


def assistant_loop(overlay: Overlay) -> None:
    print("Kabootar is listening for its wake word...")
    ear = KabootarEar()
    overlay.set_state("idle")

    while not stop_event.is_set():
        woke, leftover = ear.wait_for_wake_word(stop_event)
        if not woke or stop_event.is_set():
            break

        overlay.set_state("listening")
        if leftover:
            # They said the command in the same breath as the wake word
            # ("Kabootar, open YouTube") — no need to listen again.
            print(f"Woke up — command included: {leftover!r}")
            command = leftover
        else:
            print("Woke up — listening for a command...")
            command = ear.listen_command()

        if not command:
            print("Didn't catch anything.")
            overlay.set_state("idle")
            continue

        print(f"You said: {command}")
        overlay.set_state("thinking")
        try:
            reply = brain.ask(command)
        except Exception as exc:  # noqa: BLE001 - keep the assistant alive on any failure
            reply = "Sorry, I ran into a problem handling that."
            print(f"Error from brain.ask: {exc}")

        print(f"Kabootar: {reply}")
        overlay.set_state("speaking")
        tts.speak(reply)
        overlay.set_state("idle")


def make_tray_icon(overlay: Overlay):
    import pystray
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((2, 2, 62, 62), fill=(37, 99, 235, 255))
    draw.text((20, 18), "K", fill="white")

    def on_quit(icon, _item):
        stop_event.set()
        icon.stop()
        overlay.request_quit()

    menu = pystray.Menu(pystray.MenuItem("Quit Kabootar", on_quit))
    return pystray.Icon("kabootar", img, "Kabootar", menu)


def main() -> None:
    overlay = Overlay(on_quit=stop_event.set)

    listener_thread = threading.Thread(
        target=assistant_loop, args=(overlay,), daemon=True
    )
    listener_thread.start()

    tray = make_tray_icon(overlay)
    tray_thread = threading.Thread(target=tray.run, daemon=True)
    tray_thread.start()

    try:
        overlay.run()  # blocks on the main thread until quit
    finally:
        stop_event.set()
        try:
            tray.stop()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()
