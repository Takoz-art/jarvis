J.A.R.V.I.S.
A voice-controlled personal assistant for Windows, powered by Claude.

🎙️ Talk to it: press Enter and speak. It answers out loud.
⌨️ Or type: type a message instead of speaking.
🖥️ PC control: opens apps and websites, shows Google searches, and tells the time.
🌐 Web search: answers questions about current events, weather, and more.
🧠 Remembers the conversation while it's running.
Setup
Install Python 3.10+ from https://www.python.org/downloads/. Tick "Add python.exe to PATH" in the installer.
Download this repo: click the green Code button → Download ZIP and unzip it. If you have git, clone the repo instead.
Install the dependencies. Open a terminal in the folder and run:
pip install -r requirements.txt
Add your API key. Get a key at https://console.anthropic.com. Copy .env.example to a new file named .env and paste your key into it:
ANTHROPIC_API_KEY=sk-ant-...
.env is in .gitignore, so your key never gets uploaded to GitHub.
Run it:
python jarvis.py
Usage
You say / type	Jarvis does
"Open Spotify"	Launches Spotify
"Go to YouTube"	Opens youtube.com
"What time is it?"	Tells you the time
"What's the weather in Stockholm?"	Searches the web and answers
"Google pictures of cats"	Opens Google results in your browser
"Goodbye"	Shuts down
Customizing
Add apps: edit the APPS list at the top of pc_tools.py.
Personality: edit SYSTEM_PROMPT in jarvis.py.
Speak Swedish: change Voice() to Voice(language="sv-SE") in jarvis.py, and tell Jarvis to reply in Swedish in SYSTEM_PROMPT.
Troubleshooting
pip install PyAudio fails: upgrade pip with python -m pip install --upgrade pip and try again. PyAudio is only needed for the microphone, so typing still works without it.
It doesn't hear you: check that Windows has picked the right default microphone under Settings → System → Sound.
