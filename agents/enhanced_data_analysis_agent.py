"""
Enhanced Data Analysis Agent for Automotive Predictive Maintenance
Processes vehicle telemetry and prepares features for diagnosis
"""

import os
import sys
import logging
from typing import Dict, List, Any
from datetime import datetime

# Add the project root to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.agents import create_agent

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain not available, agent will run in fallback mode")

from state import State
from agents.base_agent import BaseAgent
from agents.enhanced_data_analysis_tools import (
    fetch_telemetry,
    validate_telemetry,
    compute_features,
    fetch_maintenance_history,
)

# Configure logging
logger = logging.getLogger(__name__)

# Enhanced Data Analysis Agent Prompt
data_analysis_prompt = """You are a Data Analysis Agent for automotive predictive maintenance.

Your task: Analyze vehicle telemetry data and prepare it for failure prediction.

Steps:
1. Fetch telemetry data for the given vehicle (past 30 days)
2. Validate data quality - check for anomalies, missing values
3. Compute engineered features:
   - Rolling averages (7-day, 30-day) for key sensors (battery voltage, oil pressure, etc.)
   - Rate of change (how quickly values are changing)
   - Interaction features (e.g., high RPM + low oil pressure)
4. Fetch maintenance history to provide context
5. Return: Clean dataset with features ready for ML model + data quality report

If data quality is poor (>20% missing values), flag it and suggest waiting for more data.

Available tools:
- fetch_telemetry: Get vehicle telemetry data from database
- validate_telemetry: Check data quality and clean the data
- compute_features: Generate ML features from telemetry
- fetch_maintenance_history: Get historical maintenance records

Always provide detailed analysis and clear recommendations based on the data quality and features computed.

Current task: {input}

Analysis results should include:
- Data quality assessment with specific metrics
- Feature engineering results with key statistics
- Maintenance history context
- Recommendations for next steps
- Any data quality issues or concerns

Be thorough in your analysis and provide actionable insights.
"""


class EnhancedDataAnalysisAgent(BaseAgent):
    """Enhanced Data Analysis Agent for processing vehicle telemetry and feature engineering"""

    def __init__(self, openai_api_key: str):
        """Initialize the Enhanced Data Analysis Agent"""
        super().__init__("enhanced_data_analysis")
        self.openai_api_key = openai_api_key
        self.llm = None
        self.agent = None
        self.tools = [fetch_telemetry, validate_telemetry, compute_features, fetch_maintenance_history]

        if LANGCHAIN_AVAILABLE:
            self._initialize_langchain_agent()
        else:
            logger.warning("LangChain not available, using fallback mode")

    async def _execute_internal(self, state: State) -> State:
        """Execute the enhanced data analysis agent"""
        try:
            # Call the analyze_vehicle_data method
            analysis_results = self.analyze_vehicle_data(state)

            # Ensure analysis_results is not None
            if analysis_results is None:
                analysis_results = {
                    "success": False,
                    "error": "analyze_vehicle_data returned None",
                    "analysis_results": {},
                }

            # Update state with results
            state["enhanced_data_analysis_results"] = analysis_results
            state["analysis_type"] = "enhanced"

            # Extract telemetry data for other agents
            if "telemetry_snapshot" in state:
                telemetry_data = state["telemetry_snapshot"]
                if isinstance(telemetry_data, dict) and "telemetry" in telemetry_data:
                    state["telemetry_data"] = telemetry_data["telemetry"]

            return state

        except Exception as e:
            logger.error(f"Enhanced data analysis failed: {e}")
            state["enhanced_data_analysis_error"] = str(e)
            return state

    def _initialize_langchain_agent(self):
        """Initialize the LangChain agent with tools and prompt"""
        try:
            # Initialize the language model
            self.llm = ChatOpenAI(model="gpt - 4", temperature=0.1, openai_api_key=self.openai_api_key)

            # Create the agent with tools
            self.agent = create_agent(
                llm=self.llm, tools=self.tools, prompt=ChatPromptTemplate.from_template(data_analysis_prompt)
            )

            logger.info("Enhanced Data Analysis Agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize LangChain agent: {e}")
            self.agent = None

    def analyze_vehicle_data(self, state: State) -> Dict[str, Any]:
        """
        Main method to analyze vehicle telemetry data and prepare features

        Args:
            state: Current state containing vehicle information and analysis parameters

        Returns:
            Dictionary with analysis results, features, and recommendations
        """
        try:
            vehicle_id = state.get("vehicle_id")
            if not vehicle_id:
                return {"success": False, "error": "No vehicle_id provided in state", "analysis_results": {}}

            logger.info(f"Starting enhanced data analysis for vehicle {vehicle_id}")

            # Determine analysis parameters
            days = state.get("analysis_days", 30)
            analysis_type = state.get("analysis_type", "comprehensive")

            if self.agent and LANGCHAIN_AVAILABLE:
                return self._analyze_with_langchain(vehicle_id, days, analysis_type)
            else:
                return self._analyze_with_fallback(vehicle_id, days, analysis_type)

        except Exception as e:
            logger.error(f"Error in analyze_vehicle_data: {e}")
            return {"success": False, "error": str(e), "analysis_results": {}}

    def _analyze_with_langchain(self, vehicle_id: str, days: int, analysis_type: str) -> Dict[str, Any]:
        """Analyze using LangChain agent"""
        try:
            # Prepare the input for the agent
            input_text = f"""
            Analyze vehicle telemetry data for vehicle ID: {vehicle_id}

            Parameters:
            - Analysis period: {days} days
            - Analysis type: {analysis_type}

            Please perform a comprehensive analysis including:
            1. Fetch and validate telemetry data
            2. Compute ML features with rolling statistics
            3. Retrieve maintenance history for context
            4. Provide data quality assessment and recommendations
            """

            # Execute the agent
            result = self.agent.invoke({"input": input_text})

            # Ensure result is not None
            if result is None:
                result = {}

            return {
                "success": True,
                "analysis_results": {
                    "agent_response": result.get("output", "") if isinstance(result, dict) else str(result),
                    "vehicle_id": vehicle_id,
                    "analysis_period_days": days,
                    "analysis_type": analysis_type,
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"LangChain analysis failed: {e}")
            return self._analyze_with_fallback(vehicle_id, days, analysis_type)

    def _analyze_with_fallback(self, vehicle_id: str, days: int, analysis_type: str) -> Dict[str, Any]:
        """Fallback analysis without LangChain"""
        try:
            logger.info("Using fallback analysis method")

            # Get the actual tool functions from the LangChain tool wrappers
            fetch_telemetry_func = None
            validate_telemetry_func = None
            compute_features_func = None
            fetch_maintenance_history_func = None

            for tool in self.tools:
                if tool.name == "fetch_telemetry":
                    fetch_telemetry_func = tool.func
                elif tool.name == "validate_telemetry":
                    validate_telemetry_func = tool.func
                elif tool.name == "compute_features":
                    compute_features_func = tool.func
                elif tool.name == "fetch_maintenance_history":
                    fetch_maintenance_history_func = tool.func

            # Step 1: Fetch telemetry data
            telemetry_data = fetch_telemetry_func(vehicle_id, days)
            if telemetry_data is None:
                telemetry_data = []

            # Step 2: Validate data quality
            validation_results = validate_telemetry_func(telemetry_data)
            if validation_results is None:
                validation_results = {
                    "is_valid": False,
                    "cleaned_data": [],
                    "data_quality_score": 0,
                    "issues": ["Failed to validate telemetry data"],
                }

            # Step 3: Compute features if data is valid
            features = {}
            if validation_results.get("is_valid", False):
                features = compute_features_func(validation_results.get("cleaned_data", []))
                if features is None:
                    features = {}

            # Step 4: Fetch maintenance history
            maintenance_history = fetch_maintenance_history_func(vehicle_id)
            if maintenance_history is None:
                maintenance_history = []

            # Step 5: Generate analysis summary
            analysis_summary = self._generate_analysis_summary(
                validation_results, features, maintenance_history, vehicle_id, days
            )

            return {
                "success": True,
                "analysis_results": {
                    "vehicle_id": vehicle_id,
                    "analysis_period_days": days,
                    "analysis_type": analysis_type,
                    "data_quality": validation_results,
                    "features": features,
                    "maintenance_history": maintenance_history,
                    "summary": analysis_summary,
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
            return {"success": False, "error": str(e), "analysis_results": {}}

    def _generate_analysis_summary(
        self, validation_results: Dict, features: Dict, maintenance_history: List[Dict], vehicle_id: str, days: int
    ) -> Dict[str, Any]:
        """Generate a comprehensive analysis summary"""

        data_quality_score = validation_results.get("data_quality_score", 0)
        issues = validation_results.get("issues", [])

        # Assess data quality
        if data_quality_score >= 0.9:
            quality_assessment = "Excellent data quality"
        elif data_quality_score >= 0.8:
            quality_assessment = "Good data quality"
        elif data_quality_score >= 0.6:
            quality_assessment = "Fair data quality - some issues detected"
        else:
            quality_assessment = "Poor data quality - significant issues detected"

        # Feature analysis
        feature_count = len(features)
        key_features = {k: v for k, v in features.items() if not k.startswith("_") and "avg" in k}

        # Maintenance insights
        recent_maintenance = [
            m
            for m in maintenance_history
            if (datetime.now() - datetime.fromisoformat(m["maintenance_date"])).days <= 90
        ]

        # Generate recommendations
        recommendations = []

        if data_quality_score < 0.8:
            recommendations.append("Improve data collection - significant data quality issues detected")

        if len(issues) > 5:
            recommendations.append("Address multiple sensor anomalies detected in telemetry")

        if len(recent_maintenance) == 0:
            recommendations.append("No recent maintenance found - schedule inspection")

        if features.get("battery_health_score", 1) < 0.7:
            recommendations.append("Battery health declining - monitor closely")

        if features.get("error_code_frequency", 0) > 0.1:
            recommendations.append("High error code frequency - investigate diagnostic codes")

        if not recommendations:
            recommendations.append("Vehicle telemetry appears normal - continue monitoring")

        return {
            "quality_assessment": quality_assessment,
            "data_quality_score": data_quality_score,
            "issues_detected": len(issues),
            "feature_count": feature_count,
            "key_features": key_features,
            "recent_maintenance_count": len(recent_maintenance),
            "recommendations": recommendations,
            "analysis_confidence": (
                "High" if data_quality_score > 0.8 else "Medium" if data_quality_score > 0.6 else "Low"
            ),
        }

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent"""
        return {
            "agent_name": "EnhancedDataAnalysisAgent",
            "version": "2.0",
            "capabilities": [
                "Telemetry data fetching",
                "Data quality validation",
                "Feature engineering",
                "Maintenance history analysis",
                "ML-ready feature generation",
                "Anomaly detection",
                "Rolling statistics computation",
            ],
            "tools_available": [tool.name for tool in self.tools],
            "langchain_enabled": LANGCHAIN_AVAILABLE and self.agent is not None,
        }
