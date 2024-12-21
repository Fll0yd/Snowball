import json
import requests
import re
import time
import random
from cachetools import TTLCache
from Snowball.core.logger import SnowballLogger
from Snowball.core.ai.decision_maker import DecisionMaker
from Snowball.core.ai.memory import Memory


class SnowballAI:
    """Simplified Snowball AI for querying and combining responses."""
    irrelevant_patterns = [
        r"As an AI language model",
        r"I'm a \d+-year-old boy",
        r"I'm sorry.*(not know|can't)",
        r"Amazon Snowball",
        r"I don't know",
        r"I'm back from a long break",
        r"server.*group.*specific",  # Off-topic server ideas
        r"only available to",        # Partial/incomplete responses
        r"I've been thinking about"  # Indications of unrelated brainstorming
    ]

    def __init__(self):
        self.logger = SnowballLogger()
        self.decision_maker = DecisionMaker(self.logger)
        self.api_keys = self._load_api_keys()
        if not self.api_keys:
            self.logger.log_error("Error loading API keys: API keys are missing or invalid.")
        self.metadata_cache = TTLCache(maxsize=500, ttl=300)
        self.response_cache = TTLCache(maxsize=500, ttl=300)  # Cache for responses
        self.memory = Memory(logger=self.logger)  # Initialize Memory module
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
        system_role = ()
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

    def query_api_with_retry(self, api_func, prompt, retries=3, delay=2):
        """Retry API queries with exponential backoff."""
        for attempt in range(retries):
            try:
                return api_func(prompt)
            except requests.exceptions.RequestException as e:
                self.logger.log_error(f"API query failed: {e}")
                time.sleep(delay * (2 ** attempt))
        return self.fallback_response(prompt)

    def detect_query_type(self, user_input):
        """Determine the query type based on keywords."""
        sensitive_keywords = ["politics", "controversial", "sensitive", "explicit", "uncensored"]
        
        if any(word in user_input.lower() for word in sensitive_keywords):
            return "Sensitive"
        if any(word in user_input.lower() for word in ["joke", "funny", "creative", "story"]):
            return "Creative"
        if any(word in user_input.lower() for word in ["how", "what", "why"]):
            return "Factual"
        return "General"

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

    def validate_response(self, response, query_type):
        """Validate responses based on query type."""
        if query_type == "Factual" and ("I think" in response or "I'm not sure" in response):
            self.logger.log_warning("Factual query returned an uncertain response.")
            return False
        if query_type == "Creative" and len(response.split()) < 5:  # Example: Too short for creative responses
            self.logger.log_warning("Creative query returned an unengaging response.")
            return False
        if "I don't know" in response.lower():
            return False
        return True

    def decide_best_response(self, gpt_response, grok_response, prompt):
        """Decide which response to use with enhanced logging."""
        query_type = self.detect_query_type(prompt)
        responses = {"GPT-4": gpt_response, "Grok": grok_response}
        scored_responses = self.decision_maker.score_responses(responses, prompt)
        self.logger.log_event(f"Query: {prompt}, Type: {query_type}, Scores: {scored_responses}")

        # Use Grok for sensitive content explicitly
        if query_type == "Sensitive" and "Grok" in scored_responses:
            self.logger.log_event("Selected Grok for handling sensitive content.")
            return scored_responses["Grok"]

        # Use GPT-4 for factual queries if response is valid
        if "GPT-4" in scored_responses:
            if self.validate_response(scored_responses["GPT-4"], "Factual"):
                self.logger.log_event("Selected GPT-4 for factual accuracy.")
                return scored_responses["GPT-4"]

        # Fallback to Grok for factual queries if GPT-4 fails
        if not gpt_response and "Grok" in scored_responses:
            self.logger.log_event("Fallback to Grok for factual accuracy due to GPT-4 failure.")
            return scored_responses["Grok"]

        # Use Grok for creative queries if valid
        if "Grok" in scored_responses:
            if self.validate_response(scored_responses["Grok"], query_type):
                self.logger.log_event(f"Selected Grok for {query_type} response.")
                return scored_responses["Grok"]

        # Default fallback
        self.logger.log_event("Fallback to GPT-4 due to scoring tie or ambiguity.")
        return scored_responses.get("GPT-4", "I'm having trouble processing your request.")

    def process_user_input(self, user_input):
        """Process user input and generate a response."""
        if not user_input.strip():
            return "It seems you didn't provide any input. How can I assist you?"

        try:
            query_type = self.detect_query_type(user_input)
            formatted_prompt = self.format_prompt(user_input)

            if query_type == "Sensitive":
                # Route sensitive queries directly to Grok
                grok_response = self.query_with_cache(self.query_grok, formatted_prompt)
                if grok_response:
                    self.memory.store_interaction(user_input, grok_response, query_type)
                    return grok_response
                return self.fallback_response(user_input)

            # Handle other query types
            gpt_response = self.query_with_cache(self.query_gpt4, formatted_prompt)
            grok_response = None

            if query_type == "Creative":
                grok_response = self.query_with_cache(self.query_grok, formatted_prompt)

            best_response = self.decide_best_response(gpt_response, grok_response, user_input)
            self.memory.store_interaction(user_input, best_response, query_type)
            return best_response or self.fallback_response(user_input)
        except requests.exceptions.RequestException as e:
            self.logger.log_error(f"Network error during processing: {e}")
            return "I'm having trouble connecting to the server. Please try again later."
        except Exception as e:
            self.logger.log_error(f"Unexpected error processing input: {e}")
            return "An unexpected error occurred while processing your request."
