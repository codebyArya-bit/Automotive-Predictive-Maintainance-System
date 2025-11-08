#!/usr/bin/env python3
"""
Direct test for the LangGraph workflow to isolate NoneType errors
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from master_agent import MasterAgent
from state import StateManager


async def test_workflow_direct():
    """Test the LangGraph workflow directly with detailed logging"""

    print("=== Testing LangGraph Workflow Directly ===")

    # Initialize master agent
    master_agent = MasterAgent()

    # Test scenario that's failing
    vehicle_id = "VIN123456789CRITICAL"
    session_id = f"test_session_{vehicle_id}"

    print(f"\n--- Creating Initial State ---")
    initial_state = StateManager.create_initial_state(vehicle_id, session_id)

    print(f"Initial state type: {type(initial_state)}")
    print(f"Initial state keys: {list(initial_state.keys())}")

    # Add telemetry data
    telemetry_data = {
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
    }

    initial_state["telemetry_snapshot"] = telemetry_data

    print(f"\n--- Testing Workflow Execution ---")

    try:
        # Execute the workflow step by step
        config = {"configurable": {"thread_id": f"vehicle_{vehicle_id}"}}

        print(f"Config: {config}")
        print(f"About to invoke workflow with state type: {type(initial_state)}")

        # Test the workflow
        result = await master_agent.app.ainvoke(initial_state, config=config)

        print(f"✓ Workflow executed successfully")
        print(f"Result type: {type(result)}")

        if result is None:
            print("✗ ERROR: Workflow returned None!")
        else:
            print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")

            # Check specific fields
            if isinstance(result, dict):
                print(f"workflow_failed: {result.get('workflow_failed', 'Not set')}")
                print(f"workflow_error: {result.get('workflow_error', 'Not set')}")
                print(f"escalate_to_human: {result.get('escalate_to_human', 'Not set')}")
                print(f"escalation_reason: {result.get('escalation_reason', 'Not set')}")

    except Exception as e:
        print(f"✗ Workflow execution failed: {str(e)}")
        import traceback

        traceback.print_exc()

    print(f"\n--- Testing Individual Workflow Steps ---")

    try:
        # Test health check step
        print("Testing health check...")
        health_result = await master_agent._perform_health_check(initial_state)
        print(f"Health check result type: {type(health_result)}")

        # Test analysis method choice
        print("Testing analysis method choice...")
        analysis_method = master_agent._choose_analysis_method(health_result)
        print(f"Analysis method chosen: {analysis_method}")

        # Test data analysis step
        print("Testing data analysis step...")
        if analysis_method == "basic":
            analysis_result = await master_agent._execute_data_analysis(health_result)
        else:
            analysis_result = await master_agent._execute_enhanced_data_analysis(health_result)

        print(f"Analysis result type: {type(analysis_result)}")
        if analysis_result is None:
            print("✗ ERROR: Analysis step returned None!")
        else:
            print(
                f"Analysis result keys: {list(analysis_result.keys()) if isinstance(analysis_result, dict) else 'Not a dict'}"
            )

    except Exception as e:
        print(f"✗ Individual step testing failed: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_workflow_direct())
