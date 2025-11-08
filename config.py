"""
Configuration settings for the Master Agent Orchestration System
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class Config:
    # API Keys and External Services
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Prediction Thresholds
    PREDICTION_THRESHOLD_HIGH = 0.7  # 70% probability threshold
    PREDICTION_THRESHOLD_MEDIUM = 0.5  # 50% probability threshold

    # Priority Levels
    PRIORITY_LEVELS = {
        "P0": {"name": "Critical", "contact_method": "voice", "escalate_immediately": True},
        "P1": {"name": "High", "contact_method": "voice", "escalate_immediately": False},
        "P2": {"name": "Medium", "contact_method": "app_notification", "escalate_immediately": False},
        "P3": {"name": "Low", "contact_method": "app_notification", "escalate_immediately": False},
    }

    # Customer Engagement Settings
    SENTIMENT_THRESHOLD = 3.0  # Out of 10, below this escalates to human
    ESCALATION_SENTIMENT_THRESHOLD = float(os.getenv("ESCALATION_SENTIMENT_THRESHOLD", "3.0"))  # Escalation threshold
    MAX_RETRY_ATTEMPTS = 3
    RETRY_BACKOFF_FACTOR = 2  # Exponential backoff multiplier

    # Monitoring and Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "8000"))

    # Agent Timeouts (in seconds)
    AGENT_TIMEOUT = {
        "data_analysis": 30,
        "diagnosis": 45,
        "customer_engagement": 120,
        "scheduling": 60,
        "feedback": 30,
        "manufacturing_insights": 90,
        "ueba_monitoring": 15,
    }
    AGENT_TIMEOUT_SECONDS = int(os.getenv("AGENT_TIMEOUT_SECONDS", "60"))  # Default agent timeout

    # Database and Storage
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///automotive_ai.db")

    @classmethod
    def get_priority_config(cls, priority: str) -> Dict[str, Any]:
        """Get configuration for a specific priority level"""
        return cls.PRIORITY_LEVELS.get(priority, cls.PRIORITY_LEVELS["P3"])

    @classmethod
    def should_contact_customer(cls, prediction_probability: float, priority: str) -> bool:
        """Determine if customer should be contacted based on prediction and priority"""
        return prediction_probability >= cls.PREDICTION_THRESHOLD_HIGH and priority in ["P0", "P1"]

    @classmethod
    def should_escalate_to_human(cls, sentiment_score: float, customer_confused: bool = False) -> bool:
        """Determine if interaction should be escalated to human agent"""
        return sentiment_score < cls.SENTIMENT_THRESHOLD or customer_confused
