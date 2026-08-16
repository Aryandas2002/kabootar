"""Gemini function-calling declarations for the actions in tools_impl.py.

Gemini's Interactions API takes tool declarations as flat dicts:
{"type": "function", "name": ..., "description": ..., "parameters": <JSON schema>}
and returns FunctionCallStep.arguments as an already-parsed dict — see brain.py for the loop
that executes these and sends results back.
"""

import tools_impl

TOOL_DECLARATIONS = [
    {
        "type": "function",
        "name": "open_app",
        "description": (
            "Open a desktop application by name (e.g. Chrome, Notepad, Spotify, VS Code, "
            "Calculator)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "The plain-language app name, as the user said it.",
                }
            },
            "required": ["app_name"],
        },
    },
    {
        "type": "function",
        "name": "open_website",
        "description": (
            "Open a website, or search Google if given a plain-language query instead of a URL."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query_or_url": {
                    "type": "string",
                    "description": 'A URL ("github.com") or a search query ("best pizza near me").',
                }
            },
            "required": ["query_or_url"],
        },
    },
    {
        "type": "function",
        "name": "control_volume",
        "description": "Adjust the system volume: nudge it up/down or toggle mute.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["up", "down", "mute", "unmute"],
                },
                "steps": {
                    "type": "integer",
                    "description": "How many volume-key presses for up/down (~2% each). Default 2.",
                },
            },
            "required": ["action"],
        },
    },
    {
        "type": "function",
        "name": "take_screenshot",
        "description": "Take a screenshot of the current screen and save it to disk.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "name": "lock_pc",
        "description": "Lock the Windows workstation (same as Win+L).",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "name": "open_folder",
        "description": "Open a folder or file in File Explorer.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "An absolute or ~-relative filesystem path.",
                }
            },
            "required": ["path"],
        },
    },
    {
        "type": "function",
        "name": "run_claude_code",
        "description": (
            "Hand a coding/dev-repo task off to the Claude Code CLI running in the current "
            'project folder (e.g. "check git status", "run the tests"). Not for general '
            "questions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "instruction": {
                    "type": "string",
                    "description": "What to ask Claude Code to do or answer.",
                }
            },
            "required": ["instruction"],
        },
    },
]

TOOL_FUNCTIONS = {
    "open_app": tools_impl.open_app,
    "open_website": tools_impl.open_website,
    "control_volume": tools_impl.control_volume,
    "take_screenshot": tools_impl.take_screenshot,
    "lock_pc": tools_impl.lock_pc,
    "open_folder": tools_impl.open_folder,
    "run_claude_code": tools_impl.run_claude_code,
}
