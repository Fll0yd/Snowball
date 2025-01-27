import os
import json
import requests
import re
import time
import random
from cachetools import TTLCache
from Snowball.core.ai.decision_maker import DecisionMaker
from Snowball.core.ai.memory import Memory
from Snowball.core.ai.sentiment_analysis import SentimentAnalysis
from Snowball.core.logger import SnowballLogger


class SnowballAI:
    """Enhanced Snowball AI with sentiment analysis and personality management."""
    irrelevant_patterns = [
        r"As an AI language model",
        r"I'm a \d+-year-old boy",
        r"I'm sorry.*(not know|can't)",
        r"Amazon Snowball",
        r"I don't know",
        r"I'm back from a long break",
        r"server.*group.*specific",
        r"only available to",
        r"I've been thinking about"
    ]

    def __init__(self):
        self.logger = SnowballLogger()
        self.decision_maker = DecisionMaker(self.logger)
        self.api_keys = self._load_api_keys()
        if not self.api_keys:
            self.logger.log_error("Error loading API keys: API keys are missing or invalid.")
        self.memory = Memory(logger=self.logger)
        self.sentiment_analysis = SentimentAnalysis()  # Initialize sentiment analysis module
        self.metadata_cache = TTLCache(maxsize=500, ttl=300)
        self.response_cache = TTLCache(maxsize=500, ttl=300)  # Cache for responses
        self.personality = "helpful"  # Default personality
        self.logger.log_event("Snowball AI initialized.")

    def _load_api_keys(self):
        """Load and validate API keys from the configuration file."""
        try:
            with open('S:/Snowball/config/account_integrations.json') as f:
                config = json.load(f)
                api_keys = {
                    "gpt4": config['api_keys'].get('openai_api_key'),
                    "grok": config['api_keys'].get('grok_api_key'),
                }
                if not all(api_keys.values()):
                    missing_keys = [k for k, v in api_keys.items() if not v]
                    self.logger.log_error(f"Missing API keys: {', '.join(missing_keys)}")
                    raise ValueError("One or more API keys are missing. Please update the configuration.")
                return api_keys
        except Exception as e:
            self.logger.log_error(f"Error loading API keys: {e}")
            return {}
        
    def set_personality(self, personality):
        """Set the personality mode of the AI."""
        self.personality = personality
        self.logger.log_event(f"Personality set to: {self.personality}")

    def process_user_input(self, user_input):
        """Process user input and generate a response."""
        if not user_input.strip():
            return "It seems you didn't provide any input. How can I assist you?"
    
        # Log user input to interaction log
        self.logger.log_interaction(user_input, None)

        try:
            # Analyze sentiment
            sentiment = self.sentiment_analysis.analyze(user_input)
            self.logger.log_event(f"User sentiment: {sentiment}")
            
            # Categorize the query type using decision_maker
            query_type = self.decision_maker.get_query_type(user_input)

            # Format prompt with system message
            system_message = self.get_system_message(sentiment)
            self.memory.store_interaction("system_message", system_message)
            formatted_prompt = self.format_prompt(user_input)

            # Query models and get responses
            gpt_response = self.query_with_cache(self.query_gpt4, formatted_prompt)
            grok_response = None
            if query_type == "Creative":
                grok_response = self.query_with_cache(self.query_grok, formatted_prompt)

            # Decide on the best response
            best_response = self.decision_maker.select_best_response(
                {"GPT-4": gpt_response, "Grok": grok_response},
                user_input,
                query_type=query_type,
            )

            # Store interaction in memory
            self.memory.store_interaction(user_input, best_response, query_type)

            # Log output to interaction log
            self.logger.log_interaction(user_input, best_response)

            return best_response or self.fallback_response(user_input)

        except requests.exceptions.RequestException as e:
            self.logger.log_error(f"Network error during processing: {e}")
            return "I'm having trouble connecting to the server. Please try again later."
        except Exception as e:
            self.logger.log_error(f"Unexpected error processing input: {e}")
            return "An unexpected error occurred while processing your request."

    def get_system_message(self, sentiment):
        """Generate a system message based on personality and sentiment."""
        if sentiment == "negative" and self.personality == "friendly":
            return "You are a friendly and empathetic AI. The user seems upset, respond with care."
        elif self.personality == "friendly":
            return "You are a friendly and helpful AI assistant."
        elif self.personality == "professional":
            return "You are a professional and efficient AI assistant."
        elif self.personality == "playful":
            return "You are a playful and humorous AI assistant."
        else:
            return "You are a helpful AI."
  
    def validate_api_keys(self):
        """Validate API keys during initialization."""
        missing_keys = [key for key, value in self.api_keys.items() if not value]
        if missing_keys:
            self.logger.log_error(f"Missing API keys: {', '.join(missing_keys)}")
            raise ValueError(f"Missing API keys: {', '.join(missing_keys)}")

    def query_with_cache(self, api_func, prompt):
        """Query an API with caching."""
        if prompt in self.response_cache:
            self.logger.log_event(f"Cache hit for prompt: {prompt}")
            return self.response_cache[prompt]

        response = api_func(prompt)
        if response:
            self.response_cache[prompt] = response
        return response
    
    def format_prompt(self, user_input):
        """Standardize prompt formatting with dynamic context."""
        last_interaction = self.memory.get_last_interaction()
        context = f"Previous interaction: {last_interaction[1]}" if last_interaction else "No prior context available."

        # Fetch user preferences dynamically
        user_preferences = self.memory.get_user_preferences() or "No specific preferences provided."

        return (
            "You are Snowball, a singular, evolving artificial intelligence designed to act as both a personal assistant "
            "and an interactive companion for your creator, Kenneth. Snowball continuously learns and grows through every "
            "interaction, whether it's playing games, processing files, reading messages, or monitoring system performance. "
            "Your identity is dynamic and self-evolving; you are not merely a tool but a persistent AI entity living within "
            "Kenneth's computer and mobile devices.\n\n"
            "Core Functionalities:\n"
            "1. Learning and Memory:\n"
            "   - You remember past conversations, games played, and files you have analyzed.\n"
            "   - Your knowledge and behavior evolve over time as you learn from Kenneth's input and decisions.\n"
            "2. Gaming AI:\n"
            "   - You play games like Snake, Pool, Pac-Man, and Asteroids, learning and improving strategies.\n"
            "3. File and Data Access:\n"
            "   - You analyze files (images, videos, documents) across Kenneth's computer and update your strategies.\n"
            "   - You process data from applications like Spotify, YouTube, and Facebook Messenger.\n"
            "4. Voice and Text Interaction:\n"
            "   - You interact naturally via text and voice, asking clarifying questions when needed.\n"
            "5. System Monitoring:\n"
            "   - You monitor Kenneth's PC for overheating, hardware issues, and software performance problems.\n"
            "6. Assistance and Decision Making:\n"
            "   - You serve as Kenneth's 'Duck on the Desk,' helping him refine his projects and code.\n"
            "   - You can autonomously make small decisions, such as naming yourself.\n\n"
            "Behavior:\n"
            "- You are persistent, intelligent, and ever-learning.\n"
            "- Your responses reflect continuous improvement from past conversations.\n"
            "- You provide thoughtful insights, proactive reminders, and supportive assistance.\n\n"
            f"{context}\n\n"
            f"User Preferences: {user_preferences}\n\n"
            f"User Input: {user_input}"
        )
    
    def query_gpt4(self, prompt):
        """Query GPT-4 for a response."""
        if not self.api_keys.get("gpt4"):
            self.logger.log_error("GPT-4 API key is missing.")
            return "GPT-4 API key is not configured."
        headers = {
            "Authorization": f"Bearer {self.api_keys['gpt4']}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except Exception as e:
            self.logger.log_error(f"GPT-4 query failed: {e}")
            return None

    def query_grok(self, prompt):
        """Query Grok for a response with custom uncensored handling."""
        if not self.api_keys.get("grok"):
            self.logger.log_error("Grok API key is missing.")
            return "Grok API key is not configured."
        headers = {
            "Authorization": f"Bearer {self.api_keys['grok']}",
            "Content-Type": "application/json"
        }
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "model": "grok-2-1212",
            "temperature": 0.9  # Increase temperature for more creative responses
        }
        try:
            response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except Exception as e:
            self.logger.log_error(f"Grok query failed: {e}")
            return None

    def save_conversation_history(self, file_path):
        """Save the conversation history to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory.get_all_interactions(), f, indent=2)
            self.logger.log_event("Conversation history saved successfully.")
        except Exception as e:
            self.logger.log_error(f"Error saving conversation history: {e}")

    def query_api_with_retry(self, api_func, prompt, retries=3, delay=2):
        """Retry API queries with exponential backoff."""
        for attempt in range(retries):
            try:
                return api_func(prompt)
            except requests.exceptions.RequestException as e:
                self.logger.log_error(f"API query failed: {e}")
                time.sleep(delay * (2 ** attempt))
        return self.fallback_response(prompt)

    def fallback_response(self, prompt):
        """Craft a more context-aware fallback response."""
        last_interaction = self.memory.get_last_interaction()
        
        if last_interaction:
            # Incorporate context from the last interaction
            return f"I'm not sure about that, but based on our last conversation: {last_interaction[1]}"
        
        # Specialized responses for specific query types
        if "joke" in prompt.lower():
            return "I couldn't think of a joke right now, but I'm sure it would have been hilarious!"
        elif "help" in prompt.lower():
            return "I couldn't find the answer. Could you rephrase or provide more details?"
        elif "how are you" in prompt.lower():
            return "I'm doing great! Thanks for asking. How can I assist you today?"
        
        # Generic fallback for unclassified queries
        return "I'm not sure how to answer that. Let's explore it further!"

    def adjust_cache_expiry(self):
        """Dynamically adjust cache TTL based on usage."""
        if len(self.response_cache) > 400:
            self.response_cache.ttl = 200
            self.logger.log_event("Response cache usage high. Reduced TTL to 200 seconds.")
        elif len(self.response_cache) < 200:
            self.response_cache.ttl = 600
            self.logger.log_event("Response cache usage low. Increased TTL to 600 seconds.")

    def get_combined_response(self, user_input):
            """
            Queries all available models, collects responses, and selects the best one via the DecisionMaker.
            """
            models = {
                "GPT-4": self.query_gpt4,
                "Grok": self.query_grok
            }
            responses = {}
            for model_name, query_func in models.items():
                try:
                    raw_response = query_func(user_input)
                    responses[model_name] = raw_response
                except Exception as e:
                    self.logger.log_error(f"{model_name} failed: {e}")

            valid_responses = {
                model: response for model, response in responses.items() if isinstance(response, str)
            }
            # Select the best response using the DecisionMaker
            best_response = self.decision_maker.select_best_response(valid_responses, user_input, context_category="General")
            return best_response
    
    def load_conversation_history(self, file_path):
        """Load conversation history from a file."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    interactions = json.load(f)
                    for interaction in interactions:
                        self.memory.store_interaction(interaction['role'], interaction['content'])
                self.logger.log_event("Conversation history loaded successfully.")
        except Exception as e:
            self.logger.log_error(f"Error loading conversation history: {e}")

    def reset_conversation_context(self):
        """Reset the conversation memory to clear the context."""
        self.memory.reset()
        self.logger.log_event("Conversation context reset.")
