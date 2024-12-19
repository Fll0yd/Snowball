import json
import requests
from core.logger import SnowballLogger  # Import your centralized logger

class SnowballAI:
    """Simplified Snowball AI for querying and combining responses."""

    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.logger = SnowballLogger()  # Initialize your logger

    def _load_api_keys(self):
        with open('S:/Snowball/config/account_integrations.json') as f:
            config = json.load(f)
        return {
            "gpt4": config['api_keys'].get('openai_api_key'),
            "claude3": config['api_keys'].get('anthropic_api_key'),
            "gemini": config['api_keys'].get('google_gemini_api_key'),
        }

    def query_api(self, name, url, headers, data):
        """Generic API query function."""
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.log_error(f"{name} API Error: {e}")
            return ""

    def query_gpt4(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_keys['gpt4']}", "Content-Type": "application/json"}
        data = {"model": "gpt-4", "messages": [{"role": "user", "content": prompt}]}
        response = self.query_api("GPT-4", "https://api.openai.com/v1/chat/completions", headers, data)
        return response.get("choices", [{}])[0].get("message", {}).get("content", "")

    def query_claude3(self, prompt):
        headers = {"x-api-key": self.api_keys['claude3'], "Content-Type": "application/json"}
        data = {"model": "claude-3-opus-2024-03-04", "messages": [{"role": "user", "content": prompt}]}
        response = self.query_api("Claude 3", "https://api.anthropic.com/v1/messages", headers, data)
        return response.get("content", "")

    def query_gemini(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_keys['gemini']}", "Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        response = self.query_api("Gemini", "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent", headers, data)
        return response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

    def get_combined_response(self, user_input):
        """Get and compare responses from GPT-4, Claude 3, and Gemini, and return the best one."""
        try:
            responses = {
                "GPT-4": self.query_gpt4(user_input),
                "Claude 3": self.query_claude3(user_input),
                "Gemini": self.query_gemini(user_input),
            }

            # Log the responses to the centralized logger
            self.logger.log_interaction(user_input, f"GPT-4: {responses['GPT-4']}")
            self.logger.log_interaction(user_input, f"Claude 3: {responses['Claude 3']}")
            self.logger.log_interaction(user_input, f"Gemini: {responses['Gemini']}")

            # Select the response with the longest content as an example
            best_response = max(responses.items(), key=lambda r: len(r[1]) if r[1] else 0)
            self.logger.log_interaction(user_input, f"Best Response ({best_response[0]}): {best_response[1]}")

            return f"Best Response ({best_response[0]}): {best_response[1]}"

        except Exception as e:
            self.logger.log_error(f"Error gathering responses: {e}")
            return "I'm sorry, I encountered an issue while processing your request."
