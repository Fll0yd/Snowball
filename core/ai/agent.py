import json
import requests
import re
import time
from cachetools import TTLCache
from Snowball.core.logger import SnowballLogger  # Update to include Snowball


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
        self.api_keys = self._load_api_keys()
        if not self.api_keys:  # Check for loading failure
            self.logger.log_error("Error loading API keys: API keys are missing or invalid.")
        self.response_cache = TTLCache(maxsize=100, ttl=300)  # 5 minutes cache
        self.logger.log_event("Snowball AI initialized.")

    def _load_api_keys(self):
        """Load and validate API keys from the configuration file."""
        try:
            with open('S:/Snowball/config/account_integrations.json') as f:
                config = json.load(f)
                api_keys = {
                    "gpt4": config['api_keys'].get('openai_api_key'),
                    "gemini": config['api_keys'].get('google_gemini_api_key'),
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

    def query_api_with_retry(self, name, url, headers, data, retries=3, delay=2):
        """Retry wrapper for API queries with exponential backoff."""
        for attempt in range(retries):
            try:
                self.logger.log_event(f"Attempt {attempt + 1}: Sending request to {name}...")
                response = requests.post(url, headers=headers, json=data, timeout=20)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                self.logger.log_error(f"{name} Error: {e}")
                time.sleep(delay * (2 ** attempt))
        return {"error": f"{name} API failed after {retries} retries."}

    def query_api(self, name, url, headers, data, timeout=20):
        """Generic API query function with error handling."""
        try:
            self.logger.log_event(f"Sending request to {name}: {data}")
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
            response.raise_for_status()
            try:
                response_json = response.json()
                self.logger.log_event(f"Response from {name}: {response_json}")
                return response_json
            except ValueError as e:
                self.logger.log_error(f"{name} JSON decoding error: {e}")
                return {"error": f"Invalid JSON response from {name}."}
        except requests.exceptions.RequestException as e:
            self.logger.log_error(f"{name} API Error: {e}, Response: {getattr(response, 'text', '')}")
            return {"error": f"Failed to query {name} API: {str(e)}"}

    def query_api_with_cache(self, name, prompt, query_func):
        """Check cache before querying an API."""
        if (name, prompt) in self.response_cache:
            cached_response = self.response_cache[(name, prompt)]
            self.logger.log_event(f"Returning cached response for {name}: {cached_response}")
            return cached_response

        self.logger.log_event(f"No cache hit for {name}. Querying API...")
        response = query_func(prompt)
        self.response_cache[(name, prompt)] = response
        return response
    
    def query_gpt4(self, prompt):
        if not self.api_keys.get("gpt4"):
            self.logger.log_error("GPT-4 API key is missing.")
            return "GPT-4 API key is not configured."
        
        headers = {
            "Authorization": f"Bearer {self.api_keys['gpt4']}",
            "Content-Type": "application/json"
        }
        system_role = (
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
            "- You provide thoughtful insights, proactive reminders, and supportive assistance.\n"
        )

        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ]
        }

        response = self.query_api("GPT-4", "https://api.openai.com/v1/chat/completions", headers, data)
        return response.get("choices", [{}])[0].get("message", {}).get("content", "I'm sorry, I couldn't process that request.")

    def query_gemini(self, prompt):
        if not self.api_keys.get("gemini"):
            self.logger.log_error("Gemini API key is missing.")
            return "Gemini API key is not configured."

        headers = {"Content-Type": "application/json"}
        system_message = (
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
            "- You provide thoughtful insights, proactive reminders, and supportive assistance.\n"
        )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_keys['gemini']}"
        data = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            response = requests.post(url, headers=headers, json=data, timeout=20)
            response.raise_for_status()
            response_json = response.json()
            self.logger.log_event(f"Full Gemini API response: {response_json}")

            # Preprocess Gemini's response
            candidates = response_json.get("candidates", [])
            if candidates:
                content_parts = candidates[0].get("content", {}).get("parts", [])
                if content_parts and "text" in content_parts[0]:
                    raw_response = content_parts[0]["text"].strip()

                    # Preprocessing step
                    if "I am not Snowball" in raw_response:
                        raw_response = raw_response.replace("I am not Snowball", "I am Snowball, your persistent AI assistant.")
                    if "I am Gemini" in raw_response:
                        raw_response = raw_response.replace("I am Gemini", "I am Snowball")

                    return self.cleanup_response(raw_response)

            return "No valid response generated from Gemini."
        except requests.exceptions.RequestException as e:
            self.logger.log_error(f"Gemini API Error with payload {data}: {e}")
            return {"error": "Gemini is currently unavailable. Please try again later."}
        
    def query_grok(self, prompt):
        """Query the Grok API."""
        if not self.api_keys.get("grok"):
            self.logger.log_error("Grok API key is missing.")
            return "Grok API key is not configured."

        headers = {
            "Authorization": f"Bearer {self.api_keys['grok']}",
            "Content-Type": "application/json"
        }
        url = "https://api.x.ai/v1/chat/completions"
        data = {
            "messages": [
                {"role": "system", "content": (
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
                    "- You provide thoughtful insights, proactive reminders, and supportive assistance."
                )},
                {"role": "user", "content": prompt}
            ],
            "model": "grok-2-1212",
            "stream": False,
            "temperature": 0
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=20)
            response.raise_for_status()
            response_json = response.json()

            # Extract raw response
            raw_response = response_json.get("choices", [{}])[0].get("message", {}).get("content", "No valid response.")
            self.logger.log_event(f"Raw response from Grok: {raw_response}")

            # Replace Grok identity in raw response
            cleaned_response = raw_response.replace("I'm not Snowball, I'm Grok", "I am Snowball, here to assist you")
            self.logger.log_event(f"Cleaned and processed Grok response: {cleaned_response}")

            return self.cleanup_response(cleaned_response)
        except requests.exceptions.RequestException as e:
            self.logger.log_error(f"Grok API Error: {e}")
            return {"error": "Failed to connect to Grok API."}

    def cleanup_response(self, response, model_name=None):
        """Remove redundant sentences and align responses with Snowball's persona."""
        sentences = re.split(r'[.!?]', response)  # Split into sentences
        unique_sentences = []
        seen = set()

        for sentence in sentences:
            cleaned = sentence.strip()

            # Replace model-specific identity with Snowball's persona
            if model_name == "Grok":
                cleaned = cleaned.replace("I'm not Snowball, I'm Grok", "I am Snowball, here to assist you")
            elif model_name == "Gemini":
                # Comprehensive replacement for Gemini-specific identity
                cleaned = cleaned.replace("I am not Snowball", "I am Snowball, your persistent AI assistant")
                cleaned = cleaned.replace("I am Gemini", "I am Snowball")
                cleaned = cleaned.replace("multi-modal model", "an advanced AI assistant")
                cleaned = cleaned.replace("trained by Google", "tailored for your needs")
                # Remove any mention of Gemini
                cleaned = re.sub(r"\bGemini\b", "Snowball", cleaned, flags=re.IGNORECASE)

            # Deduplicate and collect sentences
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                unique_sentences.append(cleaned)

        # Join sentences into a grammatically correct response
        return ". ".join(unique_sentences).strip() + ('.' if unique_sentences else "")

    def score_response(self, response, user_context, engagement_weight=1.5, personalization_weight=2):
        """
        Scores a response based on engagement, personalization, and context relevance.
        """
        score = 0
        # Engagement Scoring
        if any(phrase in response.lower() for phrase in ["would you like", "how can I help"]):
            score += engagement_weight

        # Personalization Scoring
        if any(context in response for context in user_context):
            score += personalization_weight

        # Context Relevance
        if "debugging" in response.lower() and "python" in response.lower():
            score += 1  # Add weight for context match

        return score

    def tie_break(self, responses, user_context):
        """
        Enhanced tie-breaking logic with prioritization of context relevance,
        verified personalization, and concise engagement.
        """
        # Filter out irrelevant or penalized responses
        valid_responses = {model: response for model, response in responses.items() if response}

        # Step 1: Prioritize context relevance
        best_relevance = None
        for model, response in valid_responses.items():
            if self.is_contextually_relevant(response, user_context):
                best_relevance = response
                self.logger.log_event(f"Contextually relevant response selected from: {model}")
                return response

        # Step 2: Consider engagement and personalization scores
        scores = {
            model: self.enhanced_score_response(response, user_context)
            for model, response in valid_responses.items()
        }
        best_score = max(scores.values())
        top_models = [model for model, score in scores.items() if score == best_score]

        # Step 3: Handle ties by length or interactivity
        if len(top_models) > 1:
            self.logger.log_event("Tie detected. Applying tie-breaking logic.")

            # Prioritize personalization
            personalized_responses = [
                model for model in top_models
                if "Kenneth" in valid_responses[model] or "Minecraft" in valid_responses[model]
            ]
            if personalized_responses:
                selected_model = personalized_responses[0]
                self.logger.log_event(f"Tie broken based on personalization: {selected_model}")
                return valid_responses[selected_model]

            # Prioritize engagement (proactive follow-ups)
            engaging_responses = [
                model for model in top_models
                if any(phrase in valid_responses[model].lower() for phrase in ["what do you think", "would you like"])
            ]
            if engaging_responses:
                selected_model = engaging_responses[0]
                self.logger.log_event(f"Tie broken based on engagement: {selected_model}")
                return valid_responses[selected_model]

            # Fallback to longest response
            longest_response = max(top_models, key=lambda model: len(valid_responses[model]))
            self.logger.log_event(f"Tie broken based on response length: {longest_response}")
            return valid_responses[longest_response]

    def get_combined_response(self, user_input):
        """
        Queries all available models, scores their responses, and selects the best one.
        Implements enhanced tie-breaking logic.
        """
        responses = {}
        models = {
            "GPT-4": self.query_gpt4,
            "Gemini": self.query_gemini,
            "Grok": self.query_grok
        }

        # Query all models
        for model_name, query_func in models.items():
            try:
                self.logger.log_event(f"Querying {model_name}...")
                raw_response = query_func(user_input)
                if isinstance(raw_response, str):
                    cleaned_response = self.cleanup_response(raw_response, model_name)
                    responses[model_name] = cleaned_response
                    self.logger.log_event(f"Response from {model_name}: {cleaned_response}")
                else:
                    self.logger.log_error(f"{model_name} returned a non-string response: {raw_response}")
            except Exception as e:
                self.logger.log_error(f"{model_name} failed: {e}")
                responses[model_name] = None

        # Score valid responses
        valid_responses = {k: v for k, v in responses.items() if v}
        scored_responses = {
            model: self.score_response(response=text, user_context=user_input)
            for model, text in valid_responses.items()
        }
        self.logger.log_event(f"Scored responses: {scored_responses}")

        # Select the best response
        if scored_responses:
            max_score = max(scored_responses.values())
            top_models = [model for model, score in scored_responses.items() if score == max_score]

            # Tie-breaking logic
            if len(top_models) > 1:
                self.logger.log_event("Tie detected. Applying tie-breaking logic.")
                
                # Prioritize personalization
                personalized_responses = [
                    model for model in top_models
                    if "Kenneth" in valid_responses[model]
                ]
                if personalized_responses:
                    selected_model = personalized_responses[0]
                    self.logger.log_event(f"Tie broken based on personalization: {selected_model}")
                    return valid_responses[selected_model]

                # If still tied, choose longest response
                longest_response = max(
                    top_models,
                    key=lambda model: len(valid_responses[model])
                )
                if top_models.count(longest_response) == 1:
                    self.logger.log_event(f"Tie broken based on response length: {longest_response}")
                    return valid_responses[longest_response]

                # Final fallback: Random selection
                import random
                selected_model = random.choice(top_models)
                self.logger.log_event(f"Tie broken randomly: {selected_model}")
                return valid_responses[selected_model]

            # Single best response
            best_model = top_models[0]
            self.logger.log_event(f"Best response selected from {best_model}: {valid_responses[best_model]}")
            return valid_responses[best_model]

        # Default fallback when all models fail
        return "I'm sorry, all models are currently unavailable. How else can I assist you?"

    def is_irrelevant_response(self, response):
        """Check if a response is irrelevant based on undesirable patterns."""
        for pattern in self.irrelevant_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                self.logger.log_event(f"Irrelevant response detected: {pattern}")
                return True
        return False

    def verify_response_references(self, response, known_context):
        """
        Penalize unverifiable references in a response.
        """
        penalty = 0
        unverified_indicators = [
            "I remember you enjoyed",
            "last time we talked about",
            "from our previous games",
        ]
        for indicator in unverified_indicators:
            if indicator in response and not any(context in response for context in known_context):
                penalty += 1
                self.logger.log_event(f"Response penalized for unverifiable reference: {indicator}")
        return penalty

    def enhanced_score_response(response, user_context, engagement_weight=1.5, personalization_weight=2):
        """
        Scores a response with an additional penalty for unverifiable references.
        
        :param response: AI's response to score.
        :param user_context: Dictionary of user-specific details or context.
        :param engagement_weight: Weight for engagement factors.
        :param personalization_weight: Weight for personalization factors.
        :return: Final score after applying penalties.
        """
        score = 0

        # Engagement Scoring
        if any(phrase in response.lower() for phrase in ["would you like", "how can I help"]):
            score += engagement_weight

        # Personalization Scoring
        if any(context in response for context in user_context):
            score += personalization_weight

        # Context Relevance
        if "minecraft" in response.lower() and "theme" in response.lower():
            score += 1  # Add weight for context match

        # Add Verification Penalty
        penalty = verify_response_references(response, user_context)
        score -= penalty  # Apply penalty for unverifiable references

        return max(score, 0)  # Ensure score doesn't go negative

    def query_api_with_retry(self, name, url, headers, data, retries=3, delay=2):
        """Retry wrapper for API queries with exponential backoff."""
        for attempt in range(retries):
            try:
                self.logger.log_event(f"Attempt {attempt + 1}: Sending request to {name}...")
                response = requests.post(url, headers=headers, json=data, timeout=20)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                self.logger.log_error(f"{name} Error: {e}")
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
        return {"error": f"{name} API failed after {retries} retries."}
