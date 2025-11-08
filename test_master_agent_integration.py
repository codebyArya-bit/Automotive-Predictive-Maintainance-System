#!/usr/bin/env python3
"""
Integration tests for the Enhanced Data Analysis Agent with the Master Agent system
Tests the complete workflow routing and agent integration
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from master_agent import MasterAgent


class TestMasterAgentIntegration:
    """Test suite for Master Agent integration with Enhanced Data Analysis Agent"""

    def __init__(self):
        self.master_agent = None
        self.test_results = []

    async def setup_master_agent(self):
        """Initialize the master agent for testing"""
        try:
            self.master_agent = MasterAgent()
            print("✓ Master Agent initialized successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize Master Agent: {e}")
            return False

    async def test_enhanced_analysis_routing(self):
        """Test that enhanced analysis is properly routed in the workflow"""
        print("\n=== Testing Enhanced Analysis Routing ===")

        try:
            # Test data that should trigger enhanced analysis
            telemetry_data = {
                "vehicle_id": "INTEGRATION_TEST_001",
                "telemetry": {
                    f"sensor_{i}": {"value": i * 10, "timestamp": datetime.now().isoformat()} for i in range(15)
                },  # More than 10 data points
                "use_enhanced_analysis": True,
            }

            # Process through master agent
            result = await self.master_agent.process_vehicle(
                vehicle_id="INTEGRATION_TEST_001", telemetry_data=telemetry_data
            )

            # Verify enhanced analysis was executed
            enhanced_completed = result.get("enhanced_data_analysis_completed", False)
            basic_completed = result.get("data_analysis_completed", False)

            if enhanced_completed and not basic_completed:
                print("✓ Enhanced analysis routing working correctly")
                print(f"  - Enhanced analysis executed: {enhanced_completed}")
                print(f"  - Basic analysis skipped: {not basic_completed}")
                return True
            else:
                print(f"✗ Enhanced analysis routing failed")
                print(f"  - Enhanced analysis executed: {enhanced_completed}")
                print(f"  - Basic analysis executed: {basic_completed}")
                return False

        except Exception as e:
            print(f"✗ Enhanced analysis routing test failed: {e}")
            return False

    async def test_basic_analysis_routing(self):
        """Test that basic analysis is used for simple scenarios"""
        print("\n=== Testing Basic Analysis Routing ===")

        try:
            # Test data that should trigger basic analysis
            telemetry_data = {
                "vehicle_id": "BASIC_TEST_001",
                "telemetry": {
                    f"sensor_{i}": {"value": i * 5, "timestamp": datetime.now().isoformat()} for i in range(5)
                },  # Less than 10 data points
                "use_enhanced_analysis": False,
            }

            # Process through master agent
            result = await self.master_agent.process_vehicle(vehicle_id="BASIC_TEST_001", telemetry_data=telemetry_data)

            # Verify basic analysis was executed
            enhanced_completed = result.get("enhanced_data_analysis_completed", False)
            basic_completed = result.get("data_analysis_completed", False)

            if basic_completed and not enhanced_completed:
                print("✓ Basic analysis routing working correctly")
                print(f"  - Basic analysis executed: {basic_completed}")
                print(f"  - Enhanced analysis skipped: {not enhanced_completed}")
                return True
            else:
                print(f"✗ Basic analysis routing failed")
                print(f"  - Basic analysis executed: {basic_completed}")
                print(f"  - Enhanced analysis executed: {enhanced_completed}")
                return False

        except Exception as e:
            print(f"✗ Basic analysis routing test failed: {e}")
            return False

    async def test_workflow_completion(self):
        """Test that the complete workflow executes successfully with enhanced analysis"""
        print("\n=== Testing Complete Workflow with Enhanced Analysis ===")

        try:
            # Test data for complete workflow
            telemetry_data = {
                "vehicle_id": "WORKFLOW_TEST_001",
                "telemetry": {
                    "engine_temp": {"value": 95, "timestamp": datetime.now().isoformat()},
                    "oil_pressure": {"value": 30, "timestamp": datetime.now().isoformat()},
                    "brake_wear": {"value": 0.8, "timestamp": datetime.now().isoformat()},
                    "battery_voltage": {"value": 12.1, "timestamp": datetime.now().isoformat()},
                    "fuel_efficiency": {"value": 25.5, "timestamp": datetime.now().isoformat()},
                    "tire_pressure_fl": {"value": 32, "timestamp": datetime.now().isoformat()},
                    "tire_pressure_fr": {"value": 31, "timestamp": datetime.now().isoformat()},
                    "tire_pressure_rl": {"value": 30, "timestamp": datetime.now().isoformat()},
                    "tire_pressure_rr": {"value": 29, "timestamp": datetime.now().isoformat()},
                    "transmission_temp": {"value": 180, "timestamp": datetime.now().isoformat()},
                    "coolant_level": {"value": 0.7, "timestamp": datetime.now().isoformat()},
                    "air_filter_condition": {"value": 0.6, "timestamp": datetime.now().isoformat()},
                },
                "customer_info": {
                    "name": "Test Customer",
                    "phone": "+1234567890",
                    "email": "test@example.com",
                    "preferred_contact": "phone",
                },
                "use_enhanced_analysis": True,
                "analysis_type": "predictive",
            }

            # Process through master agent
            result = await self.master_agent.process_vehicle(
                vehicle_id="WORKFLOW_TEST_001", telemetry_data=telemetry_data
            )

            # Check which agents were executed
            agents_executed = [k.replace("_completed", "") for k in result.keys() if k.endswith("_completed")]

            print(f"✓ Workflow completed successfully")
            print(f"  - Agents executed: {', '.join(agents_executed)}")
            print(f"  - Enhanced analysis included: {'enhanced_data_analysis' in agents_executed}")
            print(f"  - Escalated to human: {result.get('escalate_to_human', False)}")

            # Verify enhanced analysis results are present
            if "enhanced_data_analysis_completed" in result:
                print(f"  - Enhanced analysis results available: ✓")
                return True
            else:
                print(f"  - Enhanced analysis results missing: ✗")
                return False

        except Exception as e:
            print(f"✗ Complete workflow test failed: {e}")
            return False

    async def test_agent_health_status(self):
        """Test that the enhanced data analysis agent is properly registered and healthy"""
        print("\n=== Testing Agent Health Status ===")

        try:
            # Get system health
            health_data = await self.master_agent.get_system_health()

            # Check if enhanced data analysis agent is registered
            agents = health_data.get("agents", {})
            enhanced_agent_health = agents.get("enhanced_data_analysis", {})

            if enhanced_agent_health:
                status = enhanced_agent_health.get("status", "unknown")
                circuit_breaker = enhanced_agent_health.get("circuit_breaker", {})

                print(f"✓ Enhanced Data Analysis Agent health check:")
                print(f"  - Status: {status}")
                print(f"  - Circuit Breaker State: {circuit_breaker.get('state', 'unknown')}")
                print(f"  - Failure Count: {circuit_breaker.get('failure_count', 0)}")

                return status == "healthy"
            else:
                print("✗ Enhanced Data Analysis Agent not found in health status")
                return False

        except Exception as e:
            print(f"✗ Agent health status test failed: {e}")
            return False

    async def test_error_handling_integration(self):
        """Test error handling and fallback mechanisms in the integrated system"""
        print("\n=== Testing Error Handling Integration ===")

        try:
            # Test with invalid data that might cause errors
            telemetry_data = {
                "vehicle_id": "ERROR_TEST_001",
                "telemetry": {"invalid_sensor": {"value": "not_a_number", "timestamp": "invalid_date"}},
                "use_enhanced_analysis": True,
            }

            # Process through master agent
            result = await self.master_agent.process_vehicle(vehicle_id="ERROR_TEST_001", telemetry_data=telemetry_data)

            # Check if the system handled errors gracefully
            workflow_failed = result.get("workflow_failed", False)
            escalated = result.get("escalate_to_human", False)

            print(f"✓ Error handling test completed:")
            print(f"  - Workflow failed: {workflow_failed}")
            print(f"  - Escalated to human: {escalated}")
            print(f"  - System remained stable: ✓")

            return True  # As long as the system doesn't crash, it's a success

        except Exception as e:
            print(f"✗ Error handling integration test failed: {e}")
            return False


async def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting Master Agent Integration Tests")
    print("=" * 60)

    test_suite = TestMasterAgentIntegration()

    # Setup
    if not await test_suite.setup_master_agent():
        print("❌ Failed to setup Master Agent. Aborting tests.")
        return

    # Run tests
    tests = [
        test_suite.test_enhanced_analysis_routing,
        test_suite.test_basic_analysis_routing,
        test_suite.test_workflow_completion,
        test_suite.test_agent_health_status,
        test_suite.test_error_handling_integration,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")

    print("\n" + "=" * 60)
    print(f"INTEGRATION TEST RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED! ✓")
        print("\nThe Enhanced Data Analysis Agent is successfully integrated with the Master Agent system.")
    else:
        print(f"⚠️  {total - passed} tests failed. Please review the integration.")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_integration_tests())
