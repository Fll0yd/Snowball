import openai
import random
import json
from Snowball.decom.OLDinitializer import SnowballInitializer

class Conversation:
    def __init__(self):
        initializer = SnowballInitializer()
        self.api_key = initializer.openai_api_key
        openai.api_key = self.api_key
        self.logger = initializer.logger
        self.memory = initializer.memory
        self.sentiment_analysis = initializer.sentiment_analysis
        self.decision_maker = initializer.decision_maker

        self.personality = "helpful"  # Default personality mode

    def set_personality(self, personality):
        """Set the personality mode of the AI, such as 'friendly', 'professional', 'playful'."""
        self.personality = personality
        self.logger.log_event(f"Personality set to: {self.personality}")

    def process_input(self, user_input):
        try:
            # Analyzing sentiment to adjust response
            sentiment = self.sentiment_analysis.analyze(user_input)
            self.logger.log_event(f"User sentiment: {sentiment}")

            # Append user input to memory to maintain conversation context
            self.memory.store_interaction("user_input", user_input)
            system_message = self.get_system_message(sentiment)
            self.memory.store_interaction("system_message", system_message)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_message}] + self.memory.get_recent_interactions(),
                max_tokens=150,
                temperature=0.9
            )

            # Extract the AI's response
            ai_response = response.choices[0].message['content']
            self.memory.store_interaction("assistant_response", ai_response)

            return ai_response
        except Exception as e:
            self.logger.log_event(f"Error processing input: {e}")
            return "I'm sorry, I encountered an error while processing your request."

    def generate_name(self, suggestions):
        try:
            prompt = "Generate a unique and creative name for an AI assistant. Here are some suggestions: " + ", ".join(suggestions) + "."
            response = openai.Completion.create(
                model="gpt-3.5-turbo",
                prompt=prompt,
                max_tokens=50,
                temperature=0.7
            )
            generated_name = response.choices[0].text.strip()
            self.logger.log_event(f"Generated name: {generated_name}")
            return generated_name
        except Exception as e:
            self.logger.log_event(f"Error generating name: {e}")
            return "Snowball"

    def refine_response(self, responses):
        """Select the most contextually appropriate response from multiple models."""
        # Placeholder implementation for comparing multiple responses
        if len(responses) == 0:
            return "I couldn't generate a response."
        return random.choice(responses)  # In future, implement a more intelligent selection process

    def get_system_message(self, sentiment):
        """Generate a system message to set the AI's behavior based on personality and sentiment."""
        if sentiment == "negative" and self.personality == "friendly":
            content = "You are a friendly and empathetic AI assistant. The user seems upset, respond with care."
        elif self.personality == "friendly":
            content = "You are a friendly and helpful AI assistant."
        elif self.personality == "professional":
            content = "You are a professional and efficient AI assistant."
        elif self.personality == "playful":
            content = "You are a playful and humorous AI assistant."
        else:
            content = "You are a helpful AI."
        return content

    def save_conversation_history(self, file_path):
        """Save the conversation history to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory.get_all_interactions(), f, indent=2)
            self.logger.log_event("Conversation history saved successfully.")
        except Exception as e:
            self.logger.log_event(f"Error saving conversation history: {e}")

    def load_conversation_history(self, file_path):
        """Load conversation history from a file."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    interactions = json.load(f)
                    for interaction in interactions:
                        self.memory.store_interaction(interaction['role'], interaction['content'])
                self.logger.log_event("Conversation history loaded successfully.")
            else:
                self.logger.log_event("No conversation history file found.")
        except Exception as e:
            self.logger.log_event(f"Error loading conversation history: {e}")

    def reset_conversation_context(self):
        """Reset the conversation memory to clear the context."""
        self.memory.reset()
        self.logger.log_event("Conversation context reset.")

    def get_user_feedback(self, response):
        """Simulate obtaining user feedback to refine future responses."""
        # This could be implemented with an actual user interface for feedback
        feedback = "positive"  # Placeholder value; replace with actual user input mechanism
        self.logger.log_event(f"User feedback on response '{response}': {feedback}")
        return feedback

    def provide_refined_response(self, user_input):
        """Refine the AI response based on user feedback."""
        initial_response = self.process_input(user_input)
        feedback = self.get_user_feedback(initial_response)

        if feedback == "negative":
            self.logger.log_event("Generating a refined response based on user feedback.")
            return self.process_input(user_input)
        return initial_response

    def get_conversation_summary(self):
        """Generate a summary of the current conversation context."""
        if not self.memory.has_interactions():
            return "There is no active conversation."

        summary_prompt = "Summarize the following conversation: " + \
                         "\n".join([f"{m['role']}: {m['content']}" for m in self.memory.get_all_interactions() if m['role'] != 'system'])
        try:
            response = openai.Completion.create(
                model="gpt-3.5-turbo",
                prompt=summary_prompt,
                max_tokens=150,
                temperature=0.7
            )
            summary = response.choices[0].text.strip()
            self.logger.log_event("Generated conversation summary.")
            return summary
        except Exception as e:
            self.logger.log_event(f"Error generating conversation summary: {e}")
            return "Sorry, I couldn't generate a summary."
