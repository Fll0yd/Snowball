from Snowball.core.ai.reinforcement import QLearningAgent

class DecisionMaker:
    def __init__(self, logger, state_size=10, action_size=3):
        self.logger = logger
        self.sentiment_analyzer = sentiment_analyzer  # Integrate SentimentAnalysis module
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

        # Initialize reinforcement learning agent
        self.reinforcement_agent = QLearningAgent(
            state_size=state_size,
            action_size=action_size,
            logger=self.logger
        )
        self.logger.log_event("Reinforcement agent initialized in DecisionMaker.")

    def detect_query_type(self, user_input):
        """Determine the query type based on keywords and sentiment."""
        try:
            # Analyze sentiment to refine query type detection
            sentiment = self.sentiment_analyzer.hybrid_sentiment_analysis(user_input)
            self.logger.log_event(f"Hybrid sentiment analysis result: {sentiment} for input: {user_input}")

            sensitive_keywords = ["politics", "controversial", "sensitive", "explicit", "uncensored"]
            if any(word in user_input.lower() for word in sensitive_keywords):
                query_type = "Sensitive"
            elif any(word in user_input.lower() for word in ["joke", "funny", "creative", "story"]):
                query_type = "Creative"
            elif any(word in user_input.lower() for word in ["how", "what", "why"]):
                query_type = "Factual"
            else:
                query_type = "General"

            # Incorporate sentiment into query type categorization
            if sentiment == "Negative" and query_type == "General":
                query_type = "Sensitive"  # Escalate to sensitive if sentiment is negative
            elif sentiment == "Positive" and query_type == "Factual":
                query_type = "Creative"  # Reclassify as creative if sentiment is positive

            self.logger.log_event(f"Final query type: {query_type} based on sentiment: {sentiment}")
            return query_type
        except Exception as e:
            self.logger.log_error(f"Error detecting query type: {e}")
            return "General"
        
    def log_sentiment_comparison(self, distilbert_result, gpt_result, input_text):
        """Log the sentiment analysis results for comparison."""
        self.logger.log_decision(
            f"Sentiment analysis comparison for input: {input_text}\n"
            f"DistilBERT result: {distilbert_result}\n"
            f"ChatGPT result: {gpt_result}\n"
        )

    def process_file_analysis(self, file_metadata, analysis_result):
        """Process file analysis results with reinforcement learning."""
        interaction = {
            "user_input": f"Analyzed file: {file_metadata['name']}",
            "metadata": [file_metadata["size"], file_metadata["last_modified"]],
            "success": analysis_result.get("success", False),
            "error": analysis_result.get("error", False)
        }
        self.reinforcement_agent.learn_from_interaction(interaction)

    def decide_best_response(self, gpt_response, grok_response, prompt):
        """Decide which response to use with sentiment analysis insights."""
        try:
            # Detect query type (with sentiment analysis)
            query_type = self.detect_query_type(prompt)

            # Log the initial responses
            responses = {"GPT-4": gpt_response, "Grok": grok_response}
            self.logger.log_event(f"Received responses: {responses}")

            # Score responses based on query type
            scored_responses = {
                model: self.score_response(model, response, query_type, prompt)
                for model, response in responses.items() if response
            }

            # Send interaction data to reinforcement agent
            interaction = {
                "user_input": prompt,
                "responses": scored_responses,
                "query_type": query_type,
                "success": bool(scored_responses)  # Example: Success is true if responses exist
            }
            self.reinforcement_agent.learn_from_interaction(interaction)

            self.logger.log_event(f"Scored responses: {scored_responses}")

            # Resolve ties or choose the best response
            if not scored_responses:
                self.logger.log_event("No valid responses found. Returning fallback.")
                return "I'm unable to provide a meaningful response at the moment."

            best_model = self.resolve_tie(scored_responses, responses, query_type)
            self.logger.log_event(f"Selected best model: {best_model} with score: {scored_responses.get(best_model)}")
            return responses[best_model]
        except Exception as e:
            self.logger.log_error(f"Error in decision-making: {e}")
            return "An error occurred while selecting the best response."

    def log_unified_decision(self, user_input, query_type, sentiment, chosen_model, response):
        """Log unified decision details."""
        log_entry = {
            "user_input": user_input,
            "query_type": query_type,
            "sentiment": sentiment,
            "chosen_model": chosen_model,
            "response": response,
        }
        self.logger.log_decision(json.dumps(log_entry, indent=2))

    def integrate_sentiment_into_scores(self, sentiment, model_name, score):
        """Adjust scores based on sentiment analysis results, factoring in confidence."""
        sentiment_weights = {"Positive": 1.2, "Negative": 0.8, "Neutral": 1.0}
        sentiment_weight = sentiment_weights.get(sentiment["label"], 1.0)
        confidence_adjustment = sentiment["confidence"]

        adjusted_score = score * sentiment_weight * confidence_adjustment
        self.logger.log_event(
            f"Adjusted score for {model_name}: {adjusted_score} "
            f"(Original: {score}, Sentiment: {sentiment['label']}, Confidence: {confidence_adjustment})"
        )
        return adjusted_score

    def validate_response(self, response, query_type):
        """Validate responses based on query type."""
        valid = True
        if query_type == "Factual" and ("I think" in response or "I'm not sure" in response):
            self.logger.log_warning("Factual query returned an uncertain response.")
            valid = False
        if query_type == "Creative" and len(response.split()) < 5:
            self.logger.log_warning("Creative query returned an unengaging response.")
            valid = False
        if "I don't know" in response.lower():
            valid = False

        self.logger.log_event(f"Validated response: '{response}' for query type: {query_type}. Valid: {valid}")
        return valid

    def calculate_penalty(self, response, query_type):
        penalty = 0
        if query_type == "Factual" and "I think" in response:
            penalty += 2
        if "I don't know" in response.lower():
            penalty += 3
        if query_type == "Creative" and len(response.split()) < 5:
            penalty += 2
        self.logger.log_event(f"Calculated penalty: {penalty} for response: {response}")
        return penalty

    def calculate_weights(self, query_type, user_input):
        """Determine weights based on query type and input."""
        factual_weight = 3 if query_type == "Factual" else 1
        creative_weight = 3 if query_type == "Creative" else 1
        engagement_weight = 2
        if query_type == "Creative" and any(word in user_input.lower() for word in ["joke", "funny", "poem", "story"]):
            creative_weight += 2
        self.logger.log_event(f"Calculated weights: Factual={factual_weight}, Creative={creative_weight}, Engagement={engagement_weight}")
        return factual_weight, creative_weight, engagement_weight

    def calculate_complexity_weight(self, user_input):
        """Adjust weight based on query complexity."""
        query_complexity = len(user_input.split())
        complexity_weight = 2.0 if query_complexity > 15 else 1.5 if query_complexity > 10 else 1.0
        self.logger.log_event(f"Calculated complexity weight: {complexity_weight} for input: {user_input}")
        return complexity_weight

    def normalize_scores(self, scores):
        max_score = max(scores.values(), default=1)
        normalized_scores = {model: (score / max_score) * 10 for model, score in scores.items()}
        self.logger.log_event(f"Normalized scores: {normalized_scores}")
        return normalized_scores

    def resolve_tie(self, normalized_scores, valid_responses, query_type):
        """Resolve ties by considering query type and historical averages."""
        tie_models = [model for model, score in normalized_scores.items() if score == max(normalized_scores.values())]

        if len(tie_models) > 1:
            self.logger.log_event(f"Tie detected between models: {tie_models}")
            if query_type in ["Factual", "General"] and "GPT-4" in tie_models:
                return "GPT-4"
            if query_type in ["Creative", "Sensitive"] and "Grok" in tie_models:
                return "Grok"

            historical_averages = {
                model: self.scoring_data[model]["total_score"] / max(self.scoring_data[model]["count"], 1)
                for model in tie_models
            }
            best_model = max(historical_averages, key=historical_averages.get)
            self.logger.log_event(f"Tie resolved using historical averages: {best_model}")
            return best_model

        return max(normalized_scores, key=normalized_scores.get)

    def score_response(self, model_name, response, query_types, user_input):
        """
        Scores the response from a model based on its relevance, engagement, and appropriateness
        for the given query types. Supports multi-category queries by averaging scores.
        """
        try:
            if isinstance(query_types, str):
                query_types = [query_types]

            combined_score = 0
            sentiment = self.sentiment_analyzer.hybrid_sentiment_analysis(user_input)

            for query_type in query_types:
                penalty = self.calculate_penalty(response, query_type)
                factual_weight, creative_weight, engagement_weight = self.calculate_weights(query_type, user_input)
                complexity_weight = self.calculate_complexity_weight(user_input)

                # Boost engagement score for specific phrases in the response
                if "What do you think?" in response or "How can I help further?" in response:
                    engagement_weight += 1  # Increment engagement weight

                # Calculate score for the current query type
                score = (
                    (factual_weight * (query_type == "Factual")) +
                    (creative_weight * (query_type == "Creative")) +
                    engagement_weight
                ) - penalty
                score *= complexity_weight
                score = self.integrate_sentiment_into_scores(sentiment, model_name, score)
                combined_score += max(score, 0)

            average_score = combined_score / len(query_types)
            normalized_score = self.normalize_scores({model_name: average_score})[model_name]
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

    def update_game_strategy(self, game_state, action_outcome):
        """Update game strategy based on state and outcome."""
        interaction = {
            "user_input": f"Game state updated: {game_state}",
            "success": action_outcome.get("win", False),
            "error": action_outcome.get("loss", False),
            "metadata": [game_state.get("score", 0), game_state.get("time", 0)]
        }
        self.reinforcement_agent.learn_from_interaction(interaction)

    def update_sentiment_weights(self):
        """Update sentiment weights dynamically based on logged performance data."""
        sentiment_data = {"Positive": [], "Negative": [], "Neutral": []}

        # Example: Read from logs or other data sources
        # This is a placeholder; actual implementation will depend on the logging mechanism
        for entry in self.logger.get_decision_logs():
            sentiment = entry.get("sentiment")
            score = entry.get("score")
            if sentiment in sentiment_data:
                sentiment_data[sentiment].append(score)

        # Calculate average weights dynamically
        self.sentiment_weights = {
            sentiment: sum(scores) / len(scores) if scores else 1.0
            for sentiment, scores in sentiment_data.items()
        }
        self.logger.log_event(f"Updated sentiment weights: {self.sentiment_weights}")

    def update_scoring_data(self, model, score, query_type):
        """Update scoring data for models and query types."""
        try:
            self.scoring_data[model]["total_score"] += score
            self.scoring_data[model]["count"] += 1
            if query_type in self.query_type_scores:
                self.query_type_scores[query_type]["total_score"] += score
                self.query_type_scores[query_type]["count"] += 1
            self.logger.log_event(
                f"Updated scoring data for model: {model}, Score: {score}, Query Type: {query_type}"
            )
        except Exception as e:
            self.logger.log_error(f"Error updating scoring data: {e}")

    def save_reinforcement_model(self, file_name="reinforcement_model.keras"):
        """Save the reinforcement learning model."""
        self.reinforcement_agent.save_model(file_name)
        self.logger.log_event("Reinforcement model saved.")

    def load_reinforcement_model(self, file_name="reinforcement_model.keras"):
        """Load the reinforcement learning model."""
        self.reinforcement_agent.load_model(file_name)
        self.logger.log_event("Reinforcement model loaded.")
