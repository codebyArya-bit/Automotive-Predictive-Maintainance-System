#!/usr/bin/env python3
"""
Comprehensive test to debug None return from LangGraph workflow
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from master_agent import MasterAgent
from state import StateManager


async def test_workflow_none_debug():
    """Debug the None return issue in LangGraph workflow"""

    print("=== Debugging LangGraph Workflow None Return ===")

    # Initialize master agent
    master_agent = MasterAgent()

    # Test scenario that's failing
    vehicle_id = "VIN123456789DEBUG"
    session_id = f"debug_session_{vehicle_id}"

    print(f"\n--- Creating Initial State ---")
    initial_state = StateManager.create_initial_state(vehicle_id, session_id)

    # Add comprehensive telemetry data
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
            "customer_id": "CUST_DEBUG",
            "preferred_contact": "app_notification",
            "location": "Debug City, NY",
        },
    }

    initial_state["telemetry_snapshot"] = telemetry_data
    initial_state["vehicle_data"] = {"telemetry": telemetry_data["telemetry"]}

    print(f"Initial state type: {type(initial_state)}")
    print(f"Initial state keys: {list(initial_state.keys())}")

    # Test each conditional edge function
    print(f"\n--- Testing Conditional Edge Functions ---")

    analysis_method = "basic"
    diagnosis_method = "basic"

    try:
        analysis_method = master_agent._choose_analysis_method(initial_state)
        print(f"✓ _choose_analysis_method returned: {analysis_method}")

        diagnosis_method = master_agent._choose_diagnosis_method(initial_state)
        print(f"✓ _choose_diagnosis_method returned: {diagnosis_method}")

        should_escalate = master_agent._should_escalate_security(initial_state)
        print(f"✓ _should_escalate_security returned: {should_escalate}")

    except Exception as e:
        print(f"✗ Error in conditional edge functions: {str(e)}")
        import traceback

        traceback.print_exc()

    # Test workflow execution with detailed monitoring
    print(f"\n--- Testing Workflow Execution with Monitoring ---")

    try:
        config = {"configurable": {"thread_id": f"vehicle_{vehicle_id}"}}

        print(f"Config: {config}")
        print(f"About to invoke workflow...")

        # Execute the workflow with detailed logging
        result = await master_agent.app.ainvoke(initial_state, config=config)

        print(f"✓ Workflow execution completed")
        print(f"Result type: {type(result)}")
        print(f"Result is None: {result is None}")

        if result is None:
            print("✗ ERROR: Workflow returned None!")

            # Try to get workflow state
            try:
                state = await master_agent.app.aget_state(config)
                print(f"Workflow state: {state}")
                print(f"State values: {state.values if state else 'No state'}")
                print(f"State next: {state.next if state else 'No next'}")
            except Exception as state_e:
                print(f"Error getting workflow state: {str(state_e)}")

        else:
            print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")

            # Check specific fields
            if isinstance(result, dict):
                print(f"workflow_failed: {result.get('workflow_failed', 'Not set')}")
                print(f"workflow_error: {result.get('workflow_error', 'Not set')}")
                print(f"escalate_to_human: {result.get('escalate_to_human', 'Not set')}")
                print(f"escalation_reason: {result.get('escalation_reason', 'Not set')}")

                # Check agent completion flags
                agent_flags = [k for k in result.keys() if k.endswith("_completed")]
                print(f"Agent completion flags: {agent_flags}")

                # Check for None values in result
                none_keys = [k for k, v in result.items() if v is None]
                if none_keys:
                    print(f"Keys with None values: {none_keys}")

    except Exception as e:
        print(f"✗ Workflow execution failed: {str(e)}")
        import traceback

        traceback.print_exc()

    # Test individual agent executions
    print(f"\n--- Testing Individual Agent Executions ---")

    try:
        # Test data analysis agent
        print("Testing data analysis agent...")
        data_analysis_result = await master_agent._execute_data_analysis(initial_state.copy())
        print(f"✓ Data analysis completed: {data_analysis_result.get('data_analysis_completed', False)}")
        print(f"Analysis results present: {'analysis_results' in data_analysis_result}")
        if "analysis_results" in data_analysis_result:
            analysis = data_analysis_result["analysis_results"]
            if analysis is not None:
                print(f"  - Health score: {analysis.get('health_score', 'N/A')}")
                print(f"  - Anomalies: {len(analysis.get('anomalies', []))}")
                print(f"  - Warnings: {len(analysis.get('warnings', []))}")
                print(f"  - Analysis results type: {type(analysis)}")
                print(
                    f"  - Analysis results keys: {list(analysis.keys()) if isinstance(analysis, dict) else 'Not a dict'}"
                )
            else:
                print("  - Analysis results is None!")
        else:
            print("  - No analysis_results found in state!")
            print(f"  - Available keys: {list(data_analysis_result.keys())}")

        # Test diagnosis agent with analysis results
        print("\nTesting diagnosis agent...")
        diagnosis_result = await master_agent._execute_diagnosis(data_analysis_result.copy())
        print(f"✓ Diagnosis completed: {diagnosis_result.get('diagnosis_completed', False)}")
        print(f"Prediction present: {'prediction' in diagnosis_result}")

        # Check if any individual agent returned None
        if data_analysis_result is None:
            print("✗ Data analysis returned None!")
        if diagnosis_result is None:
            print("✗ Diagnosis returned None!")

    except Exception as e:
        print(f"✗ Individual agent testing failed: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_workflow_none_debug())
