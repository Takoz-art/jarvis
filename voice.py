"""Speech in (microphone -> text) and speech out (text -> voice)."""

import comtypes.client
import speech_recognition as sr

# Which speakers Jarvis talks through. Leave empty to use the Windows default device,
# or put part of a device name, e.g. "Logitech", "HyperX" or "ACER".
# Run `py -3.13 voice.py` to list your devices and hear a test.
AUDIO_OUTPUT = "Logitech"


class Voice:
    def __init__(self, language: str = "en-US", audio_output: str = AUDIO_OUTPUT) -> None:
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.0  # seconds of silence that end a sentence

        # Windows' built-in speech engine (SAPI).
        self.tts = comtypes.client.CreateObject("SAPI.SpVoice")
        self.tts.Rate = 1  # -10 (slow) .. 10 (fast)
        self.tts.Volume = 100

        # Prefer a male English voice (e.g. "Microsoft David") if one is installed.
        voices = self.tts.GetVoices()
        for i in range(voices.Count):
            if any(n in voices.Item(i).GetDescription().lower() for n in ("david", "george", "mark")):
                self.tts.Voice = voices.Item(i)
                break

        if audio_output:
            outputs = self.tts.GetAudioOutputs()
            for i in range(outputs.Count):
                if audio_output.lower() in outputs.Item(i).GetDescription().lower():
                    self.tts.AudioOutput = outputs.Item(i)
                    break
            else:
                print(f"  [audio device '{audio_output}' not found - using the default]")

    def say(self, text: str) -> None:
        print(f"Jarvis> {text}")
        self.tts.Speak(text)

    def listen(self, timeout: float | None = 6, quiet: bool = False) -> str:
        """Record one sentence from the microphone and return it as text ('' if nothing heard).

        timeout: seconds to wait for speech to start (None = wait forever).
        quiet: don't print status messages (used by wake mode, which listens constantly).
        """
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                if not quiet:
                    print("  [listening...]")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=20)
        except (OSError, AttributeError):  # AttributeError = PyAudio not installed
            raise MicrophoneError("No microphone found (or PyAudio isn't installed).")
        except sr.WaitTimeoutError:
            if not quiet:
                print("  [didn't hear anything]")
            return ""

        try:
            return self.recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            if not quiet:
                print("  [couldn't understand that]")
            return ""
        except sr.RequestError:
            print("  [speech service unavailable - check the internet connection]")
            return ""


class MicrophoneError(Exception):
    pass


if __name__ == "__main__":
    # Speaker test: lists every output device and says a line through each one.
    voice = Voice()
    outputs = voice.tts.GetAudioOutputs()
    for i in range(outputs.Count):
        name = outputs.Item(i).GetDescription()
        voice.tts.AudioOutput = outputs.Item(i)
        voice.say(f"Testing device {i + 1}.")
        print(f"  ^ device {i + 1}: {name}")
