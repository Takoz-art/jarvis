"""PC-control tools Jarvis can use. Add your own apps to APPS below."""

import os
import subprocess
import webbrowser
from datetime import datetime
from urllib.parse import quote_plus

# Friendly name -> command to launch it. Edit this list to add your own apps.
APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "file explorer": "explorer.exe",
    "command prompt": "cmd.exe",
    "task manager": "taskmgr.exe",
    "settings": "ms-settings:",
    "chrome": "chrome",
    "edge": "msedge",
    "spotify": "spotify:",
    "discord": os.path.expandvars(r"%LOCALAPPDATA%\Discord\Update.exe --processStart Discord.exe"),
    "steam": "steam:",
    "vs code": "code",
}

TOOL_DEFINITIONS = [
    {
        "name": "open_app",
        "description": "Open an application on the user's PC. Only these apps are available: "
        + ", ".join(APPS) + ".",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"app": {"type": "string", "enum": list(APPS)}},
            "required": ["app"],
            "additionalProperties": False,
        },
    },
    {
        "name": "open_website",
        "description": "Open a website in the user's default browser. Use for requests like "
        "'open YouTube' or 'go to github.com'.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "Full URL, e.g. https://youtube.com"}},
            "required": ["url"],
            "additionalProperties": False,
        },
    },
    {
        "name": "google_search",
        "description": "Open a Google search results page in the browser so the user can see it. "
        "Use only when the user wants the results shown on screen; to answer a question "
        "yourself, use web_search instead.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_time",
        "description": "Get the current local date and time on the user's PC.",
        "strict": True,
        "input_schema": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
    },
]


def open_app(app: str) -> str:
    command = APPS.get(app.lower())
    if command is None:
        raise ValueError(f"Unknown app '{app}'. Known apps: {', '.join(APPS)}")
    if command.endswith(":"):  # URI protocol like ms-settings: or spotify:
        os.startfile(command)
    else:
        subprocess.Popen(f'start "" {command}', shell=True)
    return f"Opened {app}."


def open_website(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opened {url}."


def google_search(query: str) -> str:
    webbrowser.open("https://www.google.com/search?q=" + quote_plus(query))
    return f"Showing Google results for '{query}'."


def get_time() -> str:
    return datetime.now().strftime("It is %A, %d %B %Y, %H:%M.")


_HANDLERS = {
    "open_app": open_app,
    "open_website": open_website,
    "google_search": google_search,
    "get_time": get_time,
}


def run_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Run a tool by name. Returns (result text, is_error)."""
    handler = _HANDLERS.get(name)
    if handler is None:
        return f"Unknown tool: {name}", True
    try:
        return handler(**tool_input), False
    except Exception as e:  # report the failure back to Claude instead of crashing
        return f"Error: {e}", True
