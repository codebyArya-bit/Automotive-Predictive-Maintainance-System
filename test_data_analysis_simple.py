#!/usr/bin/env python3
"""
Simple test to debug data analysis agent
"""
import asyncio
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from master_agent import MasterAgent


async def test_data_analysis():
    print("=== Simple Data Analysis Test ===")

    # Create master agent
    master_agent = MasterAgent()

    # Create test state
    test_state = {
        "vehicle_id": "VIN123456789DEBUG",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_year": 2020,
        "vin": "VIN123456789DEBUG",
        "telemetry_snapshot": {
            "engine_temperature": 95,
            "oil_pressure": 45,
            "brake_pad_thickness": 8,
            "battery_voltage": 12.4,
            "tire_pressure": [32, 31, 33, 32],
            "fuel_level": 75,
            "mileage": 45000,
            "error_codes": ["P0171", "B1234"],
        },
        "prediction": {"priority": "medium"},
        "analysis_results": None,
        "vehicle_data": {"category": "sedan"},
        "agent_executions": [],  # Add missing field
        "current_agent": "data_analysis",
        "workflow_step": "data_analysis",
        "retry_count": 0,
        "max_retries": 3,
        "last_error": None,
        "fallback_used": False,
        "escalate_to_human": False,
        "escalation_reason": None,
        "human_agent_id": None,
        "session_id": "test_session",
        "created_at": "2025 - 10 - 21T08:00:00Z",
        "updated_at": "2025 - 10 - 21T08:00:00Z",
        "ueba_flags": [],
        "compliance_status": "compliant",
        "customer_satisfaction": None,
        "feedback_collected": False,
        "improvement_suggestions": [],
    }

    print(f"Initial telemetry type: {type(test_state['telemetry_snapshot'])}")
    print(f"Initial telemetry keys: {list(test_state['telemetry_snapshot'].keys())}")

    try:
        # Test data analysis
        print("\n--- Testing Data Analysis ---")
        result = await master_agent._execute_data_analysis(test_state.copy())

        print(f"Result type: {type(result)}")
        print(f"Result keys: {list(result.keys())}")

        if "analysis_results" in result:
            analysis = result["analysis_results"]
            print(f"Analysis results type: {type(analysis)}")
            if analysis is not None:
                print(f"Analysis keys: {list(analysis.keys()) if isinstance(analysis, dict) else 'Not a dict'}")
                if isinstance(analysis, dict):
                    print(f"Health score: {analysis.get('health_score', 'N/A')}")
                    print(f"Anomalies count: {len(analysis.get('anomalies', []))}")
                    print(f"Warnings count: {len(analysis.get('warnings', []))}")
            else:
                print("Analysis results is None!")
        else:
            print("No analysis_results key found!")

    except Exception as e:
        print(f"Error during data analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_data_analysis())
