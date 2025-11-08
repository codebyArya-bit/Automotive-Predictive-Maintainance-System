"""
RCA/CAPA (Root Cause Analysis / Corrective and Preventive Action) Agent
Analyzes recurring defects and generates manufacturing improvement recommendations
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
import random

from .base_agent import BaseAgent
from state import State


class RCACAPAAgent(BaseAgent):
    """
    Agent responsible for Root Cause Analysis and Corrective/Preventive Action generation
    Feeds insights back to manufacturing team for quality improvements
    """

    def __init__(self):
        super().__init__("rca_capa")

        # Common failure patterns for RCA
        self.known_failure_patterns = {
            "brake_pad_premature_wear": {
                "component": "brake_pads",
                "typical_lifespan": 50000,
                "suppliers": ["SupplierA", "SupplierB", "SupplierC"],
            },
            "battery_early_failure": {
                "component": "battery",
                "typical_lifespan": 60000,
                "suppliers": ["SupplierD", "SupplierE"],
            },
            "alternator_bearing_failure": {
                "component": "alternator",
                "typical_lifespan": 100000,
                "suppliers": ["SupplierA", "SupplierF"],
            },
            "transmission_solenoid_failure": {
                "component": "transmission",
                "typical_lifespan": 120000,
                "suppliers": ["SupplierG", "SupplierH"],
            },
        }

    async def _execute_internal(self, state: State) -> State:
        """Perform RCA/CAPA analysis"""
        self.logger.info("Starting RCA/CAPA analysis", vehicle_id=state.get("vehicle_id", "N/A"))

        # Analyze for recurring defects across fleet
        recurring_defects = await self._identify_recurring_defects(state)

        # Perform Root Cause Analysis for each recurring defect
        rca_reports = []
        for defect in recurring_defects:
            rca_report = await self._perform_root_cause_analysis(defect, state)
            rca_reports.append(rca_report)

        # Generate CAPA (Corrective and Preventive Actions)
        capa_actions = []
        for rca_report in rca_reports:
            capa = await self._generate_corrective_and_preventive_actions(rca_report)
            capa_actions.append(capa)

        # Calculate impact and ROI
        impact_analysis = self._calculate_impact_metrics(rca_reports, capa_actions)

        # Generate manufacturing feedback
        manufacturing_feedback = self._generate_manufacturing_feedback(
            rca_reports, capa_actions, impact_analysis
        )

        # Update state
        rca_capa_data = {
            "recurring_defects": recurring_defects,
            "rca_reports": rca_reports,
            "capa_actions": capa_actions,
            "impact_analysis": impact_analysis,
            "manufacturing_feedback": manufacturing_feedback,
            "analysis_timestamp": datetime.now().isoformat(),
        }

        state["rca_capa"] = rca_capa_data

        # Add log message
        state = self._add_log_message(
            state,
            f"RCA/CAPA analysis complete - {len(rca_reports)} issues identified",
            {
                "recurring_defects_found": len(recurring_defects),
                "rca_reports_generated": len(rca_reports),
                "capa_actions_recommended": sum(len(c["corrective_actions"]) + len(c["preventive_actions"]) for c in capa_actions),
                "estimated_annual_savings": impact_analysis.get("estimated_annual_savings", 0),
            },
        )

        return state

    async def _identify_recurring_defects(self, state: State) -> List[Dict[str, Any]]:
        """Identify recurring defects across the fleet"""
        await asyncio.sleep(0.2)

        # Simulate recurring defect detection
        recurring_defects = []

        # Example: Brake pad premature wear
        if random.random() > 0.3:  # 70% chance of detecting this pattern
            recurring_defects.append({
                "defect_id": "DEF-2025-001",
                "component": "brake_pads",
                "pattern_name": "brake_pad_premature_wear",
                "affected_vehicles": 15,
                "total_fleet": 50,
                "occurrence_rate_pct": 30.0,
                "avg_failure_mileage": 32000,
                "expected_lifespan": 50000,
                "severity": "high",
                "first_detected": "2024-11-01",
                "trend": "increasing",
            })

        # Example: Battery early failure
        if random.random() > 0.5:  # 50% chance
            recurring_defects.append({
                "defect_id": "DEF-2025-002",
                "component": "battery",
                "pattern_name": "battery_early_failure",
                "affected_vehicles": 8,
                "total_fleet": 50,
                "occurrence_rate_pct": 16.0,
                "avg_failure_mileage": 38000,
                "expected_lifespan": 60000,
                "severity": "medium",
                "first_detected": "2024-12-15",
                "trend": "stable",
            })

        return recurring_defects

    async def _perform_root_cause_analysis(
        self, defect: Dict[str, Any], state: State
    ) -> Dict[str, Any]:
        """Perform 5-Why Root Cause Analysis"""
        await asyncio.sleep(0.3)

        component = defect["component"]
        pattern = defect["pattern_name"]

        # Generate 5-Why analysis
        if pattern == "brake_pad_premature_wear":
            five_why = [
                "Why did brake pads wear prematurely?",
                "Because the friction material degraded faster than expected.",
                "Why did the material degrade faster?",
                "Because the material composition changed from specification.",
                "Why did the composition change?",
                "Because Supplier B modified the formula to reduce costs.",
                "Why was the modification not detected?",
                "Because quality verification testing was not performed after supplier changes.",
                "Why was quality testing not performed?",
                "Because there was no process requiring QC approval for supplier formula changes."
            ]
            root_cause = "Missing quality control process for supplier formula modifications"
            contributing_factors = [
                "Cost reduction pressure on suppliers",
                "Inadequate supplier quality monitoring",
                "No incoming material testing",
                "Lack of supplier change notification process"
            ]

        elif pattern == "battery_early_failure":
            five_why = [
                "Why did batteries fail early?",
                "Because the internal resistance increased prematurely.",
                "Why did resistance increase?",
                "Because the electrolyte level dropped below minimum.",
                "Why did electrolyte level drop?",
                "Because the battery casing had microcracks allowing evaporation.",
                "Why were there microcracks?",
                "Because the plastic material became brittle due to heat exposure.",
                "Why was heat exposure excessive?",
                "Because battery placement near engine bay increased ambient temperature."
            ]
            root_cause = "Suboptimal battery placement causing excessive heat exposure"
            contributing_factors = [
                "Poor ventilation in battery compartment",
                "Inadequate heat shielding",
                "Design trade-off for space optimization",
                "No thermal testing during development"
            ]

        else:
            # Generic RCA
            five_why = [
                f"Why did {component} fail prematurely?",
                "Because the component quality was below specification.",
                "Why was quality below specification?",
                "Because manufacturing process had inadequate controls.",
                "Why were controls inadequate?",
                "Because process validation was not thorough.",
                "Why was validation not thorough?",
                "Because time-to-market pressures led to shortcuts."
            ]
            root_cause = "Inadequate process controls and validation"
            contributing_factors = [
                "Time-to-market pressure",
                "Insufficient process validation",
                "Lack of quality checkpoints"
            ]

        # Ishikawa (Fishbone) analysis categories
        ishikawa_analysis = {
            "Man": ["Inadequate training on quality standards", "High operator turnover"],
            "Method": ["Outdated quality control procedures", "Missing verification steps"],
            "Machine": ["Aging testing equipment", "Inadequate calibration frequency"],
            "Material": ["Supplier quality variation", "Inadequate incoming inspection"],
            "Measurement": ["Inconsistent testing protocols", "Lack of real-time monitoring"],
            "Environment": ["Temperature/humidity variations", "Inadequate facility controls"]
        }

        return {
            "defect_id": defect["defect_id"],
            "problem_statement": f"Premature {component} failure affecting {defect['affected_vehicles']} vehicles ({defect['occurrence_rate_pct']}% of fleet)",
            "rca_method": "5-Why Analysis + Ishikawa Diagram",
            "five_why_analysis": five_why,
            "root_cause": root_cause,
            "contributing_factors": contributing_factors,
            "ishikawa_analysis": ishikawa_analysis,
            "data_analyzed": {
                "affected_vehicles": defect["affected_vehicles"],
                "failure_mileage_avg": defect["avg_failure_mileage"],
                "expected_lifespan": defect["expected_lifespan"],
                "deviation_pct": round(((defect["expected_lifespan"] - defect["avg_failure_mileage"]) / defect["expected_lifespan"]) * 100, 1)
            },
            "analysis_date": datetime.now().isoformat(),
        }

    async def _generate_corrective_and_preventive_actions(
        self, rca_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate CAPA (Corrective and Preventive Actions)"""
        await asyncio.sleep(0.2)

        root_cause = rca_report["root_cause"]

        # Corrective Actions (fix current problem)
        corrective_actions = []
        if "supplier" in root_cause.lower() or "quality control" in root_cause.lower():
            corrective_actions = [
                {
                    "action_id": "CA-001",
                    "description": "Switch to alternate supplier with proven quality track record",
                    "responsible_party": "Procurement Team",
                    "target_completion": "2025-02-01",
                    "status": "pending",
                    "priority": "high"
                },
                {
                    "action_id": "CA-002",
                    "description": "Recall affected vehicles for component replacement",
                    "responsible_party": "Service Operations",
                    "target_completion": "2025-03-15",
                    "status": "pending",
                    "priority": "high"
                },
                {
                    "action_id": "CA-003",
                    "description": "Implement 100% incoming inspection for suspect component batches",
                    "responsible_party": "Quality Assurance",
                    "target_completion": "2025-01-15",
                    "status": "pending",
                    "priority": "critical"
                }
            ]

        elif "design" in root_cause.lower() or "placement" in root_cause.lower():
            corrective_actions = [
                {
                    "action_id": "CA-004",
                    "description": "Install heat shields on existing vehicles during service",
                    "responsible_party": "Engineering + Service",
                    "target_completion": "2025-02-28",
                    "status": "pending",
                    "priority": "high"
                },
                {
                    "action_id": "CA-005",
                    "description": "Modify ventilation system in affected models",
                    "responsible_party": "R&D Engineering",
                    "target_completion": "2025-04-01",
                    "status": "pending",
                    "priority": "medium"
                }
            ]

        else:
            corrective_actions = [
                {
                    "action_id": "CA-999",
                    "description": "Investigate and address root cause",
                    "responsible_party": "Quality Engineering",
                    "target_completion": "2025-02-01",
                    "status": "pending",
                    "priority": "high"
                }
            ]

        # Preventive Actions (prevent future occurrence)
        preventive_actions = [
            {
                "action_id": "PA-001",
                "description": "Establish supplier change notification and approval process",
                "responsible_party": "Supply Chain + Quality",
                "target_completion": "2025-01-31",
                "status": "pending",
                "priority": "high",
                "verification_method": "Process audit"
            },
            {
                "action_id": "PA-002",
                "description": "Implement monthly supplier quality audits",
                "responsible_party": "Quality Assurance",
                "target_completion": "2025-02-15",
                "status": "pending",
                "priority": "high",
                "verification_method": "Audit schedule and reports"
            },
            {
                "action_id": "PA-003",
                "description": "Add thermal testing to new product development validation",
                "responsible_party": "R&D Engineering",
                "target_completion": "2025-03-01",
                "status": "pending",
                "priority": "medium",
                "verification_method": "Updated validation plan"
            },
            {
                "action_id": "PA-004",
                "description": "Train all procurement staff on quality verification requirements",
                "responsible_party": "HR + Quality",
                "target_completion": "2025-02-10",
                "status": "pending",
                "priority": "medium",
                "verification_method": "Training completion records"
            }
        ]

        return {
            "defect_id": rca_report["defect_id"],
            "root_cause": root_cause,
            "corrective_actions": corrective_actions,
            "preventive_actions": preventive_actions,
            "total_actions": len(corrective_actions) + len(preventive_actions),
            "capa_owner": "Quality Engineering Manager",
            "review_date": "2025-06-01",
            "effectiveness_check_date": "2025-12-01",
        }

    def _calculate_impact_metrics(
        self, rca_reports: List[Dict], capa_actions: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate business impact of RCA/CAPA"""

        if not rca_reports:
            return {
                "estimated_annual_savings": 0,
                "defect_rate_reduction_target_pct": 0,
                "customer_satisfaction_improvement_target": 0,
            }

        # Estimate financial impact
        avg_warranty_claim_cost = 500  # USD per claim
        total_affected = sum(r["data_analyzed"]["affected_vehicles"] for r in rca_reports)
        current_annual_cost = total_affected * avg_warranty_claim_cost * 2  # Assume 2x per year

        # Expected reduction after CAPA implementation
        expected_reduction_pct = 60  # 60% reduction expected
        estimated_annual_savings = current_annual_cost * (expected_reduction_pct / 100)

        # Defect rate reduction
        total_fleet = 50  # From defect data
        current_defect_rate_pct = (total_affected / total_fleet) * 100
        target_defect_rate_pct = current_defect_rate_pct * (1 - expected_reduction_pct / 100)

        return {
            "estimated_annual_savings": round(estimated_annual_savings, 2),
            "current_defect_rate_pct": round(current_defect_rate_pct, 2),
            "target_defect_rate_pct": round(target_defect_rate_pct, 2),
            "defect_rate_reduction_target_pct": expected_reduction_pct,
            "customer_satisfaction_improvement_target": 15,  # 15% improvement
            "warranty_cost_reduction_target": estimated_annual_savings,
            "affected_vehicles_total": total_affected,
            "roi_months": 6,  # Payback period
        }

    def _generate_manufacturing_feedback(
        self, rca_reports: List[Dict], capa_actions: List[Dict], impact_analysis: Dict
    ) -> Dict[str, Any]:
        """Generate structured feedback for manufacturing team"""

        # Collect all recommended actions
        all_actions = []
        for capa in capa_actions:
            all_actions.extend(capa["corrective_actions"])
            all_actions.extend(capa["preventive_actions"])

        # Group by responsible party
        actions_by_team = {}
        for action in all_actions:
            team = action["responsible_party"]
            if team not in actions_by_team:
                actions_by_team[team] = []
            actions_by_team[team].append(action)

        # Priority actions (critical and high)
        priority_actions = [
            a for a in all_actions
            if a.get("priority") in ["critical", "high"]
        ]

        return {
            "summary": f"{len(rca_reports)} recurring defects identified requiring immediate attention",
            "total_actions_recommended": len(all_actions),
            "priority_actions_count": len(priority_actions),
            "actions_by_team": actions_by_team,
            "expected_impact": {
                "defect_rate_reduction": f"{impact_analysis['defect_rate_reduction_target_pct']}%",
                "annual_savings": f"${impact_analysis['estimated_annual_savings']:,.2f}",
                "customer_satisfaction_improvement": f"+{impact_analysis['customer_satisfaction_improvement_target']}%",
            },
            "key_recommendations": [
                "Strengthen supplier quality management process",
                "Implement comprehensive incoming inspection",
                "Enhance design validation procedures",
                "Establish continuous monitoring system"
            ],
            "next_review_date": "2025-06-01",
            "report_generated": datetime.now().isoformat(),
        }
