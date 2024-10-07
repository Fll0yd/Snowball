import json
import speech_recognition as sr
from gtts import gTTS, gTTSError
from pydub import AudioSegment
import pygame
import os
import io
from time import sleep
import pyttsx3
from core.logger import SnowballLogger

# Set the FFmpeg path directly (if using FFmpeg for audio conversion)
AudioSegment.converter = "C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffprobe = "C:/ffmpeg/bin/ffprobe.exe"

class VoiceInterface:
    def __init__(self, config_path="S:/Snowball/config/voice_settings.json"):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.logger = SnowballLogger()
        self.temp_dir = os.path.abspath("C:/temp")
        os.makedirs(self.temp_dir, exist_ok=True)

        # Try to load voice settings, fall back to defaults if the file is missing
        try:
            with open(config_path, 'r') as file:
                voice_settings = json.load(file)
            self.logger.logger.info(f"Loaded voice settings from {config_path}")
        except FileNotFoundError:
            self.logger.logger.error(f"Voice settings file not found: {config_path}, using default settings.")
            voice_settings = self.load_default_settings()

        # Voice settings
        self.language = voice_settings.get("language", "en")
        self.volume = voice_settings.get("volume", 70)
        self.speech_rate = voice_settings.get("speech_rate", 1.0)
        self.voice_gender = voice_settings.get("voice_gender", "female")
        self.engine_choice = voice_settings.get("engine", "gTTS")
        self.error_voice = voice_settings.get("error_voice", "Sorry, I didn't catch that.")

        # Configure pyttsx3 for offline TTS if chosen
        self.setup_pyttsx3()

    def load_default_settings(self):
        """Load default settings when config file is not found."""
        return {
            "language": "en",
            "volume": 70,
            "speech_rate": 1.0,
            "voice_gender": "female",
            "engine": "gTTS",
            "error_voice": "Sorry, I didn't catch that."
        }

    def setup_pyttsx3(self):
        """Configure the pyttsx3 engine based on the chosen voice gender."""
        voices = self.engine.getProperty('voices')
        if self.voice_gender.lower() == 'female':
            self.engine.setProperty('voice', voices[1].id)  # Typically, index 1 is female
        else:
            self.engine.setProperty('voice', voices[0].id)  # Typically, index 0 is male
        self.engine.setProperty('rate', self.speech_rate * 200)  # Adjust rate
        self.engine.setProperty('volume', self.volume / 100)  # Set volume

    def play_audio(self, file_path):
        """Play an audio file using pygame after converting it to WAV."""
        try:
            if os.path.exists(file_path):
                wav_path = file_path.replace(".mp3", ".wav")

                # Use in-memory file management with pydub to avoid unclosed files
                with open(file_path, 'rb') as mp3_file:
                    mp3_audio = mp3_file.read()

                # Convert MP3 to WAV using pydub
                audio = AudioSegment.from_mp3(io.BytesIO(mp3_audio))
                audio.export(wav_path, format="wav")

                # Initialize pygame and play audio
                pygame.mixer.init()
                pygame.mixer.music.load(wav_path)
                pygame.mixer.music.set_volume(self.volume / 100)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    sleep(1)

                self.logger.logger.info(f"Playing audio file: {wav_path}")
            else:
                self.logger.log_error(f"Audio file not found: {file_path}")
        except Exception as e:
            self.logger.log_error(f"Error playing audio: {e}")
        finally:
            wav_path = file_path.replace(".mp3", ".wav")
            if os.path.exists(wav_path):
                os.remove(wav_path)

    def speak(self, message):
        """Converts text to speech and plays the audio response."""
        file_path = os.path.join(self.temp_dir, "response.mp3")

        try:
            self.logger.logger.info(f"Converting text to speech: '{message}'")

            if self.engine_choice == "gTTS":
                # Use Google TTS (gTTS)
                tts = gTTS(text=message, lang=self.language, slow=self.speech_rate < 1.0)
                tts.save(file_path)
                self.play_audio(file_path)
            else:
                # Use pyttsx3 for offline TTS
                self.engine.say(message)
                self.engine.runAndWait()

            self.logger.logger.info(f"Speech synthesized: '{message}'")
        except gTTSError as e:
            self.logger.log_error(f"Google TTS service failed: {e}")
        except Exception as e:
            self.logger.log_error(f"Error during speech synthesis: {e}, {type(e).__name__}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def listen(self):
        """Listen for voice commands and return recognized text."""
        with sr.Microphone() as source:
            self.logger.logger.info("Listening for user input via microphone.")
            print("Listening...")
            try:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio)
                self.logger.logger.info(f"User input recognized: '{text}'")
                return text
            except sr.UnknownValueError:
                self.logger.logger.warning("Could not understand the audio")
                return self.error_voice
            except sr.RequestError as e:
                self.logger.logger.error(f"Speech recognition service error: {e}")
                return "Network error: Could not reach the speech recognition service."
            except Exception as e:
                self.logger.logger.error(f"Unexpected error during listening: {e}")
                return "An error occurred while processing your input."

# Example usage
if __name__ == "__main__":
    voice_interface = VoiceInterface()
    text = voice_interface.listen()
    voice_interface.speak(f"You said: {text}")
