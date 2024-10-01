import os
import shutil
import time
import json
import logging
import cv2  # For video analysis (ensure you have OpenCV installed)
import pytesseract  # For OCR in text documents
from PIL import Image  # For image processing
from plyer import notification
import numpy as np  # For numerical operations
import tensorflow as tf  # For integration with TensorFlow (ensure you have TensorFlow installed)
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing import image
from transformers import pipeline  # For sentiment analysis
from PyPDF2 import PdfReader  # For PDF analysis
import docx  # For DOCX analysis
from sklearn.metrics import accuracy_score  # For performance evaluation
from sklearn.model_selection import train_test_split  # For dataset splitting

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileMonitor:
    def __init__(self, config_file):
        """Initialize the file monitor with directory paths from a configuration file."""
        with open(config_file, 'r') as f:
            config = json.load(f)
            self.download_dir = config['download_dir']
            self.plex_dir_movies = config['plex_dir_movies']
            self.plex_dir_tv_shows = config['plex_dir_tv_shows']
            logger.info(f"Monitoring started for downloads: {self.download_dir}")

        # Load models
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")  # Load a robust sentiment analysis model
        self.image_model = self.load_image_model()  # Load the image classification model

    def load_image_model(self):
        """Load and compile a more advanced image classification model."""
        base_model = tf.keras.applications.MobileNetV2(weights='imagenet', include_top=False, input_shape=(256, 256, 3))
        base_model.trainable = False  # Freeze the base model

        model = tf.keras.Sequential([
            base_model,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dense(1, activation='sigmoid')  # Change this according to your classes
        ])

        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def monitor_files(self):
        """Continuously monitor the download directory for new files."""
        logger.info("Starting file monitoring loop.")
        processed_files = set()  # Track processed files to avoid duplicates

        while True:
            for filename in os.listdir(self.download_dir):
                if filename in processed_files:
                    continue

                file_path = os.path.join(self.download_dir, filename)
                if os.path.isfile(file_path):
                    self.process_file(file_path)
                    processed_files.add(filename)
            time.sleep(10)  # Check every 10 seconds

    def process_file(self, file_path):
        """Process a file based on its type."""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        logger.info(f"Processing file: {file_path}")

        if ext in ['.pdf']:
            self.analyze_pdf(file_path)
        elif ext in ['.docx']:
            self.analyze_docx(file_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            self.analyze_image(file_path)
        elif ext in ['.mp4', '.avi', '.mov']:
            self.analyze_video(file_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")

    def analyze_pdf(self, file_path):
        """Extract and analyze text from a PDF file."""
        logger.info(f"Analyzing PDF file: {file_path}")
        reader = PdfReader(file_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + ' '

        self.perform_text_analysis(text)

    def analyze_docx(self, file_path):
        """Extract and analyze text from a DOCX file."""
        logger.info(f"Analyzing DOCX file: {file_path}")
        doc = docx.Document(file_path)
        text = ''
        for paragraph in doc.paragraphs:
            text += paragraph.text + ' '

        self.perform_text_analysis(text)

    def perform_text_analysis(self, text):
        """Perform sentiment analysis and additional processing on extracted text."""
        if text.strip():
            logger.info("Performing sentiment analysis on extracted text.")
            sentiment = self.sentiment_analyzer(text)
            logger.info(f"Sentiment analysis result: {sentiment}")

    def analyze_image(self, file_path):
        """Analyze an image file for classification."""
        logger.info(f"Analyzing image file: {file_path}")
        img = image.load_img(file_path, target_size=(256, 256))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = self.image_model.predict(img_array)
        if prediction > 0.5:
            logger.info("Predicted class: Sad")
        else:
            logger.info("Predicted class: Happy")

    def analyze_video(self, file_path):
        """Analyze a video file for facial recognition."""
        logger.info(f"Analyzing video file: {file_path}")
        cap = cv2.VideoCapture(file_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            detected_faces = faces.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            for (x, y, w, h) in detected_faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            cv2.imshow('Video Analysis', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    config_file_path = 'config.json'  # Adjust this path as needed
    monitor = FileMonitor(config_file_path)
    monitor.monitor_files()
