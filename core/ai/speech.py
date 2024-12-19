import os
import sys
import json
import nltk
import threading
from transformers import pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from Snowball.decom.OLDinitializer import SnowballInitializer
from cachetools import LRUCache

# Ensure the core directory is in the system path for initializer import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class SentimentAnalysis:
    def __init__(self):
        self.initializer = SnowballInitializer()
        self.logger = self.initializer.logger
        self.memory = self.initializer.memory

        # Initialize cache and models
        self.cache = LRUCache(maxsize=1000)  # Cache for storing frequently analyzed texts
        self.vectorizer = TfidfVectorizer()  # Using TF-IDF for better text representation
        self.classifier = MultinomialNB()  # Naive Bayes Classifier
        self.transformer_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

        # Data Preparation for Naive Bayes Model
        nltk.download('movie_reviews')
        from nltk.corpus import movie_reviews
        self.train_classifier(movie_reviews)

    def train_classifier(self, movie_reviews):
        """Train the Naive Bayes classifier with sample data."""
        try:
            data = [movie_reviews.raw(fileid) for fileid in movie_reviews.fileids()]
            labels = [movie_reviews.categories(fileid)[0] for fileid in movie_reviews.fileids()]
            labels = [1 if label == 'pos' else 0 for label in labels]

            X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)
            X_train_tfidf = self.vectorizer.fit_transform(X_train)
            X_test_tfidf = self.vectorizer.transform(X_test)

            self.classifier.fit(X_train_tfidf, y_train)
            predictions = self.classifier.predict(X_test_tfidf)

            accuracy = accuracy_score(y_test, predictions)
            self.logger.log_event(f"Naive Bayes Classifier trained with accuracy: {accuracy:.2f}")
            self.logger.log_event(f"Classification Report:\n{classification_report(y_test, predictions)}")
        except Exception as e:
            self.logger.log_error(f"Error training classifier: {e}")

    def analyze_sentiment(self, text, use_transformer=True):
        """Analyze the sentiment of the given text."""
        try:
            if text in self.cache:
                self.logger.log_event("Sentiment result retrieved from cache.")
                return self.cache[text]

            # Using the Transformer model if enabled
            if use_transformer:
                result = self.transformer_model(text)
                sentiment_result = result[0]['label']
            else:
                # Fallback to Naive Bayes analysis
                text_vectorized = self.vectorizer.transform([text])
                sentiment_result = self.classifier.predict(text_vectorized)[0]
                sentiment_result = "Positive" if sentiment_result == 1 else "Negative"

            self.logger.log_event(f"Sentiment analysis result: {sentiment_result}")
            self.cache[text] = sentiment_result  # Store in cache

            return sentiment_result
        except Exception as e:
            self.logger.log_error(f"Error analyzing sentiment: {e}")
            return "Error"

    def get_sentiment_from_interactions(self, interactions):
        """Analyze sentiment for each interaction in the provided list."""
        try:
            sentiment_summary = []
            for interaction in interactions:
                user_input = interaction.get("user_input", "")
                sentiment = self.analyze_sentiment(user_input)
                sentiment_summary.append({"user_input": user_input, "sentiment": sentiment})
                self.memory.store_interaction(user_input, f"Sentiment: {sentiment}")
            self.logger.log_event("Sentiment analysis completed for all interactions.")
            return sentiment_summary
        except Exception as e:
            self.logger.log_error(f"Error analyzing sentiment from interactions: {e}")
            return []

    def save_sentiment_results(self, results, file_path="data/sentiment_results.json"):
        """Save the sentiment analysis results to a file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4)
            self.logger.log_event("Sentiment analysis results saved successfully.")
        except Exception as e:
            self.logger.log_error(f"Error saving sentiment results: {e}")

    def load_sentiment_results(self, file_path="data/sentiment_results.json"):
        """Load sentiment analysis results from a file."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                self.logger.log_event("Sentiment analysis results loaded successfully.")
                return results
            else:
                self.logger.log_warning(f"Sentiment results file not found: {file_path}")
                return []
        except Exception as e:
            self.logger.log_error(f"Error loading sentiment results: {e}")
            return []

    def adaptive_analysis(self, user_input):
        """Analyze sentiment using multiple methods and pick the most suitable result."""
        try:
            transformer_result = self.analyze_sentiment(user_input, use_transformer=True)
            bayes_result = self.analyze_sentiment(user_input, use_transformer=False)
            # Adaptive logic to combine or choose between results
            final_result = transformer_result if transformer_result != "Error" else bayes_result
            self.logger.log_event(f"Adaptive sentiment result: {final_result}")
            return final_result
        except Exception as e:
            self.logger.log_error(f"Error in adaptive sentiment analysis: {e}")
            return "Error"

if __name__ == "__main__":
    sentiment_analyzer = SentimentAnalysis()
    sample_text = "I absolutely love this product!"
    sentiment_result = sentiment_analyzer.analyze_sentiment(sample_text)
    print(f"Sentiment: {sentiment_result}")

    # Example for adaptive analysis
    adaptive_result = sentiment_analyzer.adaptive_analysis("The weather today is terrible.")
    print(f"Adaptive Sentiment: {adaptive_result}")
