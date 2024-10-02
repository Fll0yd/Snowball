from gtts import gTTS
import os

# Set up the directory and file
temp_dir = "C:/temp"
os.makedirs(temp_dir, exist_ok=True)
file_path = os.path.join(temp_dir, "response.mp3")

# Convert text to speech and save to the file
text = "Hello, this is a test."
tts = gTTS(text=text, lang='en')
tts.save(file_path)

# Check if the file was created
print(f"File {file_path} exists: {os.path.exists(file_path)}")
