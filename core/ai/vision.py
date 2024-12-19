import cv2
import numpy as np
import threading
from keras.models import load_model
from Snowball.decom.OLDinitializer import SnowballInitializer
import time


class Vision:
    def __init__(self, initializer=None):
        # Use components from the SnowballInitializer if available
        if initializer is None:
            initializer = SnowballInitializer()
        
        self.logger = initializer.logger
        self.config_loader = initializer.config_loader
        self.memory = initializer.memory
        self.sentiment_analysis = initializer.sentiment_analysis_module
        self.model_path = self.config_loader.load_config('vision_model_config.json').get('model_path', 'S:/Snowball/models/image_classifier.h5')

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        try:
            self.model = load_model(self.model_path)
            self.logger.log_event(f"Vision model loaded successfully from {self.model_path}")
        except Exception as e:
            self.logger.log_error(f"Error loading vision model from {self.model_path}: {e}")

        self.running_event = threading.Event()
        self.running_event.clear()

    def start_facial_recognition(self):
        self.logger.log_event("Facial recognition started.")
        cap = cv2.VideoCapture(0)
        try:
            while not self.running_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    self.logger.log_warning("Camera feed not available.")
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    face_roi = frame[y:y + h, x:x + w]
                    emotion = self.detect_emotion(face_roi)
                    self.logger.log_event(f"Detected face with emotion: {emotion}")
                    cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                cv2.imshow('Facial Recognition', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            self.logger.log_error(f"Error during facial recognition: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.logger.log_event("Facial recognition stopped.")

    def detect_emotion(self, face_roi):
        try:
            # Preprocess the face ROI for model prediction
            face_img = cv2.resize(face_roi, (48, 48))  # Resize to model input size
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            face_img = face_img / 255.0  # Normalize
            face_img = np.expand_dims(face_img, axis=0)
            face_img = np.expand_dims(face_img, axis=-1)
            
            # Predict the emotion
            prediction = self.model.predict(face_img)
            emotion_label = np.argmax(prediction)
            emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
            emotion = emotions[emotion_label]
            
            # Store the recognized emotion in memory for future context
            self.memory.store_interaction("Emotion detected", emotion)
            return emotion
        except Exception as e:
            self.logger.log_error(f"Error detecting emotion: {e}")
            return "Unknown"

    def recognize_objects(self, frame):
        """Recognize objects in the frame and classify them."""
        try:
            # Preprocess the image
            img = cv2.resize(frame, (224, 224))
            img = img / 255.0
            img = np.expand_dims(img, axis=0)
            
            # Predict using the model
            prediction = self.model.predict(img)
            object_label = np.argmax(prediction)
            self.logger.log_event(f"Object detected: {object_label}")
            return object_label
        except Exception as e:
            self.logger.log_error(f"Error recognizing objects: {e}")
            return None

    def capture_and_save_image(self, filename="captured_image.jpg"):
        """Capture an image from the webcam and save it."""
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(filename, frame)
            self.logger.log_event(f"Image captured and saved as {filename}")
        else:
            self.logger.log_warning("Unable to capture image from webcam.")
        cap.release()

    def start_object_detection(self):
        """Continuously detect objects in the webcam feed."""
        cap = cv2.VideoCapture(0)
        try:
            while not self.running_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    self.logger.log_warning("Camera feed not available.")
                    break
                object_label = self.recognize_objects(frame)
                cv2.putText(frame, f"Object: {object_label}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('Object Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            self.logger.log_error(f"Error during object detection: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.logger.log_event("Object detection stopped.")

    def stop(self):
        """Stop the vision module."""
        self.running_event.set()
        self.logger.log_event("Vision module has been stopped.")

if __name__ == "__main__":
    initializer = SnowballInitializer()
    vision = Vision(initializer)
    try:
        vision.start_facial_recognition()
    except KeyboardInterrupt:
        vision.stop()
