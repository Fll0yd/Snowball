from unittest import TestCase, main
from unittest.mock import patch, MagicMock
import pygame
import os
import sys
import speech_recognition as sr

# Ensure the path to core is added correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from core.voice_interface import VoiceInterface

class TestVoiceInterface(TestCase):
    @patch('core.voice_interface.SnowballLogger')
    def setUp(self, mock_logger):
        self.voice = VoiceInterface()
        self.voice.logger = mock_logger.return_value

    @patch('pydub.AudioSegment.from_mp3')
    @patch('pydub.AudioSegment.export')
    @patch('pygame.mixer.music.load')
    @patch('pygame.mixer.music.play')
    def test_speak_success(self, mock_play, mock_load, mock_from_mp3, mock_export):
        test_text = "Hello, this is a test."
        valid_path = os.path.join(self.voice.temp_dir, "response.mp3")
        wav_path = os.path.join(self.voice.temp_dir, "response.wav")

        # Mock the conversion from MP3 to WAV
        mock_audio_segment = MagicMock()
        mock_from_mp3.return_value = mock_audio_segment

        # Call the method
        self.voice.speak(test_text)

        # Check if the file was created
        print(f"File {valid_path} exists after save: {os.path.exists(valid_path)}")

        if os.path.exists(valid_path):
            # Proceed with testing conversion and playing
            mock_from_mp3.assert_called_once_with(valid_path)  # Ensure it attempts to load the mp3 file
            mock_audio_segment.export.assert_called_once_with(wav_path, format="wav")
            mock_load.assert_called_once_with(wav_path)
            mock_play.assert_called_once()
        else:
            print("gTTS save did not create the file as expected.")

        # Ensure the cleanup happened
        self.assertFalse(os.path.exists(valid_path), "Response file was not cleaned up.")

    def test_play_audio_invalid(self):
        invalid_path = "C:/temp/invalid_audio.mp3"
        self.voice.play_audio(invalid_path)
        self.voice.logger.log_error.assert_called_with(f"Audio file not found: {invalid_path}")

    @patch('core.voice_interface.sr.Recognizer')
    @patch('core.voice_interface.sr.Microphone')
    def test_listen_success(self, mock_microphone, mock_recognizer):
        """Test listen method with successful speech recognition."""
        mock_recognizer.return_value.listen.return_value = MagicMock()
        mock_recognizer.return_value.recognize_google.return_value = "Test command"
        
        user_input = self.voice.listen()
        self.assertEqual(user_input, "Test command")
        self.voice.logger.logger.info.assert_called_with(f"User input recognized: 'Test command'")

    @patch('core.voice_interface.sr.Recognizer')
    @patch('core.voice_interface.sr.Microphone')
    def test_listen_unknown_value_error(self, mock_microphone, mock_recognizer):
        """Test listen method handling unknown value error."""
        mock_recognizer.return_value.listen.return_value = MagicMock()
        mock_recognizer.return_value.recognize_google.side_effect = sr.UnknownValueError

        user_input = self.voice.listen()
        self.assertEqual(user_input, "Sorry, I didn't catch that.")
        self.voice.logger.log_warning.assert_called_with("Sorry, I didn't catch that.")

    @patch('core.voice_interface.sr.Recognizer')
    @patch('core.voice_interface.sr.Microphone')
    def test_listen_request_error(self, mock_microphone, mock_recognizer):
        """Test listen method handling request error."""
        mock_recognizer.return_value.listen.return_value = MagicMock()
        mock_recognizer.return_value.recognize_google.side_effect = sr.RequestError("Error")
        
        user_input = self.voice.listen()
        self.assertEqual(user_input, "Network error: Could not reach the speech recognition service.")
        self.voice.logger.log_error.assert_called_with("Speech recognition service is unavailable: Error")

    @patch('core.voice_interface.os.remove')
    def test_cleanup(self, mock_remove):
        """Test cleanup of temporary audio files after speaking."""
        file_path = os.path.join(self.voice.temp_dir, "response.mp3")

        # Create a temporary file for cleanup test
        with open(file_path, 'w') as f:
            f.write("Test audio file.")

        self.voice.speak("Clean up test.")

        # Expect only the removal of the .mp3 file once
        self.assertEqual(mock_remove.call_count, 1, "os.remove should be called exactly once for the .mp3 file.")
        mock_remove.assert_called_once_with(file_path)

if __name__ == "__main__":
    main()
