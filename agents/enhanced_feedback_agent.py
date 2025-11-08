"""
Enhanced Feedback Agent - Post-service follow-up and continuous learning
Handles customer feedback collection 24 hours after service completion,
issue escalation, and ML model retraining pipeline integration.
"""

import random
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .base_agent import BaseAgent
from state import State

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionOutcome(Enum):
    """Prediction outcome labels for ML retraining"""

    TRUE_POSITIVE = "true_positive"  # Issue was real and fixed
    FALSE_POSITIVE = "false_positive"  # Issue didn't actually exist
    FALSE_NEGATIVE = "false_negative"  # Different issue found (prediction missed it)
    TRUE_NEGATIVE = "true_negative"  # No issue predicted, no issue found


class FeedbackChannel(Enum):
    """Communication channels for feedback requests"""

    SMS = "sms"
    APP_NOTIFICATION = "app_notification"
    VOICE_CALL = "voice_call"
    EMAIL = "email"


@dataclass
class CompletedAppointment:
    """Represents a completed service appointment"""

    appointment_id: str
    customer_id: str
    vehicle_id: str
    service_details: Dict[str, Any]
    completion_date: str
    predicted_issue: str
    actual_service_performed: List[str]
    parts_replaced: List[str]
    service_cost: float
    technician_id: str
    service_center_id: str


@dataclass
class CustomerFeedback:
    """Structured customer feedback data"""

    appointment_id: str
    customer_id: str
    service_quality: int  # 1 - 5 stars
    issue_resolved: bool
    technician_professionalism: int  # 1 - 5 stars
    wait_time_satisfaction: int  # 1 - 5 stars
    nps_score: int  # 0 - 10 (Net Promoter Score)
    comments: str
    feedback_date: str
    channel_used: str


@dataclass
class SupportTicket:
    """Support ticket for unresolved issues"""

    ticket_id: str
    appointment_id: str
    customer_id: str
    issue_description: str
    priority: str
    created_date: str
    status: str
    assigned_to: str


@dataclass
class PredictionAccuracyMetrics:
    """ML model accuracy metrics"""

    total_predictions: int
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    accuracy: float


class EnhancedFeedbackAgent(BaseAgent):
    """Enhanced agent for post-service feedback and continuous learning"""

    def __init__(self):
        super().__init__("enhanced_feedback")

        # Mock database storage
        self.completed_appointments = {}
        self.customer_feedback = {}
        self.support_tickets = {}
        self.prediction_outcomes = {}
        self.ml_training_data = []

        # Customer database for personalization
        self.customers = {
            "CUST001": {"name": "Rajesh Kumar", "phone": "+91 - 98765 - 43210", "preferred_channel": "sms"},
            "CUST002": {"name": "Priya Sharma", "phone": "+91 - 98765 - 43211", "preferred_channel": "app_notification"},
            "CUST003": {"name": "Amit Singh", "phone": "+91 - 98765 - 43212", "preferred_channel": "sms"},
            "CUST004": {"name": "Sneha Patel", "phone": "+91 - 98765 - 43213", "preferred_channel": "voice_call"},
            "CUST005": {"name": "Vikram Reddy", "phone": "+91 - 98765 - 43214", "preferred_channel": "app_notification"},
        }

        # Initialize with some mock completed appointments
        self._initialize_mock_data()

        logger.info("Enhanced Feedback Agent initialized successfully")

    def _initialize_mock_data(self):
        """Initialize with mock completed appointments for testing"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

        mock_appointments = [
            CompletedAppointment(
                appointment_id="APT - 001",
                customer_id="CUST001",
                vehicle_id="VEH001",
                service_details={"predicted_issue": "battery", "service_type": "Battery Replacement"},
                completion_date=yesterday,
                predicted_issue="battery",
                actual_service_performed=["battery_replacement", "electrical_check"],
                parts_replaced=["battery", "battery_terminals"],
                service_cost=8500.0,
                technician_id="TECH001",
                service_center_id="SC001",
            ),
            CompletedAppointment(
                appointment_id="APT - 002",
                customer_id="CUST002",
                vehicle_id="VEH002",
                service_details={"predicted_issue": "brakes", "service_type": "Brake Service"},
                completion_date=yesterday,
                predicted_issue="brakes",
                actual_service_performed=["brake_inspection", "brake_fluid_change"],
                parts_replaced=["brake_fluid"],
                service_cost=3200.0,
                technician_id="TECH002",
                service_center_id="SC001",
            ),
            CompletedAppointment(
                appointment_id="APT - 003",
                customer_id="CUST003",
                vehicle_id="VEH003",
                service_details={"predicted_issue": "engine", "service_type": "Engine Diagnostics"},
                completion_date=two_days_ago,
                predicted_issue="engine",
                actual_service_performed=["engine_diagnostics", "oil_change"],
                parts_replaced=["engine_oil", "oil_filter"],
                service_cost=4500.0,
                technician_id="TECH003",
                service_center_id="SC002",
            ),
        ]

        for appointment in mock_appointments:
            self.completed_appointments[appointment.appointment_id] = appointment

    async def _execute_internal(self, state: State) -> State:
        """Execute post-service feedback collection workflow"""
        logger.info("Starting post-service feedback collection workflow")

        try:
            # Get appointments completed 24 hours ago
            target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            completed_appointments = self.get_completed_appointments(target_date)

            feedback_results = []

            for appointment in completed_appointments:
                logger.info(f"Processing feedback for appointment {appointment['appointment_id']}")

                # Send feedback request
                feedback_sent = self.send_feedback_request(appointment["customer_id"], appointment["appointment_id"])

                if feedback_sent:
                    # Simulate feedback collection (in real system, this would be async)
                    feedback = self.collect_feedback(appointment["appointment_id"])

                    if feedback:
                        # Check for unresolved issues
                        if self.detect_unresolved_issue(feedback):
                            # Create support ticket and escalate
                            ticket_id = self.create_support_ticket(
                                appointment["appointment_id"],
                                f"Customer reports unresolved issue: {feedback.get('comments', 'No details provided')}",
                            )
                            logger.warning(f"Created support ticket {ticket_id} for unresolved issue")

                        # Label prediction outcome for ML
                        prediction_outcome = self.label_prediction_outcome(
                            appointment["appointment_id"], feedback, appointment
                        )

                        # Send to ML retraining pipeline
                        labeled_data = {
                            "appointment_id": appointment["appointment_id"],
                            "prediction": appointment["predicted_issue"],
                            "actual_service": appointment["actual_service_performed"],
                            "outcome_label": prediction_outcome,
                            "feedback": feedback,
                            "timestamp": datetime.now().isoformat(),
                        }

                        ml_sent = self.send_to_ml_retraining_pipeline(labeled_data)

                        feedback_results.append(
                            {
                                "appointment_id": appointment["appointment_id"],
                                "feedback_collected": True,
                                "prediction_outcome": prediction_outcome,
                                "ml_data_sent": ml_sent,
                            }
                        )
                    else:
                        feedback_results.append(
                            {
                                "appointment_id": appointment["appointment_id"],
                                "feedback_collected": False,
                                "reason": "No response from customer",
                            }
                        )

            # Update state with results
            state["feedback_collection_results"] = feedback_results
            state["appointments_processed"] = len(completed_appointments)
            state["feedback_collected_count"] = len([r for r in feedback_results if r.get("feedback_collected")])

            # Add log message
            state = self._add_log_message(
                state,
                f"Processed {len(completed_appointments)} appointments, collected {state['feedback_collected_count']} feedback responses",
                {"results": feedback_results},
            )

            return state

        except Exception as e:
            logger.error(f"Error in feedback collection workflow: {str(e)}")
            state = self._add_log_message(state, f"Feedback collection error: {str(e)}", {"error": str(e)})
            return state

    def get_completed_appointments(self, date: str) -> List[Dict]:
        """Get appointments completed on a specific date."""
        try:
            completed = []
            for appointment_id, appointment in self.completed_appointments.items():
                if appointment.completion_date == date:
                    completed.append(
                        {
                            "appointment_id": appointment.appointment_id,
                            "customer_id": appointment.customer_id,
                            "vehicle_id": appointment.vehicle_id,
                            "service_details": appointment.service_details,
                            "predicted_issue": appointment.predicted_issue,
                            "actual_service_performed": appointment.actual_service_performed,
                            "parts_replaced": appointment.parts_replaced,
                            "service_cost": appointment.service_cost,
                        }
                    )

            logger.info(f"Found {len(completed)} completed appointments for {date}")
            return completed

        except Exception as e:
            logger.error(f"Error getting completed appointments: {str(e)}")
            return []

    def send_feedback_request(self, customer_id: str, appointment_id: str, channel: str = "sms") -> bool:
        """Send feedback request via SMS or app notification."""
        try:
            customer = self.customers.get(customer_id)
            if not customer:
                logger.error(f"Customer {customer_id} not found")
                return False

            # Use customer's preferred channel if not specified
            if channel == "sms" and customer.get("preferred_channel"):
                channel = customer["preferred_channel"]

            name = customer["name"]
            phone = customer["phone"]

            # Generate feedback messages based on channel
            if channel == "sms":
                message = f"Hi {name}! Your service is complete. How was your experience? Rate us: https://feedback.autoservice.com/{appointment_id}"
                logger.info(f"SMS sent to {phone}: {message}")

            elif channel == "app_notification":
                message = f"Hi {name}! Please rate your recent service experience."
                logger.info(f"App notification sent to {customer_id}: {message}")

            elif channel == "voice_call":
                script = f"Hi {name}, this is a quick follow-up from AutoService. Your service was completed yesterday. Just wanted to check—was the issue fully resolved?"
                logger.info(f"Voice call initiated to {phone} with script: {script}")

            elif channel == "email":
                subject = "Please rate your service experience"
                message = f"Dear {name}, we hope you're satisfied with your recent service. Please take a moment to share your feedback."
                logger.info(f"Email sent to {customer_id}: {subject}")

            # Simulate successful sending
            return True

        except Exception as e:
            logger.error(f"Error sending feedback request: {str(e)}")
            return False

    def collect_feedback(self, appointment_id: str) -> Dict:
        """Collect structured feedback."""
        try:
            # Simulate customer response (in real system, this would come from web form/app)
            # Generate realistic feedback based on appointment details
            appointment = self.completed_appointments.get(appointment_id)
            if not appointment:
                return {}

            # Simulate feedback with some randomness
            service_quality = random.randint(3, 5)  # Most customers rate 3 - 5
            issue_resolved = random.choice([True, True, True, False])  # 75% resolved
            technician_professionalism = random.randint(3, 5)
            wait_time_satisfaction = random.randint(2, 5)
            nps_score = random.randint(6, 10) if service_quality >= 4 else random.randint(0, 6)

            # Generate comments based on ratings
            if service_quality >= 4 and issue_resolved:
                comments = random.choice(
                    [
                        "Great service! The technician was professional and fixed the issue quickly.",
                        "Very satisfied with the service quality and communication.",
                        "The problem was resolved efficiently. Thank you!",
                        "Excellent work by the technical team.",
                    ]
                )
            elif not issue_resolved:
                comments = random.choice(
                    [
                        "The issue is still not completely resolved. Need follow-up.",
                        "Service was okay but the problem persists.",
                        "Still experiencing the same issue after service.",
                        "Partial fix but not completely satisfied.",
                    ]
                )
            else:
                comments = random.choice(
                    [
                        "Service was adequate but could be improved.",
                        "Average experience, nothing exceptional.",
                        "The service was okay, met basic expectations.",
                        "Room for improvement in service quality.",
                    ]
                )

            feedback = {
                "appointment_id": appointment_id,
                "customer_id": appointment.customer_id,
                "service_quality": service_quality,
                "issue_resolved": issue_resolved,
                "technician_professionalism": technician_professionalism,
                "wait_time_satisfaction": wait_time_satisfaction,
                "nps_score": nps_score,
                "comments": comments,
                "feedback_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "channel_used": "sms",
            }

            # Store feedback
            self.customer_feedback[appointment_id] = feedback

            logger.info(
                f"Feedback collected for appointment {appointment_id}: Quality={service_quality}, Resolved={issue_resolved}"
            )
            return feedback

        except Exception as e:
            logger.error(f"Error collecting feedback: {str(e)}")
            return {}

    def detect_unresolved_issue(self, feedback: Dict) -> bool:
        """Detect if customer reports issue not resolved."""
        try:
            # Issue is unresolved if:
            # 1. Customer explicitly says issue not resolved
            # 2. Service quality rating is very low (< 3)
            # 3. NPS score is very low (< 4)

            issue_not_resolved = feedback.get("issue_resolved") is False
            low_service_quality = feedback.get("service_quality", 5) < 3
            very_low_nps = feedback.get("nps_score", 10) < 4

            unresolved = issue_not_resolved or low_service_quality or very_low_nps

            if unresolved:
                logger.warning(f"Unresolved issue detected for appointment {feedback.get('appointment_id')}")

            return unresolved

        except Exception as e:
            logger.error(f"Error detecting unresolved issue: {str(e)}")
            return False

    def create_support_ticket(self, appointment_id: str, issue: str) -> str:
        """Create support ticket for unresolved issues."""
        try:
            ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

            appointment = self.completed_appointments.get(appointment_id)
            if not appointment:
                logger.error(f"Appointment {appointment_id} not found for ticket creation")
                return ""

            # Determine priority based on issue severity
            feedback = self.customer_feedback.get(appointment_id, {})
            service_quality = feedback.get("service_quality", 3)

            if service_quality <= 2:
                priority = "HIGH"
            elif service_quality <= 3:
                priority = "MEDIUM"
            else:
                priority = "LOW"

            ticket = SupportTicket(
                ticket_id=ticket_id,
                appointment_id=appointment_id,
                customer_id=appointment.customer_id,
                issue_description=issue,
                priority=priority,
                created_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                status="OPEN",
                assigned_to=f"MANAGER-{appointment.service_center_id}",
            )

            # Store ticket
            self.support_tickets[ticket_id] = ticket

            # Simulate notification to service center manager
            logger.info(f"Support ticket {ticket_id} created and assigned to {ticket.assigned_to}")
            logger.info(f"Notification sent to service center manager for {priority} priority ticket")

            return ticket_id

        except Exception as e:
            logger.error(f"Error creating support ticket: {str(e)}")
            return ""

    def label_prediction_outcome(self, appointment_id: str, feedback: Dict, appointment_data: Dict) -> str:
        """Label whether prediction was accurate."""
        try:
            predicted_issue = appointment_data.get("predicted_issue", "").lower()
            actual_services = [service.lower() for service in appointment_data.get("actual_service_performed", [])]
            parts_replaced = [part.lower() for part in appointment_data.get("parts_replaced", [])]
            issue_resolved = feedback.get("issue_resolved", True)

            # True Positive: Issue was real and fixed
            # - Predicted issue matches actual service performed
            # - Customer confirms issue was resolved
            # - Parts replaced align with prediction

            prediction_matches_service = any(predicted_issue in service for service in actual_services)
            prediction_matches_parts = any(predicted_issue in part for part in parts_replaced)

            if (prediction_matches_service or prediction_matches_parts) and issue_resolved:
                outcome = PredictionOutcome.TRUE_POSITIVE.value

            # False Positive: Issue didn't actually exist
            # - Predicted issue doesn't match actual service
            # - Customer reports no issue found or minimal service performed
            elif not prediction_matches_service and not prediction_matches_parts:
                if len(actual_services) <= 1 and "inspection" in str(actual_services):
                    outcome = PredictionOutcome.FALSE_POSITIVE.value
                else:
                    # Different issue found - False Negative for the actual issue
                    outcome = PredictionOutcome.FALSE_NEGATIVE.value

            # Issue was predicted but not fully resolved
            elif prediction_matches_service and not issue_resolved:
                outcome = PredictionOutcome.TRUE_POSITIVE.value  # Issue was real, but service incomplete

            else:
                outcome = PredictionOutcome.TRUE_POSITIVE.value  # Default to positive if unclear

            # Store outcome
            self.prediction_outcomes[appointment_id] = {
                "outcome": outcome,
                "predicted_issue": predicted_issue,
                "actual_services": actual_services,
                "parts_replaced": parts_replaced,
                "issue_resolved": issue_resolved,
                "labeled_date": datetime.now().isoformat(),
            }

            logger.info(f"Prediction outcome labeled for {appointment_id}: {outcome}")
            return outcome

        except Exception as e:
            logger.error(f"Error labeling prediction outcome: {str(e)}")
            return PredictionOutcome.TRUE_POSITIVE.value  # Default

    def send_to_ml_retraining_pipeline(self, labeled_data: Dict) -> bool:
        """Send labeled data to ML retraining pipeline."""
        try:
            # Add metadata for ML training
            training_record = {
                **labeled_data,
                "data_version": "v1.0",
                "labeling_confidence": 0.85,  # Confidence in the labeling
                "training_ready": True,
                "created_at": datetime.now().isoformat(),
            }

            # Store in training data collection
            self.ml_training_data.append(training_record)

            logger.info(f"Labeled data sent to ML pipeline for appointment {labeled_data['appointment_id']}")
            logger.info(f"Training dataset now contains {len(self.ml_training_data)} records")

            # Simulate triggering retraining if enough data accumulated
            if len(self.ml_training_data) >= 100:  # Threshold for retraining
                logger.info("Training data threshold reached - triggering monthly retraining job")
                self._trigger_model_retraining()

            return True

        except Exception as e:
            logger.error(f"Error sending data to ML pipeline: {str(e)}")
            return False

    def _trigger_model_retraining(self):
        """Simulate triggering ML model retraining"""
        logger.info("ML model retraining job triggered")
        logger.info(f"Training with {len(self.ml_training_data)} labeled examples")

        # In real implementation, this would:
        # 1. Send data to ML training service
        # 2. Trigger model retraining pipeline
        # 3. Validate new model performance
        # 4. Deploy if performance improves

    def analyze_prediction_accuracy(self, start_date: str = None, end_date: str = None) -> PredictionAccuracyMetrics:
        """Monthly job to analyze prediction accuracy."""
        try:
            # Filter outcomes by date range if provided
            outcomes_to_analyze = self.prediction_outcomes

            if start_date or end_date:
                filtered_outcomes = {}
                for apt_id, outcome_data in self.prediction_outcomes.items():
                    labeled_date = outcome_data.get("labeled_date", "")
                    # Simple date filtering (in real system, use proper date parsing)
                    if start_date and labeled_date < start_date:
                        continue
                    if end_date and labeled_date > end_date:
                        continue
                    filtered_outcomes[apt_id] = outcome_data
                outcomes_to_analyze = filtered_outcomes

            # Count outcomes
            true_positives = sum(
                1
                for outcome in outcomes_to_analyze.values()
                if outcome["outcome"] == PredictionOutcome.TRUE_POSITIVE.value
            )
            false_positives = sum(
                1
                for outcome in outcomes_to_analyze.values()
                if outcome["outcome"] == PredictionOutcome.FALSE_POSITIVE.value
            )
            true_negatives = sum(
                1
                for outcome in outcomes_to_analyze.values()
                if outcome["outcome"] == PredictionOutcome.TRUE_NEGATIVE.value
            )
            false_negatives = sum(
                1
                for outcome in outcomes_to_analyze.values()
                if outcome["outcome"] == PredictionOutcome.FALSE_NEGATIVE.value
            )

            total = true_positives + false_positives + true_negatives + false_negatives

            if total == 0:
                logger.warning("No prediction outcomes available for analysis")
                return PredictionAccuracyMetrics(0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0)

            # Calculate metrics
            precision = (
                true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
            )
            recall = (
                true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
            )
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            accuracy = (true_positives + true_negatives) / total

            metrics = PredictionAccuracyMetrics(
                total_predictions=total,
                true_positives=true_positives,
                false_positives=false_positives,
                true_negatives=true_negatives,
                false_negatives=false_negatives,
                precision=precision,
                recall=recall,
                f1_score=f1_score,
                accuracy=accuracy,
            )

            logger.info(f"Prediction accuracy analysis complete:")
            logger.info(f"  Total predictions: {total}")
            logger.info(f"  Precision: {precision:.3f}")
            logger.info(f"  Recall: {recall:.3f}")
            logger.info(f"  F1-score: {f1_score:.3f}")
            logger.info(f"  Accuracy: {accuracy:.3f}")

            # Trigger retraining if accuracy drops below threshold
            if accuracy < 0.75:  # 75% accuracy threshold
                logger.warning(f"Model accuracy ({accuracy:.3f}) below threshold - triggering retraining")
                self._trigger_model_retraining()

            return metrics

        except Exception as e:
            logger.error(f"Error analyzing prediction accuracy: {str(e)}")
            return PredictionAccuracyMetrics(0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0)

    def get_feedback_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary of feedback collected in the last N days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_feedback = []

            for feedback in self.customer_feedback.values():
                feedback_date = datetime.strptime(feedback["feedback_date"], "%Y-%m-%d %H:%M:%S")
                if feedback_date >= cutoff_date:
                    recent_feedback.append(feedback)

            if not recent_feedback:
                return {"message": f"No feedback collected in the last {days} days"}

            # Calculate summary statistics
            total_feedback = len(recent_feedback)
            avg_service_quality = sum(f["service_quality"] for f in recent_feedback) / total_feedback
            avg_nps = sum(f["nps_score"] for f in recent_feedback) / total_feedback
            resolution_rate = sum(1 for f in recent_feedback if f["issue_resolved"]) / total_feedback

            # Count ratings distribution
            quality_distribution = {}
            for i in range(1, 6):
                quality_distribution[f"{i}_star"] = sum(1 for f in recent_feedback if f["service_quality"] == i)

            summary = {
                "period_days": days,
                "total_feedback_collected": total_feedback,
                "average_service_quality": round(avg_service_quality, 2),
                "average_nps_score": round(avg_nps, 2),
                "issue_resolution_rate": round(resolution_rate * 100, 1),
                "quality_rating_distribution": quality_distribution,
                "support_tickets_created": len(
                    [t for t in self.support_tickets.values() if t.created_date >= cutoff_date.strftime("%Y-%m-%d")]
                ),
            }

            return summary

        except Exception as e:
            logger.error(f"Error generating feedback summary: {str(e)}")
            return {"error": str(e)}
