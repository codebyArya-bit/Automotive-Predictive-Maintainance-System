"""
Feedback Agent - Collects customer satisfaction and improvement suggestions
"""

import asyncio
import random
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent
from state import State, Priority


class FeedbackAgent(BaseAgent):
    """Agent responsible for collecting customer feedback and satisfaction"""

    def __init__(self):
        super().__init__("feedback")

        # Feedback questions based on interaction type
        self.feedback_questions = {
            "service_scheduled": [
                "How satisfied are you with the scheduling process?",
                "Was the recommended service timeline appropriate?",
                "How clear was the communication about the issue?",
                "Would you recommend our predictive maintenance service?",
            ],
            "service_declined": [
                "What prevented you from scheduling service today?",
                "How can we improve our maintenance recommendations?",
                "What information would help you make better decisions?",
                "How satisfied are you with our communication?",
            ],
            "information_request": [
                "Did we provide the information you needed?",
                "How satisfied are you with our response time?",
                "Was the technical explanation clear and helpful?",
                "What additional information would be useful?",
            ],
            "escalated": [
                "How satisfied are you with the overall experience?",
                "What could we have done differently?",
                "Would you use our predictive maintenance service again?",
                "Any suggestions for improvement?",
            ],
        }

        # Common improvement suggestions based on feedback patterns
        self.improvement_suggestions = [
            "Provide more detailed cost estimates upfront",
            "Offer more flexible scheduling options",
            "Improve technical explanations for customers",
            "Add video explanations of vehicle issues",
            "Provide alternative service locations",
            "Offer payment plan options for expensive repairs",
            "Send follow-up reminders about scheduled appointments",
            "Provide DIY maintenance tips for minor issues",
            "Improve mobile app notification system",
            "Add live chat support for immediate questions",
        ]

    async def _execute_internal(self, state: State) -> State:
        """Collect customer feedback and satisfaction"""
        self.logger.info("Starting feedback collection", vehicle_id=state["vehicle_id"])

        # Determine feedback type based on workflow outcome
        feedback_type = self._determine_feedback_type(state)

        # Collect satisfaction rating
        satisfaction_score = await self._collect_satisfaction_rating(state, feedback_type)

        # Collect specific feedback
        feedback_responses = await self._collect_detailed_feedback(state, feedback_type)

        # Generate improvement suggestions
        suggestions = self._generate_improvement_suggestions(satisfaction_score, feedback_responses, state)

        # Update state with feedback
        state["customer_satisfaction"] = satisfaction_score
        state["feedback_collected"] = True
        state["improvement_suggestions"] = suggestions

        # Add log messages
        state = self._add_log_message(
            state,
            f"Feedback collected - Satisfaction: {satisfaction_score:.1f}/10",
            {
                "satisfaction_score": satisfaction_score,
                "feedback_type": feedback_type,
                "suggestions_count": len(suggestions),
            },
        )

        return state

    def _determine_feedback_type(self, state: State) -> str:
        """Determine type of feedback to collect based on workflow outcome"""
        if state.get("appointment"):
            return "service_scheduled"
        elif state.get("escalate_to_human"):
            return "escalated"
        elif state.get("customer_response") and state["customer_response"]["intent"] == "decline_service":
            return "service_declined"
        else:
            return "information_request"

    async def _collect_satisfaction_rating(self, state: State, feedback_type: str) -> float:
        """Collect overall satisfaction rating from customer"""
        # Simulate feedback collection delay
        await asyncio.sleep(0.5)

        # Base satisfaction influenced by various factors
        base_satisfaction = 7.0  # Start with neutral-positive

        # Adjust based on customer response sentiment
        if state.get("customer_response"):
            sentiment = state["customer_response"]["sentiment_score"]
            # Convert sentiment (1 - 10) to satisfaction adjustment (-2 to +2)
            sentiment_adjustment = (sentiment - 5.5) * 0.4
            base_satisfaction += sentiment_adjustment

        # Adjust based on prediction accuracy and priority handling
        if state.get("prediction"):
            priority = state["prediction"]["priority"]
            if priority == Priority.P0 and state.get("appointment"):
                base_satisfaction += 1.0  # Good handling of critical issue
            elif priority == Priority.P3 and not state.get("appointment"):
                base_satisfaction += 0.5  # Appropriate handling of low priority

        # Adjust based on whether service was scheduled
        if feedback_type == "service_scheduled":
            base_satisfaction += random.uniform(0.5, 1.5)
        elif feedback_type == "service_declined":
            base_satisfaction -= random.uniform(0.5, 1.0)
        elif feedback_type == "escalated":
            base_satisfaction -= random.uniform(1.0, 2.0)

        # Add some randomness
        base_satisfaction += random.uniform(-0.8, 0.8)

        # Ensure score is within valid range
        return max(1.0, min(10.0, base_satisfaction))

    async def _collect_detailed_feedback(self, state: State, feedback_type: str) -> List[Dict[str, Any]]:
        """Collect detailed feedback responses"""
        # Simulate feedback collection
        await asyncio.sleep(0.3)

        questions = self.feedback_questions[feedback_type]
        responses = []

        for question in questions:
            # Simulate customer response to each question
            response_score = random.uniform(1, 10)
            response_text = self._generate_response_text(question, response_score, state)

            responses.append(
                {
                    "question": question,
                    "score": response_score,
                    "response": response_text,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return responses

    def _generate_response_text(self, question: str, score: float, state: State) -> str:
        """Generate realistic response text based on score and context"""
        if score >= 8.0:
            positive_responses = [
                "Very satisfied with the service.",
                "Excellent communication and professionalism.",
                "The process was smooth and efficient.",
                "I appreciate the proactive approach.",
                "Great job explaining the technical details.",
            ]
            return random.choice(positive_responses)

        elif score >= 6.0:
            neutral_responses = [
                "The service was adequate.",
                "Generally satisfied but room for improvement.",
                "Process was okay, could be faster.",
                "Information was helpful but could be clearer.",
                "Decent experience overall.",
            ]
            return random.choice(neutral_responses)

        else:
            negative_responses = [
                "Not satisfied with the experience.",
                "Communication could be much better.",
                "Process was confusing and slow.",
                "I expected better service quality.",
                "Technical explanations were unclear.",
            ]
            return random.choice(negative_responses)

    def _generate_improvement_suggestions(
        self, satisfaction_score: float, feedback_responses: List[Dict[str, Any]], state: State
    ) -> List[str]:
        """Generate improvement suggestions based on feedback"""
        suggestions = []

        # Add suggestions based on satisfaction score
        if satisfaction_score < 6.0:
            suggestions.extend(
                [
                    "Improve overall customer communication",
                    "Enhance technical explanation clarity",
                    "Reduce response time for customer inquiries",
                ]
            )

        # Add suggestions based on specific feedback
        low_scoring_responses = [r for r in feedback_responses if r["score"] < 6.0]

        for response in low_scoring_responses:
            question = response["question"].lower()

            if "scheduling" in question:
                suggestions.append("Provide more flexible scheduling options")
            elif "communication" in question or "clear" in question:
                suggestions.append("Improve technical explanations for customers")
            elif "timeline" in question:
                suggestions.append("Better explain service urgency and timelines")
            elif "cost" in question or "information" in question:
                suggestions.append("Provide more detailed cost estimates upfront")

        # Add context-specific suggestions
        if state.get("customer_response"):
            intent = state["customer_response"]["intent"]

            if intent == "decline_service":
                suggestions.append("Offer payment plan options for expensive repairs")
            elif intent == "need_clarification":
                suggestions.append("Add video explanations of vehicle issues")
            elif intent == "request_cost_estimate":
                suggestions.append("Provide instant cost estimates in app")

        # Add random suggestions from common improvements
        if len(suggestions) < 3:
            additional_suggestions = random.sample(
                self.improvement_suggestions, min(3 - len(suggestions), len(self.improvement_suggestions))
            )
            suggestions.extend(additional_suggestions)

        # Remove duplicates and limit to top 5
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:5]
