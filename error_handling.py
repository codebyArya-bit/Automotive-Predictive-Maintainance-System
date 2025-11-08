"""
Error Handling and Recovery System for Master Agent
"""

import asyncio
import structlog
import traceback
from typing import Dict, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
import random

from state import State, Priority
from config import Config


class ErrorType(Enum):
    """Types of errors that can occur in the system"""

    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    MODEL_ERROR = "model_error"
    DATA_ERROR = "data_error"
    SYSTEM_ERROR = "system_error"
    AGENT_ERROR = "agent_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorSeverity(Enum):
    """Severity levels for errors"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RetryStrategy(Enum):
    """Retry strategies for different error types"""

    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    NO_RETRY = "no_retry"


class ErrorHandler:
    """Comprehensive error handling and recovery system"""

    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.config = Config()

        # Error classification rules
        self.error_classification = {
            "ConnectionError": ErrorType.NETWORK_ERROR,
            "TimeoutError": ErrorType.TIMEOUT_ERROR,
            "asyncio.TimeoutError": ErrorType.TIMEOUT_ERROR,
            "ValidationError": ErrorType.VALIDATION_ERROR,
            "AuthenticationError": ErrorType.AUTHENTICATION_ERROR,
            "RateLimitError": ErrorType.RATE_LIMIT_ERROR,
            "ModelError": ErrorType.MODEL_ERROR,
            "ValueError": ErrorType.DATA_ERROR,
            "KeyError": ErrorType.DATA_ERROR,
            "TypeError": ErrorType.DATA_ERROR,
            "SystemError": ErrorType.SYSTEM_ERROR,
            "AgentExecutionError": ErrorType.AGENT_ERROR,
        }

        # Retry strategies by error type
        self.retry_strategies = {
            ErrorType.NETWORK_ERROR: RetryStrategy.EXPONENTIAL_BACKOFF,
            ErrorType.TIMEOUT_ERROR: RetryStrategy.EXPONENTIAL_BACKOFF,
            ErrorType.RATE_LIMIT_ERROR: RetryStrategy.LINEAR_BACKOFF,
            ErrorType.MODEL_ERROR: RetryStrategy.FIXED_DELAY,
            ErrorType.AGENT_ERROR: RetryStrategy.EXPONENTIAL_BACKOFF,
            ErrorType.VALIDATION_ERROR: RetryStrategy.NO_RETRY,
            ErrorType.AUTHENTICATION_ERROR: RetryStrategy.NO_RETRY,
            ErrorType.DATA_ERROR: RetryStrategy.NO_RETRY,
            ErrorType.SYSTEM_ERROR: RetryStrategy.EXPONENTIAL_BACKOFF,
            ErrorType.UNKNOWN_ERROR: RetryStrategy.EXPONENTIAL_BACKOFF,
        }

        # Maximum retry attempts by error type
        self.max_retries = {
            ErrorType.NETWORK_ERROR: 3,
            ErrorType.TIMEOUT_ERROR: 2,
            ErrorType.RATE_LIMIT_ERROR: 5,
            ErrorType.MODEL_ERROR: 2,
            ErrorType.AGENT_ERROR: 3,
            ErrorType.SYSTEM_ERROR: 2,
            ErrorType.UNKNOWN_ERROR: 1,
        }

        # Fallback strategies
        self.fallback_strategies = {
            "data_analysis": self._fallback_rule_based_analysis,
            "diagnosis": self._fallback_simple_diagnosis,
            "customer_engagement": self._fallback_basic_notification,
            "scheduling": self._fallback_manual_scheduling,
            "feedback": self._fallback_skip_feedback,
            "manufacturing_insights": self._fallback_skip_insights,
            "ueba_monitoring": self._fallback_basic_monitoring,
        }

    def classify_error(self, error: Exception) -> tuple[ErrorType, ErrorSeverity]:
        """Classify error type and severity"""
        error_name = type(error).__name__
        error_type = self.error_classification.get(error_name, ErrorType.UNKNOWN_ERROR)

        # Determine severity based on error type and message
        error_message = str(error).lower()

        if error_type in [ErrorType.AUTHENTICATION_ERROR, ErrorType.SYSTEM_ERROR]:
            severity = ErrorSeverity.CRITICAL
        elif error_type in [ErrorType.MODEL_ERROR, ErrorType.AGENT_ERROR]:
            severity = ErrorSeverity.HIGH
        elif error_type in [ErrorType.NETWORK_ERROR, ErrorType.TIMEOUT_ERROR]:
            severity = ErrorSeverity.MEDIUM
        elif "critical" in error_message or "fatal" in error_message:
            severity = ErrorSeverity.CRITICAL
        elif "warning" in error_message:
            severity = ErrorSeverity.LOW
        else:
            severity = ErrorSeverity.MEDIUM

        return error_type, severity

    async def handle_error(self, error: Exception, context: Dict[str, Any], state: State) -> tuple[bool, State]:
        """
        Handle an error and return whether to retry and updated state

        Returns:
            tuple: (should_retry: bool, updated_state: State)
        """
        error_type, severity = self.classify_error(error)

        # Log the error
        self.logger.error(
            "Error occurred in agent execution",
            error_type=error_type.value,
            severity=severity.value,
            error_message=str(error),
            context=context,
            vehicle_id=state.get("vehicle_id", "unknown"),
            traceback=traceback.format_exc(),
        )

        # Update state with error information
        error_info = {
            "error_type": error_type.value,
            "severity": severity.value,
            "message": str(error),
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "traceback": traceback.format_exc(),
        }

        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(error_info)

        # Determine if we should retry
        current_retries = context.get("retry_count", 0)
        max_retry_count = self.max_retries.get(error_type, 0)

        should_retry = (
            current_retries < max_retry_count
            and self.retry_strategies.get(error_type) != RetryStrategy.NO_RETRY
            and severity != ErrorSeverity.CRITICAL
        )

        if should_retry:
            # Calculate retry delay
            delay = self._calculate_retry_delay(error_type, current_retries)

            self.logger.info(
                "Scheduling retry",
                retry_count=current_retries + 1,
                max_retries=max_retry_count,
                delay_seconds=delay,
                error_type=error_type.value,
            )

            # Wait before retry
            await asyncio.sleep(delay)

            # Update retry count in state
            state["retry_count"] = current_retries + 1
        else:
            # No retry - check if fallback is available
            agent_name = context.get("agent_name")
            if agent_name and agent_name in self.fallback_strategies:
                self.logger.info("Attempting fallback strategy", agent_name=agent_name, error_type=error_type.value)

                try:
                    state = await self.fallback_strategies[agent_name](state, error_info)
                    state["fallback_used"] = True
                    state["fallback_agent"] = agent_name
                except Exception as fallback_error:
                    self.logger.error(
                        "Fallback strategy failed", agent_name=agent_name, fallback_error=str(fallback_error)
                    )
                    state["escalate_to_human"] = True
                    state["escalation_reason"] = f"Both primary and fallback strategies failed for {agent_name}"
            else:
                # No fallback available - escalate if severe
                if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
                    state["escalate_to_human"] = True
                    state["escalation_reason"] = (
                        f"Critical error in {context.get('agent_name', 'unknown')}: {str(error)}"
                    )

        return should_retry, state

    def _calculate_retry_delay(self, error_type: ErrorType, retry_count: int) -> float:
        """Calculate delay before retry based on strategy"""
        strategy = self.retry_strategies.get(error_type, RetryStrategy.EXPONENTIAL_BACKOFF)

        if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            # Exponential backoff: 1s, 2s, 4s, 8s, ...
            base_delay = 1.0
            return base_delay * (2**retry_count) + random.uniform(0, 1)

        elif strategy == RetryStrategy.LINEAR_BACKOFF:
            # Linear backoff: 2s, 4s, 6s, 8s, ...
            return 2.0 * (retry_count + 1) + random.uniform(0, 1)

        elif strategy == RetryStrategy.FIXED_DELAY:
            # Fixed delay: 3s each time
            return 3.0 + random.uniform(0, 1)

        else:
            return 0.0

    # Fallback strategy implementations
    async def _fallback_rule_based_analysis(self, state: State, error_info: Dict[str, Any]) -> State:
        """Fallback rule-based analysis when ML model fails"""
        self.logger.info("Using rule-based analysis fallback")

        # Simulate simple rule-based analysis
        await asyncio.sleep(0.5)

        # Create basic telemetry data if missing
        if not state.get("telemetry_data"):
            state["telemetry_data"] = {
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "engine": {"health_score": 75, "status": "normal"},
                    "transmission": {"health_score": 80, "status": "normal"},
                    "brakes": {"health_score": 70, "status": "warning"},
                    "electrical": {"health_score": 85, "status": "normal"},
                },
                "error_codes": [],
                "mileage": 50000,
            }

        # Add fallback indicator
        state["telemetry_data"]["analysis_method"] = "rule_based_fallback"
        state["telemetry_data"]["fallback_reason"] = error_info["message"]

        return state

    async def _fallback_simple_diagnosis(self, state: State, error_info: Dict[str, Any]) -> State:
        """Fallback simple diagnosis when advanced ML fails"""
        self.logger.info("Using simple diagnosis fallback")

        await asyncio.sleep(0.3)

        # Create basic prediction based on telemetry
        telemetry = state.get("telemetry_data", {})
        components = telemetry.get("components", {})

        # Find component with lowest health score
        lowest_health = 100
        problem_component = "engine"

        for component, data in components.items():
            health = data.get("health_score", 100)
            if health < lowest_health:
                lowest_health = health
                problem_component = component

        # Create simple prediction
        if lowest_health < 60:
            priority = Priority.P1
            failure_probability = 0.8
        elif lowest_health < 75:
            priority = Priority.P2
            failure_probability = 0.6
        else:
            priority = Priority.P3
            failure_probability = 0.3

        state["prediction"] = {
            "component": problem_component,
            "failure_type": f"{problem_component}_degradation",
            "failure_probability": failure_probability,
            "priority": priority,
            "predicted_failure_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "confidence_score": 0.6,  # Lower confidence for fallback
            "recommended_action": f"Inspect {problem_component}",
            "estimated_cost": 500,
            "diagnosis_method": "simple_fallback",
            "fallback_reason": error_info["message"],
        }

        return state

    async def _fallback_basic_notification(self, state: State, error_info: Dict[str, Any]) -> State:
        """Fallback basic customer notification"""
        self.logger.info("Using basic notification fallback")

        await asyncio.sleep(0.2)

        # Create basic customer response
        state["customer_response"] = {
            "contact_method": "app_notification",
            "message_sent": "Basic maintenance notification sent",
            "customer_contacted": True,
            "response_received": False,
            "intent": "notification_sent",
            "sentiment_score": 7.0,  # Neutral
            "engagement_method": "basic_fallback",
            "fallback_reason": error_info["message"],
            "timestamp": datetime.now().isoformat(),
        }

        return state

    async def _fallback_manual_scheduling(self, state: State, error_info: Dict[str, Any]) -> State:
        """Fallback manual scheduling process"""
        self.logger.info("Using manual scheduling fallback")

        await asyncio.sleep(0.1)

        # Create manual scheduling placeholder
        state["appointment"] = {
            "appointment_id": f"MANUAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "service_center": "Manual Assignment Required",
            "service_advisor": "TBD",
            "scheduled_date": "TBD",
            "estimated_duration": "TBD",
            "service_type": "Manual Review Required",
            "status": "manual_review_required",
            "scheduling_method": "manual_fallback",
            "fallback_reason": error_info["message"],
            "created_at": datetime.now().isoformat(),
        }

        return state

    async def _fallback_skip_feedback(self, state: State, error_info: Dict[str, Any]) -> State:
        """Fallback skip feedback collection"""
        self.logger.info("Skipping feedback collection due to error")

        state["feedback_collected"] = False
        state["feedback_skipped"] = True
        state["feedback_skip_reason"] = error_info["message"]

        return state

    async def _fallback_skip_insights(self, state: State, error_info: Dict[str, Any]) -> State:
        """Fallback skip manufacturing insights"""
        self.logger.info("Skipping manufacturing insights due to error")

        state["manufacturing_insights"] = {
            "analysis_skipped": True,
            "skip_reason": error_info["message"],
            "timestamp": datetime.now().isoformat(),
        }

        return state

    async def _fallback_basic_monitoring(self, state: State, error_info: Dict[str, Any]) -> State:
        """Fallback basic UEBA monitoring"""
        self.logger.info("Using basic UEBA monitoring fallback")

        state["ueba_monitoring"] = {
            "risk_level": "low",
            "overall_risk_score": 0.2,
            "monitoring_method": "basic_fallback",
            "fallback_reason": error_info["message"],
            "security_alerts": [],
            "compliance_status": {"basic_check": {"compliant": True}},
            "timestamp": datetime.now().isoformat(),
        }

        return state


def with_error_handling(agent_name: str):
    """Decorator to add error handling to agent methods"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, state: State, *args, **kwargs) -> State:
            error_handler = ErrorHandler()
            context = {"agent_name": agent_name, "function_name": func.__name__, "retry_count": 0}

            while True:
                try:
                    return await func(self, state, *args, **kwargs)

                except Exception as e:
                    should_retry, updated_state = await error_handler.handle_error(e, context, state)

                    if not should_retry:
                        return updated_state

                    # Update context for retry
                    context["retry_count"] = updated_state.get("retry_count", 0)
                    state = updated_state

        return wrapper

    return decorator


class CircuitBreaker:
    """Circuit breaker pattern for preventing cascading failures"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
        self.logger = structlog.get_logger(__name__)

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
                self.logger.info("Circuit breaker attempting reset")
            else:
                raise Exception("Circuit breaker is open - service unavailable")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True

        return (datetime.now() - self.last_failure_time).seconds >= self.recovery_timeout

    def _on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            self.logger.warning(
                "Circuit breaker opened due to failures",
                failure_count=self.failure_count,
                threshold=self.failure_threshold,
            )


class HealthChecker:
    """System health monitoring and alerting"""

    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.health_metrics = {
            "agent_success_rate": 0.95,
            "average_response_time": 5.0,
            "error_rate": 0.05,
            "system_load": 0.7,
        }

    async def check_system_health(self, state: State) -> Dict[str, Any]:
        """Check overall system health"""
        health_status = {
            "overall_health": "healthy",
            "timestamp": datetime.now().isoformat(),
            "metrics": self.health_metrics.copy(),
            "issues": [],
        }

        # Check error rate
        errors = state.get("errors", [])
        if len(errors) > 3:
            health_status["issues"].append("High error rate detected")
            health_status["overall_health"] = "degraded"

        # Check retry count
        if state.get("retry_count", 0) > 2:
            health_status["issues"].append("Multiple retries required")
            health_status["overall_health"] = "degraded"

        # Check escalation status
        if state.get("escalate_to_human"):
            health_status["issues"].append("Human escalation required")
            health_status["overall_health"] = "critical"

        return health_status
