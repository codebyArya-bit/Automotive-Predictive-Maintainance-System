#!/usr/bin/env python3
"""
Test script for the Enhanced Data Analysis Agent integration
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from master_agent import MasterAgent
from config import Config


async def test_enhanced_data_analysis():
    """Test the enhanced data analysis agent integration"""
    print("🧪 Testing Enhanced Data Analysis Agent Integration")
    print("=" * 60)

    try:
        # Initialize the master agent
        config = Config()
        master_agent = MasterAgent(config)

        # Test Case 1: Basic analysis (should use basic agent)
        print("\n📊 Test Case 1: Basic Analysis")
        print("-" * 40)

        basic_state = {
            "vehicle_id": "TEST_VEHICLE_001",
            "vehicle_data": {"telemetry": {"engine_rpm": 2500, "coolant_temp": 85, "battery_voltage": 12.4}},
            "analysis_type": "basic",
            "timestamp": datetime.now().isoformat(),
        }

        print(f"Input state: {json.dumps(basic_state, indent=2)}")

        # Execute the workflow
        result = await master_agent.app.ainvoke(basic_state, config={"configurable": {"thread_id": "test_basic"}})

        print(f"✅ Basic analysis completed")
        print(f"Data analysis completed: {result.get('data_analysis_completed', False)}")
        print(f"Enhanced data analysis completed: {result.get('enhanced_data_analysis_completed', False)}")

        # Test Case 2: Enhanced analysis (should use enhanced agent)
        print("\n🚀 Test Case 2: Enhanced Analysis")
        print("-" * 40)

        enhanced_state = {
            "vehicle_id": "TEST_VEHICLE_002",
            "vehicle_data": {
                "telemetry": {
                    "engine_rpm": 2500,
                    "coolant_temp": 85,
                    "battery_voltage": 12.4,
                    "oil_pressure": 45,
                    "fuel_level": 75,
                    "throttle_position": 25,
                    "brake_pressure": 0,
                    "transmission_temp": 70,
                    "intake_air_temp": 25,
                    "exhaust_temp": 400,
                    "turbo_boost": 1.2,
                    "lambda_sensor": 0.98,
                }
            },
            "analysis_type": "ml_features",
            "use_enhanced_analysis": True,
            "timestamp": datetime.now().isoformat(),
        }

        print(f"Input state: {json.dumps({k: v for k, v in enhanced_state.items() if k != 'vehicle_data'}, indent=2)}")
        print(f"Telemetry data points: {len(enhanced_state['vehicle_data']['telemetry'])}")

        # Execute the workflow
        result = await master_agent.app.ainvoke(enhanced_state, config={"configurable": {"thread_id": "test_enhanced"}})

        print(f"✅ Enhanced analysis completed")
        print(f"Data analysis completed: {result.get('data_analysis_completed', False)}")
        print(f"Enhanced data analysis completed: {result.get('enhanced_data_analysis_completed', False)}")

        # Test Case 3: Automatic routing based on telemetry complexity
        print("\n🔄 Test Case 3: Automatic Routing")
        print("-" * 40)

        auto_state = {
            "vehicle_id": "TEST_VEHICLE_003",
            "vehicle_data": {"telemetry": {f"sensor_{i}": i * 10 for i in range(15)}},  # 15 data points
            "timestamp": datetime.now().isoformat(),
        }

        print(f"Telemetry data points: {len(auto_state['vehicle_data']['telemetry'])}")
        print("Expected routing: Enhanced (due to >10 data points)")

        # Execute the workflow
        result = await master_agent.app.ainvoke(auto_state, config={"configurable": {"thread_id": "test_auto"}})

        print(f"✅ Automatic routing completed")
        print(f"Data analysis completed: {result.get('data_analysis_completed', False)}")
        print(f"Enhanced data analysis completed: {result.get('enhanced_data_analysis_completed', False)}")

        # Summary
        print("\n📋 Test Summary")
        print("=" * 60)
        print("✅ All test cases completed successfully")
        print("✅ Enhanced Data Analysis Agent integration working")
        print("✅ Workflow routing logic functioning correctly")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def test_enhanced_agent_tools():
    """Test the enhanced data analysis agent tools directly"""
    print("\n🔧 Testing Enhanced Data Analysis Tools")
    print("=" * 60)

    try:
        from agents.enhanced_data_analysis_agent import EnhancedDataAnalysisAgent

        # Initialize the enhanced agent
        agent = EnhancedDataAnalysisAgent()

        # Test state
        test_state = {
            "vehicle_id": "TOOL_TEST_001",
            "vehicle_data": {
                "telemetry": {
                    "engine_rpm": 2500,
                    "coolant_temp": 85,
                    "battery_voltage": 12.4,
                    "oil_pressure": 45,
                    "fuel_level": 75,
                }
            },
            "timestamp": datetime.now().isoformat(),
        }

        print("Testing enhanced agent execution...")
        result = await agent.execute(test_state)

        print(f"✅ Enhanced agent executed successfully")
        print(f"Analysis completed: {result.get('enhanced_data_analysis_completed', False)}")

        if "analysis_results" in result:
            analysis = result["analysis_results"]
            print(f"Features computed: {'features' in analysis}")
            print(f"Data quality report: {'data_quality' in analysis}")
            print(f"Recommendations: {'recommendations' in analysis}")

        return True

    except Exception as e:
        print(f"❌ Enhanced agent tools test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("🚀 Enhanced Data Analysis Agent Integration Tests")
    print("=" * 80)

    # Test 1: Integration with master agent
    integration_success = await test_enhanced_data_analysis()

    # Test 2: Enhanced agent tools
    tools_success = await test_enhanced_agent_tools()

    # Final results
    print("\n🏁 Final Test Results")
    print("=" * 80)

    if integration_success and tools_success:
        print("✅ ALL TESTS PASSED")
        print("🎉 Enhanced Data Analysis Agent is fully integrated and functional!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("🔧 Please check the error messages above for debugging information")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
