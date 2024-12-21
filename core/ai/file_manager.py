import os
import hashlib
import threading
import time
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from PyPDF2 import PdfReader
import docx
from PIL import Image
import pytesseract
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

class FileEventHandler(FileSystemEventHandler):
    """Custom event handler for file system changes."""

    def __init__(self, logger, priority_queue):
        self.logger = logger
        self.priority_queue = priority_queue

    def on_created(self, event):
        if not event.is_directory:
            self.logger.log_task(f"File created: {event.src_path}", "Created")
            self.priority_queue.put((1, event.src_path))  # Low priority for creation

    def on_modified(self, event):
        if not event.is_directory:
            self.logger.log_task(f"File modified: {event.src_path}", "Modified")
            self.priority_queue.put((0, event.src_path))  # High priority for modification

class FileManager:
    def __init__(self, logger, memory, scan_dir='S:/', allowed_extensions=None, scan_interval=10):
        self.logger = logger
        self.memory = memory
        self.scan_dir = scan_dir
        self.priority_queue = PriorityQueue()
        self.processed_hashes = set()
        self.observer = Observer()
        self.allowed_extensions = allowed_extensions or {'.txt', '.py', '.json', '.log', '.pdf', '.docx', '.jpg', '.jpeg', '.png'}
        self.scan_interval = scan_interval  # Default to 10 seconds

        # Load pre-trained models
        self.image_model = self.load_image_model()
        self.text_model = self.load_text_model()

    def load_image_model(self):
        """Load a pre-trained image classification model."""
        try:
            model = load_model('S:/Snowball/models/image_classification_model.h5')
            self.logger.log_task("Image classification model loaded successfully.", "Loaded")
            return model
        except Exception as e:
            self.logger.log_error(f"Error loading image classification model: {e}")
            return None

    def load_text_model(self):
        """Load a pre-trained text classification model."""
        try:
            model = load_model('S:/Snowball/models/text_classification_model.h5')
            self.logger.log_task("Text classification model loaded successfully.", "Loaded")
            return model
        except Exception as e:
            self.logger.log_error(f"Error loading text classification model: {e}")
            return None

    def hash_file(self, file_path):
        """Generate a hash for a file to track processed files."""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                hasher.update(f.read())
            file_hash = hasher.hexdigest()
            self.logger.log_task(f"Generated hash for file: {file_path}", "Hash Generated")
            return file_hash
        except Exception as e:
            self.logger.log_error(f"Error hashing file: {e}")
            return None

    def scan_and_index_drive(self):
        """Scan and index all files on the S:/ drive."""
        try:
            self.logger.log_event("Starting drive scan and index.")
            for root, _, files in os.walk(self.scan_dir):
                for file_name in files:
                    if os.path.splitext(file_name)[1].lower() not in self.allowed_extensions:
                        continue

                    file_path = os.path.join(root, file_name)
                    last_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()

                    self.memory.store_file_metadata(file_name, file_path, last_modified)
            self.logger.log_event("Drive scan and indexing completed.")
        except Exception as e:
            self.logger.log_error(f"Error scanning and indexing drive: {e}")

    def analyze_pdf(self, file_path):
        """Extract and analyze text from a PDF file."""
        try:
            reader = PdfReader(file_path)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + ' '

            # Predict document type using the text model
            prediction = self.text_model.predict([text])
            document_type = "Important" if prediction[0] > 0.5 else "General"

            self.logger.log_task(f"Analyzed PDF file: {file_path} (Type: {document_type})", "Analyzed")
            self.memory.store_file_analysis(file_path, text)
        except Exception as e:
            self.logger.log_error(f"Error analyzing PDF file: {file_path}, {e}")

    def analyze_docx(self, file_path):
        """Extract and analyze text from a DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = ' '.join([paragraph.text for paragraph in doc.paragraphs])

            # Predict document type using the text model
            prediction = self.text_model.predict([text])
            document_type = "Important" if prediction[0] > 0.5 else "General"

            self.logger.log_task(f"Analyzed DOCX file: {file_path} (Type: {document_type})", "Analyzed")
            self.memory.store_file_analysis(file_path, text)
        except Exception as e:
            self.logger.log_error(f"Error analyzing DOCX file: {file_path}, {e}")

    def analyze_text(self, file_path):
        """Extract and analyze text from a TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            # Predict document type using the text model
            prediction = self.text_model.predict([text])
            document_type = "Important" if prediction[0] > 0.5 else "General"

            self.logger.log_task(f"Analyzed TXT file: {file_path} (Type: {document_type})", "Analyzed")
            self.memory.store_file_analysis(file_path, text)
        except Exception as e:
            self.logger.log_error(f"Error analyzing TXT file: {file_path}, {e}")

    def analyze_image(self, file_path):
        """Perform OCR and image classification on an image file."""
        try:
            # Perform OCR
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)

            # Image classification
            img = load_img(file_path, target_size=(224, 224))
            img_array = img_to_array(img) / 255.0
            img_array = img_array.reshape((1, *img_array.shape))
            prediction = self.image_model.predict(img_array)
            classification = "Relevant" if prediction[0] > 0.5 else "Irrelevant"

            self.logger.log_task(f"Analyzed Image file: {file_path} (Classification: {classification})", "Analyzed")
            self.memory.store_file_analysis(file_path, text)
        except Exception as e:
            self.logger.log_error(f"Error analyzing Image file: {file_path}, {e}")

    def start_monitoring(self):
        """Start monitoring the S:/ drive."""
        if not os.path.exists(self.scan_dir):
            self.logger.log_error(f"Directory {self.scan_dir} does not exist. Cannot start monitoring.")
            return

        event_handler = FileEventHandler(self.logger, self.priority_queue)
        self.observer.schedule(event_handler, self.scan_dir, recursive=True)
        self.observer.start()
        self.logger.log_event(f"Started monitoring directory: {self.scan_dir}")

        try:
            monitoring_thread = threading.Thread(target=self.monitor_files, daemon=True)
            monitoring_thread.start()
        except Exception as e:
            self.logger.log_error(f"Unexpected error in start_monitoring: {e}")
            self.stop_monitoring()  # Ensure observer stops in case of an error

    def monitor_files(self):
        """Continuously monitor the S:/ drive for new files."""
        self.logger.log_event("Monitoring loop started.")
        try:
            while True:
                while not self.priority_queue.empty():
                    _, file_path = self.priority_queue.get()
                    if not os.path.exists(file_path):
                        self.logger.log_warning(f"File no longer exists: {file_path}")
                        continue
                    self.process_file(file_path)
                time.sleep(self.scan_interval)
        except Exception as e:
            self.logger.log_error(f"Error in monitor_files loop: {e}")

    def process_file(self, file_path):
        """Analyze a file based on its type."""
        try:
            file_hash = self.hash_file(file_path)
            if not file_hash or file_hash in self.processed_hashes:
                self.logger.log_task(f"File already processed: {file_path}", "Skipped")
                return

            _, ext = os.path.splitext(file_path)
            ext = ext.lower()

            if ext in ['.pdf']:
                self.analyze_pdf(file_path)
            elif ext in ['.docx']:
                self.analyze_docx(file_path)
            elif ext in ['.txt']:
                self.analyze_text(file_path)
            elif ext in ['.jpg', '.jpeg', '.png']:
                self.analyze_image(file_path)
            else:
                self.logger.log_warning(f"Unsupported file type skipped: {file_path} (Extension: {ext})")

            self.processed_hashes.add(file_hash)
        except Exception as e:
            self.logger.log_error(f"Error processing file: {file_path}, {e}")

    def stop_monitoring(self):
        """Stop monitoring the S:/ drive."""
        self.observer.stop()
