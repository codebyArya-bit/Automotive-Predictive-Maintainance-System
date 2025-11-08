"""
Customer Engagement Agent for Persuasive Voice/Chat Interactions

This agent handles proactive customer outreach for predicted vehicle failures,
providing persuasive communication with sentiment analysis and multi-language support.
"""

import os
import logging
from typing import Dict, List, Optional, TypedDict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import openai
from langchain_openai import ChatOpenAI

# from langchain_community.memory import ConversationBufferWindowMemory
from textblob import TextBlob

# from googletrans import Translator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversationState(TypedDict):
    """State management for multi-turn conversations"""

    customer_id: str
    vehicle_id: str
    prediction: Dict
    conversation_history: List[Dict]  # {role: 'agent'/'customer', message: str, timestamp: str}
    current_stage: str  # 'opening', 'explanation', 'objection_handling', 'closing'
    sentiment_score: float
    language: str
    escalation_needed: bool
    appointment_booked: bool
    discount_offered: bool


@dataclass
class CustomerProfile:
    """Customer profile data structure"""

    customer_id: str
    name: str
    phone: str
    preferred_language: str
    communication_style: str  # 'formal', 'casual', 'technical'
    past_interactions: List[Dict]
    vehicle_model: str
    vin_masked: str


class CustomerEngagementAgent:
    """
    Advanced Customer Engagement Agent for proactive vehicle maintenance outreach.

    Features:
    - Persuasive conversation management
    - Multi-language support (Hindi, English, Tamil, etc.)
    - Sentiment-based escalation detection
    - Objection handling with personalized responses
    - Discount eligibility and offer management
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the Customer Engagement Agent"""
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")

        # Initialize OpenAI client
        openai.api_key = self.openai_api_key
        self.llm = ChatOpenAI(model="gpt - 4", temperature=0.7, openai_api_key=self.openai_api_key)

        # Initialize translator
        # Simple translator mock (in production, use proper translation service)
        self.translator = None

        # Simple conversation memory implementation
        self.conversation_history: Dict[str, List[Dict]] = {}

        # Supported languages
        self.supported_languages = {
            "english": "en",
            "hindi": "hi",
            "tamil": "ta",
            "telugu": "te",
            "kannada": "kn",
            "marathi": "mr",
            "gujarati": "gu",
            "bengali": "bn",
        }

        # Conversation states
        self.active_conversations: Dict[str, ConversationState] = {}

        logger.info("Customer Engagement Agent initialized successfully")

    def get_customer_profile(self, customer_id: str) -> Dict:
        """Fetch customer information and preferences"""
        try:
            # Mock implementation - in production, this would query a customer database
            mock_profiles = {
                "CUST001": {
                    "customer_id": "CUST001",
                    "name": "Rajesh Kumar",
                    "phone": "+91 - 9876543210",
                    "preferred_language": "hindi",
                    "communication_style": "formal",
                    "past_interactions": [
                        {"date": "2024 - 01 - 15", "type": "service", "satisfaction": 8},
                        {"date": "2024 - 03 - 20", "type": "complaint", "resolved": True},
                    ],
                    "vehicle_model": "Maruti Swift",
                    "vin_masked": "MA3***789",
                },
                "CUST002": {
                    "customer_id": "CUST002",
                    "name": "Priya Sharma",
                    "phone": "+91 - 9123456789",
                    "preferred_language": "english",
                    "communication_style": "casual",
                    "past_interactions": [{"date": "2024 - 02 - 10", "type": "service", "satisfaction": 9}],
                    "vehicle_model": "Hyundai i20",
                    "vin_masked": "HY2***456",
                },
            }

            profile = mock_profiles.get(
                customer_id,
                {
                    "customer_id": customer_id,
                    "name": "Valued Customer",
                    "phone": "+91 - 9999999999",
                    "preferred_language": "english",
                    "communication_style": "formal",
                    "past_interactions": [],
                    "vehicle_model": "Unknown Vehicle",
                    "vin_masked": "***",
                },
            )

            # Ensure customer_id is always included
            profile["customer_id"] = customer_id

            logger.info(f"Retrieved customer profile for {customer_id}")
            return profile

        except Exception as e:
            logger.error(f"Error fetching customer profile: {str(e)}")
            return {}

    def detect_sentiment(self, customer_message: str) -> float:
        """Analyze customer sentiment on a 0 - 10 scale"""
        try:
            # Use TextBlob for sentiment analysis
            blob = TextBlob(customer_message)
            polarity = blob.sentiment.polarity  # Range: -1 to 1

            # Convert to 0 - 10 scale
            sentiment_score = (polarity + 1) * 5

            logger.info(f"Sentiment analysis: {sentiment_score:.2f}/10 for message: '{customer_message[:50]}...'")
            return round(sentiment_score, 2)

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return 5.0  # Neutral sentiment as fallback

    def translate_message(self, text: str, target_language: str) -> str:
        """Translate message to customer's preferred language"""
        try:
            if target_language.lower() == "english" or target_language == "en":
                return text

            # Mock translation for demo purposes
            # In production, use proper translation service like Google Translate API
            translations = {
                "hindi": f"[Hindi] {text}",
                "tamil": f"[Tamil] {text}",
                "telugu": f"[Telugu] {text}",
                "kannada": f"[Kannada] {text}",
                "marathi": f"[Marathi] {text}",
                "gujarati": f"[Gujarati] {text}",
                "bengali": f"[Bengali] {text}",
            }

            translated_text = translations.get(target_language.lower(), text)
            logger.info(f"Mock translated message to {target_language}")
            return translated_text

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text  # Return original text if translation fails

    def fetch_discount_eligibility(self, customer_id: str, urgency: str) -> Dict:
        """Check if customer is eligible for any discounts"""
        try:
            # Mock discount logic - in production, this would check customer history, loyalty, etc.
            discount_rules = {
                "P0": {"eligible": True, "discount_percent": 15, "reason": "Critical safety issue discount"},
                "P1": {"eligible": True, "discount_percent": 10, "reason": "Early booking discount"},
                "P2": {"eligible": True, "discount_percent": 5, "reason": "Preventive maintenance discount"},
                "P3": {"eligible": False, "discount_percent": 0, "reason": "No discount available"},
            }

            # Additional customer-specific discounts
            customer_profile = self.get_customer_profile(customer_id)
            if customer_profile.get("past_interactions"):
                # Loyalty discount for returning customers
                base_discount = discount_rules.get(
                    urgency, {"eligible": False, "discount_percent": 0, "reason": "No discount"}
                )
                if base_discount["eligible"]:
                    base_discount["discount_percent"] += 5
                    base_discount["reason"] += " + Loyalty bonus"
                else:
                    base_discount = {"eligible": True, "discount_percent": 5, "reason": "Loyalty discount"}

            result = discount_rules.get(
                urgency, {"eligible": False, "discount_percent": 0, "reason": "No discount available"}
            )
            logger.info(f"Discount eligibility for {customer_id}: {result}")
            return result

        except Exception as e:
            logger.error(f"Error checking discount eligibility: {str(e)}")
            return {"eligible": False, "discount_percent": 0, "reason": "Error checking eligibility"}

    def initialize_conversation(self, customer_id: str, vehicle_id: str, prediction: Dict) -> ConversationState:
        """Initialize a new conversation state"""
        conversation_state = ConversationState(
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            prediction=prediction,
            conversation_history=[],
            current_stage="opening",
            sentiment_score=7.0,  # Start with positive assumption
            language="english",
            escalation_needed=False,
            appointment_booked=False,
            discount_offered=False,
        )

        self.active_conversations[customer_id] = conversation_state
        logger.info(f"Initialized conversation for customer {customer_id}")
        return conversation_state

    def get_opening_message(self, customer_profile: CustomerProfile, prediction: Dict) -> str:
        """Generate personalized opening message"""
        # Determine time of day greeting
        current_hour = datetime.now().hour
        if current_hour < 12:
            greeting_time = "morning"
        elif current_hour < 17:
            greeting_time = "afternoon"
        else:
            greeting_time = "evening"

        # Format the opening message
        opening_msg = f"Namaste! Good {greeting_time}, {customer_profile.name}. This is Aarti calling from AutoCare Plus. I hope you're doing well! I'm reaching out about your {customer_profile.vehicle_model}. Do you have 2 minutes to discuss something important about your vehicle's health?"

        # Translate if needed
        if customer_profile.preferred_language != "english":
            opening_msg = self.translate_message(opening_msg, customer_profile.preferred_language)

        return opening_msg

    def explain_issue(self, prediction: Dict, customer_profile: CustomerProfile) -> str:
        """Explain the predicted failure in simple, non-technical terms"""
        component = prediction.get("component", "component")
        probability = prediction.get("probability", 0)
        days_to_failure = prediction.get("days_to_failure", 7)
        priority = prediction.get("priority", "P2")

        # Adjust tone based on urgency
        if priority == "P0":
            urgency_tone = "This is quite urgent and affects your safety"
        elif priority == "P1":
            urgency_tone = "This needs attention soon to prevent inconvenience"
        else:
            urgency_tone = "This is a great opportunity for preventive care"

        explanation = f"""Thank you! So, our smart monitoring system in your car has been tracking its health 24 / 7, and we've noticed that your {component} is showing signs of wear. The sensors indicate it might fail within the next {days_to_failure} days with {probability}% probability.

{urgency_tone}. This is actually quite common after regular use, and the good news is we caught it early! This means we can replace it before you're left stranded or face any inconvenience.

Our certified technicians can fix this quickly, and we'll make sure your {customer_profile.vehicle_model} runs smoothly for years to come."""

        # Translate if needed
        if customer_profile.preferred_language != "english":
            explanation = self.translate_message(explanation, customer_profile.preferred_language)

        return explanation

    def handle_objection(self, objection_type: str, customer_profile: CustomerProfile, prediction: Dict) -> str:
        """Handle common customer objections with persuasive responses"""
        objection_responses = {
            "no_problems": """That's very common! {component} failures often happen suddenly without warning. You might notice slightly slower performance, but the real risk is it failing completely when you need your car most—like during an emergency or when you're rushing to work. Our predictive system caught this early to save you from that stress!""",
            "too_busy": """I completely understand—we're all busy! That's exactly why we're calling proactively. If we schedule service now, it takes just 1.5 hours at your convenience. But if the {component} fails unexpectedly, you'll lose hours waiting for a tow truck and dealing with the emergency. Which would you prefer?""",
            "too_expensive": """I understand cost is a concern. Let me break it down: The {component} replacement is ₹{cost} today. But if it fails suddenly, you're looking at ₹{cost} plus ₹2,000-₹3,000 for emergency towing. Plus the stress and lost time. So proactive service actually saves you money! Plus, I can offer you a {discount}% discount if you book within 24 hours.""",
            "diy_local": """Absolutely, you're welcome to! Just a couple of things to consider: Our service includes a 2-year warranty on parts and labor, and our technicians are factory-trained specifically for your {vehicle_model}. Plus, we've already identified the exact issue, so there's no diagnostic guesswork. But it's totally your choice—I just want to make sure you have all the information!""",
            "need_time": """Of course! Take all the time you need. I'll send you all the diagnostic details via SMS and our mobile app. You can review everything at your convenience and book whenever you're ready. Would you like me to follow up with you in a couple of days just as a friendly reminder?""",
        }

        # Get component and cost info
        component = prediction.get("component", "component")
        estimated_cost = prediction.get("estimated_cost", 6500)

        # Check discount eligibility
        discount_info = self.fetch_discount_eligibility(customer_profile.customer_id, prediction.get("priority", "P2"))
        discount_percent = discount_info.get("discount_percent", 0)

        # Format response
        response = objection_responses.get(objection_type, objection_responses["need_time"])
        response = response.format(
            component=component,
            cost=estimated_cost,
            discount=discount_percent,
            vehicle_model=customer_profile.vehicle_model,
        )

        # Translate if needed
        if customer_profile.preferred_language != "english":
            response = self.translate_message(response, customer_profile.preferred_language)

        return response

    def generate_closing_message(
        self, outcome: str, customer_profile: CustomerProfile, appointment_details: Dict = None
    ) -> str:
        """Generate appropriate closing message based on conversation outcome"""
        if outcome == "booked":
            closing = f"""Perfect! I've scheduled your appointment for {appointment_details.get('date')} at {appointment_details.get('time')} at our {appointment_details.get('service_center', 'nearest service center')}.

You'll receive a confirmation SMS and app notification with all the details. We'll also send a reminder 24 hours before. Thank you for trusting us with your vehicle's care, {customer_profile.name}. Have a wonderful day!"""

        elif outcome == "declined":
            closing = f"""I understand, {customer_profile.name}. No pressure at all! I've sent the diagnostic report to your mobile app so you can review it. If you change your mind, you can book directly through the app or call us anytime at 1800-AUTO-CARE.

Would you like me to follow up with you in a few days?"""

        else:  # pending/undecided
            closing = f"""No worries—take your time to think about it, {customer_profile.name}. I'll send you all the details via SMS and app notification. You can book whenever you're ready. Should I follow up with you in 2 - 3 days just as a friendly reminder?"""

        # Translate if needed
        if customer_profile.preferred_language != "english":
            closing = self.translate_message(closing, customer_profile.preferred_language)

        return closing

    def check_escalation_needed(self, sentiment_score: float, conversation_history: List[Dict]) -> bool:
        """Determine if conversation needs human escalation"""
        # Escalate if sentiment is very low
        if sentiment_score < 3.0:
            return True

        # Escalate if customer has been frustrated for multiple turns
        recent_messages = conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history
        low_sentiment_count = sum(1 for msg in recent_messages if msg.get("sentiment", 5) < 4)

        if low_sentiment_count >= 2:
            return True

        # Check for escalation keywords
        escalation_keywords = ["manager", "supervisor", "complaint", "angry", "frustrated", "legal", "lawyer"]
        recent_customer_messages = [msg["message"].lower() for msg in recent_messages if msg["role"] == "customer"]

        for message in recent_customer_messages:
            if any(keyword in message for keyword in escalation_keywords):
                return True

        return False

    def process_customer_response(self, customer_id: str, customer_message: str) -> Dict[str, Any]:
        """Process customer response and generate appropriate agent reply"""
        try:
            # Get conversation state
            conversation_state = self.active_conversations.get(customer_id)
            if not conversation_state:
                return {"error": "No active conversation found"}

            # Analyze sentiment
            sentiment_score = self.detect_sentiment(customer_message)
            conversation_state["sentiment_score"] = sentiment_score

            # Add customer message to history
            conversation_state["conversation_history"].append(
                {
                    "role": "customer",
                    "message": customer_message,
                    "timestamp": datetime.now().isoformat(),
                    "sentiment": sentiment_score,
                }
            )

            # Check for escalation
            if self.check_escalation_needed(sentiment_score, conversation_state["conversation_history"]):
                conversation_state["escalation_needed"] = True
                escalation_message = "I'm sorry if I've caused any frustration—that wasn't my intention. Let me connect you with one of our senior advisors who can address your concerns better. Please hold for just a moment."

                # Translate if needed
                customer_profile = self.get_customer_profile(customer_id)
                if customer_profile.get("preferred_language", "english") != "english":
                    escalation_message = self.translate_message(
                        escalation_message, customer_profile["preferred_language"]
                    )

                return {
                    "agent_response": escalation_message,
                    "escalation_needed": True,
                    "conversation_state": conversation_state,
                    "sentiment_score": sentiment_score,
                }

            # Generate contextual response based on current stage and customer input
            customer_profile_data = self.get_customer_profile(customer_id)
            customer_profile = CustomerProfile(**customer_profile_data)

            # Determine response based on conversation stage and customer input
            agent_response = self._generate_contextual_response(customer_message, conversation_state, customer_profile)

            # Add agent response to history
            conversation_state["conversation_history"].append(
                {"role": "agent", "message": agent_response, "timestamp": datetime.now().isoformat()}
            )

            return {
                "agent_response": agent_response,
                "escalation_needed": False,
                "conversation_state": conversation_state,
                "sentiment_score": sentiment_score,
            }

        except Exception as e:
            logger.error(f"Error processing customer response: {str(e)}")
            return {"error": f"Processing error: {str(e)}"}

    def _generate_contextual_response(
        self, customer_message: str, conversation_state: ConversationState, customer_profile: CustomerProfile
    ) -> str:
        """Generate contextual response based on conversation flow"""
        current_stage = conversation_state["current_stage"]
        customer_message_lower = customer_message.lower()

        # Detect customer intent
        if any(word in customer_message_lower for word in ["yes", "okay", "sure", "go ahead", "tell me"]):
            if current_stage == "opening":
                conversation_state["current_stage"] = "explanation"
                return self.explain_issue(conversation_state["prediction"], customer_profile)
            elif current_stage == "explanation":
                conversation_state["current_stage"] = "closing"
                return "Great! Would you like to schedule the service? I can check our available slots for you."

        elif any(word in customer_message_lower for word in ["no", "not interested", "busy", "later"]):
            if current_stage == "opening":
                return "I understand you're busy. This will just take a minute and could save you from a roadside breakdown. May I quickly explain what we found?"
            else:
                conversation_state["current_stage"] = "objection_handling"
                return self._handle_specific_objection(
                    customer_message_lower, customer_profile, conversation_state["prediction"]
                )

        elif any(word in customer_message_lower for word in ["expensive", "cost", "money", "price"]):
            conversation_state["current_stage"] = "objection_handling"
            return self.handle_objection("too_expensive", customer_profile, conversation_state["prediction"])

        elif any(word in customer_message_lower for word in ["book", "schedule", "appointment", "when"]):
            conversation_state["current_stage"] = "closing"
            conversation_state["appointment_booked"] = True
            appointment_details = {
                "date": "tomorrow",
                "time": "10:00 AM",
                "service_center": "AutoCare Plus - Main Branch",
            }
            return self.generate_closing_message("booked", customer_profile, appointment_details)

        else:
            # Default contextual response
            return "I understand your concern. Let me address that for you. Our goal is to keep you safe and prevent any inconvenience. What specific aspect would you like me to explain further?"

    def _handle_specific_objection(
        self, customer_message: str, customer_profile: CustomerProfile, prediction: Dict
    ) -> str:
        """Handle specific objections based on customer message content"""
        if "busy" in customer_message or "time" in customer_message:
            return self.handle_objection("too_busy", customer_profile, prediction)
        elif "problem" in customer_message or "fine" in customer_message:
            return self.handle_objection("no_problems", customer_profile, prediction)
        elif "myself" in customer_message or "local" in customer_message:
            return self.handle_objection("diy_local", customer_profile, prediction)
        else:
            return self.handle_objection("need_time", customer_profile, prediction)

    def start_conversation(self, customer_id: str, vehicle_id: str, prediction: Dict) -> Dict[str, Any]:
        """Start a new customer engagement conversation"""
        try:
            # Initialize conversation state
            conversation_state = self.initialize_conversation(customer_id, vehicle_id, prediction)

            # Get customer profile
            customer_profile_data = self.get_customer_profile(customer_id)
            customer_profile = CustomerProfile(**customer_profile_data)

            # Set language preference
            conversation_state["language"] = customer_profile.preferred_language

            # Generate opening message
            opening_message = self.get_opening_message(customer_profile, prediction)

            # Add to conversation history
            conversation_state["conversation_history"].append(
                {"role": "agent", "message": opening_message, "timestamp": datetime.now().isoformat()}
            )

            logger.info(f"Started conversation with customer {customer_id}")

            return {
                "success": True,
                "opening_message": opening_message,
                "conversation_state": conversation_state,
                "customer_profile": asdict(customer_profile),
            }

        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_conversation_summary(self, customer_id: str) -> Dict[str, Any]:
        """Get summary of conversation for reporting"""
        conversation_state = self.active_conversations.get(customer_id)
        if not conversation_state:
            return {"error": "No conversation found"}

        return {
            "customer_id": customer_id,
            "conversation_duration": len(conversation_state["conversation_history"]),
            "final_sentiment": conversation_state["sentiment_score"],
            "outcome": "booked" if conversation_state["appointment_booked"] else "pending",
            "escalated": conversation_state["escalation_needed"],
            "language": conversation_state["language"],
            "discount_offered": conversation_state["discount_offered"],
        }
