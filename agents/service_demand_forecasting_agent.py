"""
Service Demand Forecasting Agent
Forecasts service demand for optimal scheduling and resource allocation
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random
from .base_agent import BaseAgent
from state import State


class ServiceDemandForecastingAgent(BaseAgent):
    """Agent responsible for forecasting service demand and optimizing schedules"""

    def __init__(self):
        super().__init__("service_demand_forecasting")

        # Seasonal factors by month (1.0 = average)
        self.seasonal_factors = {
            1: 1.2,   # January - Winter maintenance
            2: 1.1,   # February
            3: 1.3,   # March - Pre-summer checks
            4: 1.2,   # April
            5: 1.4,   # May - Peak service season
            6: 1.3,   # June
            7: 1.1,   # July - Lower demand
            8: 1.0,   # August
            9: 1.2,   # September - Back to school
            10: 1.3,  # October - Pre-winter prep
            11: 1.4,  # November - Winter prep peak
            12: 1.2,  # December
        }

        # Day of week patterns (Monday=0, Sunday=6)
        self.day_patterns = {
            0: 1.3,  # Monday - High
            1: 1.2,  # Tuesday
            2: 1.1,  # Wednesday
            3: 1.0,  # Thursday
            4: 1.2,  # Friday - High
            5: 1.4,  # Saturday - Peak
            6: 0.6,  # Sunday - Low
        }

        # Peak hours (hour of day -> multiplier)
        self.hour_patterns = {
            8: 0.8, 9: 1.2, 10: 1.4, 11: 1.3,
            12: 1.0, 13: 0.9, 14: 1.1, 15: 1.3,
            16: 1.4, 17: 1.2, 18: 0.8
        }

        # Service center data
        self.service_centers = {
            "Metro_Delhi": {"capacity": 20, "current_load": 0.75},
            "Metro_Mumbai": {"capacity": 18, "current_load": 0.80},
            "Metro_Bangalore": {"capacity": 22, "current_load": 0.70},
            "Tier2_Pune": {"capacity": 15, "current_load": 0.65},
            "Tier2_Hyderabad": {"capacity": 16, "current_load": 0.72},
        }

    async def _execute_internal(self, state: State) -> State:
        """Generate service demand forecast"""
        self.logger.info("Starting service demand forecasting", vehicle_id=state.get("vehicle_id", "N/A"))

        # Generate 30-day forecast
        daily_forecast = await self._generate_daily_forecast(30)

        # Generate hourly patterns for next 7 days
        hourly_forecast = await self._generate_hourly_forecast(7)

        # Analyze service center capacity
        capacity_analysis = await self._analyze_service_center_capacity(daily_forecast)

        # Generate staffing recommendations
        staffing_recommendations = self._generate_staffing_recommendations(daily_forecast, capacity_analysis)

        # Calculate optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities(
            daily_forecast, capacity_analysis
        )

        # Update state with forecast
        forecast_data = {
            "daily_forecast": daily_forecast,
            "hourly_forecast": hourly_forecast,
            "capacity_analysis": capacity_analysis,
            "staffing_recommendations": staffing_recommendations,
            "optimization_opportunities": optimization_opportunities,
            "forecast_generated_at": datetime.now().isoformat(),
            "forecast_period_days": 30,
        }

        state["demand_forecast"] = forecast_data

        # Add log message
        state = self._add_log_message(
            state,
            f"Service demand forecast generated for 30 days",
            {
                "avg_daily_demand": sum(daily_forecast) / len(daily_forecast),
                "peak_demand_day": max(daily_forecast),
                "optimization_opportunities": len(optimization_opportunities),
            },
        )

        return state

    async def _generate_daily_forecast(self, days: int) -> List[float]:
        """Generate daily demand forecast"""
        await asyncio.sleep(0.2)

        forecast = []
        base_demand = 50  # Base vehicles per day across all centers

        current_date = datetime.now()

        for day in range(days):
            future_date = current_date + timedelta(days=day)

            # Apply seasonal factor
            month = future_date.month
            seasonal = self.seasonal_factors.get(month, 1.0)

            # Apply day of week pattern
            day_of_week = future_date.weekday()
            day_pattern = self.day_patterns.get(day_of_week, 1.0)

            # Add some randomness for realism
            random_factor = random.uniform(0.9, 1.1)

            # Calculate demand
            demand = base_demand * seasonal * day_pattern * random_factor

            forecast.append(round(demand, 1))

        return forecast

    async def _generate_hourly_forecast(self, days: int) -> Dict[str, List[float]]:
        """Generate hourly demand patterns"""
        await asyncio.sleep(0.1)

        hourly_data = {}
        current_date = datetime.now()

        for day in range(days):
            future_date = current_date + timedelta(days=day)
            date_key = future_date.strftime("%Y-%m-%d")

            # Generate hourly demand for business hours (8 AM - 6 PM)
            hourly_demand = []
            for hour in range(8, 19):
                hour_multiplier = self.hour_patterns.get(hour, 1.0)
                base_hourly = 4.5  # Base vehicles per hour
                demand = base_hourly * hour_multiplier * random.uniform(0.9, 1.1)
                hourly_demand.append(round(demand, 1))

            hourly_data[date_key] = hourly_demand

        return hourly_data

    async def _analyze_service_center_capacity(self, daily_forecast: List[float]) -> Dict[str, Any]:
        """Analyze service center capacity vs. forecasted demand"""
        await asyncio.sleep(0.1)

        total_capacity = sum(center["capacity"] for center in self.service_centers.values())
        avg_forecast = sum(daily_forecast) / len(daily_forecast)
        peak_forecast = max(daily_forecast)

        # Calculate utilization
        avg_utilization = (avg_forecast / total_capacity) * 100
        peak_utilization = (peak_forecast / total_capacity) * 100

        # Identify capacity issues
        capacity_warnings = []
        if peak_utilization > 90:
            capacity_warnings.append({
                "severity": "high",
                "message": f"Peak demand ({peak_forecast:.1f}) exceeds 90% capacity",
                "recommendation": "Add temporary staff or extend hours during peak days"
            })
        elif peak_utilization > 80:
            capacity_warnings.append({
                "severity": "medium",
                "message": f"Peak demand approaches 80% capacity",
                "recommendation": "Monitor closely and prepare backup resources"
            })

        # Per-center analysis
        center_analysis = {}
        for center_name, center_data in self.service_centers.items():
            estimated_demand = (avg_forecast / len(self.service_centers)) * random.uniform(0.9, 1.1)
            utilization = (estimated_demand / center_data["capacity"]) * 100

            center_analysis[center_name] = {
                "capacity": center_data["capacity"],
                "current_load": center_data["current_load"],
                "forecasted_demand": round(estimated_demand, 1),
                "forecasted_utilization": round(utilization, 1),
                "has_capacity": utilization < 90,
            }

        return {
            "total_capacity": total_capacity,
            "avg_daily_demand": round(avg_forecast, 1),
            "peak_daily_demand": round(peak_forecast, 1),
            "avg_utilization_pct": round(avg_utilization, 1),
            "peak_utilization_pct": round(peak_utilization, 1),
            "capacity_warnings": capacity_warnings,
            "center_analysis": center_analysis,
        }

    def _generate_staffing_recommendations(
        self, daily_forecast: List[float], capacity_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate staffing recommendations based on forecast"""

        avg_demand = capacity_analysis["avg_daily_demand"]
        peak_demand = capacity_analysis["peak_daily_demand"]

        # Calculate recommended staff levels
        # Assume 1 technician can handle 5 vehicles per day
        vehicles_per_tech = 5

        regular_staff_needed = int(avg_demand / vehicles_per_tech) + 1
        peak_staff_needed = int(peak_demand / vehicles_per_tech) + 1
        additional_staff_for_peak = peak_staff_needed - regular_staff_needed

        # Identify high-demand days
        high_demand_days = []
        for i, demand in enumerate(daily_forecast):
            if demand > avg_demand * 1.2:
                date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                high_demand_days.append({
                    "date": date,
                    "demand": round(demand, 1),
                    "additional_staff": max(1, int((demand - avg_demand) / vehicles_per_tech))
                })

        return {
            "regular_staff_count": regular_staff_needed,
            "peak_staff_count": peak_staff_needed,
            "additional_staff_for_peaks": additional_staff_for_peak,
            "high_demand_days": high_demand_days[:10],  # Next 10 high-demand days
            "recommendations": [
                f"Maintain {regular_staff_needed} technicians for normal operations",
                f"Prepare {additional_staff_for_peak} additional staff for peak days",
                "Consider offering incentives for off-peak appointments",
                "Implement online booking to distribute demand evenly",
            ]
        }

    def _identify_optimization_opportunities(
        self, daily_forecast: List[float], capacity_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify opportunities to optimize scheduling and capacity"""

        opportunities = []

        # Opportunity 1: Load balancing between centers
        center_analysis = capacity_analysis["center_analysis"]
        overloaded_centers = [
            name for name, data in center_analysis.items()
            if data["forecasted_utilization"] > 85
        ]
        underutilized_centers = [
            name for name, data in center_analysis.items()
            if data["forecasted_utilization"] < 60
        ]

        if overloaded_centers and underutilized_centers:
            opportunities.append({
                "type": "load_balancing",
                "priority": "high",
                "title": "Balance Load Between Service Centers",
                "description": f"Redirect customers from {', '.join(overloaded_centers)} to {', '.join(underutilized_centers)}",
                "potential_impact": "Reduce wait times by 30%",
                "estimated_savings": "$15,000/month"
            })

        # Opportunity 2: Off-peak incentives
        avg_demand = sum(daily_forecast) / len(daily_forecast)
        low_demand_days = sum(1 for d in daily_forecast if d < avg_demand * 0.8)

        if low_demand_days > 5:
            opportunities.append({
                "type": "demand_shifting",
                "priority": "medium",
                "title": "Offer Off-Peak Discounts",
                "description": f"Incentivize {low_demand_days} low-demand days with 10-15% discounts",
                "potential_impact": "Smooth demand curve by 20%",
                "estimated_savings": "$8,000/month"
            })

        # Opportunity 3: Extended hours on peak days
        peak_utilization = capacity_analysis["peak_utilization_pct"]
        if peak_utilization > 85:
            opportunities.append({
                "type": "capacity_expansion",
                "priority": "high",
                "title": "Extend Hours on Peak Days",
                "description": "Add 2 extra hours (7AM-8AM or 6PM-7PM) on Saturday and peak weekdays",
                "potential_impact": "Increase capacity by 15%",
                "estimated_revenue": "$20,000/month"
            })

        # Opportunity 4: Predictive scheduling
        opportunities.append({
            "type": "automation",
            "priority": "medium",
            "title": "Implement AI-Driven Predictive Scheduling",
            "description": "Use forecasts to automatically suggest optimal appointment times",
            "potential_impact": "Reduce no-shows by 25%, improve utilization by 15%",
            "estimated_savings": "$12,000/month"
        })

        return opportunities


    async def get_forecast_summary(self) -> Dict[str, Any]:
        """Get a summary of current forecast (for API endpoint)"""
        daily_forecast = await self._generate_daily_forecast(30)
        capacity_analysis = await self._analyze_service_center_capacity(daily_forecast)

        return {
            "next_7_days": daily_forecast[:7],
            "next_30_days_avg": round(sum(daily_forecast) / len(daily_forecast), 1),
            "capacity_status": "healthy" if capacity_analysis["peak_utilization_pct"] < 85 else "constrained",
            "service_centers": capacity_analysis["center_analysis"],
        }
