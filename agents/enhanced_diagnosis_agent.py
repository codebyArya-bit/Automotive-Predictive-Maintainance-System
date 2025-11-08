"""
Enhanced Diagnosis Agent - ML-powered component failure prediction with RAG integration
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os

try:
    from langchain.tools import tool
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import FAISS

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

    def tool(func):
        """Fallback decorator when LangChain is not available"""
        return func


try:
    import joblib

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from .base_agent import BaseAgent
from state import State, PredictionResult, Priority


class EnhancedDiagnosisAgent(BaseAgent):
    """Enhanced Diagnosis Agent with ML models and RAG integration"""

    def __init__(self, openai_api_key: Optional[str] = None):
        super().__init__("enhanced_diagnosis")

        # Store OpenAI API key for RAG integration
        self.openai_api_key = openai_api_key

        # Component safety criticality mapping
        self.safety_critical_components = {
            "brakes": 1.0,
            "steering": 1.0,
            "engine": 0.8,
            "transmission": 0.7,
            "battery": 0.6,
            "cooling_system": 0.5,
            "electrical": 0.4,
            "tires": 0.9,
        }

        # Model paths (would be loaded from MLflow in production)
        self.model_paths = {
            "battery": "models/battery_failure_xgboost_v2.pkl",
            "transmission": "models/transmission_failure_xgboost_v2.pkl",
            "brakes": "models/brake_failure_xgboost_v2.pkl",
            "engine": "models/engine_failure_xgboost_v2.pkl",
            "cooling_system": "models/cooling_failure_xgboost_v2.pkl",
        }

        # Cost database (in production, this would be a proper database)
        self.cost_database = {
            "battery": {"parts_cost": 4500, "labor_cost": 2000, "duration_hours": 1.5},
            "transmission": {"parts_cost": 45000, "labor_cost": 15000, "duration_hours": 8.0},
            "brakes": {"parts_cost": 3500, "labor_cost": 2500, "duration_hours": 2.0},
            "engine": {"parts_cost": 85000, "labor_cost": 25000, "duration_hours": 16.0},
            "cooling_system": {"parts_cost": 8500, "labor_cost": 4000, "duration_hours": 3.0},
        }

        # Historical cases database (mock data)
        self.historical_cases = [
            {
                "case_id": "CASE - 2024 - 08 - 1234",
                "component": "battery",
                "vehicle_model": "Maruti Swift",
                "symptoms": ["low_voltage", "slow_cranking"],
                "root_cause": "Battery aging and terminal corrosion",
                "repair_action": "Battery replacement with terminal cleaning",
                "outcome": "successful",
            },
            {
                "case_id": "CASE - 2024 - 09 - 5678",
                "component": "brakes",
                "vehicle_model": "Hyundai i20",
                "symptoms": ["squealing", "reduced_stopping_power"],
                "root_cause": "Brake pad wear beyond safe limits",
                "repair_action": "Brake pad and rotor replacement",
                "outcome": "successful",
            },
        ]

        # Initialize RAG system if available
        self.rag_system = None
        if LANGCHAIN_AVAILABLE:
            self._initialize_rag_system()

    def _initialize_rag_system(self):
        """Initialize RAG system for root cause analysis"""
        try:
            # In production, this would connect to a proper vector database
            # For now, we'll create a simple FAISS index with mock data
            documents = [
                f"Case {case['case_id']}: {case['component']} failure in {case['vehicle_model']} "
                f"with symptoms {', '.join(case['symptoms'])}. Root cause: {case['root_cause']}. "
                f"Action taken: {case['repair_action']}"
                for case in self.historical_cases
            ]

            if documents:
                embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key) if self.openai_api_key else None
                if embeddings:
                    self.rag_system = FAISS.from_texts(documents, embeddings)
                    self.logger.info("RAG system initialized successfully")
                else:
                    self.logger.warning("OpenAI API key not found, RAG system disabled")
        except Exception as e:
            self.logger.warning(f"Failed to initialize RAG system: {e}")

    @tool
    def predict_battery_failure(self, features: Dict) -> Dict:
        """Predict battery failure using XGBoost model."""
        try:
            # Extract battery-specific features
            battery_features = {
                "voltage_avg": features.get("battery_voltage_avg", 12.0),
                "voltage_min": features.get("battery_voltage_min", 11.5),
                "age_months": features.get("battery_age_months", 24),
                "cranking_performance": features.get("cranking_performance", 0.8),
                "temperature_cycles": features.get("temperature_cycles", 100),
            }

            # Mock ML prediction (in production, load actual XGBoost model)
            if ML_AVAILABLE and os.path.exists(self.model_paths.get("battery", "")):
                # Load and use actual model
                model = joblib.load(self.model_paths["battery"])
                feature_vector = np.array(list(battery_features.values())).reshape(1, -1)
                probability = float(model.predict_proba(feature_vector)[0][1])
            else:
                # Fallback logic-based prediction
                voltage_factor = max(0, (12.6 - battery_features["voltage_avg"]) / 1.1)
                age_factor = min(1.0, battery_features["age_months"] / 48.0)
                cranking_factor = max(0, (1.0 - battery_features["cranking_performance"]))

                probability = min(0.95, (voltage_factor * 0.4 + age_factor * 0.4 + cranking_factor * 0.2))

            # Calculate time to failure
            if probability > 0.8:
                time_to_failure = max(1, int(30 * (1 - probability)))
            else:
                time_to_failure = max(30, int(180 * (1 - probability)))

            confidence = min(0.95, 0.6 + (probability * 0.35))

            return {
                "probability": round(probability, 3),
                "time_to_failure_days": time_to_failure,
                "confidence": round(confidence, 3),
                "model_version": "v2.3.1",
            }

        except Exception as e:
            self.logger.error(f"Battery prediction failed: {e}")
            return {"probability": 0.0, "time_to_failure_days": 365, "confidence": 0.1}

    @tool
    def predict_transmission_failure(self, features: Dict) -> Dict:
        """Predict transmission failure using ML model."""
        try:
            transmission_features = {
                "fluid_temperature": features.get("transmission_temp_avg", 80),
                "shift_quality": features.get("shift_quality_score", 0.9),
                "fluid_level": features.get("transmission_fluid_level", 1.0),
                "mileage": features.get("odometer_reading", 50000),
                "service_interval": features.get("last_service_km", 10000),
            }

            # Mock prediction logic
            temp_factor = max(0, (transmission_features["fluid_temperature"] - 90) / 50)
            shift_factor = max(0, (1.0 - transmission_features["shift_quality"]))
            mileage_factor = min(1.0, transmission_features["mileage"] / 200000)
            service_factor = min(1.0, transmission_features["service_interval"] / 50000)

            probability = min(0.9, temp_factor * 0.3 + shift_factor * 0.4 + mileage_factor * 0.2 + service_factor * 0.1)

            time_to_failure = max(7, int(365 * (1 - probability)))
            confidence = min(0.9, 0.5 + (probability * 0.4))

            return {
                "probability": round(probability, 3),
                "time_to_failure_days": time_to_failure,
                "confidence": round(confidence, 3),
                "model_version": "v2.1.0",
            }

        except Exception as e:
            self.logger.error(f"Transmission prediction failed: {e}")
            return {"probability": 0.0, "time_to_failure_days": 365, "confidence": 0.1}

    @tool
    def predict_brake_failure(self, features: Dict) -> Dict:
        """Predict brake pad wear and failure."""
        try:
            brake_features = {
                "pad_thickness": features.get("brake_pad_thickness_mm", 8.0),
                "brake_temperature": features.get("brake_temp_max", 200),
                "braking_frequency": features.get("hard_braking_events", 5),
                "mileage_since_service": features.get("brake_service_km", 15000),
            }

            # Critical safety component - more conservative prediction
            thickness_factor = max(0, (8.0 - brake_features["pad_thickness"]) / 6.0)
            temp_factor = max(0, (brake_features["brake_temperature"] - 300) / 200)
            frequency_factor = min(1.0, brake_features["braking_frequency"] / 20)
            service_factor = min(1.0, brake_features["mileage_since_service"] / 30000)

            probability = min(
                0.95, thickness_factor * 0.5 + temp_factor * 0.2 + frequency_factor * 0.15 + service_factor * 0.15
            )

            # More urgent timeline for safety-critical component
            if probability > 0.7:
                time_to_failure = max(3, int(14 * (1 - probability)))
            else:
                time_to_failure = max(14, int(90 * (1 - probability)))

            confidence = min(0.95, 0.7 + (probability * 0.25))

            return {
                "probability": round(probability, 3),
                "time_to_failure_days": time_to_failure,
                "confidence": round(confidence, 3),
                "model_version": "v2.2.0",
            }

        except Exception as e:
            self.logger.error(f"Brake prediction failed: {e}")
            return {"probability": 0.0, "time_to_failure_days": 90, "confidence": 0.1}

    @tool
    def assign_priority(self, probability: float, component: str, time_to_failure: int) -> str:
        """Assign priority level P0/P1/P2/P3 based on probability, timeline, and safety impact."""
        try:
            safety_multiplier = self.safety_critical_components.get(component, 0.5)

            # P0 (Critical): High probability + short timeline + safety critical
            if (probability > 0.9 and time_to_failure < 7) or (
                probability > 0.8 and time_to_failure < 3 and safety_multiplier >= 0.8
            ):
                return "P0"

            # P1 (High): High probability + moderate timeline
            elif (probability > 0.7 and time_to_failure < 14) or (
                probability > 0.6 and time_to_failure < 7 and safety_multiplier >= 0.7
            ):
                return "P1"

            # P2 (Medium): Moderate probability + reasonable timeline
            elif (probability > 0.5 and time_to_failure < 30) or (probability > 0.4 and safety_multiplier >= 0.8):
                return "P2"

            # P3 (Low): Preventive maintenance
            else:
                return "P3"

        except Exception as e:
            self.logger.error(f"Priority assignment failed: {e}")
            return "P3"

    @tool
    def generate_root_cause(self, component: str, features: Dict, vehicle_model: str) -> str:
        """Generate root cause hypothesis using RAG."""
        try:
            if self.rag_system and LANGCHAIN_AVAILABLE:
                # Use RAG system to find similar cases
                query = f"Root cause analysis for {component} failure in {vehicle_model} with features: {features}"
                docs = self.rag_system.similarity_search(query, k=2)

                if docs:
                    similar_cases = [doc.page_content for doc in docs]
                    return f"Based on similar cases: {'; '.join(similar_cases[:2])}"

            # Fallback to rule-based root cause analysis
            return self._fallback_root_cause_analysis(component, features, vehicle_model)

        except Exception as e:
            self.logger.error(f"Root cause generation failed: {e}")
            return self._fallback_root_cause_analysis(component, features, vehicle_model)

    def _fallback_root_cause_analysis(self, component: str, features: Dict, vehicle_model: str) -> str:
        """Fallback root cause analysis when RAG is not available"""
        root_causes = {
            "battery": "Battery aging and terminal corrosion based on voltage patterns",
            "transmission": "Transmission fluid degradation and internal wear",
            "brakes": "Brake pad wear beyond safe limits due to usage patterns",
            "engine": "Engine wear and thermal stress from operating conditions",
            "cooling_system": "Coolant system degradation and component aging",
        }

        base_cause = root_causes.get(component, f"{component} component degradation")

        # Find similar historical cases
        similar_cases = [case["case_id"] for case in self.historical_cases if case["component"] == component]

        if similar_cases:
            return f"{base_cause}. Similar cases: {', '.join(similar_cases[:2])}"
        else:
            return base_cause

    @tool
    def estimate_repair_cost(self, component: str, vehicle_model: str) -> Dict:
        """Estimate repair cost and duration."""
        try:
            base_costs = self.cost_database.get(
                component, {"parts_cost": 5000, "labor_cost": 3000, "duration_hours": 2.0}
            )

            # Adjust costs based on vehicle model (luxury vs economy)
            luxury_brands = ["BMW", "Mercedes", "Audi", "Jaguar"]
            economy_brands = ["Maruti", "Hyundai", "Tata", "Mahindra"]

            multiplier = 1.0
            if any(brand in vehicle_model for brand in luxury_brands):
                multiplier = 1.5
            elif any(brand in vehicle_model for brand in economy_brands):
                multiplier = 0.8

            parts_cost = int(base_costs["parts_cost"] * multiplier)
            labor_cost = int(base_costs["labor_cost"] * multiplier)
            total_cost = parts_cost + labor_cost

            return {
                "parts_cost": parts_cost,
                "labor_cost": labor_cost,
                "total_cost": total_cost,
                "duration_hours": base_costs["duration_hours"],
            }

        except Exception as e:
            self.logger.error(f"Cost estimation failed: {e}")
            return {"parts_cost": 5000, "labor_cost": 3000, "total_cost": 8000, "duration_hours": 2.0}

    @tool
    def find_similar_cases(self, component: str, symptoms: List[str]) -> List[Dict]:
        """Find similar historical cases."""
        try:
            similar_cases = []

            for case in self.historical_cases:
                if case["component"] == component:
                    # Calculate similarity based on symptoms overlap
                    case_symptoms = set(case["symptoms"])
                    query_symptoms = set(symptoms)

                    if case_symptoms.intersection(query_symptoms):
                        similarity_score = len(case_symptoms.intersection(query_symptoms)) / len(
                            case_symptoms.union(query_symptoms)
                        )

                        similar_cases.append(
                            {
                                "case_id": case["case_id"],
                                "vehicle_model": case["vehicle_model"],
                                "repair_action": case["repair_action"],
                                "outcome": case["outcome"],
                                "similarity_score": round(similarity_score, 2),
                            }
                        )

            # Sort by similarity score
            similar_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
            return similar_cases[:3]  # Return top 3 similar cases

        except Exception as e:
            self.logger.error(f"Similar cases search failed: {e}")
            return []

    async def _execute_internal(self, state: State) -> State:
        """Execute enhanced diagnosis with ML predictions and RAG integration"""
        try:
            self.logger.info(event="Enhanced diagnosis started", vehicle_id=state.get("vehicle_id", "unknown"))

            # Get analysis results from previous agent
            analysis_results = state.get("analysis_results")
            if not analysis_results:
                self.logger.warning(
                    event="No analysis results available for enhanced diagnosis",
                    vehicle_id=state.get("vehicle_id", "unknown"),
                )
                return state

            # Extract features for ML models
            features = self._extract_features(analysis_results, state)
            vehicle_model = state.get("vehicle_make", "Unknown") + " " + state.get("vehicle_model", "")

            # Run ML predictions for all components
            predictions = []

            # Battery prediction
            battery_pred = self.predict_battery_failure(features)
            if battery_pred["probability"] > 0.5:
                priority = self.assign_priority(
                    battery_pred["probability"], "battery", battery_pred["time_to_failure_days"]
                )
                root_cause = self.generate_root_cause("battery", features, vehicle_model)
                cost_estimate = self.estimate_repair_cost("battery", vehicle_model)
                similar_cases = self.find_similar_cases("battery", ["low_voltage", "slow_cranking"])

                predictions.append(
                    {
                        "component": "battery",
                        "failure_probability": battery_pred["probability"],
                        "confidence": battery_pred["confidence"],
                        "time_to_failure_days": battery_pred["time_to_failure_days"],
                        "priority": priority,
                        "root_cause_hypothesis": root_cause,
                        "recommended_action": "Replace battery with new 12V unit",
                        "estimated_cost_inr": cost_estimate["total_cost"],
                        "estimated_duration_hours": cost_estimate["duration_hours"],
                        "parts_available": True,
                        "similar_cases": similar_cases,
                    }
                )

            # Transmission prediction
            transmission_pred = self.predict_transmission_failure(features)
            if transmission_pred["probability"] > 0.5:
                priority = self.assign_priority(
                    transmission_pred["probability"], "transmission", transmission_pred["time_to_failure_days"]
                )
                root_cause = self.generate_root_cause("transmission", features, vehicle_model)
                cost_estimate = self.estimate_repair_cost("transmission", vehicle_model)

                predictions.append(
                    {
                        "component": "transmission",
                        "failure_probability": transmission_pred["probability"],
                        "confidence": transmission_pred["confidence"],
                        "time_to_failure_days": transmission_pred["time_to_failure_days"],
                        "priority": priority,
                        "root_cause_hypothesis": root_cause,
                        "recommended_action": "Service transmission fluid and inspect internal components",
                        "estimated_cost_inr": cost_estimate["total_cost"],
                        "estimated_duration_hours": cost_estimate["duration_hours"],
                        "parts_available": True,
                    }
                )

            # Brake prediction
            brake_pred = self.predict_brake_failure(features)
            if brake_pred["probability"] > 0.5:
                priority = self.assign_priority(brake_pred["probability"], "brakes", brake_pred["time_to_failure_days"])
                root_cause = self.generate_root_cause("brakes", features, vehicle_model)
                cost_estimate = self.estimate_repair_cost("brakes", vehicle_model)
                similar_cases = self.find_similar_cases("brakes", ["squealing", "reduced_stopping_power"])

                predictions.append(
                    {
                        "component": "brakes",
                        "failure_probability": brake_pred["probability"],
                        "confidence": brake_pred["confidence"],
                        "time_to_failure_days": brake_pred["time_to_failure_days"],
                        "priority": priority,
                        "root_cause_hypothesis": root_cause,
                        "recommended_action": "Replace brake pads and inspect rotors",
                        "estimated_cost_inr": cost_estimate["total_cost"],
                        "estimated_duration_hours": cost_estimate["duration_hours"],
                        "parts_available": True,
                        "similar_cases": similar_cases,
                    }
                )

            # Sort predictions by priority (P0 > P1 > P2 > P3)
            priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
            predictions.sort(key=lambda x: priority_order.get(x["priority"], 4))

            # Take top 3 most critical predictions
            top_predictions = predictions[:3]

            # Create enhanced prediction result
            enhanced_prediction = {
                "predictions": top_predictions,
                "model_version": "v2.3.1",
                "total_components_analyzed": len(["battery", "transmission", "brakes"]),
                "high_risk_components": len([p for p in top_predictions if p["priority"] in ["P0", "P1"]]),
                "analysis_timestamp": datetime.now().isoformat(),
            }

            # Update state with enhanced predictions
            state["enhanced_diagnosis"] = enhanced_prediction
            state["prediction"] = self._create_legacy_prediction(top_predictions)

            self.logger.info(
                event="Enhanced diagnosis completed",
                vehicle_id=state.get("vehicle_id", "unknown"),
                predictions_count=len(top_predictions),
                high_risk_count=enhanced_prediction["high_risk_components"],
            )

            return state

        except Exception as e:
            self.logger.error(
                event="Enhanced diagnosis failed", vehicle_id=state.get("vehicle_id", "unknown"), error=str(e)
            )
            return state

    def _extract_features(self, analysis_results: Dict, state: State) -> Dict:
        """Extract features from analysis results for ML models"""
        features = {}

        # Ensure analysis_results is not None
        if not analysis_results:
            analysis_results = {}

        # Extract telemetry features
        telemetry = analysis_results.get("telemetry_summary", {})
        if not telemetry:
            telemetry = {}

        features.update(
            {
                "battery_voltage_avg": (
                    telemetry.get("battery_voltage", {}).get("avg", 12.0) if telemetry.get("battery_voltage") else 12.0
                ),
                "battery_voltage_min": (
                    telemetry.get("battery_voltage", {}).get("min", 11.5) if telemetry.get("battery_voltage") else 11.5
                ),
                "engine_temp_avg": (
                    telemetry.get("engine_temperature", {}).get("avg", 90)
                    if telemetry.get("engine_temperature")
                    else 90
                ),
                "engine_temp_max": (
                    telemetry.get("engine_temperature", {}).get("max", 110)
                    if telemetry.get("engine_temperature")
                    else 110
                ),
                "brake_temp_max": (
                    telemetry.get("brake_temperature", {}).get("max", 200)
                    if telemetry.get("brake_temperature")
                    else 200
                ),
                "transmission_temp_avg": (
                    telemetry.get("transmission_temperature", {}).get("avg", 80)
                    if telemetry.get("transmission_temperature")
                    else 80
                ),
            }
        )

        # Extract vehicle information
        features.update(
            {
                "odometer_reading": state.get("odometer_reading", 50000),
                "vehicle_age_years": state.get("vehicle_age_years", 3),
                "last_service_km": state.get("last_service_km", 10000),
            }
        )

        # Extract computed features
        computed_features = analysis_results.get("computed_features", {})
        if not computed_features:
            computed_features = {}

        features.update(
            {
                "health_score": computed_features.get("overall_health_score", 0.8),
                "anomaly_count": len(analysis_results.get("anomalies", [])),
                "warning_count": len(analysis_results.get("warnings", [])),
            }
        )

        return features

    def _create_legacy_prediction(self, predictions: List[Dict]) -> Optional[PredictionResult]:
        """Create legacy prediction format for backward compatibility"""
        if not predictions:
            return None

        top_prediction = predictions[0]

        # Map priority string to Priority enum
        priority_map = {"P0": Priority.P0, "P1": Priority.P1, "P2": Priority.P2, "P3": Priority.P3}

        return PredictionResult(
            component=top_prediction["component"],
            failure_probability=top_prediction["failure_probability"],
            predicted_failure_date=datetime.now() + timedelta(days=top_prediction["time_to_failure_days"]),
            recommended_action=top_prediction["recommended_action"],
            priority=priority_map.get(top_prediction["priority"], Priority.P3),
            confidence_score=top_prediction["confidence"],
            estimated_cost=top_prediction["estimated_cost_inr"],
        )
