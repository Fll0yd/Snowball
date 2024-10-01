import json
import speech_recognition as sr
from gtts import gTTS, gTTSError
from pydub import AudioSegment
import pygame
import os
import io
from time import sleep
from core.logger import SnowballLogger
import pyttsx3

# Set the FFmpeg path directly (if using FFmpeg for audio conversion)
AudioSegment.converter = "C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffprobe = "C:/ffmpeg/bin/ffprobe.exe"

class VoiceInterface:
    def __init__(self, config_path="S:/config/voice_settings.json"):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.logger = SnowballLogger()
        self.temp_dir = os.path.abspath("C:/temp")
        os.makedirs(self.temp_dir, exist_ok=True)

        # Load voice settings from the new JSON config
        with open(config_path, 'r') as file:
            voice_settings = json.load(file)

        # Voice settings
        self.language = voice_settings.get("language", "en")
        self.volume = voice_settings.get("volume", 70)
        self.speech_rate = voice_settings.get("speech_rate", 1.0)
        self.voice_gender = voice_settings.get("voice_gender", "female")
        self.engine = voice_settings.get("engine", "gTTS")
        self.error_voice = voice_settings.get("error_voice", "Sorry, I didn't catch that.")

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
        """Respond with speech."""
        self.engine.say(message)
        self.engine.runAndWait()
        """Converts text to speech and plays the audio response."""
        file_path = os.path.join(self.temp_dir, "response.mp3")
        
        print(f"Saving speech to: {file_path}")  # Debug statement

        try:
            self.logger.logger.info(f"Converting text to speech: '{text}'")
            tts = gTTS(text=text, lang=self.language, slow=self.speech_rate < 1.0)
            tts.save(file_path)
            print(f"File {file_path} created: {os.path.exists(file_path)}")  # Debug to check if save worked

            # Play the audio after converting it to WAV
            self.play_audio(file_path)
        except gTTSError as e:
            self.logger.log_error(f"Google TTS service failed: {e}")
        except Exception as e:
            self.logger.log_error(f"Error during speech synthesis: {e}, {type(e).__name__}")
        finally:
            # Only remove the .mp3 file here
            if os.path.exists(file_path):
                os.remove(file_path)

    def listen(self):
        """Listen for voice commands."""
        with sr.Microphone() as source:
            print("Listening...")
            self.logger.logger.info("Listening for user input via microphone.")
            try:
                recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
                text = recognizer.recognize_google(audio)
                self.logger.logger.info(f"User input recognized: '{text}'")
                return text
            except sr.UnknownValueError:
                self.logger.log_warning(self.error_voice)
                return self.error_voice
            except sr.RequestError as e:
                self.logger.log_error(f"Speech recognition service is unavailable: {e}")
                return "Network error: Could not reach the speech recognition service."
            except Exception as e:
                self.logger.log_error(f"Unexpected error during listening: {e}")
                return "An error occurred while processing your input."
            try:
                command = self.recognizer.recognize_google(audio)
                print(f"Recognized command: {command}")
                return command
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")