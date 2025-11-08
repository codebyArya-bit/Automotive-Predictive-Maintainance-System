"""
Edge Case Scenarios for Demo
Demonstrates system behavior in challenging situations
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random


class EdgeCaseScenarios:
    """Handles demonstration of edge cases as required by challenge"""

    def __init__(self, master_agent=None):
        self.master_agent = master_agent
        self.scenarios = {
            "declined_appointment": self._scenario_declined_appointment,
            "urgent_failure": self._scenario_urgent_failure,
            "multi_vehicle_fleet": self._scenario_multi_vehicle_fleet,
            "recurring_defect": self._scenario_recurring_defect,
        }

    async def run_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Run a specific edge case scenario"""
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")

        scenario_func = self.scenarios[scenario_name]
        result = await scenario_func()

        return {
            "scenario": scenario_name,
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "status": "completed"
        }

    async def _scenario_declined_appointment(self) -> Dict[str, Any]:
        """
        Scenario 1: Customer Declines Appointment
        Shows how system handles negative response and re-engagement attempts
        """
        steps = []

        # Step 1: Initial prediction
        steps.append({
            "step": 1,
            "action": "Predictive Analysis",
            "description": "System detects brake pad wear prediction for Vehicle #7ALSE94T6W43T3254",
            "data": {
                "vehicle_id": "7ALSE94T6W43T3254",
                "component": "brake_pads",
                "predicted_failure": "14 days",
                "priority": "P2",
                "confidence": 0.87
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 2: Customer engagement via voice
        steps.append({
            "step": 2,
            "action": "AI Voice Call Initiated",
            "description": "Maya (AI Agent) calls customer to explain prediction",
            "data": {
                "contact_method": "voice_call",
                "customer_name": "Rajesh Kumar",
                "phone": "+91-9876543210",
                "language": "hindi"
            },
            "conversation": [
                {"speaker": "agent", "text": "Hello Mr. Kumar, this is Maya from AutoMind. I'm calling regarding your Honda Civic."},
                {"speaker": "customer", "text": "Yes, what's the issue?"},
                {"speaker": "agent", "text": "Our predictive system detected that your brake pads will need replacement within 2 weeks. Would you like to schedule a service?"},
                {"speaker": "customer", "text": "Not right now, I'm too busy."},
            ],
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 3: Objection handling
        steps.append({
            "step": 3,
            "action": "Objection Handling",
            "description": "AI attempts to address concerns and offer alternatives",
            "data": {
                "objection_type": "timing_concern",
                "ai_response": "I understand you're busy. We have weekend slots and can complete the service in just 45 minutes. Would Saturday morning work?"
            },
            "conversation": [
                {"speaker": "agent", "text": "I completely understand Mr. Kumar. We have weekend slots available, and the service takes only 45 minutes. Would Saturday morning at 9 AM work for you?"},
                {"speaker": "customer", "text": "No, I really can't commit right now. Maybe next month."},
            ],
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 4: Customer declines
        steps.append({
            "step": 4,
            "action": "Appointment Declined",
            "description": "Customer firmly declines - System switches to feedback collection",
            "data": {
                "customer_response": "declined",
                "reason": "timing_not_suitable",
                "sentiment_score": -0.3,
                "next_action": "feedback_collection"
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 5: Feedback agent takes over
        steps.append({
            "step": 5,
            "action": "Feedback Agent Activated",
            "description": "Collect reasons for decline and customer preferences",
            "data": {
                "questions_asked": [
                    "What would make scheduling more convenient for you?",
                    "Would you prefer a reminder in 1 week or 2 weeks?",
                    "Do you have any concerns about our service?"
                ],
                "responses_collected": {
                    "preferred_reminder": "2_weeks",
                    "preferred_day": "saturday",
                    "preferred_time": "morning",
                    "concerns": "none"
                }
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 6: Follow-up scheduled
        steps.append({
            "step": 6,
            "action": "Follow-up Scheduled",
            "description": "System schedules automated follow-up based on customer preference",
            "data": {
                "follow_up_method": "app_notification",
                "follow_up_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "urgency_increased": False,
                "notes": "Customer prefers Saturday morning slots. Re-engage in 2 weeks."
            },
            "timestamp": datetime.now().isoformat()
        })

        # Step 7: Escalation path if needed
        steps.append({
            "step": 7,
            "action": "Escalation Plan Set",
            "description": "If component fails before appointment, escalate to urgent (P0)",
            "data": {
                "escalation_trigger": "component_failure_detected",
                "escalation_action": "immediate_voice_call + nearest_service_center_alert",
                "monitoring": "continuous_telemetry_tracking"
            },
            "timestamp": datetime.now().isoformat()
        })

        return {
            "scenario_name": "Declined Appointment",
            "outcome": "Graceful handling with follow-up plan",
            "steps": steps,
            "key_learnings": [
                "AI handles objections professionally",
                "System doesn't force booking",
                "Feedback collected for future improvement",
                "Escalation plan in place if urgency increases"
            ]
        }

    async def _scenario_urgent_failure(self) -> Dict[str, Any]:
        """
        Scenario 2: Urgent Failure Alert (P0 Priority)
        Shows rapid response to critical failures
        """
        steps = []

        # Step 1: Critical alert detected
        steps.append({
            "step": 1,
            "action": "CRITICAL ALERT DETECTED",
            "description": "Engine overheating detected - imminent failure risk",
            "data": {
                "vehicle_id": "1TS0ANPS9KCNX8996",
                "alert_type": "engine_overheating",
                "priority": "P0",
                "temperature": 115,  # Celsius
                "threshold": 100,
                "location": {"lat": 28.6139, "lon": 77.2090, "address": "Delhi NCR"},
                "risk_level": "CRITICAL"
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.3)

        # Step 2: Immediate voice call
        steps.append({
            "step": 2,
            "action": "EMERGENCY VOICE CALL INITIATED",
            "description": "Immediate voice call to driver - no delay",
            "data": {
                "contact_method": "emergency_voice_call",
                "call_priority": "urgent",
                "ring_override": True,  # Bypasses silent mode
                "customer_name": "Vikram Singh"
            },
            "conversation": [
                {"speaker": "agent", "text": "URGENT: Mr. Singh, this is AutoMind Emergency System. Your vehicle engine is overheating critically!"},
                {"speaker": "customer", "text": "What? What should I do?"},
                {"speaker": "agent", "text": "Pull over IMMEDIATELY and turn off the engine. Do not continue driving. Towing service is being dispatched to your location."},
            ],
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.3)

        # Step 3: Automatic service dispatch
        steps.append({
            "step": 3,
            "action": "Emergency Service Dispatch",
            "description": "Towing and emergency service automatically dispatched",
            "data": {
                "service_type": "emergency_towing",
                "nearest_service_center": "Metro Service Center - Delhi",
                "eta_minutes": 25,
                "tow_truck_id": "TOW-DL-042",
                "service_advisor_assigned": "Priya Sharma",
                "estimated_repair_time": "2-3 hours"
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.3)

        # Step 4: Real-time customer updates
        steps.append({
            "step": 4,
            "action": "Real-Time Updates Sent",
            "description": "Customer receives SMS + App notifications with live tracking",
            "data": {
                "notifications_sent": [
                    {"type": "sms", "content": "Tow truck dispatched - ETA 25 min"},
                    {"type": "app_push", "content": "Track your tow truck in real-time"},
                    {"type": "app_push", "content": "Service bay reserved - Priority handling"}
                ],
                "live_tracking_link": "https://automind.com/track/TOW-DL-042"
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.3)

        # Step 5: Diagnosis begins remotely
        steps.append({
            "step": 5,
            "action": "Remote Diagnosis Started",
            "description": "AI analyzes telemetry to prepare diagnosis for technician",
            "data": {
                "probable_causes": [
                    {"cause": "coolant_leak", "probability": 0.65},
                    {"cause": "thermostat_failure", "probability": 0.25},
                    {"cause": "water_pump_failure", "probability": 0.10}
                ],
                "parts_ordered": ["coolant", "thermostat", "gasket_kit"],
                "estimated_cost": "$450-$650",
                "technician_briefed": True
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.3)

        # Step 6: Human escalation (as needed)
        steps.append({
            "step": 6,
            "action": "Human Supervisor Notified",
            "description": "Service center manager alerted for priority handling",
            "data": {
                "escalation_reason": "P0_emergency",
                "manager_name": "Rajesh Gupta",
                "manager_phone": "+91-9999888877",
                "priority_flag": True,
                "customer_care_call_scheduled": True
            },
            "timestamp": datetime.now().isoformat()
        })

        return {
            "scenario_name": "Urgent Failure Alert (P0)",
            "outcome": "Rapid response with zero downtime",
            "response_time_seconds": 45,
            "steps": steps,
            "key_features": [
                "Immediate detection and alert",
                "Emergency voice call bypassing silent mode",
                "Automatic towing dispatch",
                "Real-time tracking and updates",
                "Remote diagnosis for faster service",
                "Human escalation for priority handling"
            ]
        }

    async def _scenario_multi_vehicle_fleet(self) -> Dict[str, Any]:
        """
        Scenario 3: Multi-Vehicle Fleet Scheduling
        Shows bulk operations and optimized scheduling
        """
        steps = []

        # Step 1: Fleet analysis
        fleet_vehicles = [
            {"id": f"FLEET-{i:03d}", "mileage": 70000 + (i * 5000), "last_service": 90 - (i * 10)}
            for i in range(1, 6)
        ]

        steps.append({
            "step": 1,
            "action": "Fleet Health Analysis",
            "description": "Analyze 5-vehicle corporate fleet for maintenance needs",
            "data": {
                "fleet_owner": "ABC Logistics",
                "fleet_size": 5,
                "vehicles": fleet_vehicles,
                "vehicles_needing_service": 5,
                "total_estimated_time": "11 hours",
                "estimated_cost": "$2,250"
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 2: Service demand forecast check
        steps.append({
            "step": 2,
            "action": "Service Capacity Check",
            "description": "Demand forecasting agent optimizes scheduling",
            "data": {
                "current_utilization": 75,
                "available_slots_this_week": 12,
                "fleet_requires_slots": 5,
                "recommendation": "staggered_scheduling",
                "optimal_days": ["Monday", "Tuesday", "Wednesday"]
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 3: Optimized schedule generated
        steps.append({
            "step": 3,
            "action": "Optimized Fleet Schedule Generated",
            "description": "AI creates staggered schedule to minimize fleet downtime",
            "data": {
                "schedule": [
                    {"vehicle": "FLEET-001", "day": "Monday", "time": "08:00", "bay": "A1", "duration": "2h"},
                    {"vehicle": "FLEET-002", "day": "Monday", "time": "10:30", "bay": "A2", "duration": "2.5h"},
                    {"vehicle": "FLEET-003", "day": "Tuesday", "time": "09:00", "bay": "A1", "duration": "2h"},
                    {"vehicle": "FLEET-004", "day": "Tuesday", "time": "14:00", "bay": "B1", "duration": "3h"},
                    {"vehicle": "FLEET-005", "day": "Wednesday", "time": "08:00", "bay": "A2", "duration": "1.5h"},
                ],
                "total_fleet_downtime": "11 hours spread over 3 days",
                "business_impact": "minimal - max 2 vehicles down at once"
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 4: Fleet manager approval
        steps.append({
            "step": 4,
            "action": "Fleet Manager Notified",
            "description": "Single notification to fleet manager with bulk approval option",
            "data": {
                "notification_type": "bulk_scheduling_proposal",
                "approval_required": True,
                "approval_method": "one_click_approve",
                "alternative_times_available": True
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 5: Bulk confirmation
        steps.append({
            "step": 5,
            "action": "Bulk Appointments Confirmed",
            "description": "All 5 vehicles scheduled with single approval",
            "data": {
                "appointments_created": 5,
                "confirmation_sent_to": "fleet_manager + individual_drivers",
                "calendar_invites": True,
                "reminder_schedule": ["1_day_before", "2_hours_before"]
            },
            "timestamp": datetime.now().isoformat()
        })

        return {
            "scenario_name": "Multi-Vehicle Fleet Scheduling",
            "outcome": "Optimized scheduling minimizing business impact",
            "efficiency_gain": "40% faster than manual scheduling",
            "steps": steps,
            "key_benefits": [
                "Single interface for fleet management",
                "AI-optimized scheduling reduces downtime",
                "Bulk approval saves time",
                "Forecasting prevents overbooking",
                "Minimal business disruption"
            ]
        }

    async def _scenario_recurring_defect(self) -> Dict[str, Any]:
        """
        Scenario 4: Recurring Defect Pattern Detection
        Shows RCA/CAPA process in action
        """
        steps = []

        # Step 1: Pattern detection
        steps.append({
            "step": 1,
            "action": "Recurring Defect Detected",
            "description": "Same brake pad failure across 15 vehicles",
            "data": {
                "defect_pattern": "brake_pad_premature_wear",
                "affected_vehicles": 15,
                "total_fleet": 50,
                "occurrence_rate": 30.0,
                "avg_failure_mileage": 32000,
                "expected_lifespan": 50000,
                "severity": "high"
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 2: RCA triggered
        steps.append({
            "step": 2,
            "action": "Root Cause Analysis Initiated",
            "description": "RCA/CAPA Agent performs 5-Why analysis",
            "data": {
                "rca_method": "5-Why Analysis + Ishikawa Diagram",
                "five_why_completed": True,
                "root_cause_identified": "Missing QC process for supplier formula changes",
                "contributing_factors": [
                    "Cost reduction pressure on suppliers",
                    "Inadequate supplier monitoring",
                    "No incoming material testing"
                ]
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 3: CAPA generation
        steps.append({
            "step": 3,
            "action": "CAPA Actions Generated",
            "description": "Corrective and Preventive Actions recommended",
            "data": {
                "corrective_actions": 3,
                "preventive_actions": 4,
                "priority_actions": 2,
                "responsible_teams": ["Procurement", "Quality Assurance", "Engineering"],
                "target_completion": "2025-03-31",
                "estimated_cost": "$125,000",
                "expected_savings": "$300,000/year"
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 4: Manufacturing feedback
        steps.append({
            "step": 4,
            "action": "Manufacturing Team Notified",
            "description": "RCA/CAPA report sent to manufacturing for action",
            "data": {
                "report_sent_to": [
                    "Quality Engineering Manager",
                    "Procurement Director",
                    "Plant Manager - APAC"
                ],
                "dashboard_updated": True,
                "action_tracking_enabled": True,
                "review_meeting_scheduled": "2025-01-15"
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 5: Immediate corrective action
        steps.append({
            "step": 5,
            "action": "Immediate Actions Taken",
            "description": "Critical fixes implemented while preventive actions planned",
            "data": {
                "immediate_actions": [
                    {"action": "Switch to Supplier C", "status": "in_progress"},
                    {"action": "100% incoming inspection", "status": "implemented"},
                    {"action": "Recall affected vehicles", "status": "planned"}
                ],
                "affected_customers_notified": True,
                "service_priority": "high"
            },
            "timestamp": datetime.now().isoformat()
        })

        await asyncio.sleep(0.5)

        # Step 6: Effectiveness tracking
        steps.append({
            "step": 6,
            "action": "Effectiveness Tracking Enabled",
            "description": "Monitor defect rate reduction over next 6 months",
            "data": {
                "tracking_metrics": [
                    "defect_occurrence_rate",
                    "warranty_claim_rate",
                    "customer_satisfaction",
                    "supplier_quality_score"
                ],
                "target_defect_reduction": "60%",
                "review_frequency": "monthly",
                "effectiveness_check_date": "2025-06-01"
            },
            "timestamp": datetime.now().isoformat()
        })

        return {
            "scenario_name": "Recurring Defect Pattern + RCA/CAPA",
            "outcome": "Manufacturing quality improvement with measurable impact",
            "expected_roi": "2.4x within 12 months",
            "steps": steps,
            "manufacturing_impact": {
                "defect_rate_reduction_target": "60%",
                "annual_savings": "$300,000",
                "customer_satisfaction_improvement": "+15%",
                "warranty_cost_reduction": "$180,000/year"
            }
        }

    def get_all_scenarios(self) -> List[str]:
        """Get list of all available scenarios"""
        return list(self.scenarios.keys())

    def get_scenario_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all scenarios"""
        return {
            "declined_appointment": "Customer declines appointment - shows graceful handling and re-engagement",
            "urgent_failure": "Critical engine failure - shows rapid emergency response",
            "multi_vehicle_fleet": "Fleet of 5 vehicles - shows optimized bulk scheduling",
            "recurring_defect": "Recurring brake failure - shows RCA/CAPA process and manufacturing feedback"
        }
