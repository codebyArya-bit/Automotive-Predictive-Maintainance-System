"""
Data Analysis Agent - Processes vehicle telemetry data and performs initial analysis
"""

import asyncio
import random
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent
from state import State, TelemetryData


class DataAnalysisAgent(BaseAgent):
    """Agent responsible for analyzing vehicle telemetry data"""

    def __init__(self):
        super().__init__("data_analysis")

        # Thresholds for various components
        self.thresholds = {
            "engine_temperature": {"normal": (80, 105), "warning": (105, 120), "critical": 120},
            "oil_pressure": {"normal": (25, 80), "warning": (15, 25), "critical": 15},
            "brake_pad_thickness": {"normal": 8.0, "warning": 4.0, "critical": 2.0},
            "tire_pressure": {"normal": (30, 35), "warning": (25, 30), "critical": 25},
            "battery_voltage": {"normal": (12.4, 14.4), "warning": (11.8, 12.4), "critical": 11.8},
            "transmission_fluid_level": {"normal": 0.8, "warning": 0.5, "critical": 0.3},
        }

    async def _execute_internal(self, state: State) -> State:
        """Analyze vehicle telemetry data"""
        self.logger.info("Starting telemetry data analysis", vehicle_id=state["vehicle_id"])

        # Simulate fetching telemetry data if not present
        if not state["telemetry_snapshot"]:
            state["telemetry_snapshot"] = await self._fetch_telemetry_data(state["vehicle_id"])

        # Perform analysis
        analysis_results = await self._analyze_telemetry(state["telemetry_snapshot"])

        # Store analysis results
        state["analysis_results"] = analysis_results

        # Add log message
        state = self._add_log_message(
            state,
            f"Telemetry analysis completed. Found {len(analysis_results['anomalies'])} anomalies.",
            {"analysis_summary": analysis_results["summary"]},
        )

        return state

    async def _fetch_telemetry_data(self, vehicle_id: str) -> TelemetryData:
        """Simulate fetching telemetry data from vehicle systems"""
        # Simulate API call delay
        await asyncio.sleep(0.5)

        # Generate realistic telemetry data
        current_time = datetime.now().isoformat()

        # Simulate some variation in data
        base_values = {
            "engine_temperature": 95 + random.normalvariate(0, 5),
            "oil_pressure": 45 + random.normalvariate(0, 8),
            "brake_pad_thickness": 6.5 + random.normalvariate(0, 1.5),
            "battery_voltage": 13.2 + random.normalvariate(0, 0.3),
            "transmission_fluid_level": 0.85 + random.normalvariate(0, 0.1),
            "mileage": 45000 + random.randint(0, 5000),
        }

        # Occasionally introduce anomalies for testing
        if random.random() < 0.3:  # 30% chance of anomaly
            anomaly_type = random.choice(["high_temp", "low_oil", "worn_brakes"])
            if anomaly_type == "high_temp":
                base_values["engine_temperature"] = 115 + random.normalvariate(0, 3)
            elif anomaly_type == "low_oil":
                base_values["oil_pressure"] = 18 + random.normalvariate(0, 2)
            elif anomaly_type == "worn_brakes":
                base_values["brake_pad_thickness"] = 3.0 + random.normalvariate(0, 0.5)

        return TelemetryData(
            timestamp=current_time,
            engine_temperature=base_values["engine_temperature"],
            oil_pressure=base_values["oil_pressure"],
            brake_pad_thickness=base_values["brake_pad_thickness"],
            tire_pressure={
                "front_left": 32.0 + random.normalvariate(0, 1),
                "front_right": 32.0 + random.normalvariate(0, 1),
                "rear_left": 30.0 + random.normalvariate(0, 1),
                "rear_right": 30.0 + random.normalvariate(0, 1),
            },
            battery_voltage=base_values["battery_voltage"],
            transmission_fluid_level=base_values["transmission_fluid_level"],
            mileage=int(base_values["mileage"]),
            error_codes=self._generate_error_codes(),
        )

    def _generate_error_codes(self) -> List[str]:
        """Generate realistic error codes"""
        possible_codes = ["P0300", "P0420", "P0171", "P0174", "P0128", "B1234", "C1201", "U0100", "P0456", "P0442"]

        # 70% chance of no error codes
        if random.random() < 0.7:
            return []

        # Return 1 - 3 error codes
        num_codes = random.randint(1, 3)
        return random.sample(possible_codes, num_codes)

    async def _analyze_telemetry(self, telemetry: TelemetryData) -> Dict[str, Any]:
        """Analyze telemetry data for anomalies and patterns"""
        anomalies = []
        warnings = []

        # Add null check for telemetry data
        if telemetry is None:
            self.logger.error("Telemetry data is None")
            return {
                "anomalies": [],
                "warnings": [],
                "health_score": 0,
                "summary": "No telemetry data available",
                "error_codes": [],
            }

        # Extract telemetry dict if it's wrapped
        if isinstance(telemetry, dict) and "telemetry" in telemetry:
            telemetry_data = telemetry["telemetry"]
        else:
            telemetry_data = telemetry

        # Additional null check for extracted telemetry data
        if telemetry_data is None:
            self.logger.error("Extracted telemetry data is None")
            return {
                "anomalies": [],
                "warnings": [],
                "health_score": 0,
                "summary": "No telemetry data available",
                "error_codes": [],
            }

        # Simulate anomaly detection using simple statistical methods
        simple_anomalies = []

        # Check for extreme values using simple thresholds
        if telemetry_data.get("engine_temperature", 0) > 100:
            simple_anomalies.append(
                {
                    "parameter": "engine_temperature",
                    "value": telemetry_data["engine_temperature"],
                    "severity": "high",
                    "description": "Engine temperature exceeds normal range",
                }
            )

        if telemetry_data.get("brake_pad_thickness", 10) < 2:
            simple_anomalies.append(
                {
                    "parameter": "brake_pad_thickness",
                    "value": telemetry_data["brake_pad_thickness"],
                    "severity": "high",
                    "description": "Brake pad thickness critically low",
                }
            )

        if telemetry_data.get("oil_pressure", 50) < 20:
            simple_anomalies.append(
                {
                    "parameter": "oil_pressure",
                    "value": telemetry_data["oil_pressure"],
                    "severity": "medium",
                    "description": "Oil pressure below recommended level",
                }
            )

        # Analyze engine temperature
        temp = telemetry_data.get("engine_temperature", 0)
        if temp > self.thresholds["engine_temperature"]["critical"]:
            anomalies.append(
                {
                    "component": "engine",
                    "parameter": "temperature",
                    "value": temp,
                    "severity": "critical",
                    "message": f"Engine temperature critically high: {temp:.1f}°C",
                }
            )
        elif temp > self.thresholds["engine_temperature"]["warning"][1]:
            warnings.append(
                {
                    "component": "engine",
                    "parameter": "temperature",
                    "value": temp,
                    "severity": "warning",
                    "message": f"Engine temperature elevated: {temp:.1f}°C",
                }
            )

        # Merge simple anomalies with detailed analysis
        for simple_anomaly in simple_anomalies:
            anomalies.append(
                {
                    "component": "system",
                    "parameter": simple_anomaly["parameter"],
                    "value": simple_anomaly["value"],
                    "severity": simple_anomaly["severity"],
                    "message": simple_anomaly["description"],
                }
            )

        # Analyze oil pressure
        oil_pressure = telemetry_data.get("oil_pressure", 0)
        if oil_pressure < self.thresholds["oil_pressure"]["critical"]:
            anomalies.append(
                {
                    "component": "engine",
                    "parameter": "oil_pressure",
                    "value": oil_pressure,
                    "severity": "critical",
                    "message": f"Oil pressure critically low: {oil_pressure:.1f} PSI",
                }
            )
        elif oil_pressure < self.thresholds["oil_pressure"]["warning"][0]:
            warnings.append(
                {
                    "component": "engine",
                    "parameter": "oil_pressure",
                    "value": oil_pressure,
                    "severity": "warning",
                    "message": f"Oil pressure low: {oil_pressure:.1f} PSI",
                }
            )

        # Analyze brake pad thickness
        brake_thickness = telemetry_data.get("brake_pad_thickness", 10)
        if brake_thickness < self.thresholds["brake_pad_thickness"]["critical"]:
            anomalies.append(
                {
                    "component": "brakes",
                    "parameter": "pad_thickness",
                    "value": brake_thickness,
                    "severity": "critical",
                    "message": f"Brake pads critically worn: {brake_thickness:.1f}mm",
                }
            )
        elif brake_thickness < self.thresholds["brake_pad_thickness"]["warning"]:
            warnings.append(
                {
                    "component": "brakes",
                    "parameter": "pad_thickness",
                    "value": brake_thickness,
                    "severity": "warning",
                    "message": f"Brake pads worn: {brake_thickness:.1f}mm",
                }
            )

        # Analyze tire pressures - handle both nested dict and individual fields
        tire_pressures = {}
        if "tire_pressure" in telemetry_data and isinstance(telemetry_data["tire_pressure"], dict):
            # Handle nested tire pressure dict
            tire_pressures = telemetry_data["tire_pressure"]
        else:
            # Handle individual tire pressure fields
            tire_fields = ["tire_pressure_fl", "tire_pressure_fr", "tire_pressure_rl", "tire_pressure_rr"]
            for field in tire_fields:
                if field in telemetry_data:
                    tire_name = field.replace("tire_pressure_", "")
                    tire_pressures[tire_name] = telemetry_data[field]

        for tire, pressure in tire_pressures.items():
            if pressure < self.thresholds["tire_pressure"]["critical"]:
                anomalies.append(
                    {
                        "component": "tires",
                        "parameter": f"{tire}_pressure",
                        "value": pressure,
                        "severity": "critical",
                        "message": f"{tire.replace('_', ' ').title()} tire pressure critically low: {pressure:.1f} PSI",
                    }
                )
            elif pressure < self.thresholds["tire_pressure"]["warning"][0]:
                warnings.append(
                    {
                        "component": "tires",
                        "parameter": f"{tire}_pressure",
                        "value": pressure,
                        "severity": "warning",
                        "message": f"{tire.replace('_', ' ').title()} tire pressure low: {pressure:.1f} PSI",
                    }
                )

        # Analyze battery voltage
        battery_voltage = telemetry_data.get("battery_voltage", 12.0)
        if battery_voltage < self.thresholds["battery_voltage"]["critical"]:
            anomalies.append(
                {
                    "component": "electrical",
                    "parameter": "battery_voltage",
                    "value": battery_voltage,
                    "severity": "critical",
                    "message": f"Battery voltage critically low: {battery_voltage:.1f}V",
                }
            )
        elif battery_voltage < self.thresholds["battery_voltage"]["warning"][0]:
            warnings.append(
                {
                    "component": "electrical",
                    "parameter": "battery_voltage",
                    "value": battery_voltage,
                    "severity": "warning",
                    "message": f"Battery voltage low: {battery_voltage:.1f}V",
                }
            )

        # Analyze error codes
        error_code_analysis = []
        error_codes = telemetry_data.get("error_codes", [])
        for code in error_codes:
            error_code_analysis.append(
                {
                    "code": code,
                    "description": self._get_error_code_description(code),
                    "severity": self._get_error_code_severity(code),
                }
            )

        # Calculate overall health score
        health_score = self._calculate_health_score(anomalies, warnings, telemetry)

        return {
            "timestamp": datetime.now().isoformat(),
            "vehicle_id": telemetry.get("vehicle_id", "unknown"),
            "health_score": health_score,
            "anomalies": anomalies,
            "warnings": warnings,
            "error_codes": error_code_analysis,
            "summary": {
                "total_anomalies": len(anomalies),
                "total_warnings": len(warnings),
                "critical_issues": len([a for a in anomalies if a["severity"] == "critical"]),
                "components_affected": list(set([a["component"] for a in anomalies + warnings])),
            },
        }

    def _get_error_code_description(self, code: str) -> str:
        """Get description for error codes"""
        descriptions = {
            "P0300": "Random/Multiple Cylinder Misfire Detected",
            "P0420": "Catalyst System Efficiency Below Threshold",
            "P0171": "System Too Lean (Bank 1)",
            "P0174": "System Too Lean (Bank 2)",
            "P0128": "Coolant Thermostat (Coolant Temperature Below Thermostat Regulating Temperature)",
            "B1234": "Body Control Module Communication Error",
            "C1201": "Engine Control System Malfunction",
            "U0100": "Lost Communication With ECM/PCM",
            "P0456": "Evaporative Emission Control System Leak Detected (Very Small Leak)",
            "P0442": "Evaporative Emission Control System Leak Detected (Small Leak)",
        }
        return descriptions.get(code, f"Unknown error code: {code}")

    def _get_error_code_severity(self, code: str) -> str:
        """Determine severity of error codes"""
        critical_codes = ["P0300", "C1201", "U0100"]
        warning_codes = ["P0420", "P0171", "P0174", "P0128", "B1234"]

        if code in critical_codes:
            return "critical"
        elif code in warning_codes:
            return "warning"
        else:
            return "info"

    def _calculate_health_score(self, anomalies: List[Dict], warnings: List[Dict], telemetry: TelemetryData) -> float:
        """Calculate overall vehicle health score (0 - 100)"""
        base_score = 100.0

        # Extract error codes safely from telemetry
        if telemetry is None:
            telemetry_data = {}
        elif isinstance(telemetry, dict) and "telemetry" in telemetry:
            telemetry_data = telemetry["telemetry"]
        else:
            telemetry_data = telemetry

        error_codes = telemetry_data.get("error_codes", []) if isinstance(telemetry_data, dict) else []

        # Deduct points for anomalies and warnings
        for anomaly in anomalies:
            if anomaly["severity"] == "critical":
                base_score -= 20
            else:
                base_score -= 10

        for warning in warnings:
            base_score -= 5

        # Deduct points for error codes
        for code in error_codes:
            severity = self._get_error_code_severity(code)
            if severity == "critical":
                base_score -= 15
            elif severity == "warning":
                base_score -= 8
            else:
                base_score -= 3

        # Ensure score doesn't go below 0
        return max(0.0, base_score)
