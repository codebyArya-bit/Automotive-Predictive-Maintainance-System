"""
Enhanced Manufacturing Insights Agent - Analyzes field failures and generates quality reports
"""

import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import uuid

from .base_agent import BaseAgent
from state import State, Priority


@dataclass
class FieldFailure:
    """Represents a field failure record"""

    failure_id: str
    vin: str
    component: str
    failure_type: str
    symptoms: List[str]
    mileage: int
    failure_date: datetime
    vehicle_model: str
    manufacturing_date: datetime
    repair_cost: float
    warranty_covered: bool
    severity: str  # "critical", "high", "medium", "low"


@dataclass
class FailureCluster:
    """Represents a cluster of similar failures"""

    cluster_id: str
    size: int
    common_attributes: Dict[str, Any]
    failures: List[FieldFailure]
    confidence_score: float
    priority: str


@dataclass
class ManufacturingData:
    """Manufacturing correlation data"""

    supplier_id: str
    batch_number: str
    production_line: str
    production_date_range: Tuple[datetime, datetime]
    significance_p_value: float
    affected_vins: List[str]


@dataclass
class RCAReport:
    """Root Cause Analysis report"""

    rca_id: str
    defect_type: str
    vehicle_model: str
    root_cause: str
    corrective_action: str
    effectiveness_score: float
    implementation_date: datetime
    cost_impact: float


@dataclass
class QualityRecommendation:
    """Quality improvement recommendation"""

    recommendation_id: str
    priority: str  # "P0", "P1", "P2", "P3"
    title: str
    description: str
    affected_components: List[str]
    estimated_cost_savings: float
    implementation_timeline: str
    responsible_team: str
    success_metrics: List[str]


@dataclass
class CAPARecord:
    """Corrective and Preventive Action record"""

    capa_id: str
    defect_pattern: str
    status: str  # "open", "in_progress", "completed", "verified"
    assigned_to: str
    due_date: datetime
    completion_date: Optional[datetime]
    effectiveness_verified: bool
    failure_reduction_percent: float


class EnhancedManufacturingInsightsAgent(BaseAgent):
    """Enhanced agent for comprehensive manufacturing insights and quality analysis"""

    def __init__(self):
        super().__init__("enhanced_manufacturing_insights")

        # Initialize mock databases
        self.failure_database = self._initialize_failure_database()
        self.manufacturing_database = self._initialize_manufacturing_database()
        self.rca_database = self._initialize_rca_database()
        self.capa_database = self._initialize_capa_database()

        # Quality thresholds and parameters
        self.quality_thresholds = {
            "critical_failure_count": 50,
            "high_failure_count": 30,
            "medium_failure_count": 10,
            "warranty_cost_threshold": 100000,
            "clustering_eps": 0.3,
            "clustering_min_samples": 5,
        }

        # Report templates
        self.report_templates = {
            "executive_summary": "Manufacturing Quality Report - {period}",
            "priority_levels": {
                "P0": "Critical: Safety-related, >50 failures, rapidly growing",
                "P1": "High: Non-safety, >30 failures, significant cost impact",
                "P2": "Medium: 10 - 30 failures, moderate cost",
                "P3": "Low: <10 failures, informational",
            },
        }

    def _initialize_failure_database(self) -> List[FieldFailure]:
        """Initialize mock field failure database"""
        failures = []
        components = ["engine", "transmission", "brakes", "electrical", "suspension", "hvac"]
        models = ["ModelA", "ModelB", "ModelC", "ModelD"]
        failure_types = ["premature_wear", "manufacturing_defect", "design_flaw", "material_failure"]

        for i in range(500):  # Generate 500 mock failures
            failure = FieldFailure(
                failure_id=f"F{i:04d}",
                vin=f"VIN{random.randint(10000, 99999)}",
                component=random.choice(components),
                failure_type=random.choice(failure_types),
                symptoms=[f"symptom_{j}" for j in range(random.randint(1, 4))],
                mileage=random.randint(5000, 200000),
                failure_date=datetime.now() - timedelta(days=random.randint(1, 365)),
                vehicle_model=random.choice(models),
                manufacturing_date=datetime.now() - timedelta(days=random.randint(365, 1825)),
                repair_cost=random.uniform(200, 5000),
                warranty_covered=random.choice([True, False]),
                severity=random.choice(["critical", "high", "medium", "low"]),
            )
            failures.append(failure)

        return failures

    def _initialize_manufacturing_database(self) -> Dict[str, ManufacturingData]:
        """Initialize mock manufacturing database"""
        suppliers = ["SupplierA", "SupplierB", "SupplierC", "SupplierD"]
        manufacturing_data = {}

        for i, supplier in enumerate(suppliers):
            data = ManufacturingData(
                supplier_id=supplier,
                batch_number=f"BATCH_{i:03d}",
                production_line=f"LINE_{i + 1}",
                production_date_range=(datetime.now() - timedelta(days=365), datetime.now() - timedelta(days=300)),
                significance_p_value=random.uniform(0.001, 0.05),
                affected_vins=[f"VIN{random.randint(10000, 99999)}" for _ in range(10)],
            )
            manufacturing_data[supplier] = data

        return manufacturing_data

    def _initialize_rca_database(self) -> List[RCAReport]:
        """Initialize mock RCA database"""
        rca_reports = []
        defect_types = ["premature_wear", "manufacturing_defect", "design_flaw", "material_failure"]
        models = ["ModelA", "ModelB", "ModelC", "ModelD"]

        for i in range(50):  # Generate 50 mock RCA reports
            report = RCAReport(
                rca_id=f"RCA{i:03d}",
                defect_type=random.choice(defect_types),
                vehicle_model=random.choice(models),
                root_cause=f"Root cause analysis for defect {i}",
                corrective_action=f"Corrective action plan {i}",
                effectiveness_score=random.uniform(0.6, 0.95),
                implementation_date=datetime.now() - timedelta(days=random.randint(30, 365)),
                cost_impact=random.uniform(10000, 500000),
            )
            rca_reports.append(report)

        return rca_reports

    def _initialize_capa_database(self) -> List[CAPARecord]:
        """Initialize mock CAPA database"""
        capa_records = []
        statuses = ["open", "in_progress", "completed", "verified"]

        for i in range(30):  # Generate 30 mock CAPA records
            record = CAPARecord(
                capa_id=f"CAPA{i:03d}",
                defect_pattern=f"Defect pattern {i}",
                status=random.choice(statuses),
                assigned_to=f"Team_{random.choice(['A', 'B', 'C'])}",
                due_date=datetime.now() + timedelta(days=random.randint(30, 180)),
                completion_date=(
                    datetime.now() - timedelta(days=random.randint(1, 90)) if random.choice([True, False]) else None
                ),
                effectiveness_verified=random.choice([True, False]),
                failure_reduction_percent=random.uniform(10, 80),
            )
            capa_records.append(record)

        return capa_records

    async def _execute_internal(self, state: State) -> State:
        """Execute comprehensive manufacturing insights analysis"""
        self.logger.info("Starting enhanced manufacturing insights analysis")

        # Define analysis period (last 30 days)
        period_end = datetime.now()
        period_start = period_end - timedelta(days=30)

        # Step 1: Aggregate failures for the period
        aggregated_failures = await self.aggregate_failures(period_start.isoformat(), period_end.isoformat())

        # Step 2: Cluster similar failures
        failure_clusters = await self.cluster_similar_failures(aggregated_failures)

        # Step 3: Analyze each significant cluster
        cluster_analyses = []
        for cluster in failure_clusters:
            if cluster.size >= self.quality_thresholds["medium_failure_count"]:
                # Correlate with manufacturing data
                manufacturing_correlation = await self.correlate_with_manufacturing(cluster.__dict__)

                # Retrieve historical RCA reports
                historical_rca = await self.retrieve_historical_rca(
                    cluster.common_attributes.get("failure_type", "unknown"),
                    cluster.common_attributes.get("vehicle_model", "unknown"),
                )

                # Generate recommendations
                recommendations = await self.generate_recommendations(
                    cluster.__dict__, [rca.__dict__ for rca in historical_rca]
                )

                # Estimate warranty cost impact
                cost_impact = await self.estimate_warranty_cost_impact(cluster.__dict__)

                # Forecast future failures
                forecast = await self.forecast_future_failures(
                    cluster.__dict__, [f.repair_cost for f in cluster.failures]
                )

                cluster_analysis = {
                    "cluster": cluster,
                    "manufacturing_correlation": manufacturing_correlation,
                    "historical_rca": historical_rca,
                    "recommendations": recommendations,
                    "cost_impact": cost_impact,
                    "forecast": forecast,
                }
                cluster_analyses.append(cluster_analysis)

        # Step 4: Generate comprehensive quality report
        quality_report = await self.create_quality_report(
            {
                "period": f"{period_start.date()} to {period_end.date()}",
                "cluster_analyses": cluster_analyses,
                "total_failures": len(aggregated_failures),
                "analysis_timestamp": datetime.now().isoformat(),
            }
        )

        # Step 5: Track CAPA effectiveness
        capa_effectiveness = await self._analyze_capa_effectiveness()

        # Update state with comprehensive insights
        manufacturing_insights = {
            "analysis_period": {"start": period_start.isoformat(), "end": period_end.isoformat()},
            "aggregated_failures": len(aggregated_failures),
            "failure_clusters": len(failure_clusters),
            "significant_clusters": len(cluster_analyses),
            "cluster_analyses": cluster_analyses,
            "quality_report": quality_report,
            "capa_effectiveness": capa_effectiveness,
            "analysis_timestamp": datetime.now().isoformat(),
        }

        state["manufacturing_insights"] = manufacturing_insights
        state["priority"] = Priority.P1 if len(cluster_analyses) > 5 else Priority.P2

        self._add_log_message(
            state,
            f"Manufacturing insights analysis completed. Found {len(failure_clusters)} failure clusters, "
            f"{len(cluster_analyses)} requiring immediate attention.",
        )

        return state

    async def aggregate_failures(self, period_start: str, period_end: str) -> List[Dict]:
        """Aggregate all failures in a time period"""
        start_date = datetime.fromisoformat(period_start)
        end_date = datetime.fromisoformat(period_end)

        # Filter failures by date range
        period_failures = [f for f in self.failure_database if start_date <= f.failure_date <= end_date]

        # Group by component and vehicle model
        aggregated = defaultdict(
            lambda: {
                "component": "",
                "count": 0,
                "affected_vins": set(),
                "total_cost": 0,
                "avg_mileage": 0,
                "failures": [],
            }
        )

        for failure in period_failures:
            key = f"{failure.component}_{failure.vehicle_model}"
            agg = aggregated[key]
            agg["component"] = failure.component
            agg["vehicle_model"] = failure.vehicle_model
            agg["count"] += 1
            agg["affected_vins"].add(failure.vin)
            agg["total_cost"] += failure.repair_cost
            agg["failures"].append(failure)

        # Calculate averages and convert to list
        result = []
        for key, agg in aggregated.items():
            if agg["count"] > 0:
                agg["affected_vins"] = list(agg["affected_vins"])
                agg["avg_cost"] = agg["total_cost"] / agg["count"]
                agg["avg_mileage"] = sum(f.mileage for f in agg["failures"]) / agg["count"]
                agg["avg_time_to_failure"] = agg["avg_mileage"] / 12000  # Assuming 12k miles/year
                result.append(agg)

        return sorted(result, key=lambda x: x["count"], reverse=True)

    async def cluster_similar_failures(self, failures: List[Dict]) -> List[FailureCluster]:
        """Cluster failures into patterns using ML"""
        if not failures:
            return []

        # Prepare features for clustering
        features = []
        failure_objects = []

        for failure_group in failures:
            for failure in failure_group["failures"]:
                # Create feature vector
                feature_vector = [
                    hash(failure.component) % 1000,
                    hash(failure.failure_type) % 1000,
                    hash(failure.vehicle_model) % 1000,
                    failure.mileage / 1000,  # Normalize mileage
                    failure.repair_cost / 100,  # Normalize cost
                    len(failure.symptoms),
                    (datetime.now() - failure.manufacturing_date).days / 365,  # Vehicle age in years
                ]
                features.append(feature_vector)
                failure_objects.append(failure)

        if len(features) < 2:
            return []

        # Standardize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        # Apply DBSCAN clustering
        clustering = DBSCAN(
            eps=self.quality_thresholds["clustering_eps"], min_samples=self.quality_thresholds["clustering_min_samples"]
        )
        cluster_labels = clustering.fit_predict(features_scaled)

        # Group failures by cluster
        clusters = defaultdict(list)
        for i, label in enumerate(cluster_labels):
            if label != -1:  # Ignore noise points
                clusters[label].append(failure_objects[i])

        # Create FailureCluster objects
        failure_clusters = []
        for cluster_id, cluster_failures in clusters.items():
            if len(cluster_failures) >= 3:  # Minimum cluster size
                # Analyze common attributes
                common_attributes = self._analyze_cluster_attributes(cluster_failures)

                # Calculate confidence score
                confidence_score = min(len(cluster_failures) / 50.0, 1.0)  # Max confidence at 50 failures

                # Determine priority
                priority = self._determine_cluster_priority(cluster_failures)

                cluster = FailureCluster(
                    cluster_id=f"CLUSTER_{cluster_id:03d}",
                    size=len(cluster_failures),
                    common_attributes=common_attributes,
                    failures=cluster_failures,
                    confidence_score=confidence_score,
                    priority=priority,
                )
                failure_clusters.append(cluster)

        return sorted(failure_clusters, key=lambda x: x.size, reverse=True)

    def _analyze_cluster_attributes(self, failures: List[FieldFailure]) -> Dict[str, Any]:
        """Analyze common attributes within a failure cluster"""
        components = Counter(f.component for f in failures)
        failure_types = Counter(f.failure_type for f in failures)
        models = Counter(f.vehicle_model for f in failures)
        severities = Counter(f.severity for f in failures)

        return {
            "most_common_component": components.most_common(1)[0][0],
            "most_common_failure_type": failure_types.most_common(1)[0][0],
            "most_common_model": models.most_common(1)[0][0],
            "most_common_severity": severities.most_common(1)[0][0],
            "avg_mileage": sum(f.mileage for f in failures) / len(failures),
            "avg_repair_cost": sum(f.repair_cost for f in failures) / len(failures),
            "warranty_coverage_rate": sum(1 for f in failures if f.warranty_covered) / len(failures),
        }

    def _determine_cluster_priority(self, failures: List[FieldFailure]) -> str:
        """Determine priority level for a failure cluster"""
        size = len(failures)
        has_critical = any(f.severity == "critical" for f in failures)
        avg_cost = sum(f.repair_cost for f in failures) / len(failures)

        if has_critical or size >= self.quality_thresholds["critical_failure_count"]:
            return "P0"
        elif size >= self.quality_thresholds["high_failure_count"] or avg_cost > 2000:
            return "P1"
        elif size >= self.quality_thresholds["medium_failure_count"]:
            return "P2"
        else:
            return "P3"

    async def correlate_with_manufacturing(self, failure_cluster: Dict) -> ManufacturingData:
        """Correlate failure cluster with manufacturing data"""
        # Extract VINs from cluster
        cluster_vins = [f.vin for f in failure_cluster.get("failures", [])]

        # Find manufacturing correlations
        correlations = {}
        for supplier_id, mfg_data in self.manufacturing_database.items():
            # Calculate overlap with affected VINs
            overlap = len(set(cluster_vins) & set(mfg_data.affected_vins))
            if overlap > 0:
                # Calculate statistical significance (mock chi-square test)
                expected = len(cluster_vins) * len(mfg_data.affected_vins) / 50000  # Total fleet size
                if expected > 0:
                    chi_square = ((overlap - expected) ** 2) / expected
                    p_value = max(0.001, 1 / (1 + chi_square))  # Simplified p-value calculation

                    correlations[supplier_id] = {"overlap": overlap, "p_value": p_value, "data": mfg_data}

        # Return the most significant correlation
        if correlations:
            best_correlation = min(correlations.items(), key=lambda x: x[1]["p_value"])
            return best_correlation[1]["data"]

        # Return default if no correlation found
        return ManufacturingData(
            supplier_id="Unknown",
            batch_number="N/A",
            production_line="N/A",
            production_date_range=(datetime.now(), datetime.now()),
            significance_p_value=1.0,
            affected_vins=[],
        )

    async def retrieve_historical_rca(self, defect_type: str, vehicle_model: str) -> List[RCAReport]:
        """Retrieve similar RCA reports from history using vector similarity"""
        # Simple text similarity for mock implementation
        relevant_rcas = []

        for rca in self.rca_database:
            # Calculate similarity score (mock implementation)
            type_match = 1.0 if rca.defect_type == defect_type else 0.3
            model_match = 1.0 if rca.vehicle_model == vehicle_model else 0.5

            similarity_score = (type_match + model_match) / 2.0

            if similarity_score > 0.6:  # Threshold for relevance
                relevant_rcas.append(rca)

        # Sort by effectiveness score and return top 5
        return sorted(relevant_rcas, key=lambda x: x.effectiveness_score, reverse=True)[:5]

    async def generate_recommendations(
        self, failure_pattern: Dict, historical_rca: List[Dict]
    ) -> List[QualityRecommendation]:
        """Generate actionable recommendations using LLM + RAG"""
        recommendations = []

        # Analyze failure pattern
        cluster_size = failure_pattern.get("size", 0)
        priority = failure_pattern.get("priority", "P3")
        common_attrs = failure_pattern.get("common_attributes", {})

        # Generate recommendations based on pattern analysis
        if cluster_size >= self.quality_thresholds["critical_failure_count"]:
            # Critical issue - immediate action required
            rec = QualityRecommendation(
                recommendation_id=str(uuid.uuid4()),
                priority="P0",
                title="Immediate Production Stop and Investigation",
                description=f"Critical failure pattern detected in {common_attrs.get('most_common_component', 'unknown')} component. "
                f"Immediate investigation and potential production halt required.",
                affected_components=[common_attrs.get("most_common_component", "unknown")],
                estimated_cost_savings=cluster_size * common_attrs.get("avg_repair_cost", 1000),
                implementation_timeline="Immediate (0 - 24 hours)",
                responsible_team="Quality Assurance",
                success_metrics=["Zero new failures", "Root cause identified", "Corrective action implemented"],
            )
            recommendations.append(rec)

        # Supplier-related recommendations
        if common_attrs.get("warranty_coverage_rate", 0) > 0.7:
            rec = QualityRecommendation(
                recommendation_id=str(uuid.uuid4()),
                priority=priority,
                title="Supplier Quality Improvement Program",
                description="High warranty claim rate indicates supplier quality issues. "
                "Implement enhanced supplier audits and quality controls.",
                affected_components=[common_attrs.get("most_common_component", "unknown")],
                estimated_cost_savings=cluster_size * common_attrs.get("avg_repair_cost", 1000) * 0.8,
                implementation_timeline="30 - 60 days",
                responsible_team="Supplier Quality",
                success_metrics=["Reduced defect rate by 50%", "Improved supplier scorecard", "Cost reduction"],
            )
            recommendations.append(rec)

        # Design improvement recommendations
        if common_attrs.get("avg_mileage", 100000) < 50000:
            rec = QualityRecommendation(
                recommendation_id=str(uuid.uuid4()),
                priority=priority,
                title="Design Robustness Enhancement",
                description="Early failures indicate potential design weakness. "
                "Conduct design review and durability testing.",
                affected_components=[common_attrs.get("most_common_component", "unknown")],
                estimated_cost_savings=cluster_size * common_attrs.get("avg_repair_cost", 1000) * 0.6,
                implementation_timeline="90 - 180 days",
                responsible_team="Engineering",
                success_metrics=["Increased MTBF", "Reduced early failures", "Improved durability test results"],
            )
            recommendations.append(rec)

        return recommendations

    async def estimate_warranty_cost_impact(self, failure_pattern: Dict) -> float:
        """Estimate financial impact of defect pattern"""
        cluster_size = failure_pattern.get("size", 0)
        common_attrs = failure_pattern.get("common_attributes", {})
        avg_repair_cost = common_attrs.get("avg_repair_cost", 1000)
        warranty_coverage_rate = common_attrs.get("warranty_coverage_rate", 0.5)

        # Calculate current impact
        current_impact = cluster_size * avg_repair_cost * warranty_coverage_rate

        # Project future impact (assuming linear growth)
        projected_monthly_failures = cluster_size * 1.2  # 20% growth assumption
        annual_projected_impact = projected_monthly_failures * 12 * avg_repair_cost * warranty_coverage_rate

        return {
            "current_impact": current_impact,
            "projected_annual_impact": annual_projected_impact,
            "cost_per_failure": avg_repair_cost,
            "warranty_coverage_rate": warranty_coverage_rate,
        }

    async def forecast_future_failures(self, defect_pattern: Dict, current_trend: List) -> Dict:
        """Forecast failure rate if no action taken"""
        cluster_size = defect_pattern.get("size", 0)

        # Simple linear projection (in real implementation, use Prophet or ARIMA)
        monthly_growth_rate = 0.15  # 15% monthly growth assumption

        projected_failures = []
        current_monthly = cluster_size

        for month in range(12):  # 12-month forecast
            current_monthly *= 1 + monthly_growth_rate
            projected_failures.append(int(current_monthly))

        common_attributes = defect_pattern.get("common_attributes", {})
        if common_attributes is None:
            common_attributes = {}
        total_projected_cost = sum(projected_failures) * common_attributes.get("avg_repair_cost", 1000)

        return {
            "projected_monthly_failures": projected_failures,
            "projected_total_cost": total_projected_cost,
            "growth_rate": monthly_growth_rate,
            "forecast_confidence": 0.7,  # Mock confidence level
        }

    async def simulate_corrective_action_impact(self, defect_pattern: Dict, action: str) -> Dict:
        """Simulate impact of proposed corrective action"""
        # Mock effectiveness based on action type
        effectiveness_map = {
            "supplier_change": {"reduction": 0.8, "confidence": 0.9},
            "design_modification": {"reduction": 0.7, "confidence": 0.8},
            "process_improvement": {"reduction": 0.6, "confidence": 0.85},
            "quality_control": {"reduction": 0.5, "confidence": 0.9},
        }

        effectiveness = effectiveness_map.get(action, {"reduction": 0.4, "confidence": 0.6})

        return {
            "expected_reduction_percent": effectiveness["reduction"] * 100,
            "confidence": effectiveness["confidence"],
            "implementation_cost": random.uniform(50000, 500000),
            "payback_period_months": random.randint(6, 24),
        }

    async def track_capa_status(self, capa_id: str) -> Dict:
        """Track status of corrective/preventive actions"""
        # Find CAPA record
        capa_record = next((c for c in self.capa_database if c.capa_id == capa_id), None)

        if not capa_record:
            return {"error": f"CAPA {capa_id} not found"}

        return {
            "capa_id": capa_record.capa_id,
            "status": capa_record.status,
            "assigned_to": capa_record.assigned_to,
            "due_date": capa_record.due_date.isoformat(),
            "completion_date": capa_record.completion_date.isoformat() if capa_record.completion_date else None,
            "effectiveness_verified": capa_record.effectiveness_verified,
            "days_remaining": (capa_record.due_date - datetime.now()).days,
        }

    async def measure_capa_effectiveness(self, capa_id: str, defect_type: str) -> Dict:
        """Measure if CAPA actually reduced failures"""
        capa_record = next((c for c in self.capa_database if c.capa_id == capa_id), None)

        if not capa_record:
            return {"error": f"CAPA {capa_id} not found"}

        # Mock effectiveness measurement
        return {
            "capa_id": capa_id,
            "defect_type": defect_type,
            "failure_reduction_percent": capa_record.failure_reduction_percent,
            "statistical_significance": capa_record.failure_reduction_percent > 20,
            "measurement_period": "90 days post-implementation",
            "confidence_level": 0.95 if capa_record.failure_reduction_percent > 30 else 0.8,
        }

    async def _analyze_capa_effectiveness(self) -> Dict:
        """Analyze overall CAPA effectiveness"""
        completed_capas = [c for c in self.capa_database if c.status == "completed"]
        verified_capas = [c for c in completed_capas if c.effectiveness_verified]

        if not completed_capas:
            return {"message": "No completed CAPAs to analyze"}

        avg_reduction = (
            sum(c.failure_reduction_percent for c in verified_capas) / len(verified_capas) if verified_capas else 0
        )

        return {
            "total_capas": len(self.capa_database),
            "completed_capas": len(completed_capas),
            "verified_effective": len(verified_capas),
            "effectiveness_rate": len(verified_capas) / len(completed_capas) if completed_capas else 0,
            "average_failure_reduction": avg_reduction,
            "recommendations": [
                (
                    "Improve CAPA verification process"
                    if len(verified_capas) / len(completed_capas) < 0.8
                    else "CAPA process performing well"
                ),
                "Focus on higher impact actions" if avg_reduction < 50 else "Maintain current CAPA quality",
            ],
        }

    async def create_quality_report(self, insights: Dict) -> str:
        """Generate formatted quality report for manufacturing team"""
        period = insights.get("period", "Unknown period")
        cluster_analyses = insights.get("cluster_analyses", [])
        total_failures = insights.get("total_failures", 0)

        # Prioritize clusters
        p0_clusters = [c for c in cluster_analyses if c["cluster"].priority == "P0"]
        p1_clusters = [c for c in cluster_analyses if c["cluster"].priority == "P1"]
        p2_clusters = [c for c in cluster_analyses if c["cluster"].priority == "P2"]

        report = f"""
MANUFACTURING QUALITY REPORT
Period: {period}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY
================
Total Field Failures: {total_failures}
Significant Failure Clusters: {len(cluster_analyses)}
Critical Issues (P0): {len(p0_clusters)}
High Priority Issues (P1): {len(p1_clusters)}
Medium Priority Issues (P2): {len(p2_clusters)}

CRITICAL ISSUES (P0) - IMMEDIATE ACTION REQUIRED
===============================================
"""

        for i, analysis in enumerate(p0_clusters[:5], 1):
            cluster = analysis["cluster"]
            report += f"""
{i}. {cluster.common_attributes['most_common_component'].upper()} - {cluster.common_attributes['most_common_failure_type']}
   Affected Vehicles: {cluster.size}
   Primary Model: {cluster.common_attributes['most_common_model']}
   Avg Repair Cost: ${cluster.common_attributes['avg_repair_cost']:.2f}
   Estimated Total Impact: ${analysis['cost_impact']['current_impact']:.2f}

   Recommendations:
"""
            for rec in analysis["recommendations"][:2]:
                report += f"   - {rec.title}: {rec.description[:100]}...\n"

        report += f"""

HIGH PRIORITY ISSUES (P1)
========================
"""

        for i, analysis in enumerate(p1_clusters[:5], 1):
            cluster = analysis["cluster"]
            report += f"""
{i}. {cluster.common_attributes['most_common_component']} failures in {cluster.common_attributes['most_common_model']}
   Count: {cluster.size} | Avg Cost: ${cluster.common_attributes['avg_repair_cost']:.2f}
   Key Recommendation: {analysis['recommendations'][0].title if analysis['recommendations'] else 'Under investigation'}
"""

        report += f"""

SUPPLIER SCORECARD
==================
Based on failure correlation analysis:
"""

        # Add supplier analysis
        supplier_issues = defaultdict(int)
        for analysis in cluster_analyses:
            if hasattr(analysis.get("manufacturing_correlation"), "supplier_id"):
                supplier_issues[analysis["manufacturing_correlation"].supplier_id] += analysis["cluster"].size

        for supplier, issue_count in sorted(supplier_issues.items(), key=lambda x: x[1], reverse=True):
            report += f"- {supplier}: {issue_count} related failures\n"

        report += f"""

NEXT STEPS
==========
1. Immediate investigation of all P0 issues
2. Supplier quality reviews for top 3 suppliers
3. Enhanced quality controls for high-risk components
4. Monthly follow-up on all corrective actions

Report generated by Enhanced Manufacturing Insights Agent
Contact: quality-team@automotive.com
"""

        return report
