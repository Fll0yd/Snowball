import os
import json
import logging
import time
import threading
import hashlib
from queue import PriorityQueue
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
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import SnowballLogger from the core.logger module
from core.logger import SnowballLogger
# Import Memory from core.memory module
from core.memory import Memory  # This is the missing import

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileEventHandler(FileSystemEventHandler):
    """Custom event handler for file system changes."""

    def __init__(self, memory, logger, priority_queue):
        self.memory = memory
        self.logger = logger
        self.priority_queue = priority_queue

    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            self.logger.info(f"File created: {event.src_path}")
            self.priority_queue.put((1, event.src_path))  # Low priority for creation

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            self.logger.info(f"File modified: {event.src_path}")
            self.priority_queue.put((0, event.src_path))  # High priority for modification

    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory:
            self.logger.info(f"File deleted: {event.src_path}")
            self.memory.store_interaction(f"File deleted: {event.src_path}", None)

    def on_moved(self, event):
        """Handle file move events."""
        if not event.is_directory:
            self.logger.info(f"File moved: from {event.src_path} to {event.dest_path}")
            self.memory.store_interaction(f"File moved: from {event.src_path} to {event.dest_path}", None)

class FileMonitor:
    def __init__(self, config_file):
        self.logger = SnowballLogger()
        self.memory = Memory()
        self.priority_queue = PriorityQueue()
        self.processed_hashes = set()
        self.observer = Observer()
        self.running_event = threading.Event()

        with open(config_file, 'r') as f:
            config = json.load(f)
            self.download_dir = config.get('download_dir', 'default_download_path')
            self.plex_dir_movies = config.get('plex_dir_movies', 'default_movies_path')
            self.plex_dir_tv_shows = config.get('plex_dir_tv_shows', 'default_tv_shows_path')
            self.logger.logger.info(f"Monitoring started for downloads: {self.download_dir}")

            # Load models
            self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
            self.image_model = self.load_image_model()

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
    
    def hash_file(self, file_path):
        """Generate a hash for a file to track processed files."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def monitor_files(self):
        """Continuously monitor the download directory for new files."""
        logger.info("Starting file monitoring loop.")
        while True:
            while not self.priority_queue.empty():
                _, file_path = self.priority_queue.get()
                self.process_file(file_path)
            time.sleep(10)  # Check every 10 seconds

    def process_file(self, file_path):
        """Process a file based on its type."""
        file_hash = self.hash_file(file_path)
        if file_hash in self.processed_hashes:
            logger.info(f"File already processed: {file_path}")
            return

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
        elif ext in ['.txt']:
            self.analyze_text(file_path)
        elif ext in ['.csv']:
            self.analyze_csv(file_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")

        self.processed_hashes.add(file_hash)  # Add the hash to the set after processing

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

    def analyze_text(self, file_path):
        """Extract and analyze text from a TXT file."""
        logger.info(f"Analyzing TXT file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        self.perform_text_analysis(text)

    def analyze_csv(self, file_path):
        """Extract and analyze text from a CSV file."""
        logger.info(f"Analyzing CSV file: {file_path}")
        import pandas as pd  # Import here to avoid unnecessary loading
        df = pd.read_csv(file_path)
        text = df.to_string(index=False)
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
        """Analyze a video file for object tracking and facial recognition."""
        logger.info(f"Analyzing video file: {file_path}")
        cap = cv2.VideoCapture(file_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            detected_faces = faces.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            # Placeholder for advanced tracking and learning logic
            for (x, y, w, h) in detected_faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            cv2.imshow('Video Analysis', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
    
    def start_monitoring(self):
        """Start monitoring the specified directory."""
        event_handler = FileEventHandler(self.memory, self.logger, self.priority_queue)
        self.observer.schedule(event_handler, self.download_dir, recursive=True)
        self.observer.start()
        self.logger.logger.info(f"Started monitoring directory: {self.download_dir}")

        try:
            self.monitor_files()
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    config_file = 'config.json'  # Adjust to your configuration path
    file_monitor = FileMonitor(config_file)
    file_monitor.start_monitoring()
