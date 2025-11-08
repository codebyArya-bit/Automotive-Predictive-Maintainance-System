#!/usr/bin/env python3
"""
Master Agent Orchestration System - Demo Runner
Simple script to demonstrate the system capabilities
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any

from master_agent import MasterAgent
from demo import DemoScenarios


def print_banner():
    """Print system banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🚗 Master Agent Orchestration System Demo 🚗         ║
    ║                                                              ║
    ║        Automotive Predictive Maintenance with LangGraph     ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_section(title: str):
    """Print section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_subsection(title: str):
    """Print subsection header"""
    print(f"\n{'-' * 40}")
    print(f"  {title}")
    print(f"{'-' * 40}")


def format_json(data: Dict[str, Any], indent: int = 2) -> str:
    """Format JSON data for display"""
    return json.dumps(data, indent=indent, default=str)


async def run_single_scenario(scenario_name: str, scenario_data: Dict[str, Any]):
    """Run a single demo scenario"""
    print_subsection(f"Running: {scenario_name}")

    try:
        # Initialize Master Agent
        master_agent = MasterAgent()

        # Extract scenario data
        vehicle_id = scenario_data["vehicle_id"]
        telemetry_data = scenario_data["telemetry_data"]

        print(f"📊 Vehicle ID: {vehicle_id}")
        print(f"📈 Telemetry Data:")
        for key, value in telemetry_data.items():
            if key != "customer_info":
                print(f"   • {key}: {value}")

        # Process vehicle
        start_time = time.time()
        try:
            result = await master_agent.process_vehicle(vehicle_id=vehicle_id, telemetry_data=telemetry_data)
        except Exception as e:
            print(f"\n❌ Error during vehicle processing: {str(e)}")
            import traceback

            traceback.print_exc()
            return {"success": False, "error": f"Processing error: {str(e)}"}

        processing_time = time.time() - start_time

        # Debug: Check if result is None
        if result is None:
            print(f"\n❌ Error: Workflow returned None result")
            return {"success": False, "error": "Workflow returned None result"}

        # Display results
        print(f"\n✅ Processing completed in {processing_time:.2f} seconds")

        # Show prediction if available
        if "prediction" in result and result["prediction"]:
            prediction = result["prediction"]
            print(f"\n🔍 Prediction Results:")
            print(f"   • Component: {prediction.get('component', 'N/A')}")
            print(f"   • Failure Probability: {prediction.get('failure_probability', 0):.2%}")
            print(f"   • Priority: {prediction.get('priority', 'N/A')}")
            print(f"   • Predicted Failure: {prediction.get('predicted_failure_date', 'N/A')}")

        # Show customer response if available
        if "customer_response" in result and result["customer_response"]:
            response = result["customer_response"]
            print(f"\n💬 Customer Response:")
            print(f"   • Response Type: {response.get('response_type', 'N/A')}")
            print(f"   • Sentiment: {response.get('sentiment_score', 0):.1f}/10")
            print(f"   • Intent: {response.get('intent', 'N/A')}")

        # Show appointment if scheduled
        if "appointment" in result and result["appointment"]:
            appointment = result["appointment"]
            print(f"\n📅 Appointment Scheduled:")
            print(f"   • Date: {appointment.get('date', 'N/A')}")
            print(f"   • Time: {appointment.get('time', 'N/A')}")
            print(f"   • Service Center: {appointment.get('service_center', 'N/A')}")
            print(f"   • Advisor: {appointment.get('advisor', 'N/A')}")

        # Show escalation status
        if result.get("escalate_to_human", False):
            print(f"\n⚠️  Escalated to Human Agent")
            if "escalation" in result:
                escalation = result["escalation"]
                print(f"   • Reason: {escalation.get('reason', 'N/A')}")
                print(f"   • Priority: {escalation.get('priority', 'N/A')}")

        # Show agents executed
        agents_executed = [k.replace("_completed", "") for k in result.keys() if k.endswith("_completed")]
        if agents_executed:
            print(f"\n🤖 Agents Executed: {', '.join(agents_executed)}")

        return {"success": True, "processing_time": processing_time, "result": result}

    except Exception as e:
        print(f"\n❌ Error processing scenario: {str(e)}")
        return {"success": False, "error": str(e)}


async def run_system_health_check():
    """Run system health check"""
    print_section("System Health Check")

    try:
        master_agent = MasterAgent()
        health_data = await master_agent.get_system_health()

        overall_health = health_data.get("overall_health", "unknown")
        print(f"🏥 Overall Health: {overall_health.upper()}")

        # Show component health
        components = health_data.get("components", {})
        if components:
            print(f"\n📋 Component Status:")
            for component, status in components.items():
                status_icon = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                print(f"   {status_icon} {component}: {status}")

        # Show issues if any
        issues = health_data.get("issues", [])
        if issues:
            print(f"\n⚠️  Issues Detected:")
            for issue in issues:
                print(f"   • {issue}")

        # Show metrics
        metrics = health_data.get("metrics", {})
        if metrics:
            print(f"\n📊 System Metrics:")
            for metric, value in metrics.items():
                print(f"   • {metric}: {value}")

        return health_data

    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return {"overall_health": "error", "error": str(e)}


async def run_dashboard_demo():
    """Run dashboard data demo"""
    print_section("Dashboard Data Demo")

    try:
        master_agent = MasterAgent()
        dashboard_data = await master_agent.get_dashboard_data()

        # Show agent metrics
        agent_metrics = dashboard_data.get("agent_metrics", {})
        if agent_metrics:
            print(f"🤖 Agent Performance:")
            for agent, metrics in agent_metrics.items():
                if isinstance(metrics, dict):
                    success_rate = metrics.get("success_rate", 0)
                    avg_time = metrics.get("avg_execution_time", 0)
                    print(f"   • {agent}: {success_rate:.1%} success, {avg_time:.2f}s avg")

        # Show system metrics
        system_metrics = dashboard_data.get("system_metrics", {})
        if system_metrics:
            print(f"\n💻 System Performance:")
            for metric, value in system_metrics.items():
                print(f"   • {metric}: {value}")

        # Show security metrics
        security_metrics = dashboard_data.get("security_metrics", {})
        if security_metrics:
            print(f"\n🔒 Security Status:")
            for metric, value in security_metrics.items():
                print(f"   • {metric}: {value}")

        return dashboard_data

    except Exception as e:
        print(f"❌ Dashboard data retrieval failed: {str(e)}")
        return {"error": str(e)}


async def main():
    """Main demo function"""
    print_banner()

    # Initialize demo scenarios
    demo_scenarios = DemoScenarios()

    # Get all scenarios
    scenarios = {
        "Critical Engine Failure": demo_scenarios.get_critical_engine_failure(),
        "Brake Maintenance Warning": demo_scenarios.get_brake_maintenance_warning(),
        "Routine Maintenance": demo_scenarios.get_routine_maintenance(),
        "Healthy Vehicle": demo_scenarios.get_healthy_vehicle(),
    }

    # Run system health check first
    await run_system_health_check()

    # Run dashboard demo
    await run_dashboard_demo()

    # Run each scenario
    print_section("Demo Scenarios")

    results = {}
    for scenario_name, scenario_data in scenarios.items():
        result = await run_single_scenario(scenario_name, scenario_data)
        results[scenario_name] = result

        # Add delay between scenarios
        if scenario_name != list(scenarios.keys())[-1]:
            print(f"\n⏳ Waiting 2 seconds before next scenario...")
            await asyncio.sleep(2)

    # Summary
    print_section("Demo Summary")

    successful_scenarios = sum(1 for r in results.values() if r["success"])
    total_scenarios = len(results)

    print(f"📊 Scenarios Executed: {total_scenarios}")
    print(f"✅ Successful: {successful_scenarios}")
    print(f"❌ Failed: {total_scenarios - successful_scenarios}")

    if successful_scenarios > 0:
        avg_processing_time = sum(r["processing_time"] for r in results.values() if r["success"]) / successful_scenarios
        print(f"⏱️  Average Processing Time: {avg_processing_time:.2f} seconds")

    # Show failed scenarios
    failed_scenarios = [name for name, result in results.items() if not result["success"]]
    if failed_scenarios:
        print(f"\n⚠️  Failed Scenarios:")
        for scenario in failed_scenarios:
            error = results[scenario].get("error", "Unknown error")
            print(f"   • {scenario}: {error}")

    print(f"\n🎉 Demo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n💡 To run the API server: python api_server.py")
    print(f"📚 API Documentation: http://localhost:8000/docs")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {str(e)}")
        import traceback

        traceback.print_exc()
