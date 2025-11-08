"""
UEBA Monitoring Agent - Tracks user behavior and system activities for security compliance
"""

import asyncio
import random
from typing import Dict, Any, List
from datetime import datetime, timedelta
import hashlib

from .base_agent import BaseAgent
from state import State, Priority


class UEBAMonitoringAgent(BaseAgent):
    """Agent responsible for User and Entity Behavior Analytics (UEBA) monitoring"""

    def __init__(self):
        super().__init__("ueba_monitoring")

        # UEBA risk thresholds
        self.risk_thresholds = {"low": 0.3, "medium": 0.6, "high": 0.8, "critical": 0.95}

        # Behavioral patterns to monitor
        self.monitored_patterns = {
            "access_patterns": {
                "unusual_hours": {"weight": 0.4, "threshold": 0.7},
                "geographic_anomaly": {"weight": 0.6, "threshold": 0.8},
                "frequency_deviation": {"weight": 0.3, "threshold": 0.6},
            },
            "data_access": {
                "sensitive_data_access": {"weight": 0.8, "threshold": 0.9},
                "bulk_data_retrieval": {"weight": 0.7, "threshold": 0.8},
                "unauthorized_queries": {"weight": 0.9, "threshold": 0.95},
            },
            "system_behavior": {
                "failed_authentications": {"weight": 0.6, "threshold": 0.7},
                "privilege_escalation": {"weight": 0.9, "threshold": 0.95},
                "unusual_api_usage": {"weight": 0.5, "threshold": 0.6},
            },
            "agent_behavior": {
                "execution_anomalies": {"weight": 0.7, "threshold": 0.8},
                "error_rate_spikes": {"weight": 0.5, "threshold": 0.7},
                "resource_consumption": {"weight": 0.4, "threshold": 0.6},
            },
        }

        # Compliance frameworks
        self.compliance_frameworks = {
            "SOX": {"requirements": ["data_integrity", "access_controls", "audit_trails"], "severity_multiplier": 1.2},
            "GDPR": {
                "requirements": ["data_protection", "privacy_controls", "consent_tracking"],
                "severity_multiplier": 1.5,
            },
            "ISO27001": {
                "requirements": ["security_controls", "risk_management", "incident_response"],
                "severity_multiplier": 1.1,
            },
            "NIST": {
                "requirements": ["cybersecurity_framework", "risk_assessment", "continuous_monitoring"],
                "severity_multiplier": 1.0,
            },
        }

        # Baseline behavior profiles (simulated)
        self.baseline_profiles = self._initialize_baseline_profiles()

    def _initialize_baseline_profiles(self) -> Dict[str, Any]:
        """Initialize baseline behavior profiles for comparison"""
        return {
            "normal_access_hours": {"start": 8, "end": 18},  # 8 AM to 6 PM
            "typical_session_duration": {"min": 15, "max": 240},  # 15 min to 4 hours
            "average_api_calls_per_session": 50,
            "normal_data_volume": {"min": 1024, "max": 10485760},  # 1KB to 10MB
            "expected_error_rate": 0.02,  # 2% error rate
            "standard_geographic_locations": ["US-East", "US-West", "EU-Central"],
            "authorized_user_agents": ["MasterAgent", "DataAnalysis", "Diagnosis", "CustomerEngagement"],
        }

    async def _execute_internal(self, state: State) -> State:
        """Perform UEBA monitoring and risk assessment"""
        self.logger.info("Starting UEBA monitoring analysis", vehicle_id=state["vehicle_id"])

        # Collect current session behavior data
        session_data = await self._collect_session_behavior(state)

        # Analyze behavioral anomalies
        anomaly_analysis = await self._analyze_behavioral_anomalies(session_data, state)

        # Assess security risks
        risk_assessment = await self._assess_security_risks(anomaly_analysis, state)

        # Check compliance violations
        compliance_status = await self._check_compliance_violations(session_data, risk_assessment)

        # Generate security alerts if needed
        security_alerts = await self._generate_security_alerts(risk_assessment, compliance_status)

        # Calculate overall risk score
        overall_risk_score = self._calculate_overall_risk_score(risk_assessment)

        # Update state with UEBA findings
        ueba_monitoring = {
            "session_data": session_data,
            "anomaly_analysis": anomaly_analysis,
            "risk_assessment": risk_assessment,
            "compliance_status": compliance_status,
            "security_alerts": security_alerts,
            "overall_risk_score": overall_risk_score,
            "risk_level": self._determine_risk_level(overall_risk_score),
            "monitoring_timestamp": datetime.now().isoformat(),
        }

        state["ueba_monitoring"] = ueba_monitoring

        # Add log message
        state = self._add_log_message(
            state,
            f"UEBA monitoring completed - Risk level: {ueba_monitoring['risk_level']}",
            {
                "risk_score": overall_risk_score,
                "anomalies_detected": len(anomaly_analysis),
                "security_alerts": len(security_alerts),
                "compliance_violations": sum(1 for c in compliance_status.values() if not c["compliant"]),
            },
        )

        return state

    async def _collect_session_behavior(self, state: State) -> Dict[str, Any]:
        """Collect current session behavioral data"""
        await asyncio.sleep(0.2)

        # Simulate session data collection
        current_time = datetime.now()
        session_start = current_time - timedelta(minutes=random.randint(5, 120))

        session_data = {
            "session_id": self._generate_session_id(state),
            "user_id": f"user_{hash(state['vehicle_id']) % 1000}",
            "session_start": session_start.isoformat(),
            "session_duration": (current_time - session_start).total_seconds(),
            "access_time": current_time.hour,
            "geographic_location": random.choice(["US-East", "US-West", "EU-Central", "APAC-North"]),
            "user_agent": state.get("current_agent", "unknown"),
            "api_calls_made": self._count_api_calls(state),
            "data_accessed": self._calculate_data_volume(state),
            "authentication_attempts": random.randint(1, 3),
            "failed_authentications": random.randint(0, 1),
            "privilege_level": "standard",
            "ip_address": self._generate_ip_address(),
            "device_fingerprint": self._generate_device_fingerprint(state),
        }

        return session_data

    def _generate_session_id(self, state: State) -> str:
        """Generate unique session ID"""
        session_data = f"{state['vehicle_id']}_{datetime.now().isoformat()}"
        return hashlib.md5(session_data.encode()).hexdigest()[:16]

    def _count_api_calls(self, state: State) -> int:
        """Count API calls made during session"""
        # Simulate API call counting based on agent executions
        base_calls = 10

        if state.get("agent_executions"):
            base_calls += len(state["agent_executions"]) * 5

        if state.get("telemetry_data"):
            base_calls += 15  # Data retrieval calls

        if state.get("prediction"):
            base_calls += 8  # ML model calls

        return base_calls + random.randint(0, 20)

    def _calculate_data_volume(self, state: State) -> int:
        """Calculate volume of data accessed"""
        base_volume = 1024  # 1KB base

        if state.get("telemetry_data"):
            base_volume += 50000  # 50KB telemetry data

        if state.get("prediction"):
            base_volume += 10000  # 10KB prediction data

        if state.get("customer_response"):
            base_volume += 5000  # 5KB customer data

        return base_volume + random.randint(0, 100000)

    def _generate_ip_address(self) -> str:
        """Generate simulated IP address"""
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

    def _generate_device_fingerprint(self, state: State) -> str:
        """Generate device fingerprint"""
        device_data = f"{state['vehicle_id']}_device"
        return hashlib.sha256(device_data.encode()).hexdigest()[:32]

    async def _analyze_behavioral_anomalies(self, session_data: Dict[str, Any], state: State) -> List[Dict[str, Any]]:
        """Analyze behavioral anomalies against baseline profiles"""
        await asyncio.sleep(0.3)

        anomalies = []

        # Check access time anomalies
        access_hour = session_data["access_time"]
        normal_hours = self.baseline_profiles["normal_access_hours"]

        if access_hour < normal_hours["start"] or access_hour > normal_hours["end"]:
            anomalies.append(
                {
                    "type": "unusual_access_hours",
                    "severity": "medium",
                    "description": f"Access at {access_hour}:00 outside normal hours ({normal_hours['start']}-{normal_hours['end']})",
                    "risk_score": 0.6,
                    "evidence": {"access_hour": access_hour, "normal_range": normal_hours},
                }
            )

        # Check geographic anomalies
        if session_data["geographic_location"] not in self.baseline_profiles["standard_geographic_locations"]:
            anomalies.append(
                {
                    "type": "geographic_anomaly",
                    "severity": "high",
                    "description": f"Access from unusual location: {session_data['geographic_location']}",
                    "risk_score": 0.8,
                    "evidence": {"location": session_data["geographic_location"]},
                }
            )

        # Check API usage anomalies
        api_calls = session_data["api_calls_made"]
        expected_calls = self.baseline_profiles["average_api_calls_per_session"]

        if api_calls > expected_calls * 3:  # 3x normal usage
            anomalies.append(
                {
                    "type": "excessive_api_usage",
                    "severity": "medium",
                    "description": f"Excessive API usage: {api_calls} calls (normal: ~{expected_calls})",
                    "risk_score": 0.7,
                    "evidence": {"api_calls": api_calls, "expected": expected_calls},
                }
            )

        # Check data volume anomalies
        data_volume = session_data["data_accessed"]
        normal_volume = self.baseline_profiles["normal_data_volume"]

        if data_volume > normal_volume["max"] * 5:  # 5x normal volume
            anomalies.append(
                {
                    "type": "bulk_data_access",
                    "severity": "high",
                    "description": f"Large data volume accessed: {data_volume} bytes",
                    "risk_score": 0.8,
                    "evidence": {"data_volume": data_volume, "normal_max": normal_volume["max"]},
                }
            )

        # Check authentication anomalies
        if session_data["failed_authentications"] > 0:
            anomalies.append(
                {
                    "type": "authentication_failures",
                    "severity": "medium",
                    "description": f"{session_data['failed_authentications']} failed authentication attempts",
                    "risk_score": 0.5,
                    "evidence": {"failed_attempts": session_data["failed_authentications"]},
                }
            )

        # Check agent behavior anomalies
        if state.get("agent_executions"):
            error_count = sum(1 for exec in state["agent_executions"] if exec["status"] == "error")
            total_executions = len(state["agent_executions"])
            error_rate = error_count / total_executions if total_executions > 0 else 0

            if error_rate > self.baseline_profiles["expected_error_rate"] * 3:
                anomalies.append(
                    {
                        "type": "high_error_rate",
                        "severity": "medium",
                        "description": f"High agent error rate: {error_rate:.2%}",
                        "risk_score": 0.6,
                        "evidence": {"error_rate": error_rate, "errors": error_count, "total": total_executions},
                    }
                )

        return anomalies

    async def _assess_security_risks(self, anomalies: List[Dict[str, Any]], state: State) -> Dict[str, Any]:
        """Assess security risks based on anomalies and context"""
        await asyncio.sleep(0.2)

        risk_categories = {
            "data_exfiltration": 0.0,
            "unauthorized_access": 0.0,
            "privilege_escalation": 0.0,
            "insider_threat": 0.0,
            "system_compromise": 0.0,
        }

        # Assess risks based on anomalies
        for anomaly in anomalies:
            anomaly_type = anomaly["type"]
            risk_score = anomaly["risk_score"]

            if anomaly_type in ["bulk_data_access", "excessive_api_usage"]:
                risk_categories["data_exfiltration"] = max(risk_categories["data_exfiltration"], risk_score)

            if anomaly_type in ["geographic_anomaly", "authentication_failures"]:
                risk_categories["unauthorized_access"] = max(risk_categories["unauthorized_access"], risk_score)

            if anomaly_type in ["unusual_access_hours", "high_error_rate"]:
                risk_categories["insider_threat"] = max(risk_categories["insider_threat"], risk_score * 0.8)

            if anomaly_type in ["excessive_api_usage", "high_error_rate"]:
                risk_categories["system_compromise"] = max(risk_categories["system_compromise"], risk_score * 0.7)

        # Additional context-based risk assessment
        if state.get("prediction") and state["prediction"]["priority"] == Priority.P0:
            # Critical predictions might indicate system manipulation
            risk_categories["system_compromise"] += 0.3

        if state.get("escalate_to_human"):
            # Escalations might indicate suspicious activity
            risk_categories["insider_threat"] += 0.2

        # Normalize risk scores
        for category in risk_categories:
            risk_categories[category] = min(1.0, risk_categories[category])

        return {
            "risk_categories": risk_categories,
            "highest_risk_category": max(risk_categories, key=risk_categories.get),
            "risk_factors": self._identify_risk_factors(anomalies, state),
            "mitigation_recommendations": self._generate_mitigation_recommendations(risk_categories),
        }

    def _identify_risk_factors(self, anomalies: List[Dict[str, Any]], state: State) -> List[str]:
        """Identify specific risk factors"""
        risk_factors = []

        for anomaly in anomalies:
            if anomaly["severity"] == "high":
                risk_factors.append(f"High severity anomaly: {anomaly['description']}")

        if len(anomalies) > 3:
            risk_factors.append("Multiple behavioral anomalies detected simultaneously")

        if state.get("retry_count", 0) > 2:
            risk_factors.append("Multiple retry attempts indicating potential system probing")

        return risk_factors

    def _generate_mitigation_recommendations(self, risk_categories: Dict[str, float]) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []

        for category, score in risk_categories.items():
            if score > 0.7:
                if category == "data_exfiltration":
                    recommendations.append("Implement data loss prevention (DLP) controls")
                    recommendations.append("Monitor and restrict bulk data access")
                elif category == "unauthorized_access":
                    recommendations.append("Strengthen authentication mechanisms")
                    recommendations.append("Implement geographic access controls")
                elif category == "insider_threat":
                    recommendations.append("Enhance user behavior monitoring")
                    recommendations.append("Implement privileged access management")
                elif category == "system_compromise":
                    recommendations.append("Conduct security incident investigation")
                    recommendations.append("Implement additional system monitoring")

        return list(set(recommendations))  # Remove duplicates

    async def _check_compliance_violations(
        self, session_data: Dict[str, Any], risk_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for compliance framework violations"""
        await asyncio.sleep(0.1)

        compliance_status = {}

        for framework, requirements in self.compliance_frameworks.items():
            violations = []
            compliant = True

            # Check framework-specific requirements
            if "data_integrity" in requirements["requirements"]:
                if risk_assessment["risk_categories"]["data_exfiltration"] > 0.5:
                    violations.append("Potential data integrity compromise detected")
                    compliant = False

            if "access_controls" in requirements["requirements"]:
                if risk_assessment["risk_categories"]["unauthorized_access"] > 0.6:
                    violations.append("Access control violations detected")
                    compliant = False

            if "audit_trails" in requirements["requirements"]:
                if session_data["failed_authentications"] > 0:
                    violations.append("Authentication failures require audit trail review")
                    compliant = False

            if "privacy_controls" in requirements["requirements"]:
                if session_data["data_accessed"] > 1000000:  # 1MB threshold for GDPR
                    violations.append("Large personal data access requires privacy review")
                    compliant = False

            compliance_status[framework] = {
                "compliant": compliant,
                "violations": violations,
                "severity_multiplier": requirements["severity_multiplier"],
                "last_checked": datetime.now().isoformat(),
            }

        return compliance_status

    async def _generate_security_alerts(
        self, risk_assessment: Dict[str, Any], compliance_status: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate security alerts based on risk assessment"""
        await asyncio.sleep(0.1)

        alerts = []

        # Generate alerts for high-risk categories
        for category, score in risk_assessment["risk_categories"].items():
            if score > 0.8:
                alerts.append(
                    {
                        "alert_id": self._generate_alert_id(),
                        "type": "security_risk",
                        "category": category,
                        "severity": "high",
                        "title": f"High {category.replace('_', ' ').title()} Risk Detected",
                        "description": f"Risk score of {score:.2f} detected for {category}",
                        "timestamp": datetime.now().isoformat(),
                        "requires_immediate_action": True,
                        "recommended_actions": risk_assessment["mitigation_recommendations"],
                    }
                )

        # Generate alerts for compliance violations
        for framework, status in compliance_status.items():
            if not status["compliant"]:
                alerts.append(
                    {
                        "alert_id": self._generate_alert_id(),
                        "type": "compliance_violation",
                        "category": framework,
                        "severity": "medium" if status["severity_multiplier"] < 1.3 else "high",
                        "title": f"{framework} Compliance Violation",
                        "description": f"Violations: {', '.join(status['violations'])}",
                        "timestamp": datetime.now().isoformat(),
                        "requires_immediate_action": status["severity_multiplier"] > 1.2,
                        "recommended_actions": ["Review compliance procedures", "Conduct compliance audit"],
                    }
                )

        return alerts

    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        alert_data = f"alert_{datetime.now().isoformat()}_{random.randint(1000, 9999)}"
        return hashlib.md5(alert_data.encode()).hexdigest()[:12]

    def _calculate_overall_risk_score(self, risk_assessment: Dict[str, Any]) -> float:
        """Calculate overall risk score"""
        risk_categories = risk_assessment["risk_categories"]

        # Weighted average of risk categories
        weights = {
            "data_exfiltration": 0.25,
            "unauthorized_access": 0.25,
            "privilege_escalation": 0.20,
            "insider_threat": 0.15,
            "system_compromise": 0.15,
        }

        overall_score = sum(risk_categories[category] * weights[category] for category in risk_categories)

        return min(1.0, overall_score)

    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on score"""
        if risk_score >= self.risk_thresholds["critical"]:
            return "critical"
        elif risk_score >= self.risk_thresholds["high"]:
            return "high"
        elif risk_score >= self.risk_thresholds["medium"]:
            return "medium"
        elif risk_score >= self.risk_thresholds["low"]:
            return "low"
        else:
            return "minimal"
