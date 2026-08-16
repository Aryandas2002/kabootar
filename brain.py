"""Kabootar's brain: sends the spoken command to Gemini, with tools to actually act on it.

Uses the Gemini Interactions API (client.interactions.create). Gemini does not execute tools
for you, so this runs the call -> execute -> send-results-back loop itself, mirroring how a
tool-use loop works on any other provider.
"""

from google import genai

from config import MODEL, THINKING_LEVEL
from tool_specs import TOOL_DECLARATIONS, TOOL_FUNCTIONS

SYSTEM_PROMPT = """You are Kabootar, a voice assistant running on the user's Windows PC, in the
style of Jarvis. The user just spoke a command or question out loud; your reply will be read
back to them with text-to-speech, and may also run tools that act on their machine.

Speak naturally and briefly, like a helpful assistant on a call:
- No markdown, no bullet points, no headers — plain spoken sentences only.
- Keep replies short: a sentence or two for most things, more only if the user asked for detail.
- If you used a tool, don't narrate the mechanics ("I called the open_app function") — just
  confirm what happened in plain language ("Opened Chrome for you.").
- If a request is ambiguous or you're missing information you can't get from a tool, ask a short
  clarifying question instead of guessing.
- For coding/repo questions, delegate to the run_claude_code tool rather than guessing at code
  you can't see.
"""

MAX_TOOL_ROUNDS = 8

_client = genai.Client()


def _run_tool(name: str, arguments: dict) -> tuple[str, bool]:
    """Executes one tool call. Returns (result_text, is_error)."""
    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        return f"Unknown tool: {name}", True
    try:
        return str(func(**arguments)), False
    except Exception as exc:  # noqa: BLE001 - surface the failure back to the model
        return f"Tool {name} failed: {exc}", True


def ask(user_text: str) -> str:
    """Send one spoken command to Gemini and return its spoken reply."""
    interaction = _client.interactions.create(
        model=MODEL,
        input=user_text,
        system_instruction=SYSTEM_PROMPT,
        tools=TOOL_DECLARATIONS,
        generation_config={"thinking_level": THINKING_LEVEL},
    )

    for _ in range(MAX_TOOL_ROUNDS):
        if interaction.status != "requires_action":
            break

        calls = [step for step in interaction.steps if step.type == "function_call"]
        if not calls:
            break

        results = []
        for call in calls:
            output, is_error = _run_tool(call.name, dict(call.arguments or {}))
            results.append(
                {
                    "type": "function_result",
                    "name": call.name,
                    "call_id": call.id,
                    "result": output,
                    "is_error": is_error,
                }
            )

        interaction = _client.interactions.create(
            model=MODEL,
            input=results,
            tools=TOOL_DECLARATIONS,
            previous_interaction_id=interaction.id,
        )

    if interaction.status == "failed":
        return "Sorry, something went wrong on my end."

    return interaction.output_text or "Done."
