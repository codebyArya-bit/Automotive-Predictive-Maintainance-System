"""Master Agent for Automotive Predictive Maintenance Orchestration"""

import traceback
from typing import Dict, Any, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from state import State, StateManager
from config import Config
from error_handling import ErrorHandler, CircuitBreaker, HealthChecker
from monitoring import PerformanceMonitor, UEBAComplianceMonitor, StructuredLogger, MonitoringDashboard

# Import all worker agents
from agents import (
    DataAnalysisAgent,
    DiagnosisAgent,
    CustomerEngagementAgent,
    SchedulingAgent,
    FeedbackAgent,
    ManufacturingInsightsAgent,
    UEBAMonitoringAgent,
)
from agents.enhanced_data_analysis_agent import EnhancedDataAnalysisAgent
from agents.enhanced_diagnosis_agent import EnhancedDiagnosisAgent


class MasterAgent:
    """
    Master Agent that orchestrates all worker agents using LangGraph
    with comprehensive error handling, monitoring, and UEBA compliance
    """

    def __init__(self):
        self.config = Config()
        self.logger = StructuredLogger()
        self.error_handler = ErrorHandler()
        self.health_checker = HealthChecker()

        # Initialize monitoring systems
        self.performance_monitor = PerformanceMonitor()
        self.ueba_monitor = UEBAComplianceMonitor()
        self.dashboard = MonitoringDashboard(self.performance_monitor, self.ueba_monitor)

        # Initialize circuit breakers for each agent
        self.circuit_breakers = {
            "data_analysis": CircuitBreaker(failure_threshold=3, recovery_timeout=60),
            "enhanced_data_analysis": CircuitBreaker(failure_threshold=3, recovery_timeout=60),
            "diagnosis": CircuitBreaker(failure_threshold=3, recovery_timeout=60),
            "enhanced_diagnosis": CircuitBreaker(failure_threshold=3, recovery_timeout=60),
            "customer_engagement": CircuitBreaker(failure_threshold=5, recovery_timeout=30),
            "scheduling": CircuitBreaker(failure_threshold=3, recovery_timeout=60),
            "feedback": CircuitBreaker(failure_threshold=5, recovery_timeout=30),
            "manufacturing_insights": CircuitBreaker(failure_threshold=3, recovery_timeout=120),
            "ueba_monitoring": CircuitBreaker(failure_threshold=2, recovery_timeout=30),
        }

        # Initialize worker agents
        self.data_analysis_agent = DataAnalysisAgent()
        self.enhanced_data_analysis_agent = EnhancedDataAnalysisAgent(openai_api_key=self.config.OPENAI_API_KEY)
        self.diagnosis_agent = DiagnosisAgent()
        self.enhanced_diagnosis_agent = EnhancedDiagnosisAgent(openai_api_key=self.config.OPENAI_API_KEY)
        self.customer_engagement_agent = CustomerEngagementAgent()
        self.scheduling_agent = SchedulingAgent()
        self.feedback_agent = FeedbackAgent()
        self.manufacturing_insights_agent = ManufacturingInsightsAgent()
        self.ueba_monitoring_agent = UEBAMonitoringAgent()

        # Build the workflow graph
        self.workflow = self._build_workflow()

        # Compile the workflow with memory for state persistence
        memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=memory)

        self.logger.logger.info("Master Agent initialized with enhanced monitoring and error handling")

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with all agents and conditional edges"""
        workflow = StateGraph(State)

        # Add all agent nodes
        workflow.add_node("data_analysis", self._execute_data_analysis)
        workflow.add_node("enhanced_data_analysis", self._execute_enhanced_data_analysis)
        workflow.add_node("diagnosis", self._execute_diagnosis)
        workflow.add_node("enhanced_diagnosis", self._execute_enhanced_diagnosis)
        workflow.add_node("customer_engagement", self._execute_customer_engagement)
        workflow.add_node("scheduling", self._execute_scheduling)
        workflow.add_node("feedback", self._execute_feedback)
        workflow.add_node("manufacturing_insights", self._execute_manufacturing_insights)
        workflow.add_node("ueba_monitoring", self._execute_ueba_monitoring)
        workflow.add_node("human_escalation", self._handle_human_escalation)
        workflow.add_node("health_check", self._perform_health_check)

        # Set entry point
        workflow.set_entry_point("health_check")

        # Define workflow edges with enhanced decision logic
        workflow.add_conditional_edges(
            "health_check",
            self._choose_analysis_method,
            {"basic": "data_analysis", "enhanced": "enhanced_data_analysis"},
        )

        # Route to appropriate diagnosis method based on analysis type
        workflow.add_conditional_edges(
            "data_analysis", self._choose_diagnosis_method, {"basic": "diagnosis", "enhanced": "enhanced_diagnosis"}
        )
        workflow.add_conditional_edges(
            "enhanced_data_analysis",
            self._choose_diagnosis_method,
            {"basic": "diagnosis", "enhanced": "enhanced_diagnosis"},
        )

        # Conditional edge from diagnosis (both basic and enhanced)
        workflow.add_conditional_edges(
            "diagnosis",
            self._should_contact_customer,
            {"contact": "customer_engagement", "monitor": "manufacturing_insights", "escalate": "human_escalation"},
        )
        workflow.add_conditional_edges(
            "enhanced_diagnosis",
            self._should_contact_customer,
            {"contact": "customer_engagement", "monitor": "manufacturing_insights", "escalate": "human_escalation"},
        )

        # Conditional edge from customer engagement
        workflow.add_conditional_edges(
            "customer_engagement",
            self._parse_customer_response,
            {
                "book_appointment": "scheduling",
                "declined": "feedback",
                "escalate": "human_escalation",
                "continue_engagement": "customer_engagement",
            },
        )

        # Edges from scheduling
        workflow.add_edge("scheduling", "feedback")

        # Conditional edge from feedback
        workflow.add_conditional_edges(
            "feedback",
            self._should_run_manufacturing_insights,
            {"run_insights": "manufacturing_insights", "complete": "ueba_monitoring"},
        )

        # Edge from manufacturing insights
        workflow.add_edge("manufacturing_insights", "ueba_monitoring")

        # Conditional edge from UEBA monitoring
        workflow.add_conditional_edges(
            "ueba_monitoring", self._should_escalate_security, {"escalate": "human_escalation", "complete": END}
        )

        # Human escalation always ends the workflow
        workflow.add_edge("human_escalation", END)

        return workflow

    async def process_vehicle(
        self,
        vehicle_id: str,
        telemetry_data: Optional[Dict[str, Any]] = None,
        config_override: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a vehicle through the complete workflow with monitoring

        Args:
            vehicle_id: Unique identifier for the vehicle
            telemetry_data: Raw telemetry data from the vehicle
            config_override: Optional configuration overrides

        Returns:
            Final state after processing
        """
        # Create initial state
        session_id = f"session_{vehicle_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        initial_state_typed = StateManager.create_initial_state(vehicle_id, session_id)

        # Debug: Check if initial_state_typed is None
        if initial_state_typed is None:
            self.logger.logger.error(
                "StateManager.create_initial_state returned None", vehicle_id=vehicle_id, session_id=session_id
            )
            return {"error": "Failed to create initial state", "vehicle_id": vehicle_id, "workflow_failed": True}

        # Convert to regular dict to ensure compatibility
        initial_state = dict(initial_state_typed)

        # Debug: Check if dict conversion failed
        if initial_state is None:
            self.logger.logger.error(
                "Dict conversion of initial_state failed", vehicle_id=vehicle_id, session_id=session_id
            )
            return {
                "error": "Failed to convert initial state to dict",
                "vehicle_id": vehicle_id,
                "workflow_failed": True,
            }

        # Add telemetry data if provided
        if telemetry_data:
            initial_state["telemetry_snapshot"] = telemetry_data

        # Add audit trail for compliance
        initial_state["audit_trail"] = [
            {
                "action": "workflow_started",
                "timestamp": datetime.now().isoformat(),
                "vehicle_id": vehicle_id,
                "user_id": "system",
                "details": {"telemetry_keys": list(telemetry_data.keys()) if telemetry_data else []},
            }
        ]
        initial_state["access_logged"] = True
        initial_state["customer_consent_tracked"] = True  # Assume consent obtained

        # Apply configuration overrides
        if config_override:
            initial_state.update(config_override)

        # Debug: Print initial_state to see what's happening
        print(f"DEBUG: initial_state type: {type(initial_state)}")
        print(f"DEBUG: initial_state value: {initial_state}")

        # Determine priority for monitoring - use safe access
        if initial_state and isinstance(initial_state, dict):
            prediction = initial_state.get("prediction", {})
            if prediction and isinstance(prediction, dict):
                priority = prediction.get("priority", "P3")
            else:
                priority = "P3"
        else:
            priority = "P3"
            print(f"DEBUG: initial_state is not a valid dict, using default priority P3")

        # Monitor the entire workflow
        async with self.performance_monitor.monitor_workflow(vehicle_id, priority):
            try:
                # Execute the workflow
                config = {"configurable": {"thread_id": f"vehicle_{vehicle_id}"}}

                # Add detailed logging before workflow execution
                self.logger.logger.info(
                    "Starting workflow execution",
                    vehicle_id=vehicle_id,
                    initial_state_keys=list(initial_state.keys()) if initial_state else [],
                    initial_state_type=type(initial_state).__name__,
                )

                result = await self.app.ainvoke(initial_state, config=config)

                # Log the result type and keys
                self.logger.logger.info(
                    "Workflow execution completed",
                    vehicle_id=vehicle_id,
                    result_type=type(result).__name__ if result else "None",
                    result_keys=list(result.keys()) if result and isinstance(result, dict) else [],
                )

                # Ensure result is not None
                if result is None:
                    self.logger.logger.error("Workflow returned None result", vehicle_id=vehicle_id)
                    result = initial_state.copy()
                    result["workflow_failed"] = True
                    result["workflow_error"] = "Workflow returned None"
                    result["escalate_to_human"] = True
                    result["escalation_reason"] = "Workflow execution failed"

                # Log successful completion
                prediction = result.get("prediction", {}) if result else {}
                final_priority = prediction.get("priority") if prediction and isinstance(prediction, dict) else None
                self.logger.logger.info(
                    event="Vehicle processing completed successfully",
                    vehicle_id=vehicle_id,
                    final_priority=final_priority,
                    escalated=result.get("escalate_to_human", False) if result else False,
                    total_agents_executed=len([k for k in result.keys() if k.endswith("_completed")]) if result else 0,
                )

                return result

            except Exception as e:
                # Log the exception with full details
                self.logger.logger.error(
                    "Workflow execution failed with exception",
                    vehicle_id=vehicle_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    error_args=e.args if hasattr(e, "args") else [],
                    traceback=traceback.format_exc(),
                )

                # Special handling for NoneType errors
                if "'NoneType' object has no attribute 'get'" in str(e):
                    self.logger.logger.error(
                        "CRITICAL: NoneType error detected - detailed analysis",
                        vehicle_id=vehicle_id,
                        error_location=traceback.format_exc(),
                        initial_state_snapshot=str(initial_state)[:1000] if initial_state else "None",
                    )

                # Create error state
                result = initial_state.copy()
                result["workflow_failed"] = True
                result["workflow_error"] = str(e)
                result["escalate_to_human"] = True
                result["escalation_reason"] = f"Workflow execution failed: {str(e)}"

                return result

    # Enhanced agent execution methods with monitoring and error handling

    async def _execute_data_analysis(self, state: State) -> State:
        """Execute data analysis agent with monitoring"""
        return await self._execute_agent_with_monitoring("data_analysis", state)

    async def _execute_enhanced_data_analysis(self, state: State) -> State:
        """Execute enhanced data analysis agent with monitoring"""
        return await self._execute_agent_with_monitoring("enhanced_data_analysis", state)

    async def _execute_diagnosis(self, state: State) -> State:
        """Execute diagnosis agent with monitoring"""
        return await self._execute_agent_with_monitoring("diagnosis", state)

    async def _execute_enhanced_diagnosis(self, state: State) -> State:
        """Execute enhanced diagnosis agent with ML models and RAG"""
        return await self._execute_agent_with_monitoring("enhanced_diagnosis", state)

    async def _execute_customer_engagement(self, state: State) -> State:
        """Execute customer engagement agent with monitoring"""
        return await self._execute_agent_with_monitoring("customer_engagement", state)

    async def _execute_scheduling(self, state: State) -> State:
        """Execute scheduling agent with monitoring"""
        return await self._execute_agent_with_monitoring("scheduling", state)

    async def _execute_feedback(self, state: State) -> State:
        """Execute feedback agent with monitoring"""
        return await self._execute_agent_with_monitoring("feedback", state)

    async def _execute_manufacturing_insights(self, state: State) -> State:
        """Execute manufacturing insights agent with monitoring"""
        return await self._execute_agent_with_monitoring("manufacturing_insights", state)

    async def _execute_ueba_monitoring(self, state: State) -> State:
        """Execute UEBA monitoring agent with compliance checks"""
        # First perform UEBA monitoring
        state = await self._execute_agent_with_monitoring("ueba_monitoring", state)

        # Then perform additional compliance checks
        session_data = {
            "duration": 300,  # Simulated session duration
            "data_volume": 50,  # MB
            "api_calls": 25,
            "error_rate": 0.01,
        }

        # Monitor session behavior
        anomalies, risk_factors = await self.ueba_monitor.monitor_session_behavior(state, session_data)

        # Check compliance violations
        violations = await self.ueba_monitor.check_compliance_violations(state, "predictive_maintenance")

        # Calculate risk score
        risk_score = self.ueba_monitor.calculate_risk_score(anomalies, risk_factors, violations)

        # Update state with UEBA results
        state["ueba_analysis"] = {
            "anomalies": anomalies,
            "risk_factors": risk_factors,
            "violations": violations,
            "risk_score": risk_score,
            "timestamp": datetime.now().isoformat(),
        }

        # Update Prometheus metrics
        self.performance_monitor.metrics.risk_score.labels(vehicle_id=state.get("vehicle_id", "unknown")).set(
            risk_score
        )

        return state

    async def _execute_agent_with_monitoring(self, agent_name: str, state: State) -> State:
        """Execute an agent with comprehensive monitoring and error handling"""
        # Add detailed logging for debugging
        self.logger.logger.info(
            "Agent execution starting",
            agent_name=agent_name,
            vehicle_id=state.get("vehicle_id", "unknown") if state else "no_state",
            state_type=type(state).__name__ if state else "None",
            state_keys=list(state.keys()) if state and isinstance(state, dict) else [],
        )

        circuit_breaker = self.circuit_breakers[agent_name]

        # Get the appropriate agent
        if agent_name == "data_analysis":
            agent = self.data_analysis_agent
        elif agent_name == "enhanced_data_analysis":
            agent = self.enhanced_data_analysis_agent
        elif agent_name == "diagnosis":
            agent = self.diagnosis_agent
        elif agent_name == "enhanced_diagnosis":
            agent = self.enhanced_diagnosis_agent
        elif agent_name == "customer_engagement":
            agent = self.customer_engagement_agent
        elif agent_name == "scheduling":
            agent = self.scheduling_agent
        elif agent_name == "feedback":
            agent = self.feedback_agent
        elif agent_name == "manufacturing_insights":
            agent = self.manufacturing_insights_agent
        elif agent_name == "ueba_monitoring":
            agent = self.ueba_monitoring_agent
        else:
            raise ValueError(f"Unknown agent: {agent_name}")

        # Log agent details
        self.logger.logger.info(
            "Agent selected for execution",
            agent_name=agent_name,
            agent_type=type(agent).__name__ if agent else "None",
            has_execute_method=hasattr(agent, "execute") if agent else False,
        )

        # Monitor agent execution
        async with self.performance_monitor.monitor_agent_execution(agent_name, state):
            try:
                # Execute with circuit breaker protection
                result_state = await circuit_breaker.call(agent.execute, state)

                # Log successful execution
                self.logger.logger.info(
                    "Agent execution completed successfully",
                    agent_name=agent_name,
                    result_type=type(result_state).__name__ if result_state else "None",
                    result_keys=list(result_state.keys()) if result_state and isinstance(result_state, dict) else [],
                )

                # Mark agent as completed
                result_state[f"{agent_name}_completed"] = True
                result_state[f"{agent_name}_timestamp"] = datetime.now().isoformat()

                # Add to audit trail
                if "audit_trail" not in result_state:
                    result_state["audit_trail"] = []

                result_state["audit_trail"].append(
                    {
                        "action": f"{agent_name}_completed",
                        "timestamp": datetime.now().isoformat(),
                        "vehicle_id": state.get("vehicle_id", "unknown"),
                        "user_id": "system",
                        "details": {"agent": agent_name, "success": True},
                    }
                )

                return result_state

            except Exception as e:
                # Log the exception with full details
                import traceback

                self.logger.logger.error(
                    "Agent execution failed with exception",
                    agent_name=agent_name,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    error_args=e.args if hasattr(e, "args") else [],
                    traceback=traceback.format_exc(),
                )

                # Handle agent execution error
                context = {
                    "agent_name": agent_name,
                    "function_name": "execute",
                    "retry_count": state.get("retry_count", 0),
                }

                should_retry, error_state = await self.error_handler.handle_error(e, context, state)

                if not should_retry:
                    # Add to audit trail
                    if "audit_trail" not in error_state:
                        error_state["audit_trail"] = []

                    error_state["audit_trail"].append(
                        {
                            "action": f"{agent_name}_failed",
                            "timestamp": datetime.now().isoformat(),
                            "vehicle_id": state.get("vehicle_id", "unknown"),
                            "user_id": "system",
                            "details": {
                                "agent": agent_name,
                                "error": str(e),
                                "fallback_used": error_state.get("fallback_used", False),
                            },
                        }
                    )

                return error_state

    async def _perform_health_check(self, state: State) -> State:
        """Perform system health check before processing"""
        # Add logging to track state
        self.logger.logger.info(
            "Health check starting",
            vehicle_id=state.get("vehicle_id", "unknown") if state else "no_state",
            state_type=type(state).__name__ if state else "None",
            state_keys=list(state.keys()) if state and isinstance(state, dict) else [],
        )

        health_status = await self.health_checker.check_system_health(state)

        state["health_check"] = health_status
        state["health_check_timestamp"] = datetime.now().isoformat()

        # Log health status
        self.logger.logger.info(
            event="System health check completed",
            vehicle_id=state.get("vehicle_id", "unknown"),
            health_status=health_status["overall_health"],
            issues=health_status.get("issues", []),
        )

        return state

    async def _handle_human_escalation(self, state: State) -> State:
        """Handle escalation to human agent"""
        escalation_reason = state.get("escalation_reason", "Unknown reason")

        # Safe priority extraction
        prediction = state.get("prediction", {}) if state else {}
        priority = prediction.get("priority", "P3") if prediction and isinstance(prediction, dict) else "P3"

        self.logger.logger.warning(
            "Escalating to human agent",
            vehicle_id=state.get("vehicle_id", "unknown"),
            reason=escalation_reason,
            priority=priority,
        )

        # Create escalation record
        customer_response = state.get("customer_response", {})
        if customer_response is None:
            customer_response = {}

        state["human_escalation"] = {
            "timestamp": datetime.now().isoformat(),
            "reason": escalation_reason,
            "priority": priority,
            "customer_sentiment": customer_response.get("sentiment", 5),
            "context": {
                "prediction": state.get("prediction"),
                "customer_response": state.get("customer_response"),
                "appointment": state.get("appointment"),
            },
        }

        # Add to audit trail
        if "audit_trail" not in state:
            state["audit_trail"] = []

        state["audit_trail"].append(
            {
                "action": "human_escalation",
                "timestamp": datetime.now().isoformat(),
                "vehicle_id": state.get("vehicle_id", "unknown"),
                "user_id": "system",
                "details": {"reason": escalation_reason, "priority": priority},
            }
        )

        # Update metrics
        self.performance_monitor.metrics.escalations_total.labels(reason=escalation_reason, priority=priority).inc()

        return state

    # Decision logic methods
    def _choose_analysis_method(self, state: State) -> str:
        """
        Choose between basic and enhanced data analysis based on requirements

        Returns:
            "basic" - Use basic data analysis agent
            "enhanced" - Use enhanced data analysis agent with LangChain tools
        """
        # Check if enhanced analysis is requested or needed
        if state.get("use_enhanced_analysis", False):
            return "enhanced"

        # Use enhanced analysis for complex scenarios or when ML features are needed
        vehicle_data = state.get("vehicle_data", {})
        telemetry_snapshot = state.get("telemetry_snapshot", {})

        # Safe access to telemetry data with proper null checks
        vehicle_telemetry = vehicle_data.get("telemetry", {}) if vehicle_data else {}
        snapshot_telemetry = telemetry_snapshot.get("telemetry", {}) if telemetry_snapshot else {}
        telemetry = vehicle_telemetry or snapshot_telemetry

        # Ensure telemetry is a dict before checking length
        if not isinstance(telemetry, dict):
            telemetry = {}

        # If we have rich telemetry data, use enhanced analysis
        if len(telemetry) > 10:  # More than 10 data points
            return "enhanced"

        # Check for specific analysis requirements
        analysis_type = state.get("analysis_type", "basic")
        if analysis_type in ["ml_features", "predictive", "advanced"]:
            return "enhanced"

        # Default to basic analysis
        return "basic"

    def _choose_diagnosis_method(self, state: State) -> str:
        """
        Choose between basic and enhanced diagnosis based on analysis complexity and requirements

        Returns:
            "basic" - Use basic diagnosis agent
            "enhanced" - Use enhanced diagnosis agent with ML models and RAG
        """
        # Check if enhanced diagnosis is explicitly requested
        if state.get("use_enhanced_diagnosis", False):
            return "enhanced"

        # Use enhanced diagnosis if we have ML features or complex analysis results
        analysis_results = state.get("analysis_results", {})
        if analysis_results is None:
            analysis_results = {}
        prediction = state.get("prediction", {})
        if prediction is None:
            prediction = {}

        # If analysis detected complex patterns or multiple anomalies, use enhanced diagnosis
        if analysis_results.get("anomaly_count", 0) > 3:
            return "enhanced"

        # If prediction indicates high-risk scenarios, use enhanced diagnosis
        if prediction.get("priority") in ["P0", "P1"]:
            return "enhanced"

        # Use enhanced diagnosis for vehicles with complex systems or high value
        vehicle_data = state.get("vehicle_data", {})
        if vehicle_data is None:
            vehicle_data = {}
        vehicle_info = vehicle_data.get("vehicle_info", {})

        # Enhanced diagnosis for luxury/premium vehicles or complex systems
        if vehicle_info.get("category") in ["luxury", "premium", "commercial"]:
            return "enhanced"

        # Check if we need ML-based failure prediction
        analysis_type = state.get("analysis_type", "basic")
        if analysis_type in ["ml_features", "predictive", "advanced"]:
            return "enhanced"

        # Default to basic diagnosis for simple cases
        return "basic"

    def _should_contact_customer(self, state: State) -> str:
        """
        Decide whether to contact customer based on prediction severity

        Returns:
            "contact" - Contact customer for high priority issues
            "monitor" - Continue monitoring for low priority
            "escalate" - Escalate to human for critical issues
        """
        prediction = state.get("prediction", {})

        if not prediction:
            return "monitor"

        probability = prediction.get("probability", 0)
        priority = prediction.get("priority", "P3")

        # Check for system errors that require escalation
        if state.get("workflow_failed") or state.get("critical_error"):
            state["escalation_reason"] = "System error detected"
            return "escalate"

        # High probability and critical priority - contact customer
        if probability >= self.config.PREDICTION_THRESHOLD_HIGH and priority in ["P0", "P1"]:
            return "contact"

        # Medium probability and high priority - contact customer
        if probability >= self.config.PREDICTION_THRESHOLD_MEDIUM and priority == "P1":
            return "contact"

        # Critical priority always requires contact
        if priority == "P0":
            return "contact"

        # Otherwise, just monitor
        return "monitor"

    def _parse_customer_response(self, state: State) -> str:
        """
        Parse customer response and decide next action

        Returns:
            "book_appointment" - Customer agreed to service
            "declined" - Customer declined service
            "escalate" - Escalate to human agent
            "monitor" - Continue monitoring
        """
        customer_response = state.get("customer_response", {})

        if not customer_response:
            return "monitor"

        intent = customer_response.get("intent", "unknown")
        sentiment = customer_response.get("sentiment", 5)

        # Low sentiment or confusion - escalate to human
        if sentiment <= self.config.ESCALATION_SENTIMENT_THRESHOLD:
            state["escalation_reason"] = f"Low customer sentiment: {sentiment}/10"
            return "escalate"

        if intent == "confused" or intent == "questions":
            state["escalation_reason"] = "Customer needs human assistance"
            return "escalate"

        # Customer agreed to service
        if intent == "positive" or intent == "book_appointment":
            return "book_appointment"

        # Customer declined service
        if intent == "negative" or intent == "declined":
            return "declined"

        # Default to monitoring
        return "monitor"

    def _after_scheduling_decision(self, state: State) -> str:
        """
        Decide next action after scheduling

        Returns:
            "feedback" - Collect feedback
            "insights" - Generate manufacturing insights
            "escalate" - Escalate to human
        """
        appointment = state.get("appointment")

        if not appointment:
            state["escalation_reason"] = "Failed to schedule appointment"
            return "escalate"

        # Check if appointment was successfully booked
        if appointment.get("status") == "confirmed":
            return "feedback"
        elif appointment.get("status") == "pending":
            return "feedback"
        else:
            state["escalation_reason"] = "Appointment scheduling failed"
            return "escalate"

    def _after_feedback_decision(self, state: State) -> str:
        """
        Decide next action after feedback collection

        Returns:
            "insights" - Generate manufacturing insights
            "complete" - Complete workflow
            "escalate" - Escalate to human
        """
        feedback = state.get("feedback", {})

        # If feedback indicates issues, escalate
        if feedback.get("satisfaction_rating", 5) <= 3:
            state["escalation_reason"] = "Low customer satisfaction"
            return "escalate"

        # Check if we should generate manufacturing insights
        prediction = state.get("prediction", {})
        if prediction is None:
            prediction = {}
        if prediction.get("priority") in ["P0", "P1"]:
            return "insights"

        # Otherwise complete the workflow
        return "complete"

    def _should_run_manufacturing_insights(self, state: State) -> str:
        """
        Decide whether to run manufacturing insights

        Returns:
            "run_insights" - Generate manufacturing insights
            "complete" - Skip insights and complete
        """
        prediction = state.get("prediction", {})
        if prediction is None:
            prediction = {}
        priority = prediction.get("priority", "P3")

        # Run insights for high priority issues
        if priority in ["P0", "P1"]:
            return "run_insights"

        # Skip insights for low priority
        return "complete"

    def _should_escalate_security(self, state: State) -> str:
        """
        Decide whether to escalate based on security analysis

        Returns:
            "escalate" - Escalate to human for security issues
            "complete" - Complete workflow normally
        """
        ueba_analysis = state.get("ueba_analysis", {})
        if ueba_analysis is None:
            ueba_analysis = {}
        risk_level = ueba_analysis.get("risk_level", "low")
        security_alerts = ueba_analysis.get("security_alerts", [])

        # Escalate for high risk or critical alerts
        if risk_level in ["high", "critical"]:
            state["escalation_reason"] = f"Security risk level: {risk_level}"
            return "escalate"

        # Check for critical security alerts
        critical_alerts = [alert for alert in security_alerts if alert.get("severity") == "critical"]
        if critical_alerts:
            state["escalation_reason"] = f"Critical security alerts: {len(critical_alerts)}"
            return "escalate"

        return "complete"

    # Utility methods
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data for monitoring"""
        return await self.dashboard.get_dashboard_data()

    async def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        # Create a basic state for health checking
        basic_state = {"vehicle_id": "health_check", "errors": [], "retry_count": 0, "escalate_to_human": False}

        # Get health status from health checker
        health_status = await self.health_checker.check_system_health(basic_state)

        # Add circuit breaker information
        health_status["circuit_breakers"] = self.get_circuit_breaker_status()

        # Add agent information
        health_status["agents"] = {
            "data_analysis": {
                "status": "healthy",
                "circuit_breaker": health_status["circuit_breakers"]["data_analysis"],
            },
            "enhanced_data_analysis": {
                "status": "healthy",
                "circuit_breaker": health_status["circuit_breakers"]["enhanced_data_analysis"],
            },
            "diagnosis": {"status": "healthy", "circuit_breaker": health_status["circuit_breakers"]["diagnosis"]},
            "customer_engagement": {
                "status": "healthy",
                "circuit_breaker": health_status["circuit_breakers"]["customer_engagement"],
            },
            "scheduling": {"status": "healthy", "circuit_breaker": health_status["circuit_breakers"]["scheduling"]},
            "feedback": {"status": "healthy", "circuit_breaker": health_status["circuit_breakers"]["feedback"]},
            "manufacturing_insights": {
                "status": "healthy",
                "circuit_breaker": health_status["circuit_breakers"]["manufacturing_insights"],
            },
            "ueba_monitoring": {
                "status": "healthy",
                "circuit_breaker": health_status["circuit_breakers"]["ueba_monitoring"],
            },
        }

        return health_status

    def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        return {
            name: {
                "state": breaker.state,  # state is already a string
                "failure_count": breaker.failure_count,
                "last_failure_time": breaker.last_failure_time.isoformat() if breaker.last_failure_time else None,
                "next_attempt": (
                    getattr(breaker, "next_attempt", None).isoformat()
                    if getattr(breaker, "next_attempt", None)
                    else None
                ),
            }
            for name, breaker in self.circuit_breakers.items()
        }

    async def get_workflow_status(self, vehicle_id: str) -> Dict[str, Any]:
        """Get current workflow status for a vehicle"""
        try:
            config = {"configurable": {"thread_id": f"vehicle_{vehicle_id}"}}
            # Get the current state from the workflow
            state = await self.app.aget_state(config)

            return {
                "vehicle_id": vehicle_id,
                "current_state": state.values if state else None,
                "next_steps": state.next if state else [],
                "is_complete": len(state.next) == 0 if state else False,
            }

        except Exception as e:
            self.logger.error("Error getting workflow status", vehicle_id=vehicle_id, error=str(e))
            return {
                "vehicle_id": vehicle_id,
                "error": str(e),
                "current_state": None,
                "next_steps": [],
                "is_complete": False,
            }

    async def resume_workflow(self, vehicle_id: str, user_input: Optional[str] = None) -> Dict[str, Any]:
        """Resume a paused workflow with optional user input"""
        try:
            config = {"configurable": {"thread_id": f"vehicle_{vehicle_id}"}}

            # If user input is provided, update the state
            if user_input:
                current_state = await self.app.aget_state(config)
                if current_state and current_state.values:
                    updated_state = current_state.values.copy()
                    updated_state["user_input"] = user_input
                    updated_state["resume_timestamp"] = datetime.now().isoformat()

                    # Resume the workflow
                    result = await self.app.ainvoke(updated_state, config=config)
                    return result

            # Resume without additional input
            current_state = await self.app.aget_state(config)
            if current_state and current_state.values:
                result = await self.app.ainvoke(current_state.values, config=config)
                return result

            return {"error": "No workflow state found for vehicle"}

        except Exception as e:
            self.logger.error("Error resuming workflow", vehicle_id=vehicle_id, error=str(e))
            return {"error": str(e)}
