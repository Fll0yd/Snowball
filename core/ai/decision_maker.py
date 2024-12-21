class DecisionMaker:
    """
    Handles decision-making logic for Snowball AI, including scoring and selecting responses
    between GPT-4 and Grok.
    """
    def __init__(self, logger):
        self.logger = logger
        self.scoring_data = {
            "GPT-4": {"total_score": 0, "count": 0},
            "Grok": {"total_score": 0, "count": 0},
        }
        self.query_count = 0  # Track the number of queries
        self.query_type_scores = {
            "Factual": {"total_score": 0, "count": 0},
            "Creative": {"total_score": 0, "count": 0},
            "General": {"total_score": 0, "count": 0},
        }

    def score_response(self, model_name, response, query_type, user_input):
        """
        Scores the response from a model based on its relevance, engagement, and appropriateness
        for the given query type.
        """
        try:
            # Initialize scoring weights
            factual_weight = 3 if query_type == "Factual" else 1
            creative_weight = 3 if query_type == "Creative" else 1
            engagement_weight = 2
            penalty = 0

            # Check for relevance
            if query_type == "Factual" and "I think" in response:
                penalty += 2  # Penalize uncertain responses for factual queries
            if "I don't know" in response.lower():
                penalty += 3

            # Encourage creative responses for creative queries
            if query_type == "Creative" and any(word in user_input.lower() for word in ["joke", "funny", "poem", "story"]):
                creative_weight += 2

            # Final score
            score = (
                factual_weight * (1 if query_type == "Factual" else 0) +
                creative_weight * (1 if query_type == "Creative" else 0) +
                engagement_weight
            ) - penalty

            self.logger.log_event(f"Scored {model_name} response: {score} (Penalty: {penalty})")
            return max(score, 0)  # Ensure non-negative scores
        except Exception as e:
            self.logger.log_error(f"Error scoring response for {model_name}: {e}")
            return 0

    def select_best_response(self, responses, user_input, query_type="General"):
        """
        Select the best response from GPT-4 and Grok.
        """
        try:
            scored_responses = {}
            for model, response in responses.items():
                if response:  # Ensure the response is valid
                    scored_responses[model] = self.score_response(model, response, query_type, user_input)

            # Log the scores for debugging
            self.logger.log_event(f"Scored responses: {scored_responses}")

            # Prefer GPT-4 for factual or general queries
            if query_type in ["Factual", "General"] and "GPT-4" in scored_responses:
                return responses["GPT-4"]

            # Prefer Grok for creative or humorous queries
            if query_type == "Creative" and "Grok" in scored_responses:
                return responses["Grok"]

            # Fallback to the model with the highest score
            best_model = max(scored_responses, key=scored_responses.get)
            self.logger.log_event(f"Selected best response from {best_model}")
            return responses[best_model]
        except Exception as e:
            self.logger.log_error(f"Error selecting best response: {e}")
            return "I'm having trouble deciding on a response."

    def log_cumulative_scores(self):
        """
        Logs cumulative scoring trends for all models.
        """
        try:
            self.logger.log_event("Cumulative Scoring Trends:")
            for model, data in self.scoring_data.items():
                average_score = data["total_score"] / data["count"] if data["count"] > 0 else 0
                self.logger.log_event(
                    f"{model}: Total Score = {data['total_score']}, Count = {data['count']}, Average = {average_score:.2f}"
                )
        except Exception as e:
            self.logger.log_error(f"Error logging cumulative scores: {e}")

    def update_scoring_data(self, model, score, query_type):
        """
        Update scoring data for models and query types.
        """
        try:
            self.scoring_data[model]["total_score"] += score
            self.scoring_data[model]["count"] += 1
            if query_type in self.query_type_scores:
                self.query_type_scores[query_type]["total_score"] += score
                self.query_type_scores[query_type]["count"] += 1
        except Exception as e:
            self.logger.log_error(f"Error updating scoring data: {e}")
