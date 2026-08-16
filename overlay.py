"""A tiny always-on-top status widget — the "Kabootar just woke up" visual, Jarvis-style.

Tkinter must run on the main thread, so this exposes a thread-safe `set_state()` that
background threads call; the widget itself polls a queue on the Tk main loop.
"""

import queue
import tkinter as tk

_STATES = {
    "idle": ("\U0001F54A  Say “Kabootar” to wake me", "#2b2b2b", "#8a8a8a"),
    "listening": ("\U0001F54A  Listening...", "#1b3a2b", "#4ade80"),
    "thinking": ("\U0001F54A  Thinking...", "#2b2b1b", "#facc15"),
    "speaking": ("\U0001F54A  Speaking...", "#1b2a3a", "#60a5fa"),
}

_QUIT = object()


class Overlay:
    def __init__(self, on_quit=None):
        self._queue: "queue.Queue" = queue.Queue()
        self._on_quit = on_quit
        self.root = tk.Tk()
        self.root.title("Kabootar")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        try:
            self.root.attributes("-alpha", 0.92)
        except tk.TclError:
            pass

        self.label = tk.Label(
            self.root,
            text=_STATES["idle"][0],
            font=("Segoe UI", 11),
            padx=16,
            pady=10,
            bg=_STATES["idle"][1],
            fg=_STATES["idle"][2],
        )
        self.label.pack()

        self._place_bottom_right()
        self.root.protocol("WM_DELETE_WINDOW", self._request_quit)
        self.root.after(120, self._poll)

    def _place_bottom_right(self) -> None:
        self.root.update_idletasks()
        w = max(self.label.winfo_reqwidth() + 4, 260)
        h = self.label.winfo_reqheight() + 4
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = sw - w - 24
        y = sh - h - 60
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def set_state(self, state: str) -> None:
        """Thread-safe: call from any thread to update the widget."""
        self._queue.put(state)

    def request_quit(self) -> None:
        """Thread-safe: call from any thread to close the overlay and stop the mainloop."""
        self._queue.put(_QUIT)

    def _request_quit(self) -> None:
        self.request_quit()

    def _poll(self) -> None:
        try:
            while True:
                item = self._queue.get_nowait()
                if item is _QUIT:
                    if self._on_quit:
                        self._on_quit()
                    self.root.destroy()
                    return
                text, bg, fg = _STATES.get(item, _STATES["idle"])
                self.label.config(text=text, bg=bg, fg=fg)
                self.root.config(bg=bg)
                self._place_bottom_right()
        except queue.Empty:
            pass
        self.root.after(120, self._poll)

    def run(self) -> None:
        """Blocking — call from the main thread only."""
        self.root.mainloop()
