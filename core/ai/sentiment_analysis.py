import json
import openai
from transformers import pipeline
from cachetools import LRUCache
from Snowball.core.logger import SnowballLogger
from Snowball.core.ai.memory import Memory

class SentimentAnalysis:
    def __init__(self, logger=None, memory=None, openai_api_key=None, escalation_threshold=20, neutral_confidence=0.6):
        self.logger = logger or SnowballLogger()
        self.memory = memory or Memory(logger=self.logger)
        self.openai_api_key = openai_api_key
        self.escalation_threshold = escalation_threshold
        self.neutral_confidence = neutral_confidence

        # Initialize cache and Transformer-based sentiment model
        self.cache = LRUCache(maxsize=1000)
        self.transformer_model = pipeline(
            "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        self.logger.log_event("SentimentAnalysis module initialized.")

    def analyze_sentiment(self, text):
        """Analyze the sentiment of the given text with confidence score."""
        try:
            if text in self.cache:
                self.logger.log_event("Sentiment result retrieved from cache.")
                return self.cache[text]

            # Analyze sentiment using the Transformer model
            result = self.transformer_model(text)
            sentiment_result = result[0]['label']
            confidence = result[0].get('score', 1.0)  # Default to 1.0 if no confidence provided

            self.logger.log_event(f"Sentiment analysis result: {sentiment_result}, Confidence: {confidence}")
            self.cache[text] = {"label": sentiment_result, "confidence": confidence}  # Store in cache

            return {"label": sentiment_result, "confidence": confidence}
        except Exception as e:
            self.logger.log_error(f"Error analyzing sentiment: {e}")
            return {"label": "Error", "confidence": 0.0}

    def analyze_with_gpt(self, text):
        """Analyze sentiment using ChatGPT for ambiguous or complex cases."""
        try:
            prompt = (
                "Analyze the sentiment of the following text and return Positive, Negative, or Neutral:\n"
                f"Text: {text}"
            )
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=50,
                temperature=0.7
            )

            sentiment_result = response.choices[0].text.strip()
            self.logger.log_event(f"ChatGPT sentiment analysis result: {sentiment_result}")
            return sentiment_result
        except Exception as e:
            self.logger.log_error(f"Error analyzing sentiment with ChatGPT: {e}")
            return "Error"

    def hybrid_sentiment_analysis(self, text):
        """Perform hybrid sentiment analysis using DistilBERT and ChatGPT."""
        try:
            # First-pass analysis with DistilBERT
            distilbert_result = self.analyze_sentiment(text)

            # Escalate to ChatGPT if confidence is low or input is complex
            if distilbert_result["label"] == "Neutral" or len(text.split()) > self.escalation_threshold:
                self.logger.log_event("Confidence low or input complex, escalating to ChatGPT.")

                gpt_result = self.analyze_with_gpt(text)
                
                # Log both results for decision-making improvements
                self.logger.log_decision(
                    f"Sentiment analysis comparison: DistilBERT={distilbert_result}, ChatGPT={gpt_result}, "
                    f"Reason: {'Low confidence' if distilbert_result == 'Neutral' else 'High complexity'}"
                )

                return gpt_result if gpt_result != "Error" else distilbert_result

            return distilbert_result
        except Exception as e:
            self.logger.log_error(f"Error in hybrid sentiment analysis: {e}")
            return "Error"

    def get_sentiment_from_interactions(self, interactions):
        """Analyze sentiment for each interaction in the provided list."""
        try:
            sentiment_summary = []
            for interaction in interactions:
                user_input = interaction.get("user_input", "")
                sentiment = self.hybrid_sentiment_analysis(user_input)

                # Store the sentiment with metadata
                self.memory.store_interaction(
                    user_input, f"Sentiment: {sentiment['label']}, Confidence: {sentiment['confidence']}"
                )
                sentiment_summary.append({"user_input": user_input, "sentiment": sentiment})

            self.logger.log_event("Sentiment analysis completed for all interactions.")
            return sentiment_summary
        except Exception as e:
            self.logger.log_error(f"Error analyzing sentiment from interactions: {e}")
            return []

if __name__ == "__main__":
    logger = SnowballLogger()
    memory = Memory(logger=logger)
    openai_api_key = "your-openai-api-key-here"

    sentiment_analyzer = SentimentAnalysis(logger=logger, memory=memory, openai_api_key=openai_api_key)

    # Example sentiment analysis
    sample_text = "I absolutely love this product!"
    sentiment_result = sentiment_analyzer.hybrid_sentiment_analysis(sample_text)
    print(f"Sentiment: {sentiment_result}")

    # Example interaction analysis
    interactions = [
        {"user_input": "This is amazing!"},
        {"user_input": "I'm so disappointed."}
    ]
    sentiment_summary = sentiment_analyzer.get_sentiment_from_interactions(interactions)
    print("Sentiment Summary:", sentiment_summary)
