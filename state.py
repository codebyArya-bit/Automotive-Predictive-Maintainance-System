"""
State management for the Master Agent Orchestration System
"""

from typing import TypedDict, Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class Priority(Enum):
    P0 = "P0"  # Critical
    P1 = "P1"  # High
    P2 = "P2"  # Medium
    P3 = "P3"  # Low


class ContactMethod(Enum):
    VOICE = "voice"
    APP_NOTIFICATION = "app_notification"
    EMAIL = "email"
    SMS = "sms"


class AgentStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class PredictionResult(TypedDict):
    component: str
    failure_probability: float
    predicted_failure_date: Optional[str]
    confidence_score: float
    priority: Priority
    recommended_action: str
    estimated_cost: Optional[float]


class TelemetryData(TypedDict):
    timestamp: str
    engine_temperature: float
    oil_pressure: float
    brake_pad_thickness: float
    tire_pressure: Dict[str, float]
    battery_voltage: float
    transmission_fluid_level: float
    mileage: int
    error_codes: List[str]


class CustomerResponse(TypedDict):
    response_text: str
    sentiment_score: float
    intent: str
    confidence: float
    timestamp: str
    channel: ContactMethod


class AppointmentDetails(TypedDict):
    appointment_id: str
    scheduled_date: str
    service_type: str
    estimated_duration: int  # in minutes
    service_advisor: str
    location: str
    status: str


class ConversationMessage(TypedDict):
    timestamp: str
    agent: str
    message: str
    message_type: str  # "system", "user", "agent"
    metadata: Optional[Dict[str, Any]]


class AgentExecution(TypedDict):
    agent_name: str
    status: AgentStatus
    start_time: Optional[str]
    end_time: Optional[str]
    execution_time: Optional[float]
    error_message: Optional[str]
    retry_count: int


class State(TypedDict):
    # Core Vehicle Information
    vehicle_id: str
    vehicle_make: Optional[str]
    vehicle_model: Optional[str]
    vehicle_year: Optional[int]
    vin: Optional[str]

    # Telemetry and Analysis Data
    telemetry_snapshot: Optional[TelemetryData]
    prediction: Optional[PredictionResult]
    analysis_results: Optional[Dict[str, Any]]

    # Customer Interaction
    customer_id: Optional[str]
    customer_response: Optional[CustomerResponse]
    contact_method: Optional[ContactMethod]
    conversation_history: List[ConversationMessage]

    # Appointment and Scheduling
    appointment: Optional[AppointmentDetails]

    # Workflow Management
    current_agent: str
    agent_executions: List[AgentExecution]
    workflow_step: str

    # Error Handling and Retries
    retry_count: int
    max_retries: int
    last_error: Optional[str]
    fallback_used: bool

    # Escalation and Human Handoff
    escalate_to_human: bool
    escalation_reason: Optional[str]
    human_agent_id: Optional[str]

    # Monitoring and Compliance
    session_id: str
    created_at: str
    updated_at: str
    ueba_flags: List[str]
    compliance_status: str

    # Feedback and Learning
    customer_satisfaction: Optional[float]
    feedback_collected: bool
    improvement_suggestions: List[str]


class StateManager:
    """Utility class for managing state transitions and validations"""

    @staticmethod
    def create_initial_state(vehicle_id: str, session_id: str) -> State:
        """Create initial state for a new workflow session"""
        current_time = datetime.now().isoformat()

        return State(
            # Core Vehicle Information
            vehicle_id=vehicle_id,
            vehicle_make=None,
            vehicle_model=None,
            vehicle_year=None,
            vin=None,
            # Telemetry and Analysis Data
            telemetry_snapshot=None,
            prediction=None,
            analysis_results=None,
            # Customer Interaction
            customer_id=None,
            customer_response=None,
            contact_method=None,
            conversation_history=[],
            # Appointment and Scheduling
            appointment=None,
            # Workflow Management
            current_agent="data_analysis",
            agent_executions=[],
            workflow_step="initialization",
            # Error Handling and Retries
            retry_count=0,
            max_retries=3,
            last_error=None,
            fallback_used=False,
            # Escalation and Human Handoff
            escalate_to_human=False,
            escalation_reason=None,
            human_agent_id=None,
            # Monitoring and Compliance
            session_id=session_id,
            created_at=current_time,
            updated_at=current_time,
            ueba_flags=[],
            compliance_status="compliant",
            # Feedback and Learning
            customer_satisfaction=None,
            feedback_collected=False,
            improvement_suggestions=[],
        )

    @staticmethod
    def update_agent_status(
        state: State, agent_name: str, status: AgentStatus, error_message: Optional[str] = None
    ) -> State:
        """Update the status of a specific agent execution"""
        current_time = datetime.now().isoformat()
        state["updated_at"] = current_time

        # Find existing execution or create new one
        execution = None
        for exec_record in state["agent_executions"]:
            if exec_record["agent_name"] == agent_name:
                execution = exec_record
                break

        if execution is None:
            execution = AgentExecution(
                agent_name=agent_name,
                status=status,
                start_time=current_time if status == AgentStatus.IN_PROGRESS else None,
                end_time=None,
                execution_time=None,
                error_message=error_message,
                retry_count=0,
            )
            state["agent_executions"].append(execution)
        else:
            execution["status"] = status
            if status == AgentStatus.IN_PROGRESS and execution["start_time"] is None:
                execution["start_time"] = current_time
            elif status in [AgentStatus.COMPLETED, AgentStatus.FAILED]:
                execution["end_time"] = current_time
                if execution["start_time"]:
                    start_dt = datetime.fromisoformat(execution["start_time"])
                    end_dt = datetime.fromisoformat(current_time)
                    execution["execution_time"] = (end_dt - start_dt).total_seconds()

            if error_message:
                execution["error_message"] = error_message

            if status == AgentStatus.RETRYING:
                execution["retry_count"] += 1

        return state

    @staticmethod
    def add_conversation_message(
        state: State, agent: str, message: str, message_type: str = "agent", metadata: Optional[Dict[str, Any]] = None
    ) -> State:
        """Add a message to the conversation history"""
        conversation_message = ConversationMessage(
            timestamp=datetime.now().isoformat(),
            agent=agent,
            message=message,
            message_type=message_type,
            metadata=metadata,
        )

        state["conversation_history"].append(conversation_message)
        state["updated_at"] = datetime.now().isoformat()

        return state

    @staticmethod
    def should_escalate(state: State) -> bool:
        """Determine if the workflow should be escalated to a human agent"""
        # Check explicit escalation flag
        if state["escalate_to_human"]:
            return True

        # Check customer sentiment
        if state["customer_response"] and state["customer_response"]["sentiment_score"] < 3.0:
            return True

        # Check retry count
        if state["retry_count"] >= state["max_retries"]:
            return True

        # Check for critical priority with failed agents
        if state["prediction"] and state["prediction"]["priority"] == Priority.P0:
            failed_agents = [exec for exec in state["agent_executions"] if exec["status"] == AgentStatus.FAILED]
            if failed_agents:
                return True

        return False
