import json
import speech_recognition as sr
from gtts import gTTS, gTTSError
from pydub import AudioSegment
import pygame
import os
import io
import time
import pyttsx3
from core.logger import SnowballLogger
from openai import OpenAI
from core.config_loader import ConfigLoader
import concurrent.futures
import uuid

client = OpenAI()  # This will automatically use the `OPENAI_API_KEY` from the environment

# Set the FFmpeg path directly (if using FFmpeg for audio conversion)
AudioSegment.converter = "C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffprobe = "C:/ffmpeg/bin/ffprobe.exe"

class VoiceInterface:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.logger = SnowballLogger()
        self.temp_dir = os.path.abspath("C:/temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

        # Load voice settings using ConfigLoader
        voice_settings = ConfigLoader.load_config("interface_settings.json")

        # Voice settings
        self.language = voice_settings.get("language", "en-US")
        self.volume = voice_settings.get("volume", 70)
        self.speech_rate = voice_settings.get("speech_rate", 1.0)
        self.voice_gender = voice_settings.get("voice_gender", "female")
        self.engine_choice = voice_settings.get("engine", "gTTS")
        self.error_voice = voice_settings.get("error_voice", "Sorry, I didn't catch that.")

        # Log loaded voice settings
        self.logger.log_config_change("language", None, self.language, user="System Initialization")
        self.logger.log_config_change("volume", None, self.volume, user="System Initialization")
        self.logger.log_config_change("speech_rate", None, self.speech_rate, user="System Initialization")
        self.logger.log_config_change("voice_gender", None, self.voice_gender, user="System Initialization")
        self.logger.log_config_change("engine", None, self.engine_choice, user="System Initialization")

        # Configure pyttsx3 for offline TTS if chosen
        self.setup_pyttsx3()

    def setup_pyttsx3(self):
        """Configure the pyttsx3 engine based on the chosen voice gender."""
        voices = self.engine.getProperty('voices')
        if self.voice_gender.lower() == 'female':
            self.engine.setProperty('voice', voices[1].id)  # Typically, index 1 is female
        else:
            self.engine.setProperty('voice', voices[0].id)  # Typically, index 0 is male
        self.engine.setProperty('rate', self.speech_rate * 200)  # Adjust rate
        self.engine.setProperty('volume', self.volume / 100)  # Set volume
        self.logger.log_event("pyttsx3 TTS engine configured with gender: {} and speech rate: {}".format(self.voice_gender, self.speech_rate))

    def play_audio(self, file_path):
        """Play an audio file using pygame after converting it to WAV."""
        def play():
            try:
                if not os.path.exists(file_path):
                    self.logger.log_error(f"Audio file not found: {file_path}")
                    return

                wav_path = os.path.join(self.temp_dir, "response.wav")

                # Convert MP3 to WAV using pydub
                with open(file_path, 'rb') as mp3_file:
                    mp3_audio = mp3_file.read()
                audio = AudioSegment.from_mp3(io.BytesIO(mp3_audio))
                audio.export(wav_path, format="wav")

                # Initialize pygame and play audio
                pygame.mixer.init()
                pygame.mixer.music.load(wav_path)
                pygame.mixer.music.set_volume(self.volume / 100)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                # Stop mixer to release the file
                pygame.mixer.music.stop()
                pygame.mixer.quit()

                self.logger.log_event(f"Playing audio file: {wav_path}")
            except Exception as e:
                self.logger.log_error(f"Error playing audio: {e}")
            finally:
                # Ensure the WAV file is removed even if an error occurs
                if os.path.exists(wav_path):
                    try:
                        time.sleep(0.5)  # Short delay to make sure file is released
                        os.remove(wav_path)
                    except Exception as e:
                        self.logger.log_warning(f"Error removing WAV file: {e}")

        # Run the play function in a separate thread to keep the UI responsive
        self.executor.submit(play)

    def speak(self, message):
        """Converts text to speech and plays the audio response."""
        unique_id = str(uuid.uuid4())  # Create a unique identifier for the file
        file_path = os.path.join(self.temp_dir, f"response_{unique_id}.mp3")

        def synthesize_and_play():
            try:
                self.logger.log_event(f"Converting text to speech: '{message}'")

                if self.engine_choice == "gTTS":
                    # Use Google TTS (gTTS)
                    tts = gTTS(text=message, lang='en', slow=self.speech_rate < 1.0)
                    tts.save(file_path)
                    self.play_audio(file_path)
                else:
                    # Use pyttsx3 for offline TTS
                    self.engine.say(message)
                    self.engine.runAndWait()

                self.logger.log_event(f"Speech synthesized: '{message}'")
            except gTTSError as e:
                self.logger.log_error(f"Google TTS service failed: {e}")
            except Exception as e:
                self.logger.log_error(f"Error during speech synthesis: {e}, {type(e).__name__}")
            finally:
                # Retry mechanism for deleting the file, up to 5 times
                retries = 5
                for attempt in range(retries):
                    if os.path.exists(file_path):
                        try:
                            time.sleep(0.5)  # Delay before attempting to delete
                            os.remove(file_path)
                            self.logger.log_event(f"Successfully removed MP3 file on attempt {attempt + 1}")
                            break
                        except Exception as e:
                            if attempt < retries - 1:
                                self.logger.log_warning(f"Error removing MP3 file (attempt {attempt + 1}): {e}. Retrying...")
                                time.sleep(1.5)  # Wait for a longer duration before retrying
                            else:
                                # Final attempt failed
                                self.logger.log_error(f"Error removing MP3 file after {retries} attempts: {e}")

        # Run the synthesis and play in a separate thread
        self.executor.submit(synthesize_and_play)

    def listen(self):
        """Listen for voice commands and return recognized text."""
        with sr.Microphone() as source:
            self.logger.log_event("Listening for user input via microphone.")
            print("Listening...")
            try:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio)
                self.logger.log_event(f"User input recognized: '{text}'")
                return text
            except sr.UnknownValueError:
                self.logger.log_warning("Could not understand the audio")
                return self.error_voice
            except sr.RequestError as e:
                self.logger.log_error(f"Speech recognition service error: {e}")
                return "Network error: Could not reach the speech recognition service."
            except Exception as e:
                self.logger.log_error(f"Unexpected error during listening: {e}")
                return "An error occurred while processing your input."

    def generate_greeting(self):
        """Generate a unique greeting using OpenAI's GPT."""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a friendly AI assistant."},
                    {"role": "user", "content": "Generate a greeting for a user who has just launched me."}
                ],
                max_tokens=50,
                temperature=0.7
            )
            greeting = response.choices[0].message.content.strip()
            self.logger.log_event(f"Generated greeting: {greeting}")
            return greeting
        except Exception as e:
            self.logger.log_error(f"Error generating greeting: {e}")
            return "Hello! I'm Snowball, your personal AI assistant. How can I help you today?"

    def speak_greeting(self):
        """Generate and speak a unique greeting asynchronously."""
        greeting = self.generate_greeting()
        self.speak(greeting)

# Example usage
if __name__ == "__main__":
    voice_interface = VoiceInterface()
    voice_interface.speak_greeting()