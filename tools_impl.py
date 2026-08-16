"""The actions Kabootar can actually take. Plain functions — tool_specs.py wraps these as
Gemini function-calling tools and dispatches to them by name.
"""

import ctypes
import os
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

from config import APP_MAP

VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
KEYEVENTF_KEYUP = 0x0002

SCREENSHOT_DIR = Path.home() / "Pictures" / "Kabootar Screenshots"


def open_app(app_name: str) -> str:
    """Open a desktop application by name (e.g. Chrome, Notepad, Spotify, VS Code, Calculator)."""
    key = app_name.strip().lower()
    target = APP_MAP.get(key)
    if target is None:
        # Fall back to letting Windows try to resolve it directly (works for
        # anything on PATH or registered as an app, e.g. "steam").
        target = key.replace(" ", "")
    try:
        os.startfile(target)  # noqa: S606 - user-directed local automation
        return f"Opened {app_name}."
    except OSError:
        try:
            subprocess.Popen(["cmd", "/c", "start", "", target], shell=False)
            return f"Opened {app_name}."
        except Exception as exc:  # noqa: BLE001
            return f"Couldn't open {app_name}: {exc}"


def open_website(query_or_url: str) -> str:
    """Open a website, or search Google if given a plain-language query instead of a URL."""
    text = query_or_url.strip()
    looks_like_url = "." in text and " " not in text
    if looks_like_url:
        url = text if text.startswith("http") else f"https://{text}"
    else:
        url = f"https://www.google.com/search?q={quote_plus(text)}"
    webbrowser.open(url)
    return f"Opened {url} in your browser."


def control_volume(action: str, steps: int = 2) -> str:
    """Adjust the system volume. action is one of up/down/mute/unmute."""
    if action in ("mute", "unmute"):
        ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_KEYUP, 0)
        return "Toggled mute."
    vk = VK_VOLUME_UP if action == "up" else VK_VOLUME_DOWN
    for _ in range(max(1, min(int(steps), 20))):
        ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
    return f"Turned volume {action}."


def take_screenshot() -> str:
    """Take a screenshot of the current screen and save it to disk."""
    from PIL import ImageGrab

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOT_DIR / f"kabootar_{datetime.now():%Y%m%d_%H%M%S}.png"
    ImageGrab.grab().save(path)
    return f"Saved screenshot to {path}"


def lock_pc() -> str:
    """Lock the Windows workstation (same as Win+L)."""
    ctypes.windll.user32.LockWorkStation()
    return "Locked the PC."


def open_folder(path: str) -> str:
    """Open a folder or file in File Explorer."""
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        return f"That path doesn't exist: {expanded}"
    os.startfile(expanded)  # noqa: S606
    return f"Opened {expanded}"


def run_claude_code(instruction: str) -> str:
    """Hand an instruction off to the Claude Code CLI running in the current project folder."""
    cwd = os.environ.get("KABOOTAR_CODE_CWD", os.getcwd())
    try:
        result = subprocess.run(
            ["claude", "-p", instruction],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except FileNotFoundError:
        return "Claude Code CLI isn't installed or isn't on PATH."
    except subprocess.TimeoutExpired:
        return "Claude Code took too long and was stopped."

    output = (result.stdout or "").strip()
    if result.returncode != 0 and not output:
        return f"Claude Code failed: {(result.stderr or '').strip()[:500]}"
    return output or "Claude Code finished with no output."
