import time
import threading
import numpy as np
import os
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from apscheduler.schedulers.background import BackgroundScheduler
from Snowball.decom.OLDinitializer import SnowballInitializer


class Training:
    def __init__(self, initializer):
        # Use components from SnowballInitializer
        self.logger = initializer.logger
        self.memory = initializer.memory
        self.config_loader = initializer.config_loader

        # Load configuration settings
        self.settings = self.config_loader.load_config("training_settings.json")
        self.batch_size = self.settings.get("batch_size", 32)
        self.learning_rate = self.settings.get("learning_rate", 0.001)
        self.training_interval = self.settings.get("training_interval", 3600)  # default: hourly
        self.model_path = self.settings.get("model_path", "data/models/trained_model.h5")

        # Initialize model
        self.model = self.build_model()
        if os.path.exists(self.model_path):
            self.load_model(self.model_path)

        # Scheduler for background training tasks
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.train_model, 'interval', seconds=self.training_interval)
        self.scheduler.start()

        # Metrics for tracking training progress
        self.training_history = {
            "loss": [],
            "accuracy": []
        }

        self.logger.log_event("Training module initialized successfully.")

    def build_model(self):
        """Build a simple neural network for training."""
        model = Sequential()
        model.add(Dense(64, input_dim=10, activation='relu'))  # Placeholder input dimension
        model.add(Dense(32, activation='relu'))
        model.add(Dense(1, activation='sigmoid'))  # Output for binary classification
        model.compile(optimizer=Adam(learning_rate=self.learning_rate), loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def train_model(self):
        """Train the model using data from memory and reinforcement modules."""
        self.logger.log_event("Starting model training...")

        # Fetch training data from memory and other sources
        interactions = self.memory.get_all_interactions()
        if not interactions:
            self.logger.log_warning("No training data available. Skipping training.")
            return

        # Extract features and labels from interactions
        X, y = self.prepare_training_data(interactions)
        if X is None or y is None:
            self.logger.log_warning("Insufficient training data after preparation. Skipping training.")
            return

        # Split data into training and validation sets
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train the model
        history = self.model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=10, batch_size=self.batch_size, verbose=1)

        # Log training metrics
        loss = history.history['loss'][-1]
        accuracy = history.history['accuracy'][-1]
        self.training_history['loss'].append(loss)
        self.training_history['accuracy'].append(accuracy)
        self.logger.log_event(f"Training completed. Loss: {loss}, Accuracy: {accuracy}")

        # Save the trained model
        self.save_model(self.model_path)

    def prepare_training_data(self, interactions):
        """Prepare features and labels for training from interaction data."""
        try:
            X, y = [], []
            for interaction in interactions:
                # Placeholder for feature extraction from interactions
                # Example: Convert user input and AI response to numerical vectors
                feature_vector = self.extract_features(interaction)
                label = interaction.get('label', 0)  # Assume a binary label (0 or 1)

                X.append(feature_vector)
                y.append(label)

            return np.array(X), np.array(y)
        except Exception as e:
            self.logger.log_error(f"Error preparing training data: {e}")
            return None, None

    def extract_features(self, interaction):
        """Extract features from an interaction."""
        # Placeholder: Convert text interaction to feature vector
        return np.random.rand(10)  # Example: Random feature vector of length 10

    def start_training_loop(self):
        """Start the training loop in a separate thread."""
        threading.Thread(target=self.train_model, daemon=True).start()

    def save_model(self, path):
        """Save the trained model to a file."""
        try:
            self.model.save(path)
            self.logger.log_event(f"Model saved successfully at {path}")
        except Exception as e:
            self.logger.log_error(f"Error saving model: {e}")

    def load_model(self, path):
        """Load a pre-trained model from a file."""
        try:
            self.model = load_model(path)
            self.logger.log_event(f"Model loaded successfully from {path}")
        except Exception as e:
            self.logger.log_error(f"Error loading model: {e}")

    def visualize_training_metrics(self):
        """Visualize training metrics like loss and accuracy over time."""
        if not self.training_history['loss']:
            self.logger.log_warning("No training history available to visualize.")
            return

        plt.figure(figsize=(12, 5))

        # Loss plot
        plt.subplot(1, 2, 1)
        plt.plot(self.training_history['loss'], label='Loss')
        plt.title('Training Loss Over Time')
        plt.xlabel('Training Sessions')
        plt.ylabel('Loss')
        plt.legend()

        # Accuracy plot
        plt.subplot(1, 2, 2)
        plt.plot(self.training_history['accuracy'], label='Accuracy')
        plt.title('Training Accuracy Over Time')
        plt.xlabel('Training Sessions')
        plt.ylabel('Accuracy')
        plt.legend()

        plt.tight_layout()
        plt.savefig(f"training_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.show()

    def stop_training(self):
        """Stop the training scheduler gracefully."""
        self.scheduler.shutdown()
        self.logger.log_event("Training scheduler stopped.")

    def fine_tune_model(self, feedback_data):
        """Fine-tune the model based on user feedback."""
        # Placeholder for fine-tuning logic using feedback data
        self.logger.log_event("Fine-tuning model based on feedback data.")
        # Extract features and labels from feedback data and train the model further
        pass

    def adaptive_learning(self, new_data):
        """Adaptively train the model with new data."""
        # Use reinforcement or other learning techniques to adapt the model in real-time
        self.logger.log_event("Performing adaptive learning with new data.")
        pass


if __name__ == "__main__":
    initializer = SnowballInitializer()
    training_module = Training(initializer)
    try:
        training_module.start_training_loop()
    except KeyboardInterrupt:
        training_module.stop_training()
