class DecisionMaker:
    def __init__(self, logger):
        self.logger = logger
        self.scoring_data = {
            "GPT-4": {"total_score": 0, "count": 0},
            "Grok": {"total_score": 0, "count": 0},
        }
        self.query_type_scores = {
            "Factual": {"total_score": 0, "count": 0},
            "Creative": {"total_score": 0, "count": 0},
            "General": {"total_score": 0, "count": 0},
            "Sensitive": {"total_score": 0, "count": 0},
        }

    def calculate_penalty(self, response, query_type):
        penalty = 0
        if query_type == "Factual" and "I think" in response:
            penalty += 2
        if "I don't know" in response.lower():
            penalty += 3
        if query_type == "Creative" and len(response.split()) < 5:
            penalty += 2
        return penalty * (1 + self.query_count / 100)  # Increase penalty slightly over time

    def calculate_weights(self, query_type, user_input):
        """Determine weights based on query type and input."""
        factual_weight = 3 if query_type == "Factual" else 1
        creative_weight = 3 if query_type == "Creative" else 1
        engagement_weight = 2
        # Encourage creative responses for creative queries
        if query_type == "Creative" and any(word in user_input.lower() for word in ["joke", "funny", "poem", "story"]):
            creative_weight += 2
        return factual_weight, creative_weight, engagement_weight
   
    def calculate_complexity_weight(self, user_input):
        """Adjust weight based on query complexity."""
        query_complexity = len(user_input.split())
        if query_complexity > 15:
            return 2.0
        if query_complexity > 10:
            return 1.5
        return 1.0

    def normalize_scores(self, scores):
        max_score = max(scores.values(), default=1)
        return {model: (score / max_score) * 10 for model, score in scores.items()}

    def get_dynamic_threshold(self, model_name):
        return self.scoring_data[model_name]["total_score"] / max(self.scoring_data[model_name]["count"], 1)

    def score_response(self, model_name, response, query_types, user_input):
        """
        Scores the response from a model based on its relevance, engagement, and appropriateness
        for the given query types. Supports multi-category queries by averaging scores.
        """
        try:
            if isinstance(query_types, str):
                query_types = [query_types]  # Convert single query type to a list

            combined_score = 0
            for query_type in query_types:
                # Calculate penalties, weights, and complexity adjustment for each query type
                penalty = self.calculate_penalty(response, query_type)
                factual_weight, creative_weight, engagement_weight = self.calculate_weights(query_type, user_input)
                complexity_weight = self.calculate_complexity_weight(user_input)

                # Boost engagement score for specific phrases in the response
                if "What do you think?" in response or "How can I help further?" in response:
                    engagement_weight += 1  # Increment engagement weight

                complexity_weight = self.calculate_complexity_weight(user_input)

                # Calculate score for the current query type
                score = (
                    (factual_weight * (query_type == "Factual")) +
                    (creative_weight * (query_type == "Creative")) +
                    engagement_weight
                ) - penalty
                score *= complexity_weight

                combined_score += max(score, 0)  # Ensure score is non-negative

            # Average the combined score across all query types
            average_score = combined_score / len(query_types)
            normalized_score = self.normalize_scores({model_name: average_score})[model_name]  # Normalize the score

            self.logger.log_event(
                f"Scored {model_name} response: {normalized_score} "
                f"(Combined Score: {combined_score}, Query Types: {query_types})"
            )
            return normalized_score
        except Exception as e:
            self.logger.log_error(f"Error scoring response for {model_name}: {e}")
            return 0
    
    def resolve_tie(self, normalized_scores, valid_responses, query_type):
        """Resolve ties by considering query type and historical averages."""
        tie_models = [model for model, score in normalized_scores.items() if score == max(normalized_scores.values())]

        if len(tie_models) > 1:
            self.logger.log_event(f"Tie detected between models: {tie_models}")

            # Prefer GPT-4 for Factual/General queries, Grok for Creative/Sensitive queries
            if query_type in ["Factual", "General"] and "GPT-4" in tie_models:
                return "GPT-4"
            if query_type in ["Creative", "Sensitive"] and "Grok" in tie_models:
                return "Grok"

            # Use historical averages as a fallback
            historical_averages = {
                model: self.scoring_data[model]["total_score"] / max(self.scoring_data[model]["count"], 1)
                for model in tie_models
            }
            best_model = max(historical_averages, key=historical_averages.get)
            self.logger.log_event(f"Tie resolved using historical averages: {best_model}")
            return best_model

        # Default to the highest-scoring model
        return max(normalized_scores, key=normalized_scores.get)

    def select_best_response(self, responses, user_input, query_type="General"):
        """Select the best response from GPT-4 and Grok."""
        try:
            valid_responses = {model: response for model, response in responses.items() if response}
            if not valid_responses:
                self.logger.log_error("No valid responses found. Returning default fallback.")
                return "I'm unable to provide a meaningful response at the moment."

            scored_responses = {
                model: self.score_response(model, response, query_type, user_input)
                for model, response in valid_responses.items()
            }

            normalized_scores = self.normalize_scores(scored_responses)
            self.logger.log_event(f"Normalized scored responses: {normalized_scores}")

            # Resolve ties or return the highest-scoring model
            best_model = self.resolve_tie(normalized_scores, valid_responses, query_type)

            self.logger.log_event(f"Selected best response from {best_model}")
            return valid_responses[best_model]
        except Exception as e:
            self.logger.log_error(f"Error selecting best response: {e}")
            return "An error occurred while selecting the best response."

    def log_cumulative_scores(self):
        """Logs cumulative scoring trends for all models and query types."""
        try:
            self.logger.log_event("Cumulative Scoring Trends:")
            for model, data in self.scoring_data.items():
                average_score = data["total_score"] / data["count"] if data["count"] > 0 else 0
                self.logger.log_event(
                    f"{model}: Total Score = {data['total_score']}, Count = {data['count']}, Average = {average_score:.2f}"
                )
            for query_type, data in self.query_type_scores.items():
                average_score = data["total_score"] / data["count"] if data["count"] > 0 else 0
                self.logger.log_event(
                    f"Query Type: {query_type} -> Total Score = {data['total_score']}, Count = {data['count']}, Average = {average_score:.2f}"
                )
        except Exception as e:
            self.logger.log_error(f"Error logging cumulative scores: {e}")

    def update_scoring_data(self, model, score, query_type):
        """Update scoring data for models and query types."""
        try:
            self.scoring_data[model]["total_score"] += score
            self.scoring_data[model]["count"] += 1
            if query_type in self.query_type_scores:
                self.query_type_scores[query_type]["total_score"] += score
                self.query_type_scores[query_type]["count"] += 1
        except Exception as e:
            self.logger.log_error(f"Error updating scoring data: {e}")