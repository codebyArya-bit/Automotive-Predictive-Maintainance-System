"""
Configuration and Error Handling for Data Analysis Agent
Provides centralized configuration and robust error handling utilities
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import traceback
from datetime import datetime


class ErrorSeverity(Enum):
    """Error severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalysisMode(Enum):
    """Analysis execution modes"""

    FULL = "full"  # Full LangChain agent with all tools
    DIRECT = "direct"  # Direct tool execution without LLM
    BASIC = "basic"  # Basic analysis with minimal processing
    FALLBACK = "fallback"  # Emergency fallback mode


@dataclass
class DatabaseConfig:
    """Database connection configuration"""

    host: str = "localhost"
    port: int = 5432
    database: str = "automotive_ai"
    user: str = "postgres"
    password: str = "password"
    connection_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create configuration from environment variables"""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "automotive_ai"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            connection_timeout=int(os.getenv("DB_TIMEOUT", "30")),
            max_retries=int(os.getenv("DB_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("DB_RETRY_DELAY", "1.0")),
        )


@dataclass
class DataQualityConfig:
    """Data quality validation configuration"""

    min_data_quality_score: float = 0.8
    max_missing_percentage: float = 20.0
    min_data_points: int = 100
    min_time_span_hours: int = 24
    sensor_ranges: Dict[str, tuple] = None
    required_fields: List[str] = None

    def __post_init__(self):
        if self.sensor_ranges is None:
            self.sensor_ranges = {
                "engine_rpm": (0, 8000),
                "coolant_temp": (-40, 150),
                "battery_voltage": (10.0, 16.0),
                "oil_pressure": (0, 100),
                "brake_pad_thickness": (0, 15),
                "tire_pressure_fl": (15, 50),
                "tire_pressure_fr": (15, 50),
                "tire_pressure_rl": (15, 50),
                "tire_pressure_rr": (15, 50),
                "transmission_fluid_level": (0.0, 1.0),
                "mileage": (0, 1000000),
            }

        if self.required_fields is None:
            self.required_fields = ["timestamp", "vehicle_id", "engine_rpm", "coolant_temp", "battery_voltage"]


@dataclass
class FeatureEngineeringConfig:
    """Feature engineering configuration"""

    rolling_windows: Dict[str, int] = None
    trend_window: int = 24
    volatility_window: int = 168
    correlation_threshold: float = 0.7
    anomaly_threshold: float = 2.0

    def __post_init__(self):
        if self.rolling_windows is None:
            self.rolling_windows = {"7d": 168, "30d": 720}  # 7 days * 24 hours  # 30 days * 24 hours


@dataclass
class AgentConfig:
    """Main agent configuration"""

    analysis_mode: AnalysisMode = AnalysisMode.FULL
    openai_api_key: Optional[str] = None
    max_iterations: int = 10
    timeout_seconds: int = 300
    enable_caching: bool = True
    cache_ttl_hours: int = 1
    log_level: str = "INFO"

    # Sub-configurations
    database: DatabaseConfig = None
    data_quality: DataQualityConfig = None
    feature_engineering: FeatureEngineeringConfig = None

    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig.from_env()
        if self.data_quality is None:
            self.data_quality = DataQualityConfig()
        if self.feature_engineering is None:
            self.feature_engineering = FeatureEngineeringConfig()

        # Get OpenAI API key from environment if not provided
        if self.openai_api_key is None:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")


class DataAnalysisError(Exception):
    """Base exception for data analysis errors"""

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        error_code: str = None,
        context: Dict[str, Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()


class DatabaseConnectionError(DataAnalysisError):
    """Database connection related errors"""

    def __init__(self, message: str, context: Dict[str, Any] = None):
        super().__init__(message, severity=ErrorSeverity.HIGH, error_code="DB_CONNECTION_ERROR", context=context)


class DataValidationError(DataAnalysisError):
    """Data validation related errors"""

    def __init__(self, message: str, context: Dict[str, Any] = None):
        super().__init__(message, severity=ErrorSeverity.MEDIUM, error_code="DATA_VALIDATION_ERROR", context=context)


class FeatureComputationError(DataAnalysisError):
    """Feature computation related errors"""

    def __init__(self, message: str, context: Dict[str, Any] = None):
        super().__init__(
            message, severity=ErrorSeverity.MEDIUM, error_code="FEATURE_COMPUTATION_ERROR", context=context
        )


class LangChainAgentError(DataAnalysisError):
    """LangChain agent execution errors"""

    def __init__(self, message: str, context: Dict[str, Any] = None):
        super().__init__(message, severity=ErrorSeverity.HIGH, error_code="LANGCHAIN_AGENT_ERROR", context=context)


class ErrorHandler:
    """Centralized error handling for data analysis operations"""

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_history: List[DataAnalysisError] = []
        self.max_history_size = 100

    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> DataAnalysisError:
        """Handle and log errors with appropriate severity"""

        # Convert to DataAnalysisError if needed
        if isinstance(error, DataAnalysisError):
            analysis_error = error
        else:
            analysis_error = DataAnalysisError(message=str(error), severity=ErrorSeverity.MEDIUM, context=context)

        # Add to error history
        self.error_history.append(analysis_error)
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)

        # Log the error
        log_data = {
            "error_code": analysis_error.error_code,
            "severity": analysis_error.severity.value,
            "context": analysis_error.context,
            "timestamp": analysis_error.timestamp.isoformat(),
        }

        if analysis_error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.error(f"Data Analysis Error: {analysis_error.message}", extra=log_data)
        elif analysis_error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"Data Analysis Warning: {analysis_error.message}", extra=log_data)
        else:
            self.logger.info(f"Data Analysis Info: {analysis_error.message}", extra=log_data)

        return analysis_error

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors"""
        if not self.error_history:
            return {"total_errors": 0, "by_severity": {}, "recent_errors": []}

        # Count by severity
        severity_counts = {}
        for error in self.error_history:
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Get recent errors (last 10)
        recent_errors = []
        for error in self.error_history[-10:]:
            recent_errors.append(
                {
                    "message": error.message,
                    "severity": error.severity.value,
                    "error_code": error.error_code,
                    "timestamp": error.timestamp.isoformat(),
                }
            )

        return {"total_errors": len(self.error_history), "by_severity": severity_counts, "recent_errors": recent_errors}

    def should_fallback(self) -> bool:
        """Determine if system should switch to fallback mode"""
        if len(self.error_history) < 3:
            return False

        # Check recent errors (last 5)
        recent_errors = self.error_history[-5:]
        critical_errors = sum(1 for e in recent_errors if e.severity == ErrorSeverity.CRITICAL)
        high_errors = sum(1 for e in recent_errors if e.severity == ErrorSeverity.HIGH)

        # Fallback if too many severe errors
        return critical_errors >= 2 or high_errors >= 3


class RetryHandler:
    """Handles retry logic for operations"""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, exponential_backoff: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.exponential_backoff = exponential_backoff

    async def retry_async(self, func, *args, **kwargs):
        """Retry an async function with exponential backoff"""
        import asyncio

        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt == self.max_retries:
                    break

                # Calculate delay
                if self.exponential_backoff:
                    delay = self.base_delay * (2**attempt)
                else:
                    delay = self.base_delay

                await asyncio.sleep(delay)

        # If we get here, all retries failed
        raise last_exception

    def retry_sync(self, func, *args, **kwargs):
        """Retry a synchronous function with exponential backoff"""
        import time

        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt == self.max_retries:
                    break

                # Calculate delay
                if self.exponential_backoff:
                    delay = self.base_delay * (2**attempt)
                else:
                    delay = self.base_delay

                time.sleep(delay)

        # If we get here, all retries failed
        raise last_exception


# Global configuration instance
default_config = AgentConfig()

# Global error handler
global_error_handler = ErrorHandler()

# Global retry handler
global_retry_handler = RetryHandler()
