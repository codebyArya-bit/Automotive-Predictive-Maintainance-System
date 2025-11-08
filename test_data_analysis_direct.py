#!/usr/bin/env python3
"""
Direct test for data_analysis_agent to isolate NoneType errors
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.data_analysis_agent import DataAnalysisAgent
from state import StateManager


async def test_data_analysis_agent():
    """Test the data_analysis_agent directly with various scenarios"""

    print("=== Testing Data Analysis Agent Directly ===")

    # Initialize agent
    agent = DataAnalysisAgent()

    # Test scenarios
    scenarios = [
        {
            "name": "Critical Engine Failure",
            "vehicle_id": "VIN123456789CRITICAL",
            "telemetry_data": {
                "telemetry": {
                    "engine_temperature": 120.5,
                    "oil_pressure": 15.2,
                    "brake_pad_thickness": {"front_left": 8.5, "front_right": 8.3, "rear_left": 7.8, "rear_right": 7.9},
                    "tire_pressure": {"front_left": 32.1, "front_right": 31.8, "rear_left": 30.5, "rear_right": 30.7},
                    "battery_voltage": 11.8,
                    "transmission_fluid_level": 85.2,
                    "mileage": 87500,
                    "error_codes": ["P0300", "P0420", "C1201"],
                },
                "customer_info": {
                    "customer_id": "CUST_001",
                    "preferred_contact": "app_notification",
                    "location": "New York, NY",
                },
            },
        },
        {
            "name": "Routine Maintenance",
            "vehicle_id": "VIN456789123ROUTINE",
            "telemetry_data": {
                "telemetry": {
                    "engine_temperature": 95.2,
                    "oil_pressure": 35.8,
                    "brake_pad_thickness": {"front_left": 4.2, "front_right": 4.1, "rear_left": 5.8, "rear_right": 5.9},
                    "tire_pressure": {"front_left": 31.5, "front_right": 31.2, "rear_left": 30.8, "rear_right": 31.0},
                    "battery_voltage": 12.4,
                    "transmission_fluid_level": 78.5,
                    "mileage": 45000,
                    "error_codes": ["P0171"],
                },
                "customer_info": {
                    "customer_id": "CUST_002",
                    "preferred_contact": "email",
                    "location": "Los Angeles, CA",
                },
            },
        },
        {"name": "None Telemetry Test", "vehicle_id": "VIN_NONE_TEST", "telemetry_data": None},
        {"name": "Empty Telemetry Test", "vehicle_id": "VIN_EMPTY_TEST", "telemetry_data": {}},
    ]

    for scenario in scenarios:
        print(f"\n--- Testing: {scenario['name']} ---")

        try:
            # Create initial state
            session_id = f"test_session_{scenario['vehicle_id']}"
            state = StateManager.create_initial_state(scenario["vehicle_id"], session_id)

            # Add telemetry data
            if scenario["telemetry_data"]:
                state["telemetry_snapshot"] = scenario["telemetry_data"]

            print(f"State created: {type(state)}")
            print(f"State keys: {list(state.keys())}")

            # Execute agent
            result = await agent.execute(state)

            print(f"✓ Agent executed successfully")
            print(f"Result type: {type(result)}")
            print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")

            # Check for analysis results
            if "analysis_results" in result:
                analysis = result["analysis_results"]
                print(f"Analysis results: {analysis}")

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_data_analysis_agent())
