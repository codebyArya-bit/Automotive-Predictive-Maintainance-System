#!/usr/bin/env python3
"""
Comprehensive Demo Script for Master Agent Orchestration System
Showcases the complete workflow with realistic automotive predictive maintenance scenarios
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List

from master_agent import MasterAgent
from config import Config


class DemoScenarios:
    """Enhanced demo scenarios with realistic data and compelling storytelling"""

    @staticmethod
    def get_critical_engine_failure() -> Dict[str, Any]:
        """Critical engine failure scenario - Enhanced with realistic data and story"""
        return {
            "vehicle_id": "FL - 2847-CRIT",
            "vin": "1HGBH41JXMN109186",
            "make": "Ford",
            "model": "Transit Connect",
            "year": 2019,
            "mileage": 87543,
            "location": {"lat": 25.7617, "lng": -80.1918, "address": "Downtown Miami, FL"},
            "telemetry_data": {
                "engine_temperature": 245,  # Critical - normal is 180 - 220°F
                "oil_pressure": 15,  # Critical - normal is 25 - 65 PSI
                "coolant_level": 25,  # Low - normal is 80 - 100%
                "battery_voltage": 11.8,  # Low - normal is 12.6V
                "fuel_level": 78,
                "vehicle_speed": 0,  # Vehicle stopped due to engine failure
                "engine_rpm": 0,
                "odometer": 87543,
                "engine_hours": 2847,
                "error_codes": ["P0217", "P0522", "P0128"],  # Engine overheating, oil pressure, coolant temp
                "last_maintenance": "2024 - 01 - 15",
                "next_maintenance_due": "2024 - 02 - 15",
                "outside_temp": 89,  # Hot Florida weather
                "humidity": 78,
                "weather": "Sunny, high heat index",
                "traffic_density": "Heavy",
                "timestamp": datetime.now().isoformat(),
            },
            "driver_info": {
                "name": "Carlos Rodriguez",
                "id": "DR - 4521",
                "experience_years": 8,
                "safety_rating": 4.7,
                "contact": "+1 - 305 - 555 - 0142",
            },
            "fleet_info": {
                "company": "Miami Express Delivery",
                "route": "Route 15 - Downtown to Airport",
                "cargo_type": "Medical supplies",
                "cargo_value": 45000,
                "delivery_priority": "Critical",
            },
            "customer_info": {
                "name": "Miami General Hospital",
                "type": "Healthcare",
                "phone": "+1 - 305 - 555 - 7890",
                "email": "logistics@miamigeneral.com",
                "preferred_contact": "voice",
                "location": "Miami, FL",
                "priority_level": "Critical",
                "contract_value": 250000,
                "relationship_years": 5,
                "satisfaction_score": 9.2,
            },
            "business_impact": {
                "delivery_delay_cost": 2500,
                "customer_satisfaction_risk": "High",
                "replacement_vehicle_needed": True,
                "estimated_repair_cost": 3500,
                "downtime_hours": 8,
            },
            "expected_outcome": "immediate_emergency_response_and_replacement",
            "story": "A delivery truck carrying critical medical supplies to Miami General Hospital has suffered a catastrophic engine failure in heavy downtown traffic. The engine temperature has spiked to dangerous levels, oil pressure has dropped critically low, and the vehicle has automatically shut down to prevent further damage. With a high-value customer expecting time-sensitive medical supplies, this scenario tests our system's ability to coordinate emergency response, arrange immediate replacement transportation, and maintain customer satisfaction during a crisis.",
        }

    @staticmethod
    def get_brake_maintenance_warning() -> Dict[str, Any]:
        """Brake maintenance warning scenario - Enhanced with predictive insights"""
        return {
            "vehicle_id": "TX - 1923-WARN",
            "vin": "2T1BURHE0JC014587",
            "make": "Toyota",
            "model": "Camry Hybrid",
            "year": 2020,
            "mileage": 62341,
            "location": {"lat": 32.7767, "lng": -96.7970, "address": "Dallas Business District, TX"},
            "telemetry_data": {
                "engine_temperature": 195,  # Normal
                "oil_pressure": 42,
                "brake_pad_thickness": {
                    "front_left": 3.2,  # mm - Warning threshold is 3.0mm
                    "front_right": 3.1,
                    "rear_left": 4.1,
                    "rear_right": 4.0,
                },
                "brake_fluid_level": 65,  # % - Should be >70%
                "brake_temp": 185,  # °F - Elevated from city driving
                "abs_activations": 23,  # Recent count - higher than normal
                "brake_pressure": 1250,  # PSI - Normal range
                "vibration_detected": True,
                "stopping_distance_increase": 8,  # % increase from baseline
                "tire_pressure_fl": 31.5,  # PSI - Slightly low
                "tire_pressure_fr": 32.0,
                "tire_pressure_rl": 31.8,
                "tire_pressure_rr": 32.2,
                "battery_voltage": 12.6,
                "fuel_level": 45,
                "vehicle_speed": 35,
                "engine_rpm": 1800,
                "error_codes": ["C1201"],  # ABS/Brake system warning
                "last_brake_service": "2023 - 08 - 20",
                "predicted_failure_date": "2024 - 03 - 15",
                "confidence_score": 0.87,
                "timestamp": datetime.now().isoformat(),
            },
            "driver_info": {
                "name": "Jennifer Martinez",
                "id": "DR - 7832",
                "experience_years": 12,
                "safety_rating": 4.9,
                "contact": "+1 - 214 - 555 - 0198",
                "driving_style": "Conservative",
            },
            "fleet_info": {
                "company": "Dallas Corporate Services",
                "route": "Route 8 - Executive Transport",
                "service_type": "Executive transportation",
                "client_tier": "Premium",
                "daily_utilization": "High",
            },
            "predictive_analysis": {
                "wear_rate": "Accelerated due to city driving",
                "failure_probability": 0.23,
                "recommended_action": "Schedule maintenance within 2 weeks",
                "cost_if_delayed": 850,
                "safety_risk_score": 6.5,
                "optimal_service_window": "2024 - 02 - 28 to 2024 - 03 - 05",
            },
            "customer_info": {
                "name": "Jennifer Martinez",
                "type": "Corporate Executive",
                "phone": "+1 - 214 - 555 - 0198",
                "email": "j.martinez@dallascorp.com",
                "preferred_contact": "app_notification",
                "location": "Dallas, TX",
                "priority_level": "High",
                "preferred_service_time": "Evening after 6 PM",
                "communication_preference": "Text and email",
                "service_history": "Always on time, values quality",
                "satisfaction_score": 9.6,
            },
            "expected_outcome": "proactive_maintenance_scheduling",
            "story": "Our predictive maintenance AI has detected early signs of brake wear in an executive transport vehicle. While the brakes are still safe, advanced analytics predict they'll need service within two weeks. The system must balance safety, customer convenience, and cost-effectiveness by scheduling proactive maintenance during the optimal service window, preventing more expensive repairs and ensuring uninterrupted service for our premium client.",
        }

    @staticmethod
    def get_routine_maintenance() -> Dict[str, Any]:
        """Routine maintenance scenario - Enhanced with optimization insights"""
        return {
            "vehicle_id": "CA - 5612-MAINT",
            "vin": "5NPE34AF4JH012345",
            "make": "Hyundai",
            "model": "Sonata",
            "year": 2021,
            "mileage": 45678,
            "location": {"lat": 34.0522, "lng": -118.2437, "address": "Los Angeles Metro Area, CA"},
            "telemetry_data": {
                "engine_temperature": 190,  # Normal
                "oil_pressure": 38,
                "oil_life_remaining": 15,  # % remaining - due for change
                "air_filter_condition": 68,  # % - Could be optimized
                "tire_pressure_fl": 31.5,  # PSI - Slightly low
                "tire_pressure_fr": 32.0,
                "tire_pressure_rl": 31.8,
                "tire_pressure_rr": 32.2,
                "tire_tread_depth": {
                    "front_left": 6.2,  # mm - Good condition
                    "front_right": 6.1,
                    "rear_left": 6.8,
                    "rear_right": 6.7,
                },
                "battery_voltage": 12.7,
                "fuel_efficiency": 34.2,  # MPG - Good for hybrid
                "battery_health": 94,  # % - Excellent
                "emissions_level": "Ultra Low",
                "last_service": "2023 - 11 - 15",
                "service_interval": 7500,  # miles
                "miles_since_service": 7234,
                "next_service_due": "Within 500 miles",
                "timestamp": datetime.now().isoformat(),
            },
            "driver_info": {
                "name": "Michael Chen",
                "id": "DR - 2156",
                "experience_years": 6,
                "safety_rating": 4.8,
                "contact": "+1 - 323 - 555 - 0176",
                "driving_style": "Efficient",
            },
            "fleet_info": {
                "company": "LA Green Logistics",
                "route": "Route 12 - Eco-Friendly Deliveries",
                "service_type": "Sustainable delivery",
                "environmental_rating": "A+",
                "carbon_offset_program": True,
            },
            "optimization_opportunities": {
                "fuel_savings_potential": 12,  # % improvement possible
                "emission_reduction": 8,  # % reduction possible
                "tire_pressure_optimization": "2 PSI adjustment needed",
                "route_efficiency_gain": 5,  # % time savings
                "maintenance_bundling": ["Oil change", "Air filter", "Tire rotation"],
                "cost_savings": 85,  # $ from bundled service
            },
            "sustainability_metrics": {
                "carbon_footprint": "15% below fleet average",
                "eco_driving_score": 92,
                "fuel_efficiency_rank": "Top 10%",
                "environmental_impact": "Positive",
            },
            "customer_info": {
                "name": "Michael Chen",
                "type": "Eco-conscious driver",
                "phone": "+1 - 323 - 555 - 0176",
                "email": "m.chen@lagreenlogistics.com",
                "preferred_contact": "app_notification",
                "location": "Los Angeles, CA",
                "priority_level": "Standard",
                "preferred_service_time": "Weekend mornings",
                "communication_preference": "Mobile app notifications",
                "loyalty_program": "Green Miles Rewards",
                "satisfaction_score": 8.9,
            },
            "expected_outcome": "optimized_maintenance_scheduling",
            "story": "A hybrid vehicle in our eco-friendly fleet is approaching its routine maintenance interval. While all systems are functioning well, our AI has identified several optimization opportunities that could improve fuel efficiency by 12% and reduce emissions by 8%. The system must coordinate a comprehensive service appointment that bundles multiple maintenance items, maximizes environmental benefits, and aligns with the driver's sustainability values and schedule preferences.",
        }

    @staticmethod
    def get_healthy_vehicle() -> Dict[str, Any]:
        """Healthy vehicle scenario - Enhanced with performance optimization"""
        return {
            "vehicle_id": "NY - 8734-OPT",
            "vin": "1G1ZD5ST8JF123456",
            "make": "Chevrolet",
            "model": "Malibu",
            "year": 2022,
            "mileage": 28456,
            "location": {"lat": 40.7128, "lng": -74.0060, "address": "Manhattan Financial District, NY"},
            "telemetry_data": {
                "engine_temperature": 195,  # °F - Perfect operating temperature
                "oil_pressure": 45,  # PSI - Excellent
                "oil_life_remaining": 78,  # % - Good condition
                "coolant_level": 95,  # % - Excellent
                "battery_voltage": 12.8,  # V - Perfect
                "fuel_level": 82,  # % - Good
                "tire_pressure_fl": 32.0,  # PSI - Perfect
                "tire_pressure_fr": 32.0,
                "tire_pressure_rl": 32.0,
                "tire_pressure_rr": 32.0,
                "brake_pad_thickness": 8.5,  # mm - Excellent condition
                "air_filter_efficiency": 92,  # % - Very good
                "fuel_efficiency": 28.5,  # MPG - Above average for city driving
                "emissions_compliance": "Exceeds standards",
                "last_service": "2024 - 01 - 10",
                "next_service": "Not due for 3,000 miles",
                "timestamp": datetime.now().isoformat(),
            },
            "driver_info": {
                "name": "Sarah Johnson",
                "id": "DR - 9847",
                "experience_years": 15,
                "safety_rating": 5.0,
                "contact": "+1 - 212 - 555 - 0134",
                "driving_style": "Professional",
            },
            "fleet_info": {
                "company": "NYC Executive Transport",
                "route": "Route 3 - Financial District Circuit",
                "service_type": "Premium business transport",
                "client_tier": "Platinum",
                "utilization_rate": "Optimal",
            },
            "performance_metrics": {
                "acceleration_score": 95,  # Excellent responsiveness
                "braking_efficiency": 98,  # Outstanding stopping power
                "handling_rating": 94,  # Superior maneuverability
                "comfort_index": 96,  # Premium ride quality
                "noise_level": "Whisper quiet",
                "vibration_level": "Minimal",
                "overall_condition": "Exceptional",
            },
            "optimization_insights": {
                "route_efficiency": 97,  # % - Nearly optimal
                "fuel_optimization": "Achieving 105% of EPA rating",
                "driver_performance": "Exemplary eco-driving",
                "maintenance_prediction": "No issues forecasted",
                "cost_per_mile": "$0.42 - 15% below fleet average",
                "customer_satisfaction": "Consistently 5-star ratings",
            },
            "ai_recommendations": {
                "continue_current_maintenance": True,
                "driver_recognition": "Commend excellent driving habits",
                "route_optimization": "Current routes are optimal",
                "cost_savings": "Vehicle performing 15% above expectations",
                "predictive_insights": "No maintenance needed for 90 days",
            },
            "customer_info": {
                "name": "Manhattan Financial Group",
                "type": "Corporate VIP",
                "phone": "+1 - 212 - 555 - 7890",
                "email": "transport@manhattanfg.com",
                "preferred_contact": "app_notification",
                "location": "New York, NY",
                "priority_level": "Platinum",
                "service_expectations": "Flawless execution",
                "communication_preference": "Proactive updates",
                "contract_value": 180000,
                "satisfaction_score": 9.8,
            },
            "expected_outcome": "performance_monitoring_and_optimization",
            "story": "This vehicle represents the gold standard of our fleet - everything is operating at peak performance. Our AI monitoring system tracks this exceptional vehicle to understand what makes it so successful, using these insights to optimize the entire fleet. The system analyzes perfect operational patterns, driver behavior, and maintenance practices to replicate this success across other vehicles, while ensuring this premium service continues to exceed our VIP client's expectations.",
        }

    @staticmethod
    def get_winter_weather_scenario() -> Dict[str, Any]:
        """New scenario: Winter weather emergency response"""
        return {
            "vehicle_id": "MN - 4521-SNOW",
            "vin": "1FTFW1ET8JFC12345",
            "make": "Ford",
            "model": "F - 150",
            "year": 2020,
            "mileage": 73892,
            "location": {"lat": 44.9778, "lng": -93.2650, "address": "Minneapolis, MN - Highway 35W"},
            "telemetry_data": {
                "engine_temperature": 165,  # °F - Struggling to warm up
                "battery_voltage": 11.2,  # V - Cold weather impact
                "tire_pressure_fl": 28.5,  # PSI - Reduced due to cold
                "tire_pressure_fr": 28.0,
                "tire_pressure_rl": 29.0,
                "tire_pressure_rr": 28.8,
                "fuel_level": 23,  # % - Critical in emergency
                "traction_control_events": 47,  # High due to ice
                "abs_activations": 12,  # Frequent due to conditions
                "heater_usage": 100,  # % - Maximum
                "defrost_active": True,
                "emergency_flashers": True,
                "outside_temp": -12,  # °F - Extreme cold
                "wind_chill": -28,  # °F - Dangerous
                "snow_depth": 8,  # inches
                "visibility": 0.25,  # miles - Blizzard conditions
                "road_conditions": "Ice covered",
                "weather_alert": "Blizzard Warning",
                "timestamp": datetime.now().isoformat(),
            },
            "driver_info": {
                "name": "Robert Anderson",
                "id": "DR - 3344",
                "experience_years": 20,
                "safety_rating": 4.9,
                "contact": "+1 - 612 - 555 - 0187",
                "winter_driving_certified": True,
            },
            "emergency_situation": {
                "type": "Weather-related breakdown",
                "severity": "High risk",
                "passenger_count": 2,
                "medical_conditions": "Elderly passenger with heart condition",
                "estimated_exposure_time": "45 minutes",
                "nearest_shelter": "2.3 miles",
                "emergency_services_eta": "25 minutes",
            },
            "customer_info": {
                "name": "Robert Anderson",
                "type": "Emergency situation",
                "phone": "+1 - 612 - 555 - 0187",
                "email": "r.anderson@email.com",
                "preferred_contact": "voice",
                "location": "Minneapolis, MN",
                "priority_level": "Emergency",
                "medical_alert": "Passenger with heart condition",
            },
            "expected_outcome": "emergency_response_and_rescue_coordination",
            "story": "A pickup truck carrying two passengers, including an elderly person with a heart condition, has broken down during a severe blizzard on a Minneapolis highway. With temperatures at -12°F, wind chill at -28°F, and limited fuel for heating, this becomes a life-threatening emergency. Our AI system must coordinate immediate emergency response, dispatch rescue services, and ensure passenger safety while managing the extreme weather conditions.",
        }

    @staticmethod
    def get_electric_vehicle_scenario() -> Dict[str, Any]:
        """New scenario: Electric vehicle range optimization"""
        return {
            "vehicle_id": "CA - 7890-EV",
            "vin": "5YJ3E1EA8JF123456",
            "make": "Tesla",
            "model": "Model 3",
            "year": 2023,
            "mileage": 15678,
            "location": {"lat": 37.7749, "lng": -122.4194, "address": "San Francisco, CA - Highway 101"},
            "telemetry_data": {
                "battery_charge_level": 18,  # % - Low battery
                "range_remaining": 42,  # miles
                "battery_health": 96,  # % - Excellent
                "charging_rate_capability": "250kW Supercharging",
                "temperature_impact": -15,  # % range reduction due to cold
                "energy_consumption": 285,  # Wh/mile - Higher than optimal
                "regenerative_braking_efficiency": 89,  # % - Good
                "climate_control_usage": 12,  # % energy usage
                "battery_temperature": 68,  # °F - Optimal range
                "motor_efficiency": 94,  # % - Excellent
                "timestamp": datetime.now().isoformat(),
            },
            "driver_info": {
                "name": "Alex Kim",
                "id": "DR - 5566",
                "experience_years": 8,
                "safety_rating": 4.7,
                "contact": "+1 - 415 - 555 - 0199",
                "ev_experience": "Advanced",
            },
            "route_analysis": {
                "destination": "San Jose, CA",
                "distance_remaining": 48,  # miles
                "elevation_changes": "Moderate hills",
                "traffic_conditions": "Heavy",
                "nearest_supercharger": 3.2,  # miles
                "charging_stations_enroute": 4,
                "estimated_arrival_charge": 8,  # % - Cutting it close
                "optimal_charging_stop": "Palo Alto Supercharger",
            },
            "optimization_factors": {
                "eco_mode_available": True,
                "route_alternatives": 2,
                "charging_strategy": "Fast charge to 80% in 25 minutes",
                "cost_optimization": "Off-peak charging available",
                "time_vs_energy_tradeoff": "Moderate",
            },
            "customer_info": {
                "name": "Alex Kim",
                "type": "Tech professional",
                "phone": "+1 - 415 - 555 - 0199",
                "email": "alex.kim@techcorp.com",
                "preferred_contact": "app_notification",
                "location": "San Francisco, CA",
                "priority_level": "High",
                "ev_adoption_stage": "Early adopter",
                "charging_preferences": "Fast and convenient",
                "sustainability_focus": "Very high",
            },
            "expected_outcome": "intelligent_range_optimization_and_charging_guidance",
            "story": "An electric vehicle with 18% battery charge is navigating heavy San Francisco traffic with 48 miles to go to reach San Jose. The AI system must optimize the route, manage energy consumption, and guide the driver to the most efficient charging strategy. This scenario showcases our system's ability to handle the unique challenges of electric vehicle fleet management, including range anxiety, charging infrastructure, and energy optimization.",
        }


class DemoRunner:
    """Main demo runner class"""

    def __init__(self):
        self.master_agent = MasterAgent()
        self.config = Config()
        self.scenarios = DemoScenarios()

    async def run_comprehensive_demo(self):
        """Run a comprehensive demo showcasing all system capabilities"""
        print("\n" + "=" * 80)
        print("🚗 AUTOMIND AI - COMPREHENSIVE SYSTEM DEMONSTRATION")
        print("=" * 80)

        await self._display_system_info()

        # Enhanced scenario list with new scenarios
        scenarios = [
            ("Critical Engine Failure", self.scenarios.get_critical_engine_failure()),
            ("Brake Maintenance Warning", self.scenarios.get_brake_maintenance_warning()),
            ("Routine Maintenance", self.scenarios.get_routine_maintenance()),
            ("Healthy Vehicle Monitoring", self.scenarios.get_healthy_vehicle()),
            ("Winter Weather Emergency", self.scenarios.get_winter_weather_scenario()),
            ("Electric Vehicle Optimization", self.scenarios.get_electric_vehicle_scenario()),
        ]

        results = []
        start_time = time.time()

        for i, (scenario_name, scenario_data) in enumerate(scenarios, 1):
            print(f"\n{'=' * 60}")
            print(f"📋 SCENARIO {i}/6: {scenario_name.upper()}")
            print(f"{'=' * 60}")

            # Display enhanced scenario story
            if "story" in scenario_data:
                print(f"\n📖 SCENARIO STORY:")
                print(f"   {scenario_data['story']}")

            # Display vehicle and location info
            print(f"\n🚗 VEHICLE INFO:")
            print(f"   Vehicle ID: {scenario_data['vehicle_id']}")
            if "make" in scenario_data and "model" in scenario_data:
                print(f"   Vehicle: {scenario_data['year']} {scenario_data['make']} {scenario_data['model']}")
            if "location" in scenario_data:
                print(f"   Location: {scenario_data['location']['address']}")

            # Display driver info if available
            if "driver_info" in scenario_data:
                driver = scenario_data["driver_info"]
                print(f"\n👤 DRIVER INFO:")
                print(f"   Name: {driver['name']} (ID: {driver['id']})")
                print(f"   Experience: {driver['experience_years']} years")
                print(f"   Safety Rating: {driver['safety_rating']}/5.0")

            # Display fleet info if available
            if "fleet_info" in scenario_data:
                fleet = scenario_data["fleet_info"]
                print(f"\n🏢 FLEET INFO:")
                print(f"   Company: {fleet['company']}")
                if "route" in fleet:
                    print(f"   Route: {fleet['route']}")
                if "service_type" in fleet:
                    print(f"   Service Type: {fleet['service_type']}")

            print(f"\n⚡ PROCESSING SCENARIO...")

            try:
                # Simulate AI processing with realistic delay
                await asyncio.sleep(2)

                result = await self._run_scenario(scenario_data)
                results.append(
                    {
                        "scenario": scenario_name,
                        "result": result,
                        "timestamp": datetime.now().isoformat(),
                        "data": scenario_data,
                    }
                )

            except Exception as e:
                print(f"❌ Error processing scenario: {str(e)}")
                results.append(
                    {
                        "scenario": scenario_name,
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                        "data": scenario_data,
                    }
                )

            # Add pause between scenarios for better readability
            if i < len(scenarios):
                print(f"\n⏳ Preparing next scenario...")
                await asyncio.sleep(1)

        time.time() - start_time
        await self._display_demo_summary(results)
        await self._display_system_metrics()

        return results

    async def _display_system_info(self):
        """Display system information and health status"""
        print("📊 System Information:")
        print(f"   • Configuration: {self.config.__class__.__name__}")
        print(
            f"   • Prediction Thresholds: High={self.config.PREDICTION_THRESHOLD_HIGH}, Medium={self.config.PREDICTION_THRESHOLD_MEDIUM}"
        )
        print(f"   • Escalation Sentiment Threshold: {self.config.ESCALATION_SENTIMENT_THRESHOLD}")
        print(f"   • Agent Timeout: {self.config.AGENT_TIMEOUT_SECONDS}s")

        # Check system health
        try:
            health_status = await self.master_agent.get_system_health()
            print(f"   • System Health: {health_status.get('overall_health', 'Unknown')}")

            if health_status.get("issues"):
                print(f"   • Health Issues: {len(health_status['issues'])}")
        except Exception as e:
            print(f"   • System Health: Unable to check ({str(e)})")

        print()

    async def _run_scenario(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single scenario and return results"""
        vehicle_id = scenario_data["vehicle_id"]
        telemetry_data = scenario_data["telemetry_data"]
        customer_info = scenario_data["customer_info"]
        expected_outcome = scenario_data["expected_outcome"]

        print(f"   Vehicle ID: {vehicle_id}")
        print(f"   Customer: {customer_info['name']} ({customer_info['location']})")
        print(f"   Expected Outcome: {expected_outcome}")
        print()

        start_time = time.time()

        try:
            # Add customer info to telemetry for processing
            enhanced_telemetry = {**telemetry_data, "customer_info": customer_info}

            # Process vehicle through Master Agent
            print("   🔄 Processing through Master Agent workflow...")
            result = await self.master_agent.process_vehicle(vehicle_id, enhanced_telemetry)

            processing_time = time.time() - start_time

            # Display results
            await self._display_scenario_results(result, processing_time, expected_outcome)

            return {
                "success": True,
                "processing_time": processing_time,
                "final_state": result,
                "agents_executed": [k for k in result.keys() if k.endswith("_completed")],
                "escalated": result.get("escalate_to_human", False),
                "prediction": result.get("prediction", {}),
                "customer_response": result.get("customer_response", {}),
                "appointment": result.get("appointment", {}),
                "feedback": result.get("feedback", {}),
            }

        except Exception as e:
            processing_time = time.time() - start_time
            print(f"   ❌ Error: {str(e)}")

            return {"success": False, "error": str(e), "processing_time": processing_time}

    async def _display_scenario_results(self, result: Dict[str, Any], processing_time: float, expected_outcome: str):
        """Display detailed results for a scenario"""
        print(f"   ⏱️  Processing Time: {processing_time:.2f}s")

        # Show prediction results
        prediction = result.get("prediction", {})
        if prediction:
            print(
                f"   🔍 Prediction: {prediction.get('issue_type', 'Unknown')} "
                f"(Priority: {prediction.get('priority', 'Unknown')}, "
                f"Probability: {prediction.get('probability', 0):.1%})"
            )

        # Show customer engagement
        customer_response = result.get("customer_response", {})
        if customer_response:
            print(
                f"   💬 Customer Response: {customer_response.get('intent', 'Unknown')} "
                f"(Sentiment: {customer_response.get('sentiment', 0)}/10)"
            )

        # Show appointment details
        appointment = result.get("appointment", {})
        if appointment:
            service_center = appointment.get("service_center", {})
            if service_center is None:
                service_center = {}
            # Ensure service_center is a dict before calling .get()
            if not isinstance(service_center, dict):
                service_center = {}
            print(
                f"   📅 Appointment: {appointment.get('status', 'Unknown')} "
                f"at {service_center.get('name', 'Unknown Center')}"
            )
            if appointment.get("date"):
                print(f"      Date: {appointment['date']} at {appointment.get('time', 'Unknown time')}")

        # Show feedback
        feedback = result.get("feedback", {})
        if feedback:
            print(f"   📝 Feedback: Satisfaction {feedback.get('satisfaction_rating', 0)}/10")

        # Show escalation status
        if result.get("escalate_to_human"):
            escalation_reason = result.get("escalation_reason", "Unknown reason")
            print(f"   🚨 Escalated to Human: {escalation_reason}")

        # Show UEBA analysis
        ueba_analysis = result.get("ueba_analysis", {})
        if ueba_analysis:
            risk_score = ueba_analysis.get("risk_score", 0)
            print(f"   🛡️  Security Risk Score: {risk_score:.2f}/10")

            violations = ueba_analysis.get("violations", [])
            if violations:
                print(f"      Compliance Violations: {len(violations)}")

        # Show agents executed
        agents_executed = [k.replace("_completed", "") for k in result.keys() if k.endswith("_completed")]
        if agents_executed:
            print(f"   🤖 Agents Executed: {', '.join(agents_executed)}")

        # Validate against expected outcome
        self._validate_outcome(result, expected_outcome)

        print()

    def _validate_outcome(self, result: Dict[str, Any], expected_outcome: str):
        """Validate the result against expected outcome"""
        prediction = result.get("prediction", {})
        customer_response = result.get("customer_response", {})
        appointment = result.get("appointment", {})
        escalated = result.get("escalate_to_human", False)

        if expected_outcome == "immediate_contact_and_scheduling":
            if prediction.get("priority") in ["P0", "P1"] and customer_response and appointment:
                print("   ✅ Outcome: As expected - immediate contact and scheduling")
            else:
                print("   ⚠️  Outcome: Unexpected - should have contacted and scheduled")

        elif expected_outcome == "contact_and_schedule_maintenance":
            if customer_response and (appointment or escalated):
                print("   ✅ Outcome: As expected - contacted customer")
            else:
                print("   ⚠️  Outcome: Unexpected - should have contacted customer")

        elif expected_outcome == "app_notification_and_optional_scheduling":
            if customer_response or prediction.get("priority") in ["P2", "P3"]:
                print("   ✅ Outcome: As expected - appropriate notification level")
            else:
                print("   ⚠️  Outcome: Unexpected - notification level mismatch")

        elif expected_outcome == "monitoring_only":
            if not customer_response and not escalated:
                print("   ✅ Outcome: As expected - monitoring only")
            else:
                print("   ⚠️  Outcome: Unexpected - should be monitoring only")

    async def _display_demo_summary(self, results: List[Dict[str, Any]]):
        """Display summary of all demo results"""
        print("\n📈 Demo Summary")
        print("=" * 40)

        successful_scenarios = [r for r in results if r["result"]["success"]]
        failed_scenarios = [r for r in results if not r["result"]["success"]]

        print(f"   • Total Scenarios: {len(results)}")
        print(f"   • Successful: {len(successful_scenarios)}")
        print(f"   • Failed: {len(failed_scenarios)}")

        if successful_scenarios:
            avg_processing_time = sum(r["result"]["processing_time"] for r in successful_scenarios) / len(
                successful_scenarios
            )
            print(f"   • Average Processing Time: {avg_processing_time:.2f}s")

            escalated_count = sum(1 for r in successful_scenarios if r["result"]["escalated"])
            print(f"   • Escalations: {escalated_count}/{len(successful_scenarios)}")

            # Priority distribution
            priorities = [
                r["result"]["prediction"].get("priority", "Unknown")
                for r in successful_scenarios
                if r["result"]["prediction"]
            ]
            priority_counts = {p: priorities.count(p) for p in set(priorities)}
            print(f"   • Priority Distribution: {priority_counts}")

        if failed_scenarios:
            print(f"\n   ❌ Failed Scenarios:")
            for result in failed_scenarios:
                print(f"      • {result['scenario']}: {result['result']['error']}")

        print()

    async def _display_system_metrics(self):
        """Display system metrics and monitoring data"""
        print("📊 System Metrics & Monitoring")
        print("=" * 40)

        try:
            # Get dashboard data
            dashboard_data = await self.master_agent.get_dashboard_data()

            print("   Agent Performance:")
            agent_metrics = dashboard_data.get("agent_metrics", {})
            for agent_name, metrics in agent_metrics.items():
                print(
                    f"      • {agent_name}: {metrics.get('execution_count', 0)} executions, "
                    f"{metrics.get('avg_duration', 0):.2f}s avg"
                )

            print("\n   System Health:")
            system_metrics = dashboard_data.get("system_metrics", {})
            print(f"      • CPU Usage: {system_metrics.get('cpu_usage', 0):.1f}%")
            print(f"      • Memory Usage: {system_metrics.get('memory_usage', 0):.1f}%")
            print(f"      • Active Workflows: {system_metrics.get('active_workflows', 0)}")

            print("\n   Security & Compliance:")
            security_metrics = dashboard_data.get("security_metrics", {})
            print(f"      • Risk Score: {security_metrics.get('avg_risk_score', 0):.2f}/10")
            print(f"      • Compliance Violations: {security_metrics.get('violations_count', 0)}")
            print(f"      • Anomalies Detected: {security_metrics.get('anomalies_count', 0)}")

        except Exception as e:
            print(f"   ⚠️  Unable to retrieve metrics: {str(e)}")

        # Circuit breaker status
        try:
            cb_status = self.master_agent.get_circuit_breaker_status()
            print("\n   Circuit Breaker Status:")
            for agent_name, status in cb_status.items():
                state = status["state"]
                failure_count = status["failure_count"]
                print(f"      • {agent_name}: {state} (failures: {failure_count})")
        except Exception as e:
            print(f"   ⚠️  Unable to retrieve circuit breaker status: {str(e)}")

        print()


async def main():
    """Main demo function"""
    print("🚀 Starting Master Agent Orchestration System Demo")
    print("This demo showcases automotive predictive maintenance workflows")
    print()

    demo_runner = DemoRunner()

    try:
        results = await demo_runner.run_comprehensive_demo()

        print("✅ Demo completed successfully!")
        print(f"   Results saved with {len(results)} scenarios processed")

        # Optionally save results to file
        with open("demo_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print("   📄 Detailed results saved to demo_results.json")

    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
