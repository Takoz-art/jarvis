"""Speech in (microphone -> text) and speech out (text -> voice)."""

import pyttsx3
import speech_recognition as sr


class Voice:
    def __init__(self, language: str = "en-US") -> None:
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.0  # seconds of silence that end a sentence

        self.tts = pyttsx3.init()
        self.tts.setProperty("rate", 185)
        # Prefer a male English voice (e.g. "Microsoft David") if one is installed.
        for v in self.tts.getProperty("voices"):
            if "david" in v.name.lower() or "george" in v.name.lower():
                self.tts.setProperty("voice", v.id)
                break

    def say(self, text: str) -> None:
        print(f"Jarvis> {text}")
        self.tts.say(text)
        self.tts.runAndWait()

    def listen(self) -> str:
        """Record one sentence from the microphone and return it as text ('' if nothing heard)."""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                print("  [listening...]")
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=20)
        except (OSError, AttributeError):  # AttributeError = PyAudio not installed
            print("  [no microphone found - type your message instead]")
            return ""
        except sr.WaitTimeoutError:
            print("  [didn't hear anything]")
            return ""

        try:
            return self.recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            print("  [couldn't understand that]")
            return ""
        except sr.RequestError:
            print("  [speech service unavailable - type your message instead]")
            return ""
