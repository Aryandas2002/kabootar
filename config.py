"""Kabootar settings: wake word variants, model choice, and the app-name -> launch-target map."""

import os

# Words/phrases that count as "Kabootar" — speech recognition regularly mishears it,
# so we match against several plausible transcriptions rather than an exact string.
WAKE_WORDS = [
    "kabootar",
    "kabutar",
    "cabootar",
    "kabotar",
    "kaboo tar",
    "kabu tar",
    "cobitar",
    "kabuter",
    "cuckoo tar",
    "kabootr",
]

MODEL = os.environ.get("KABOOTAR_MODEL", "gemini-3.5-flash")
THINKING_LEVEL = os.environ.get("KABOOTAR_THINKING_LEVEL", "low")

# How long (seconds) to listen for a command after the wake word fires.
COMMAND_PHRASE_TIME_LIMIT = 8
# How long to wait in silence before giving up on a command.
COMMAND_TIMEOUT = 5

# Friendly name -> how to launch it. Values are passed to os.startfile / subprocess.
# Extend this freely — it's just a lookup table.
APP_MAP = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "browser": "chrome",
    "edge": "msedge",
    "firefox": "firefox",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "explorer": "explorer",
    "file explorer": "explorer",
    "files": "explorer",
    "paint": "mspaint",
    "cmd": "cmd",
    "command prompt": "cmd",
    "terminal": "wt",
    "powershell": "powershell",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "spotify": "spotify",
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
    "code": "code",
    "settings": "ms-settings:",
    "task manager": "taskmgr",
    "control panel": "control",
}
