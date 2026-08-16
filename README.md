# Kabootar 🕊️

A Jarvis-style voice assistant for Windows. Say **"Kabootar"**, it wakes up, listens for a
command, and either answers you out loud or actually does the thing (opens an app, opens a
website, adjusts volume, takes a screenshot, locks the PC, or hands a coding task to Claude Code).

## How it works

- A background thread listens to your mic in short bursts and checks each phrase for something
  that sounds like "Kabootar" (fuzzy-matched, since speech recognition mishears it a lot).
- On wake, a small always-on-top status widget appears bottom-right and it listens for your
  command.
- Your command goes to Gemini (`gemini-3.5-flash` by default) via Google's Interactions API,
  which can either just answer you or call a tool to actually take the action. `brain.py` runs
  that call/execute/respond loop itself.
- The reply is spoken back to you with offline text-to-speech.

## Setup

1. **Install dependencies** (from this folder):

   ```bash
   pip install -r requirements.txt
   ```

2. **Add your Gemini API key.** Copy `.env.example` to `.env` and paste in a free key from
   <https://aistudio.google.com/apikey>:

   ```bash
   cp .env.example .env
   ```

   Or just set it for the session:

   ```powershell
   $env:GEMINI_API_KEY = "AIza..."
   ```

3. **Run it:**

   ```bash
   python kabootar.py
   ```

   Say "Kabootar" out loud, wait for the status widget to say "Listening...", then speak your
   command.

4. **Quit:** right-click the tray icon in the taskbar corner → **Quit Kabootar**.

## What you can say

- "Kabootar, open Chrome" / "open Spotify" / "open notepad"
- "Kabootar, search for the weather in Kochi" (opens a browser search)
- "Kabootar, turn the volume down"
- "Kabootar, take a screenshot"
- "Kabootar, lock the PC"
- "Kabootar, ask Claude Code to check git status" (runs `claude -p ...` in the current folder —
  set `KABOOTAR_CODE_CWD` env var to point it at a specific project)
- Or just ask it anything — "Kabootar, what's the capital of France?"

## Extending it

- **Apps it knows how to open** live in `config.py` → `APP_MAP`. Add your own (Discord, Steam,
  etc.) — the value is whatever `os.startfile()` or the Windows `start` command would accept.
- **New abilities:** add a plain function to `tools_impl.py`, then register it in
  `tool_specs.py` — a JSON-schema entry in `TOOL_DECLARATIONS` (name, description, parameters)
  and a name → function mapping in `TOOL_FUNCTIONS`. The description is what Gemini uses to
  decide when to call it.
- **Wake-word variants** (to catch more mishearings) are in `config.py` → `WAKE_WORDS`.
- **Speed vs. quality:** `gemini-3.5-flash` is the default brain, already fast. `KABOOTAR_MODEL`
  in `.env` can point at another Gemini model (e.g. `gemini-3.1-flash-lite` for even snappier
  simple commands, or `gemini-3.1-pro-preview` for harder requests). `KABOOTAR_THINKING_LEVEL`
  (`minimal`/`low`/`medium`/`high`) trades latency for reasoning depth — `low` is the default.

## Notes / limits

- Wake-word and command recognition use the free Google Web Speech API via the
  `SpeechRecognition` package — it needs an internet connection and isn't a true low-power local
  wake-word engine, so there's a small amount of always-on network chatter while idle.
- Deliberately left out: shutdown/restart/delete-type system commands. If you want those, add
  them to `tools_impl.py` yourself — they're one-liners, but risky enough that they shouldn't be
  in by default.
- Text-to-speech uses Windows' built-in SAPI voices via `pyttsx3` (offline, no extra setup).
