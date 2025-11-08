"""
Manufacturing Insights Agent - Analyzes patterns across vehicle fleet for manufacturing improvements
"""

import asyncio
import random
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent
from state import State, Priority


class ManufacturingInsightsAgent(BaseAgent):
    """Agent responsible for analyzing fleet-wide patterns and generating manufacturing insights"""

    def __init__(self):
        super().__init__("manufacturing_insights")

        # Component failure patterns by vehicle model/year
        self.component_patterns = {
            "engine": {
                "common_failures": ["oil_pump", "timing_chain", "head_gasket", "fuel_injector"],
                "typical_mileage": {"oil_pump": 80000, "timing_chain": 120000, "head_gasket": 150000},
                "seasonal_factors": {"summer": 1.3, "winter": 0.8},
            },
            "transmission": {
                "common_failures": ["clutch", "torque_converter", "valve_body", "solenoid"],
                "typical_mileage": {"clutch": 100000, "torque_converter": 150000, "valve_body": 120000},
                "seasonal_factors": {"summer": 1.1, "winter": 0.9},
            },
            "brakes": {
                "common_failures": ["brake_pads", "rotors", "calipers", "brake_fluid"],
                "typical_mileage": {"brake_pads": 30000, "rotors": 60000, "calipers": 100000},
                "seasonal_factors": {"summer": 1.0, "winter": 1.4},
            },
            "electrical": {
                "common_failures": ["battery", "alternator", "starter", "wiring_harness"],
                "typical_mileage": {"battery": 50000, "alternator": 100000, "starter": 120000},
                "seasonal_factors": {"summer": 1.2, "winter": 1.5},
            },
        }

        # Manufacturing quality metrics
        self.quality_thresholds = {
            "defect_rate": 0.02,  # 2% acceptable defect rate
            "early_failure_rate": 0.01,  # 1% early failure rate
            "warranty_claim_rate": 0.05,  # 5% warranty claim rate
            "customer_satisfaction": 8.0,  # Minimum 8.0 / 10 satisfaction
        }

        # Simulated fleet data for analysis
        self.fleet_data = self._initialize_fleet_data()

    def _initialize_fleet_data(self) -> Dict[str, Any]:
        """Initialize simulated fleet data for analysis"""
        return {
            "total_vehicles": 50000,
            "models": ["ModelA", "ModelB", "ModelC", "ModelD"],
            "production_years": [2020, 2021, 2022, 2023, 2024],
            "manufacturing_plants": ["Plant_NA", "Plant_EU", "Plant_APAC"],
            "supplier_data": {
                "SupplierA": {"components": ["engine", "transmission"], "quality_score": 8.5},
                "SupplierB": {"components": ["brakes", "electrical"], "quality_score": 7.8},
                "SupplierC": {"components": ["engine", "electrical"], "quality_score": 9.1},
                "SupplierD": {"components": ["transmission", "brakes"], "quality_score": 8.2},
            },
        }

    async def _execute_internal(self, state: State) -> State:
        """Analyze manufacturing patterns and generate insights"""
        self.logger.info("Starting manufacturing insights analysis", vehicle_id=state["vehicle_id"])

        # Analyze current vehicle's data in context of fleet
        vehicle_analysis = await self._analyze_vehicle_context(state)

        # Generate fleet-wide pattern analysis
        pattern_analysis = await self._analyze_fleet_patterns(state)

        # Identify manufacturing quality issues
        quality_issues = await self._identify_quality_issues(state, vehicle_analysis)

        # Generate improvement recommendations
        recommendations = await self._generate_manufacturing_recommendations(
            vehicle_analysis, pattern_analysis, quality_issues
        )

        # Calculate impact metrics
        impact_metrics = self._calculate_impact_metrics(recommendations, state)

        # Update state with insights
        manufacturing_insights = {
            "vehicle_context": vehicle_analysis,
            "fleet_patterns": pattern_analysis,
            "quality_issues": quality_issues,
            "recommendations": recommendations,
            "impact_metrics": impact_metrics,
            "analysis_timestamp": datetime.now().isoformat(),
        }

        state["manufacturing_insights"] = manufacturing_insights

        # Add log message
        state = self._add_log_message(
            state,
            f"Manufacturing insights generated - {len(recommendations)} recommendations",
            {
                "quality_issues_found": len(quality_issues),
                "recommendations_count": len(recommendations),
                "potential_cost_savings": impact_metrics.get("potential_savings", 0),
            },
        )

        return state

    async def _analyze_vehicle_context(self, state: State) -> Dict[str, Any]:
        """Analyze current vehicle in context of fleet data"""
        await asyncio.sleep(0.3)

        vehicle_id = state["vehicle_id"]

        # Extract vehicle information (simulated)
        vehicle_info = self._extract_vehicle_info(vehicle_id)

        # Analyze component health relative to fleet average
        component_comparison = {}
        if state.get("telemetry_data"):
            for component, data in state["telemetry_data"]["components"].items():
                fleet_avg = self._get_fleet_average_health(component, vehicle_info)
                component_comparison[component] = {
                    "current_health": data.get("health_score", 0),
                    "fleet_average": fleet_avg,
                    "relative_performance": data.get("health_score", 0) - fleet_avg,
                    "percentile": self._calculate_percentile(data.get("health_score", 0), component),
                }

        return {
            "vehicle_info": vehicle_info,
            "component_comparison": component_comparison,
            "fleet_position": self._determine_fleet_position(component_comparison),
        }

    def _extract_vehicle_info(self, vehicle_id: str) -> Dict[str, Any]:
        """Extract vehicle manufacturing information from ID"""
        # Simulate vehicle info extraction
        model_idx = hash(vehicle_id) % len(self.fleet_data["models"])
        year_idx = hash(vehicle_id + "year") % len(self.fleet_data["production_years"])
        plant_idx = hash(vehicle_id + "plant") % len(self.fleet_data["manufacturing_plants"])

        return {
            "model": self.fleet_data["models"][model_idx],
            "production_year": self.fleet_data["production_years"][year_idx],
            "manufacturing_plant": self.fleet_data["manufacturing_plants"][plant_idx],
            "estimated_mileage": random.randint(10000, 150000),
            "vin_prefix": vehicle_id[:3],
        }

    def _get_fleet_average_health(self, component: str, vehicle_info: Dict[str, Any]) -> float:
        """Get fleet average health score for component"""
        # Simulate fleet average calculation
        base_health = 75.0

        # Adjust based on vehicle age
        age = 2024 - vehicle_info["production_year"]
        age_factor = max(0.5, 1.0 - (age * 0.05))

        # Adjust based on manufacturing plant quality
        plant_factors = {"Plant_NA": 1.0, "Plant_EU": 1.05, "Plant_APAC": 0.95}
        plant_factor = plant_factors.get(vehicle_info["manufacturing_plant"], 1.0)

        return base_health * age_factor * plant_factor + random.uniform(-5, 5)

    def _calculate_percentile(self, health_score: float, component: str) -> int:
        """Calculate percentile ranking for component health"""
        # Simulate percentile calculation
        if health_score >= 90:
            return random.randint(90, 99)
        elif health_score >= 80:
            return random.randint(75, 89)
        elif health_score >= 70:
            return random.randint(50, 74)
        elif health_score >= 60:
            return random.randint(25, 49)
        else:
            return random.randint(1, 24)

    def _determine_fleet_position(self, component_comparison: Dict[str, Any]) -> str:
        """Determine vehicle's overall position in fleet"""
        if not component_comparison:
            return "average"

        avg_percentile = sum(comp["percentile"] for comp in component_comparison.values()) / len(component_comparison)

        if avg_percentile >= 80:
            return "top_performer"
        elif avg_percentile >= 60:
            return "above_average"
        elif avg_percentile >= 40:
            return "average"
        elif avg_percentile >= 20:
            return "below_average"
        else:
            return "poor_performer"

    async def _analyze_fleet_patterns(self, state: State) -> Dict[str, Any]:
        """Analyze patterns across the entire fleet"""
        await asyncio.sleep(0.4)

        # Simulate fleet pattern analysis
        patterns = {
            "failure_trends": self._analyze_failure_trends(),
            "seasonal_patterns": self._analyze_seasonal_patterns(),
            "supplier_performance": self._analyze_supplier_performance(),
            "plant_quality_comparison": self._analyze_plant_quality(),
            "model_reliability": self._analyze_model_reliability(),
        }

        return patterns

    def _analyze_failure_trends(self) -> Dict[str, Any]:
        """Analyze component failure trends across fleet"""
        trends = {}

        for component, data in self.component_patterns.items():
            failure_rate = random.uniform(0.01, 0.05)  # 1 - 5% failure rate
            trend_direction = random.choice(["increasing", "decreasing", "stable"])

            trends[component] = {
                "current_failure_rate": failure_rate,
                "trend_direction": trend_direction,
                "trend_magnitude": random.uniform(0.001, 0.01),
                "most_common_failure": random.choice(data["common_failures"]),
                "average_failure_mileage": random.randint(50000, 120000),
            }

        return trends

    def _analyze_seasonal_patterns(self) -> Dict[str, Any]:
        """Analyze seasonal failure patterns"""
        current_season = self._get_current_season()

        seasonal_analysis = {}
        for component, data in self.component_patterns.items():
            seasonal_factor = data["seasonal_factors"].get(current_season, 1.0)

            seasonal_analysis[component] = {
                "current_season_factor": seasonal_factor,
                "peak_failure_season": max(data["seasonal_factors"], key=data["seasonal_factors"].get),
                "seasonal_variance": max(data["seasonal_factors"].values()) - min(data["seasonal_factors"].values()),
            }

        return seasonal_analysis

    def _get_current_season(self) -> str:
        """Determine current season"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"

    def _analyze_supplier_performance(self) -> Dict[str, Any]:
        """Analyze supplier quality performance"""
        supplier_analysis = {}

        for supplier, data in self.fleet_data["supplier_data"].items():
            # Simulate performance metrics
            defect_rate = random.uniform(0.005, 0.03)
            delivery_performance = random.uniform(0.85, 0.98)
            cost_efficiency = random.uniform(0.7, 1.2)

            supplier_analysis[supplier] = {
                "quality_score": data["quality_score"],
                "defect_rate": defect_rate,
                "delivery_performance": delivery_performance,
                "cost_efficiency": cost_efficiency,
                "components_supplied": data["components"],
                "overall_rating": self._calculate_supplier_rating(
                    data["quality_score"], defect_rate, delivery_performance, cost_efficiency
                ),
            }

        return supplier_analysis

    def _calculate_supplier_rating(self, quality: float, defect_rate: float, delivery: float, cost: float) -> str:
        """Calculate overall supplier rating"""
        # Normalize metrics and calculate weighted score
        quality_norm = quality / 10.0
        defect_norm = 1.0 - (defect_rate / 0.05)  # Lower defect rate is better
        delivery_norm = delivery
        cost_norm = min(1.0, 1.0 / cost)  # Lower cost is better

        overall_score = quality_norm * 0.4 + defect_norm * 0.3 + delivery_norm * 0.2 + cost_norm * 0.1

        if overall_score >= 0.85:
            return "excellent"
        elif overall_score >= 0.75:
            return "good"
        elif overall_score >= 0.65:
            return "acceptable"
        else:
            return "needs_improvement"

    def _analyze_plant_quality(self) -> Dict[str, Any]:
        """Analyze manufacturing plant quality comparison"""
        plant_analysis = {}

        for plant in self.fleet_data["manufacturing_plants"]:
            # Simulate plant performance metrics
            quality_score = random.uniform(7.5, 9.5)
            defect_rate = random.uniform(0.01, 0.04)
            efficiency = random.uniform(0.8, 0.95)

            plant_analysis[plant] = {
                "quality_score": quality_score,
                "defect_rate": defect_rate,
                "production_efficiency": efficiency,
                "vehicles_produced": random.randint(8000, 15000),
                "certification_level": random.choice(["ISO9001", "TS16949", "ISO14001"]),
            }

        return plant_analysis

    def _analyze_model_reliability(self) -> Dict[str, Any]:
        """Analyze reliability by vehicle model"""
        model_analysis = {}

        for model in self.fleet_data["models"]:
            # Simulate model reliability metrics
            reliability_score = random.uniform(7.0, 9.5)
            warranty_claims = random.uniform(0.02, 0.08)
            customer_satisfaction = random.uniform(7.5, 9.2)

            model_analysis[model] = {
                "reliability_score": reliability_score,
                "warranty_claim_rate": warranty_claims,
                "customer_satisfaction": customer_satisfaction,
                "units_in_fleet": random.randint(10000, 15000),
                "average_age": random.uniform(1.5, 4.0),
            }

        return model_analysis

    async def _identify_quality_issues(self, state: State, vehicle_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential manufacturing quality issues"""
        await asyncio.sleep(0.2)

        quality_issues = []

        # Check for component performance issues
        if vehicle_analysis.get("component_comparison"):
            for component, data in vehicle_analysis["component_comparison"].items():
                if data["percentile"] < 25:  # Bottom 25% performance
                    quality_issues.append(
                        {
                            "type": "component_underperformance",
                            "component": component,
                            "severity": "medium" if data["percentile"] < 10 else "low",
                            "description": f"{component} performing in bottom {data['percentile']}% of fleet",
                            "potential_causes": self._identify_potential_causes(component, data),
                        }
                    )

        # Check for systematic issues based on prediction
        if state.get("prediction"):
            prediction = state["prediction"]
            if prediction["priority"] in [Priority.P0, Priority.P1]:
                quality_issues.append(
                    {
                        "type": "critical_failure_risk",
                        "component": prediction["component"] if "component" in prediction else "unknown",
                        "severity": "high",
                        "description": f"Critical failure predicted: {prediction.get('recommended_action', 'unknown')}",
                        "potential_causes": ["manufacturing defect", "design flaw", "supplier quality issue"],
                    }
                )

        return quality_issues

    def _identify_potential_causes(self, component: str, performance_data: Dict[str, Any]) -> List[str]:
        """Identify potential causes for component underperformance"""
        causes = []

        if performance_data["relative_performance"] < -20:
            causes.extend(["manufacturing defect", "supplier quality issue"])

        if performance_data["percentile"] < 10:
            causes.extend(["design flaw", "material quality issue"])

        # Component-specific causes
        component_causes = {
            "engine": ["oil quality", "assembly tolerance", "fuel system"],
            "transmission": ["fluid quality", "gear tolerance", "electronic control"],
            "brakes": ["pad material", "rotor quality", "hydraulic system"],
            "electrical": ["wiring quality", "connector reliability", "battery chemistry"],
        }

        if component in component_causes:
            causes.extend(component_causes[component])

        return causes[:3]  # Limit to top 3 causes

    async def _generate_manufacturing_recommendations(
        self, vehicle_analysis: Dict[str, Any], pattern_analysis: Dict[str, Any], quality_issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate manufacturing improvement recommendations"""
        await asyncio.sleep(0.3)

        recommendations = []

        # Recommendations based on quality issues
        for issue in quality_issues:
            if issue["severity"] == "high":
                recommendations.append(
                    {
                        "category": "quality_improvement",
                        "priority": "high",
                        "title": f"Address {issue['component']} quality issues",
                        "description": f"Investigate and resolve {issue['description']}",
                        "actions": [
                            f"Audit {issue['component']} manufacturing process",
                            "Review supplier quality controls",
                            "Implement additional testing protocols",
                        ],
                        "estimated_impact": "high",
                        "implementation_timeline": "3 - 6 months",
                    }
                )

        # Recommendations based on supplier performance
        supplier_perf = pattern_analysis.get("supplier_performance", {})
        for supplier, data in supplier_perf.items():
            if data["overall_rating"] == "needs_improvement":
                recommendations.append(
                    {
                        "category": "supplier_improvement",
                        "priority": "medium",
                        "title": f"Improve {supplier} performance",
                        "description": f"Address quality and delivery issues with {supplier}",
                        "actions": [
                            "Conduct supplier audit",
                            "Implement quality improvement plan",
                            "Consider alternative suppliers",
                        ],
                        "estimated_impact": "medium",
                        "implementation_timeline": "6 - 12 months",
                    }
                )

        # Recommendations based on plant performance
        plant_quality = pattern_analysis.get("plant_quality_comparison", {})
        best_plant = max(plant_quality.keys(), key=lambda x: plant_quality[x]["quality_score"])
        worst_plant = min(plant_quality.keys(), key=lambda x: plant_quality[x]["quality_score"])

        if plant_quality[best_plant]["quality_score"] - plant_quality[worst_plant]["quality_score"] > 1.0:
            recommendations.append(
                {
                    "category": "process_standardization",
                    "priority": "medium",
                    "title": "Standardize manufacturing processes across plants",
                    "description": f"Share best practices from {best_plant} with {worst_plant}",
                    "actions": [
                        "Conduct cross-plant knowledge transfer",
                        "Standardize quality control procedures",
                        "Implement unified training programs",
                    ],
                    "estimated_impact": "high",
                    "implementation_timeline": "6 - 18 months",
                }
            )

        return recommendations

    def _calculate_impact_metrics(self, recommendations: List[Dict[str, Any]], state: State) -> Dict[str, Any]:
        """Calculate potential impact metrics for recommendations"""
        total_recommendations = len(recommendations)
        high_priority_count = sum(1 for r in recommendations if r["priority"] == "high")

        # Estimate potential cost savings
        potential_savings = 0
        for rec in recommendations:
            if rec["estimated_impact"] == "high":
                potential_savings += random.randint(500000, 2000000)
            elif rec["estimated_impact"] == "medium":
                potential_savings += random.randint(100000, 500000)
            else:
                potential_savings += random.randint(50000, 100000)

        return {
            "total_recommendations": total_recommendations,
            "high_priority_recommendations": high_priority_count,
            "potential_savings": potential_savings,
            "estimated_roi": random.uniform(2.5, 8.0),
            "quality_improvement_potential": random.uniform(0.1, 0.5),
            "customer_satisfaction_impact": random.uniform(0.2, 0.8),
        }
