"""
Diagnosis Agent - Interprets analysis results and generates predictive maintenance recommendations
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .base_agent import BaseAgent
from state import State, PredictionResult, Priority


class DiagnosisAgent(BaseAgent):
    """Agent responsible for diagnosing issues and predicting maintenance needs"""

    def __init__(self):
        super().__init__("diagnosis")

        # Component failure patterns and prediction models
        self.failure_patterns = {
            "engine": {
                "high_temperature": {"base_probability": 0.15, "time_to_failure_days": 30},
                "low_oil_pressure": {"base_probability": 0.25, "time_to_failure_days": 14},
                "error_codes": {"base_probability": 0.10, "time_to_failure_days": 60},
            },
            "brakes": {
                "worn_pads": {"base_probability": 0.80, "time_to_failure_days": 90},
                "critical_wear": {"base_probability": 0.95, "time_to_failure_days": 7},
            },
            "tires": {
                "low_pressure": {"base_probability": 0.05, "time_to_failure_days": 180},
                "critical_pressure": {"base_probability": 0.30, "time_to_failure_days": 30},
            },
            "electrical": {
                "low_battery": {"base_probability": 0.20, "time_to_failure_days": 45},
                "critical_battery": {"base_probability": 0.60, "time_to_failure_days": 14},
            },
        }

        # Cost estimates for different repairs
        self.repair_costs = {
            "engine_overhaul": {"min": 3000, "max": 8000},
            "oil_change": {"min": 50, "max": 120},
            "brake_pad_replacement": {"min": 200, "max": 600},
            "tire_replacement": {"min": 400, "max": 1200},
            "battery_replacement": {"min": 100, "max": 300},
            "diagnostic_check": {"min": 100, "max": 200},
        }

    async def _execute_internal(self, state: State) -> State:
        """Diagnose issues and generate predictions"""
        self.logger.info("Starting diagnosis and prediction", vehicle_id=state["vehicle_id"])

        # Validate that we have analysis results
        if not self._validate_state(state, ["analysis_results"]):
            raise ValueError("Analysis results not available for diagnosis")

        analysis_results = state["analysis_results"]

        # Generate predictions based on analysis
        prediction = await self._generate_prediction(analysis_results, state)

        # Store prediction in state
        state["prediction"] = prediction

        # Add log message
        priority_text = prediction["priority"].value if prediction["priority"] else "Unknown"
        state = self._add_log_message(
            state,
            f"Diagnosis completed. Priority: {priority_text}, "
            f"Failure probability: {prediction['failure_probability']:.1%}",
            {"prediction_summary": self._create_prediction_summary(prediction)},
        )

        return state

    async def _generate_prediction(self, analysis_results: Dict[str, Any], state: State) -> PredictionResult:
        """Generate predictive maintenance recommendations"""
        # Simulate ML model processing time
        await asyncio.sleep(0.3)

        # Ensure analysis_results is not None
        if analysis_results is None:
            analysis_results = {}

        anomalies = analysis_results.get("anomalies", [])
        warnings = analysis_results.get("warnings", [])
        health_score = analysis_results.get("health_score", 100)

        # Determine primary component at risk
        primary_component = self._identify_primary_component(anomalies, warnings)

        # Calculate failure probability
        failure_probability = self._calculate_failure_probability(anomalies, warnings, health_score)

        # Determine priority based on probability and severity
        priority = self._determine_priority(failure_probability, anomalies)

        # Predict failure date
        predicted_failure_date = self._predict_failure_date(primary_component, anomalies, warnings)

        # Generate recommended action
        recommended_action = self._generate_recommended_action(primary_component, anomalies, warnings, priority)

        # Estimate repair cost
        estimated_cost = self._estimate_repair_cost(primary_component, anomalies)

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(anomalies, warnings, health_score)

        return PredictionResult(
            component=primary_component,
            failure_probability=failure_probability,
            predicted_failure_date=predicted_failure_date,
            confidence_score=confidence_score,
            priority=priority,
            recommended_action=recommended_action,
            estimated_cost=estimated_cost,
        )

    def _identify_primary_component(self, anomalies: List[Dict], warnings: List[Dict]) -> str:
        """Identify the component most at risk"""
        component_scores = {}

        # Score based on anomalies (higher weight)
        for anomaly in anomalies:
            component = anomaly["component"]
            severity_weight = 3 if anomaly["severity"] == "critical" else 2
            component_scores[component] = component_scores.get(component, 0) + severity_weight

        # Score based on warnings (lower weight)
        for warning in warnings:
            component = warning["component"]
            component_scores[component] = component_scores.get(component, 0) + 1

        if not component_scores:
            return "general"

        # Return component with highest score
        return max(component_scores, key=component_scores.get)

    def _calculate_failure_probability(self, anomalies: List[Dict], warnings: List[Dict], health_score: float) -> float:
        """Calculate probability of component failure"""
        base_probability = 0.05  # 5% base probability

        # Increase probability based on anomalies
        for anomaly in anomalies:
            if anomaly["severity"] == "critical":
                base_probability += 0.30
            else:
                base_probability += 0.15

        # Increase probability based on warnings
        for warning in warnings:
            base_probability += 0.08

        # Adjust based on health score
        health_factor = (100 - health_score) / 100
        base_probability += health_factor * 0.20

        # Cap at 95% maximum
        return min(0.95, base_probability)

    def _determine_priority(self, failure_probability: float, anomalies: List[Dict]) -> Priority:
        """Determine priority level based on probability and severity"""
        # Check for critical anomalies
        critical_anomalies = [a for a in anomalies if a["severity"] == "critical"]

        if critical_anomalies and failure_probability >= 0.8:
            return Priority.P0
        elif failure_probability >= 0.7:
            return Priority.P1
        elif failure_probability >= 0.4:
            return Priority.P2
        else:
            return Priority.P3

    def _predict_failure_date(self, component: str, anomalies: List[Dict], warnings: List[Dict]) -> Optional[str]:
        """Predict when component failure might occur"""
        if component not in self.failure_patterns:
            return None

        # Find the most severe issue for this component
        component_issues = [a for a in anomalies + warnings if a["component"] == component]

        if not component_issues:
            return None

        # Use the most severe issue to determine timeline
        most_severe = max(component_issues, key=lambda x: 3 if x["severity"] == "critical" else 1)

        # Get base timeline from failure patterns
        if most_severe["severity"] == "critical":
            if component == "brakes" and "pad" in most_severe["parameter"]:
                days_to_failure = self.failure_patterns[component]["critical_wear"]["time_to_failure_days"]
            elif component == "engine":
                days_to_failure = self.failure_patterns[component]["low_oil_pressure"]["time_to_failure_days"]
            else:
                days_to_failure = 14  # Default critical timeline
        else:
            # Use appropriate pattern based on issue type
            if component == "brakes":
                days_to_failure = self.failure_patterns[component]["worn_pads"]["time_to_failure_days"]
            elif component == "engine":
                days_to_failure = self.failure_patterns[component]["high_temperature"]["time_to_failure_days"]
            else:
                days_to_failure = 60  # Default warning timeline

        # Add some randomness to make it more realistic
        days_to_failure += np.random.randint(-7, 8)
        days_to_failure = max(1, days_to_failure)  # Ensure at least 1 day

        failure_date = datetime.now() + timedelta(days=days_to_failure)
        return failure_date.isoformat()

    def _generate_recommended_action(
        self, component: str, anomalies: List[Dict], warnings: List[Dict], priority: Priority
    ) -> str:
        """Generate recommended maintenance action"""
        if priority == Priority.P0:
            return f"IMMEDIATE ACTION REQUIRED: Stop driving and service {component} immediately. Safety risk present."

        elif priority == Priority.P1:
            return f"Schedule urgent service for {component} within 1 - 2 days. Avoid extended driving."

        elif priority == Priority.P2:
            return f"Schedule service for {component} within 1 - 2 weeks. Monitor closely."

        else:
            return f"Schedule routine maintenance for {component} at next convenient time."

    def _estimate_repair_cost(self, component: str, anomalies: List[Dict]) -> Optional[float]:
        """Estimate repair cost based on component and severity"""
        cost_mapping = {
            "engine": "engine_overhaul" if any(a["severity"] == "critical" for a in anomalies) else "oil_change",
            "brakes": "brake_pad_replacement",
            "tires": "tire_replacement",
            "electrical": "battery_replacement",
        }

        repair_type = cost_mapping.get(component, "diagnostic_check")
        cost_range = self.repair_costs.get(repair_type, {"min": 100, "max": 500})

        # Return average cost with some variation
        avg_cost = (cost_range["min"] + cost_range["max"]) / 2
        variation = np.random.uniform(0.8, 1.2)  # ±20% variation

        return round(avg_cost * variation, 2)

    def _calculate_confidence_score(self, anomalies: List[Dict], warnings: List[Dict], health_score: float) -> float:
        """Calculate confidence in the prediction"""
        base_confidence = 0.7  # 70% base confidence

        # Increase confidence with more data points
        data_points = len(anomalies) + len(warnings)
        confidence_boost = min(0.2, data_points * 0.05)
        base_confidence += confidence_boost

        # Adjust based on health score clarity
        if health_score < 50 or health_score > 90:
            base_confidence += 0.1  # Clear good or bad health

        # Reduce confidence if mixed signals
        critical_count = len([a for a in anomalies if a["severity"] == "critical"])
        if critical_count > 0 and health_score > 70:
            base_confidence -= 0.15  # Mixed signals

        return min(0.95, max(0.3, base_confidence))

    def _create_prediction_summary(self, prediction: PredictionResult) -> Dict[str, Any]:
        """Create a summary of the prediction for logging"""
        return {
            "component": prediction["component"],
            "probability": f"{prediction['failure_probability']:.1%}",
            "priority": prediction["priority"].value,
            "confidence": f"{prediction['confidence_score']:.1%}",
            "estimated_cost": prediction["estimated_cost"],
            "failure_date": prediction["predicted_failure_date"],
        }
