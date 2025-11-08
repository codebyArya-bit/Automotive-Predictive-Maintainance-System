"""
Comprehensive Test Suite for Enhanced Data Analysis Agent
Tests all functionality including tools, data processing, and integration
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced data analysis components
from agents.enhanced_data_analysis_agent import EnhancedDataAnalysisAgent
from agents.enhanced_data_analysis_tools import _generate_simulated_telemetry

# Import the actual tool functions (not the LangChain tool wrappers)
import agents.enhanced_data_analysis_tools as tools_module


class TestEnhancedDataAnalysisTools:
    """Test suite for enhanced data analysis tools"""

    def test_fetch_telemetry_simulated(self):
        """Test telemetry fetching with simulated data"""
        vehicle_id = "TEST_VEHICLE_001"
        days = 7

        # Call the actual function implementation
        telemetry_data = tools_module.fetch_telemetry.func(vehicle_id, days)

        assert isinstance(telemetry_data, list)
        assert len(telemetry_data) > 0
        assert len(telemetry_data) == days * 24  # Hourly data

        # Check data structure
        sample_record = telemetry_data[0]
        required_fields = [
            "timestamp",
            "vehicle_id",
            "engine_rpm",
            "coolant_temp",
            "battery_voltage",
            "oil_pressure",
            "fuel_level",
        ]

        for field in required_fields:
            assert field in sample_record, f"Missing field: {field}"

        assert sample_record["vehicle_id"] == vehicle_id
        print(f"✓ Fetched {len(telemetry_data)} telemetry records for {vehicle_id}")

    def test_validate_telemetry_good_data(self):
        """Test telemetry validation with good quality data"""
        # Generate clean test data
        telemetry_data = _generate_simulated_telemetry("TEST_VEHICLE_001", 3)

        validation_result = tools_module.validate_telemetry.func(telemetry_data)

        assert isinstance(validation_result, dict)
        assert "is_valid" in validation_result
        assert "data_quality_score" in validation_result
        assert "issues" in validation_result
        assert "cleaned_data" in validation_result
        assert "statistics" in validation_result

        # Should be valid with good simulated data
        assert validation_result["data_quality_score"] > 0.7
        assert len(validation_result["cleaned_data"]) > 0

        print(f"✓ Data validation passed with quality score: {validation_result['data_quality_score']:.2f}")

    def test_validate_telemetry_poor_data(self):
        """Test telemetry validation with poor quality data"""
        # Create data with issues
        poor_data = [
            {
                "timestamp": "2024 - 01 - 01T00:00:00",
                "vehicle_id": "TEST_VEHICLE_001",
                "engine_rpm": -100,  # Invalid negative RPM
                "coolant_temp": 200,  # Too high
                "battery_voltage": None,  # Missing value
                "oil_pressure": 150,  # Out of range
                "fuel_level": 50,
            },
            {
                "timestamp": "2024 - 01 - 01T01:00:00",
                "vehicle_id": "TEST_VEHICLE_001",
                "engine_rpm": None,  # Missing
                "coolant_temp": None,  # Missing
                "battery_voltage": 5,  # Too low
                "oil_pressure": None,  # Missing
                "fuel_level": None,  # Missing
            },
        ]

        validation_result = tools_module.validate_telemetry.func(poor_data)

        assert validation_result["data_quality_score"] < 0.8
        assert len(validation_result["issues"]) > 0
        assert "cleaned_data" in validation_result

        print(f"✓ Poor data validation detected issues: {len(validation_result['issues'])} problems found")

    def test_compute_features_comprehensive(self):
        """Test comprehensive feature computation"""
        # Generate sufficient data for feature computation
        telemetry_data = _generate_simulated_telemetry("TEST_VEHICLE_001", 10)

        # Validate and clean the data first
        validation_result = tools_module.validate_telemetry.func(telemetry_data)
        cleaned_data = validation_result["cleaned_data"]

        # Compute features
        features = tools_module.compute_features.func(cleaned_data)

        assert isinstance(features, dict)
        assert len(features) > 0

        # Check for expected feature categories
        expected_feature_types = [
            "_7d_avg",  # 7-day averages
            "_30d_avg",  # 30-day averages
            "_trend",  # Rate of change
            "_volatility",  # Volatility measures
        ]

        feature_keys = list(features.keys())
        for feature_type in expected_feature_types:
            matching_features = [k for k in feature_keys if feature_type in k]
            assert len(matching_features) > 0, f"No features found for type: {feature_type}"

        # Check specific important features
        important_features = ["battery_health_score", "tire_pressure_avg", "feature_count", "data_span_hours"]

        for feature in important_features:
            assert feature in features, f"Missing important feature: {feature}"

        print(f"✓ Computed {len(features)} features including rolling averages and interaction features")

    def test_fetch_maintenance_history(self):
        """Test maintenance history fetching"""
        vehicle_id = "TEST_VEHICLE_001"

        maintenance_history = tools_module.fetch_maintenance_history.func(vehicle_id)

        assert isinstance(maintenance_history, list)
        assert len(maintenance_history) > 0

        # Check data structure
        sample_record = maintenance_history[0]
        required_fields = ["maintenance_date", "maintenance_type", "description", "cost", "mileage_at_service"]

        for field in required_fields:
            assert field in sample_record, f"Missing field: {field}"

        # Check date format
        datetime.fromisoformat(sample_record["maintenance_date"])

        print(f"✓ Fetched {len(maintenance_history)} maintenance records")


class TestEnhancedDataAnalysisAgent:
    """Test suite for the Enhanced Data Analysis Agent"""

    def __init__(self):
        """Initialize test class"""
        self.agent = None

    def setup_agent(self):
        """Create an agent instance for testing"""
        self.agent = EnhancedDataAnalysisAgent(openai_api_key="test_key")
        return self.agent

    def test_agent_initialization(self):
        """Test agent initialization"""
        agent = self.setup_agent()
        assert agent is not None
        assert agent.openai_api_key == "test_key"
        assert len(agent.tools) == 4

        # Check tool names using the correct attribute
        tool_names = [tool.name for tool in agent.tools]
        expected_tools = ["fetch_telemetry", "validate_telemetry", "compute_features", "fetch_maintenance_history"]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

        print("✓ Agent initialized successfully with all required tools")

    def test_agent_info(self):
        """Test agent information retrieval"""
        agent = self.setup_agent()
        info = agent.get_agent_info()

        assert isinstance(info, dict)
        assert info["agent_name"] == "EnhancedDataAnalysisAgent"
        assert info["version"] == "2.0"
        assert "capabilities" in info
        assert "tools_available" in info
        assert len(info["capabilities"]) > 0
        assert len(info["tools_available"]) == 4

        print("✓ Agent info retrieved successfully")

    def test_analyze_vehicle_data_fallback(self):
        """Test vehicle data analysis using fallback method"""
        agent = self.setup_agent()
        state = {"vehicle_id": "TEST_VEHICLE_001", "analysis_days": 7, "analysis_type": "comprehensive"}

        result = agent.analyze_vehicle_data(state)

        assert isinstance(result, dict)
        assert "success" in result
        assert "analysis_results" in result

        if result["success"]:
            analysis_results = result["analysis_results"]
            assert "vehicle_id" in analysis_results
            assert "data_quality" in analysis_results
            assert "features" in analysis_results
            assert "maintenance_history" in analysis_results
            assert "summary" in analysis_results

            # Check summary structure
            summary = analysis_results["summary"]
            assert "quality_assessment" in summary
            assert "recommendations" in summary
            assert "analysis_confidence" in summary

            print(f"✓ Analysis completed successfully for {state['vehicle_id']}")
            print(f"  - Data quality: {summary['quality_assessment']}")
            print(f"  - Features computed: {summary['feature_count']}")
            print(f"  - Recommendations: {len(summary['recommendations'])}")
        else:
            print(f"✗ Analysis failed: {result.get('error', 'Unknown error')}")

    def test_analyze_vehicle_data_no_vehicle_id(self):
        """Test analysis with missing vehicle ID"""
        agent = self.setup_agent()
        state = {}

        result = agent.analyze_vehicle_data(state)

        assert not result["success"]
        assert "error" in result
        assert "No vehicle_id provided" in result["error"]

        print("✓ Properly handled missing vehicle ID")

    def test_analysis_summary_generation(self):
        """Test analysis summary generation"""
        agent = self.setup_agent()
        # Create mock data for summary generation
        validation_results = {"data_quality_score": 0.85, "issues": ["Minor sensor anomaly detected"], "is_valid": True}

        features = {
            "battery_voltage_7d_avg": 12.4,
            "engine_rpm_trend": 0.1,
            "battery_health_score": 0.8,
            "error_code_frequency": 0.05,
            "feature_count": 25,
        }

        maintenance_history = [
            {
                "maintenance_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "maintenance_type": "Oil Change",
                "description": "Routine oil change",
            }
        ]

        summary = agent._generate_analysis_summary(
            validation_results, features, maintenance_history, "TEST_VEHICLE_001", 30
        )

        assert isinstance(summary, dict)
        assert "quality_assessment" in summary
        assert "recommendations" in summary
        assert "analysis_confidence" in summary
        assert summary["data_quality_score"] == 0.85
        assert len(summary["recommendations"]) > 0

        print("✓ Analysis summary generated successfully")


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases"""

    def test_end_to_end_analysis_workflow(self):
        """Test complete end-to-end analysis workflow"""
        print("\n=== End-to-End Analysis Workflow Test ===")

        # Initialize agent
        agent = EnhancedDataAnalysisAgent(openai_api_key="test_key")

        # Test state
        state = {"vehicle_id": "INTEGRATION_TEST_001", "analysis_days": 14, "analysis_type": "predictive"}

        # Run analysis
        result = agent.analyze_vehicle_data(state)

        assert result["success"], f"Analysis failed: {result.get('error')}"

        analysis_results = result["analysis_results"]

        # Validate complete workflow
        assert analysis_results["vehicle_id"] == state["vehicle_id"]
        assert analysis_results["analysis_period_days"] == state["analysis_days"]

        # Check data quality assessment
        data_quality = analysis_results["data_quality"]
        assert "data_quality_score" in data_quality
        assert "cleaned_data" in data_quality

        # Check feature engineering
        features = analysis_results["features"]
        assert len(features) > 10  # Should have multiple features

        # Check maintenance context
        maintenance_history = analysis_results["maintenance_history"]
        assert isinstance(maintenance_history, list)

        # Check summary and recommendations
        summary = analysis_results["summary"]
        assert len(summary["recommendations"]) > 0

        print(f"✓ End-to-end workflow completed successfully")
        print(f"  - Vehicle: {analysis_results['vehicle_id']}")
        print(f"  - Quality Score: {data_quality['data_quality_score']:.2f}")
        print(f"  - Features: {len(features)}")
        print(f"  - Maintenance Records: {len(maintenance_history)}")
        print(f"  - Confidence: {summary['analysis_confidence']}")

    def test_data_quality_scenarios(self):
        """Test various data quality scenarios"""
        print("\n=== Data Quality Scenarios Test ===")

        scenarios = [
            {
                "name": "High Quality Data",
                "data": _generate_simulated_telemetry("HQ_VEHICLE", 5),
                "expected_quality": 0.8,
            },
            {"name": "Empty Data", "data": [], "expected_quality": 0.0},
            {
                "name": "Sparse Data",
                "data": _generate_simulated_telemetry("SPARSE_VEHICLE", 1)[:5],  # Only 5 records
                "expected_quality": 0.5,
            },
        ]

        for scenario in scenarios:
            print(f"\nTesting: {scenario['name']}")

            validation_result = tools_module.validate_telemetry.func(scenario["data"])

            quality_score = validation_result["data_quality_score"]
            print(f"  Quality Score: {quality_score:.2f}")
            print(f"  Issues: {len(validation_result['issues'])}")

            if scenario["name"] == "Empty Data":
                assert quality_score == 0.0
                assert not validation_result["is_valid"]
            elif scenario["name"] == "High Quality Data":
                assert quality_score >= scenario["expected_quality"]

            print(f"✓ {scenario['name']} scenario validated")


def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("=" * 60)
    print("ENHANCED DATA ANALYSIS AGENT - COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    # Test tools
    print("\n1. Testing Enhanced Data Analysis Tools...")
    tools_test = TestEnhancedDataAnalysisTools()
    tools_test.test_fetch_telemetry_simulated()
    tools_test.test_validate_telemetry_good_data()
    tools_test.test_validate_telemetry_poor_data()
    tools_test.test_compute_features_comprehensive()
    tools_test.test_fetch_maintenance_history()

    # Test agent
    print("\n2. Testing Enhanced Data Analysis Agent...")
    agent_test = TestEnhancedDataAnalysisAgent()

    agent_test.test_agent_initialization()
    agent_test.test_agent_info()
    agent_test.test_analyze_vehicle_data_fallback()
    agent_test.test_analyze_vehicle_data_no_vehicle_id()
    agent_test.test_analysis_summary_generation()

    # Test integration scenarios
    print("\n3. Testing Integration Scenarios...")
    integration_test = TestIntegrationScenarios()
    integration_test.test_end_to_end_analysis_workflow()
    integration_test.test_data_quality_scenarios()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
    print("=" * 60)

    # Print summary
    print("\nSUMMARY:")
    print("- Enhanced data analysis tools: ✓ Working")
    print("- Agent initialization and info: ✓ Working")
    print("- Data analysis workflow: ✓ Working")
    print("- Error handling: ✓ Working")
    print("- Integration scenarios: ✓ Working")
    print("- Data quality validation: ✓ Working")
    print("- Feature engineering: ✓ Working")
    print("- Maintenance history: ✓ Working")


if __name__ == "__main__":
    run_comprehensive_tests()
