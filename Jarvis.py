"""
J.A.R.V.I.S. - a voice + text personal assistant powered by Claude.

Run:  python jarvis.py
      Press Enter to speak, or type a message and press Enter.
      Say or type "goodbye" to quit.
"""

import os
import sys

import anthropic
from dotenv import load_dotenv

from pc_tools import TOOL_DEFINITIONS, run_tool
from voice import Voice

load_dotenv()

MODEL = "claude-opus-5"
MAX_HISTORY_MESSAGES = 40  # keep the conversation from growing forever

SYSTEM_PROMPT = """You are J.A.R.V.I.S., a witty, loyal and highly capable personal \
assistant running on the user's Windows PC. Address the user as "sir" occasionally, \
in the spirit of Tony Stark's assistant, but don't overdo it.

Your replies are usually read aloud by a text-to-speech voice, so:
- Keep answers short and conversational (1-3 sentences unless asked for more).
- No markdown, bullet points, emojis, code blocks or URLs in your spoken replies.

You can control the PC with your tools (open apps, open websites, tell the time) \
and search the web for current information. When the user asks you to do something \
a tool can do, just do it and confirm briefly."""

TOOLS = TOOL_DEFINITIONS + [
    {"type": "web_search_20260209", "name": "web_search", "max_uses": 3},
]


def ask_claude(client: anthropic.Anthropic, messages: list) -> str:
    """Send the conversation to Claude, run any tools it asks for, return its reply text."""
    while True:
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            thinking={"type": "adaptive"},
            output_config={"effort": "low"},  # fast, snappy answers for a voice assistant
            betas=["server-side-fallback-2026-07-01"],
            extra_body={"fallbacks": "default"},  # if a request is declined, retry on a fallback model
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "refusal":
            return "I'm afraid I can't help with that one, sir."

        if response.stop_reason == "pause_turn":
            continue  # a long web search paused; resend to let it finish

        if response.stop_reason == "tool_use":
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  [tool] {block.name} {block.input}")
                    output, is_error = run_tool(block.name, block.input)
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": output,
                        "is_error": is_error,
                    })
            messages.append({"role": "user", "content": results})
            continue

        return "".join(b.text for b in response.content if b.type == "text").strip()


def trim_history(messages: list) -> list:
    """Drop the oldest turns, always starting on a plain user text message."""
    if len(messages) <= MAX_HISTORY_MESSAGES:
        return messages
    trimmed = messages[-MAX_HISTORY_MESSAGES:]
    while trimmed and not (trimmed[0]["role"] == "user" and isinstance(trimmed[0]["content"], str)):
        trimmed.pop(0)
    return trimmed


def main() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("Missing ANTHROPIC_API_KEY. Copy .env.example to .env and paste your key in it.")

    client = anthropic.Anthropic()
    voice = Voice()
    messages: list = []

    voice.say("Jarvis online. How can I help, sir?")
    print("\n(Press Enter to speak, or type a message. Say 'goodbye' to quit.)")

    while True:
        typed = input("\nYou> ").strip()
        user_text = typed or voice.listen()
        if not user_text:
            continue
        if not typed:
            print(f"You (spoken)> {user_text}")

        if user_text.lower().strip(" .!") in {"goodbye", "bye", "exit", "quit", "shut down"}:
            voice.say("Goodbye, sir.")
            break

        turn_start = len(messages)
        messages.append({"role": "user", "content": user_text})
        try:
            reply = ask_claude(client, messages)
        except anthropic.APIConnectionError:
            reply = "I can't reach my servers right now. Check the internet connection."
            del messages[turn_start:]
        except anthropic.RateLimitError:
            reply = "I'm being rate limited. Give me a moment and try again."
            del messages[turn_start:]
        except anthropic.APIStatusError as e:
            print(f"  [error] {e.status_code}: {e.message}")
            reply = "Something went wrong on my end, sir."
            del messages[turn_start:]

        voice.say(reply or "Done.")
        messages = trim_history(messages)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nJarvis offline.")
