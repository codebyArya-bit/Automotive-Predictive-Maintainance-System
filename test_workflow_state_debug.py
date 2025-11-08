#!/usr/bin/env python3
"""
Debug test to track state changes between workflow nodes
"""
import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from master_agent import MasterAgent
from state import StateManager


async def test_workflow_state_tracking():
    """Test workflow with detailed state tracking"""
    print("=== Testing Workflow State Tracking ===")

    # Create master agent
    master_agent = MasterAgent()

    # Create initial state with all required fields
    state_manager = StateManager()
    initial_state = state_manager.create_initial_state(vehicle_id="TEST - 001", session_id="test_session")
    # Add issue description manually
    initial_state["issue_description"] = "Engine temperature warning light"

    print(f"Initial state keys: {list(initial_state.keys())}")
    print(f"Initial analysis_results: {initial_state.get('analysis_results', 'NOT_PRESENT')}")

    # Execute workflow step by step
    print("\n=== Step 1: Health Check ===")
    health_state = await master_agent._perform_health_check(initial_state)
    print(f"After health check - analysis_results: {health_state.get('analysis_results', 'NOT_PRESENT')}")

    print("\n=== Step 2: Data Analysis ===")
    analysis_state = await master_agent._execute_data_analysis(health_state)
    print(f"After data analysis - analysis_results type: {type(analysis_state.get('analysis_results'))}")
    print(
        f"After data analysis - analysis_results keys: {list(analysis_state.get('analysis_results', {}).keys()) if analysis_state.get('analysis_results') else 'None or missing'}"
    )

    # Check if analysis_results is properly set
    if "analysis_results" in analysis_state and analysis_state["analysis_results"] is not None:
        print("✓ analysis_results is present and not None")
        analysis_results = analysis_state["analysis_results"]
        print(f"  - health_score: {analysis_results.get('health_score', 'missing')}")
        print(f"  - anomalies count: {len(analysis_results.get('anomalies', []))}")
    else:
        print("✗ analysis_results is missing or None")

    print("\n=== Step 3: Diagnosis ===")
    try:
        diagnosis_state = await master_agent._execute_diagnosis(analysis_state)
        print("✓ Diagnosis completed successfully")
        print(f"After diagnosis - prediction: {diagnosis_state.get('prediction', 'NOT_PRESENT')}")
    except Exception as e:
        print(f"✗ Diagnosis failed: {e}")
        print(f"State keys at failure: {list(analysis_state.keys())}")
        print(f"analysis_results at failure: {analysis_state.get('analysis_results', 'NOT_PRESENT')}")

    print("\n=== Full Workflow Test ===")
    try:
        # Test the full workflow using the compiled app
        config = {"configurable": {"thread_id": "test_thread"}}
        final_state = await master_agent.app.ainvoke(initial_state, config)
        print("✓ Full workflow completed")
        print(f"Final state keys: {list(final_state.keys())}")
        print(f"Final analysis_results: {'Present' if final_state.get('analysis_results') else 'Missing'}")
        print(f"Final prediction: {'Present' if final_state.get('prediction') else 'Missing'}")
    except Exception as e:
        print(f"✗ Full workflow failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_workflow_state_tracking())
