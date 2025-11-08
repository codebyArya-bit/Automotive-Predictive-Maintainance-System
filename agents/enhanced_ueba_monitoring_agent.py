"""
Enhanced UEBA (User and Entity Behavior Analytics) Monitoring Agent
Advanced security monitoring with ML-based anomaly detection and automated response
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from .base_agent import BaseAgent
from state import State, Priority


# Data Models
@dataclass
class AgentAction:
    """Represents a single agent action for UEBA analysis"""

    timestamp: datetime
    agent_id: str
    action_type: str
    target_resource: str
    payload_size: int
    source_ip: str
    user_agent: str
    session_id: str
    metadata: Dict[str, Any]


class AnomalyType(Enum):
    PRIVILEGE_ESCALATION = "privilege_escalation"
    EXCESSIVE_API_CALLS = "excessive_api_calls"
    DATA_EXFILTRATION = "data_exfiltration"
    WORKFLOW_DEVIATION = "workflow_deviation"
    UNUSUAL_TIMING = "unusual_timing"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    RESOURCE_ABUSE = "resource_abuse"


class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentBaseline:
    """Behavioral baseline for an agent"""

    agent_id: str
    avg_api_calls_per_hour: float
    typical_resources_accessed: List[str]
    normal_workflow_sequence: List[str]
    usual_operating_hours: Tuple[int, int]
    average_payload_size: float
    typical_session_duration: float
    error_rate_baseline: float
    geographic_locations: List[str]
    last_updated: datetime


@dataclass
class SecurityAnomaly:
    """Detected security anomaly"""

    anomaly_id: str
    agent_id: str
    anomaly_type: AnomalyType
    severity: SeverityLevel
    confidence: float
    detected_at: datetime
    action_details: AgentAction
    baseline_deviation: Dict[str, float]
    evidence: Dict[str, Any]
    response_taken: Optional[str] = None


@dataclass
class SecurityEvent:
    """Security event for logging and reporting"""

    event_id: str
    event_type: str
    severity: SeverityLevel
    timestamp: datetime
    agent_id: str
    description: str
    evidence: Dict[str, Any]
    response_actions: List[str]
    resolved: bool = False


class EnhancedUEBAMonitoringAgent(BaseAgent):
    """Enhanced UEBA Monitoring Agent for comprehensive security monitoring"""

    def __init__(self):
        super().__init__("enhanced_ueba_monitoring")

        # Initialize mock databases
        self.ueba_logs: List[AgentAction] = []
        self.agent_baselines: Dict[str, AgentBaseline] = {}
        self.detected_anomalies: List[SecurityAnomaly] = []
        self.security_events: List[SecurityEvent] = []
        self.blocked_actions: Dict[str, str] = {}
        self.revoked_credentials: List[str] = []

        # ML Models for anomaly detection
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_model_trained = False

        # Security thresholds
        self.security_thresholds = {
            "api_call_multiplier": 3.0,  # 3x normal rate triggers alert
            "payload_size_multiplier": 5.0,  # 5x normal size triggers alert
            "off_hours_threshold": 0.8,  # Confidence threshold for off-hours detection
            "geographic_anomaly_threshold": 0.9,  # Geographic deviation threshold
            "workflow_deviation_threshold": 0.7,  # Workflow sequence deviation threshold
        }

        # Agent role permissions (for privilege escalation detection)
        self.agent_permissions = {
            "scheduling_agent": ["appointments", "service_centers", "technicians"],
            "customer_engagement_agent": ["customer_profiles", "communication_logs", "feedback"],
            "diagnosis_agent": ["telemetry_data", "diagnostic_codes", "repair_history"],
            "data_analysis_agent": ["analytics_data", "reports", "metrics"],
            "manufacturing_insights_agent": ["failure_data", "quality_reports", "manufacturing_data"],
            "feedback_agent": ["feedback_data", "surveys", "satisfaction_scores"],
        }

        # Initialize baseline learning
        self.baseline_learning_period = timedelta(days=30)
        self.learning_start_date = datetime.now()

        self.logger.info("Enhanced UEBA Monitoring Agent initialized")

    async def _execute_internal(self, state: State) -> State:
        """Execute UEBA monitoring workflow"""
        self.logger.info("Starting enhanced UEBA monitoring analysis")

        # Step 1: Collect recent agent actions
        recent_actions = await self._collect_recent_actions()

        # Step 2: Update or create baselines
        await self._update_agent_baselines(recent_actions)

        # Step 3: Detect anomalies in real-time
        anomalies = await self._detect_anomalies_realtime(recent_actions)

        # Step 4: Take automated response actions
        responses = await self._execute_automated_responses(anomalies)

        # Step 5: Generate security report
        security_report = await self._generate_security_report()

        # Update state with security insights
        security_insights = {
            "monitoring_period": {
                "start": (datetime.now() - timedelta(hours=1)).isoformat(),
                "end": datetime.now().isoformat(),
            },
            "actions_monitored": len(recent_actions),
            "anomalies_detected": len(anomalies),
            "critical_anomalies": len([a for a in anomalies if a.severity == SeverityLevel.CRITICAL]),
            "responses_executed": len(responses),
            "security_report": security_report,
            "analysis_timestamp": datetime.now().isoformat(),
        }

        state["ueba_security_insights"] = security_insights
        state["priority"] = Priority.P0 if any(a.severity == SeverityLevel.CRITICAL for a in anomalies) else Priority.P2

        self._add_log_message(
            state,
            f"UEBA monitoring completed. Analyzed {len(recent_actions)} actions, "
            f"detected {len(anomalies)} anomalies, executed {len(responses)} responses.",
        )

        return state

    async def log_agent_action(
        self, agent_id: str, action_type: str, target_resource: str, metadata: Dict[str, Any]
    ) -> None:
        """Log every agent action for UEBA analysis"""
        action = AgentAction(
            timestamp=datetime.now(),
            agent_id=agent_id,
            action_type=action_type,
            target_resource=target_resource,
            payload_size=metadata.get("payload_size", 0),
            source_ip=metadata.get("source_ip", "127.0.0.1"),
            user_agent=metadata.get("user_agent", "unknown"),
            session_id=metadata.get("session_id", f"session_{datetime.now().timestamp()}"),
            metadata=metadata,
        )

        self.ueba_logs.append(action)
        self.logger.info(f"Logged action for agent {agent_id}: {action_type} on {target_resource}")

    async def get_agent_baseline(self, agent_id: str) -> Optional[AgentBaseline]:
        """Retrieve behavioral baseline for an agent"""
        return self.agent_baselines.get(agent_id)

    async def detect_anomaly(
        self, agent_id: str, current_action: AgentAction, baseline: AgentBaseline
    ) -> Optional[SecurityAnomaly]:
        """Detect if current action deviates from baseline"""
        anomalies = []

        # Check for privilege escalation
        if await self._check_privilege_escalation(agent_id, current_action.target_resource):
            anomalies.append(
                self._create_anomaly(
                    agent_id, current_action, AnomalyType.PRIVILEGE_ESCALATION, SeverityLevel.CRITICAL, 0.95
                )
            )

        # Check for excessive API calls
        if await self._check_excessive_api_calls(agent_id, baseline):
            anomalies.append(
                self._create_anomaly(
                    agent_id, current_action, AnomalyType.EXCESSIVE_API_CALLS, SeverityLevel.MEDIUM, 0.8
                )
            )

        # Check for data exfiltration
        if await self._check_data_exfiltration(current_action, baseline):
            anomalies.append(
                self._create_anomaly(
                    agent_id, current_action, AnomalyType.DATA_EXFILTRATION, SeverityLevel.CRITICAL, 0.9
                )
            )

        # Check for workflow deviation
        if await self._check_workflow_deviation(agent_id, current_action, baseline):
            anomalies.append(
                self._create_anomaly(agent_id, current_action, AnomalyType.WORKFLOW_DEVIATION, SeverityLevel.HIGH, 0.75)
            )

        return anomalies[0] if anomalies else None

    async def block_action(self, agent_id: str, action_id: str, reason: str) -> bool:
        """Block a malicious action immediately"""
        try:
            self.blocked_actions[action_id] = reason

            # Log security event
            event = SecurityEvent(
                event_id=f"block_{datetime.now().timestamp()}",
                event_type="action_blocked",
                severity=SeverityLevel.HIGH,
                timestamp=datetime.now(),
                agent_id=agent_id,
                description=f"Blocked action {action_id}: {reason}",
                evidence={"action_id": action_id, "reason": reason},
                response_actions=["block_action"],
            )
            self.security_events.append(event)

            self.logger.warning(f"Blocked action {action_id} for agent {agent_id}: {reason}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to block action {action_id}: {str(e)}")
            return False

    async def alert_security_team(self, anomaly: SecurityAnomaly) -> None:
        """Alert security team of critical anomaly"""
        alert_data = {
            "anomaly_id": anomaly.anomaly_id,
            "agent_id": anomaly.agent_id,
            "anomaly_type": anomaly.anomaly_type.value,
            "severity": anomaly.severity.value,
            "confidence": anomaly.confidence,
            "detected_at": anomaly.detected_at.isoformat(),
            "evidence": anomaly.evidence,
            "recommended_action": self._get_recommended_action(anomaly),
        }

        # Simulate sending alerts (in real implementation, would use email/Slack/PagerDuty)
        self.logger.critical(f"SECURITY ALERT: {json.dumps(alert_data, indent=2)}")

        # Log security event
        event = SecurityEvent(
            event_id=f"alert_{datetime.now().timestamp()}",
            event_type="security_alert",
            severity=anomaly.severity,
            timestamp=datetime.now(),
            agent_id=anomaly.agent_id,
            description=f"Security alert for {anomaly.anomaly_type.value}",
            evidence=anomaly.evidence,
            response_actions=["alert_sent"],
        )
        self.security_events.append(event)

    async def revoke_agent_credentials(self, agent_id: str) -> bool:
        """Revoke API credentials for compromised agent"""
        try:
            self.revoked_credentials.append(agent_id)

            # Log security event
            event = SecurityEvent(
                event_id=f"revoke_{datetime.now().timestamp()}",
                event_type="credentials_revoked",
                severity=SeverityLevel.CRITICAL,
                timestamp=datetime.now(),
                agent_id=agent_id,
                description=f"Revoked credentials for agent {agent_id}",
                evidence={"agent_id": agent_id, "revocation_time": datetime.now().isoformat()},
                response_actions=["revoke_credentials"],
            )
            self.security_events.append(event)

            self.logger.critical(f"Revoked credentials for agent {agent_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to revoke credentials for {agent_id}: {str(e)}")
            return False

    async def _collect_recent_actions(self) -> List[AgentAction]:
        """Collect recent agent actions for analysis"""
        # Simulate collecting actions from the last hour
        cutoff_time = datetime.now() - timedelta(hours=1)
        recent_actions = [action for action in self.ueba_logs if action.timestamp >= cutoff_time]

        # If no recent actions, generate some mock data for demonstration
        if not recent_actions:
            recent_actions = await self._generate_mock_actions()

        return recent_actions

    async def _generate_mock_actions(self) -> List[AgentAction]:
        """Generate mock agent actions for demonstration"""
        mock_actions = []
        agents = ["scheduling_agent", "customer_engagement_agent", "diagnosis_agent"]
        action_types = ["api_call", "data_query", "file_access", "system_command"]
        resources = ["customer_data", "telemetry_data", "appointments", "diagnostic_reports"]

        for i in range(20):
            action = AgentAction(
                timestamp=datetime.now() - timedelta(minutes=np.random.randint(1, 60)),
                agent_id=np.random.choice(agents),
                action_type=np.random.choice(action_types),
                target_resource=np.random.choice(resources),
                payload_size=np.random.randint(1024, 1048576),  # 1KB to 1MB
                source_ip=f"192.168.1.{np.random.randint(1, 255)}",
                user_agent="AutomatedAgent / 1.0",
                session_id=f"session_{i}",
                metadata={"request_id": f"req_{i}", "duration_ms": np.random.randint(100, 5000)},
            )
            mock_actions.append(action)

        return mock_actions

    async def _update_agent_baselines(self, actions: List[AgentAction]) -> None:
        """Update or create behavioral baselines for agents"""
        agent_stats = defaultdict(list)

        # Group actions by agent
        for action in actions:
            agent_stats[action.agent_id].append(action)

        # Update baselines for each agent
        for agent_id, agent_actions in agent_stats.items():
            if agent_id not in self.agent_baselines:
                # Create new baseline
                self.agent_baselines[agent_id] = await self._create_initial_baseline(agent_id, agent_actions)
            else:
                # Update existing baseline
                await self._update_existing_baseline(agent_id, agent_actions)

    async def _create_initial_baseline(self, agent_id: str, actions: List[AgentAction]) -> AgentBaseline:
        """Create initial baseline for an agent"""
        if not actions:
            # Default baseline if no actions
            return AgentBaseline(
                agent_id=agent_id,
                avg_api_calls_per_hour=10.0,
                typical_resources_accessed=self.agent_permissions.get(agent_id, []),
                normal_workflow_sequence=["authenticate", "query", "process", "respond"],
                usual_operating_hours=(9, 17),  # 9 AM to 5 PM
                average_payload_size=10240.0,  # 10KB
                typical_session_duration=1800.0,  # 30 minutes
                error_rate_baseline=0.02,  # 2%
                geographic_locations=["US-East"],
                last_updated=datetime.now(),
            )

        # Calculate baseline metrics from actions
        payload_sizes = [action.payload_size for action in actions]
        hours = [action.timestamp.hour for action in actions]
        resources = list(set(action.target_resource for action in actions))

        return AgentBaseline(
            agent_id=agent_id,
            avg_api_calls_per_hour=len(actions),
            typical_resources_accessed=resources,
            normal_workflow_sequence=["authenticate", "query", "process", "respond"],
            usual_operating_hours=(min(hours), max(hours)),
            average_payload_size=np.mean(payload_sizes) if payload_sizes else 10240.0,
            typical_session_duration=1800.0,
            error_rate_baseline=0.02,
            geographic_locations=["US-East"],
            last_updated=datetime.now(),
        )

    async def _update_existing_baseline(self, agent_id: str, actions: List[AgentAction]) -> None:
        """Update existing baseline with new data"""
        baseline = self.agent_baselines[agent_id]

        # Update with exponential moving average
        alpha = 0.1  # Learning rate

        if actions:
            new_api_calls = len(actions)
            baseline.avg_api_calls_per_hour = (1 - alpha) * baseline.avg_api_calls_per_hour + alpha * new_api_calls

            new_payload_sizes = [action.payload_size for action in actions]
            if new_payload_sizes:
                new_avg_payload = np.mean(new_payload_sizes)
                baseline.average_payload_size = (1 - alpha) * baseline.average_payload_size + alpha * new_avg_payload

        baseline.last_updated = datetime.now()

    async def _detect_anomalies_realtime(self, actions: List[AgentAction]) -> List[SecurityAnomaly]:
        """Detect anomalies in real-time using ML and rule-based approaches"""
        anomalies = []

        for action in actions:
            baseline = await self.get_agent_baseline(action.agent_id)
            if baseline:
                anomaly = await self.detect_anomaly(action.agent_id, action, baseline)
                if anomaly:
                    anomalies.append(anomaly)

        return anomalies

    async def _check_privilege_escalation(self, agent_id: str, target_resource: str) -> bool:
        """Check if agent is accessing resources outside its role"""
        allowed_resources = self.agent_permissions.get(agent_id, [])

        # Check if target resource is in allowed list
        for allowed in allowed_resources:
            if allowed in target_resource.lower():
                return False

        # If no match found, it's a potential privilege escalation
        return True

    async def _check_excessive_api_calls(self, agent_id: str, baseline: AgentBaseline) -> bool:
        """Check if agent is making excessive API calls"""
        recent_actions = [
            action
            for action in self.ueba_logs
            if action.agent_id == agent_id and action.timestamp >= datetime.now() - timedelta(hours=1)
        ]

        current_rate = len(recent_actions)
        threshold = baseline.avg_api_calls_per_hour * self.security_thresholds["api_call_multiplier"]

        return current_rate > threshold

    async def _check_data_exfiltration(self, action: AgentAction, baseline: AgentBaseline) -> bool:
        """Check for potential data exfiltration"""
        # Check payload size
        size_threshold = baseline.average_payload_size * self.security_thresholds["payload_size_multiplier"]
        large_payload = action.payload_size > size_threshold

        # Check timing (off-hours access)
        current_hour = action.timestamp.hour
        off_hours = current_hour < baseline.usual_operating_hours[0] or current_hour > baseline.usual_operating_hours[1]

        return large_payload and off_hours

    async def _check_workflow_deviation(self, agent_id: str, action: AgentAction, baseline: AgentBaseline) -> bool:
        """Check for workflow sequence deviations"""
        # Get recent actions for this agent to check sequence
        recent_actions = [
            a
            for a in self.ueba_logs
            if a.agent_id == agent_id and a.timestamp >= datetime.now() - timedelta(minutes=30)
        ]

        if len(recent_actions) < 2:
            return False

        # Check if current action follows expected workflow
        recent_sequence = [a.action_type for a in recent_actions[-3:]]
        expected_sequence = baseline.normal_workflow_sequence

        # Simple deviation check (in real implementation, would use more sophisticated sequence analysis)
        return len(set(recent_sequence) - set(expected_sequence)) > 1

    def _create_anomaly(
        self, agent_id: str, action: AgentAction, anomaly_type: AnomalyType, severity: SeverityLevel, confidence: float
    ) -> SecurityAnomaly:
        """Create a security anomaly record"""
        return SecurityAnomaly(
            anomaly_id=f"anomaly_{datetime.now().timestamp()}",
            agent_id=agent_id,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=confidence,
            detected_at=datetime.now(),
            action_details=action,
            baseline_deviation={},
            evidence={
                "action_type": action.action_type,
                "target_resource": action.target_resource,
                "payload_size": action.payload_size,
                "timestamp": action.timestamp.isoformat(),
            },
        )

    async def _execute_automated_responses(self, anomalies: List[SecurityAnomaly]) -> List[str]:
        """Execute automated response actions based on anomaly severity"""
        responses = []

        for anomaly in anomalies:
            if anomaly.severity == SeverityLevel.CRITICAL:
                # Block action and revoke credentials
                await self.block_action(
                    anomaly.agent_id, anomaly.anomaly_id, f"Critical anomaly: {anomaly.anomaly_type.value}"
                )
                await self.revoke_agent_credentials(anomaly.agent_id)
                await self.alert_security_team(anomaly)
                responses.extend(["block_action", "revoke_credentials", "alert_security_team"])

            elif anomaly.severity == SeverityLevel.HIGH:
                # Block action and alert
                await self.block_action(
                    anomaly.agent_id, anomaly.anomaly_id, f"High severity anomaly: {anomaly.anomaly_type.value}"
                )
                await self.alert_security_team(anomaly)
                responses.extend(["block_action", "alert_security_team"])

            elif anomaly.severity == SeverityLevel.MEDIUM:
                # Log and monitor
                await self.alert_security_team(anomaly)
                responses.append("alert_security_team")

        return responses

    def _get_recommended_action(self, anomaly: SecurityAnomaly) -> str:
        """Get recommended action for an anomaly"""
        recommendations = {
            AnomalyType.PRIVILEGE_ESCALATION: "Immediately revoke agent credentials and investigate access patterns",
            AnomalyType.DATA_EXFILTRATION: "Block data export, isolate agent, and conduct forensic analysis",
            AnomalyType.EXCESSIVE_API_CALLS: "Rate-limit agent and investigate for potential DDoS or abuse",
            AnomalyType.WORKFLOW_DEVIATION: "Review agent logic and validate against expected behavior patterns",
            AnomalyType.UNUSUAL_TIMING: "Verify agent scheduling and check for unauthorized access",
            AnomalyType.GEOGRAPHIC_ANOMALY: "Validate agent deployment location and check for IP spoofing",
            AnomalyType.RESOURCE_ABUSE: "Monitor resource usage and implement usage quotas",
        }

        return recommendations.get(anomaly.anomaly_type, "Investigate anomaly and take appropriate action")

    async def _generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)

        # Filter recent events
        recent_anomalies = [a for a in self.detected_anomalies if a.detected_at >= last_24h]
        recent_events = [e for e in self.security_events if e.timestamp >= last_24h]

        # Calculate metrics
        total_actions = len([a for a in self.ueba_logs if a.timestamp >= last_24h])
        anomaly_rate = len(recent_anomalies) / max(total_actions, 1) * 100

        # Severity breakdown
        severity_counts = {
            "critical": len([a for a in recent_anomalies if a.severity == SeverityLevel.CRITICAL]),
            "high": len([a for a in recent_anomalies if a.severity == SeverityLevel.HIGH]),
            "medium": len([a for a in recent_anomalies if a.severity == SeverityLevel.MEDIUM]),
            "low": len([a for a in recent_anomalies if a.severity == SeverityLevel.LOW]),
        }

        # Top anomaly types
        anomaly_types = {}
        for anomaly in recent_anomalies:
            anomaly_type = anomaly.anomaly_type.value
            anomaly_types[anomaly_type] = anomaly_types.get(anomaly_type, 0) + 1

        return {
            "report_period": {"start": last_24h.isoformat(), "end": now.isoformat()},
            "summary": {
                "total_actions_monitored": total_actions,
                "anomalies_detected": len(recent_anomalies),
                "anomaly_rate_percent": round(anomaly_rate, 2),
                "security_events": len(recent_events),
                "agents_monitored": len(self.agent_baselines),
                "blocked_actions": len(self.blocked_actions),
                "revoked_credentials": len(self.revoked_credentials),
            },
            "severity_breakdown": severity_counts,
            "top_anomaly_types": dict(sorted(anomaly_types.items(), key=lambda x: x[1], reverse=True)[:5]),
            "agent_status": {
                agent_id: {
                    "baseline_established": True,
                    "last_activity": baseline.last_updated.isoformat(),
                    "risk_level": "low",  # Simplified risk assessment
                }
                for agent_id, baseline in self.agent_baselines.items()
            },
            "recommendations": [
                "Continue monitoring agent behaviors for baseline refinement",
                "Review and update agent permission matrices",
                "Implement additional ML models for advanced threat detection",
                "Establish incident response procedures for critical anomalies",
            ],
        }
