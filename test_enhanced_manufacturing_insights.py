"""
Comprehensive test suite for Enhanced Manufacturing Insights Agent
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.enhanced_manufacturing_insights_agent import (
    EnhancedManufacturingInsightsAgent,
    FieldFailure,
    FailureCluster,
    ManufacturingData,
    RCAReport,
    QualityRecommendation,
    CAPARecord,
)
from state import State


class TestEnhancedManufacturingInsightsAgent:
    """Test suite for Enhanced Manufacturing Insights Agent"""

    @pytest.fixture
    def agent(self):
        """Create agent instance for testing"""
        return EnhancedManufacturingInsightsAgent()

    @pytest.fixture
    def sample_state(self):
        """Create sample state for testing"""
        return State({"vehicle_id": "TEST_VIN_12345", "conversation_history": [], "updated_at": datetime.now()})

    def test_agent_initialization(self, agent):
        """Test agent initialization and data setup"""
        assert agent.agent_name == "enhanced_manufacturing_insights"
        assert len(agent.failure_database) == 500
        assert len(agent.manufacturing_database) == 4
        assert len(agent.rca_database) == 50
        assert len(agent.capa_database) == 30
        assert "critical_failure_count" in agent.quality_thresholds
        assert "executive_summary" in agent.report_templates

    @pytest.mark.asyncio
    async def test_aggregate_failures(self, agent):
        """Test failure aggregation functionality"""
        # Test with 30-day period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        aggregated = await agent.aggregate_failures(start_date.isoformat(), end_date.isoformat())

        assert isinstance(aggregated, list)
        assert len(aggregated) > 0

        # Check structure of aggregated data
        for item in aggregated:
            assert "component" in item
            assert "count" in item
            assert "affected_vins" in item
            assert "avg_cost" in item
            assert "avg_time_to_failure" in item
            assert item["count"] > 0

    @pytest.mark.asyncio
    async def test_cluster_similar_failures(self, agent):
        """Test failure clustering using ML algorithms"""
        # Get some failures to cluster
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        aggregated = await agent.aggregate_failures(start_date.isoformat(), end_date.isoformat())

        clusters = await agent.cluster_similar_failures(aggregated)

        assert isinstance(clusters, list)

        # If clusters exist, verify their structure
        if clusters:
            for cluster in clusters:
                assert isinstance(cluster, FailureCluster)
                assert cluster.size >= 3  # Minimum cluster size
                assert cluster.cluster_id.startswith("CLUSTER_")
                assert cluster.confidence_score >= 0
                assert cluster.priority in ["P0", "P1", "P2", "P3"]
                assert "most_common_component" in cluster.common_attributes

    @pytest.mark.asyncio
    async def test_correlate_with_manufacturing(self, agent):
        """Test manufacturing data correlation"""
        # Create mock failure cluster
        mock_failures = agent.failure_database[:10]
        mock_cluster = {"failures": mock_failures, "size": len(mock_failures)}

        correlation = await agent.correlate_with_manufacturing(mock_cluster)

        assert isinstance(correlation, ManufacturingData)
        assert correlation.supplier_id is not None
        assert correlation.batch_number is not None
        assert correlation.significance_p_value >= 0

    @pytest.mark.asyncio
    async def test_retrieve_historical_rca(self, agent):
        """Test RCA retrieval functionality"""
        rca_reports = await agent.retrieve_historical_rca("premature_wear", "ModelA")

        assert isinstance(rca_reports, list)
        assert len(rca_reports) <= 5  # Should return top 5

        for rca in rca_reports:
            assert isinstance(rca, RCAReport)
            assert rca.rca_id is not None
            assert rca.effectiveness_score >= 0

    @pytest.mark.asyncio
    async def test_generate_recommendations(self, agent):
        """Test recommendation generation"""
        # Create mock failure pattern
        mock_pattern = {
            "size": 25,
            "priority": "P1",
            "common_attributes": {
                "most_common_component": "engine",
                "avg_repair_cost": 1500,
                "warranty_coverage_rate": 0.8,
            },
        }

        # Get some historical RCA data
        historical_rca = [rca.__dict__ for rca in agent.rca_database[:3]]

        recommendations = await agent.generate_recommendations(mock_pattern, historical_rca)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        for rec in recommendations:
            assert isinstance(rec, QualityRecommendation)
            assert rec.priority in ["P0", "P1", "P2", "P3"]
            assert rec.title is not None
            assert rec.estimated_cost_savings >= 0

    @pytest.mark.asyncio
    async def test_estimate_warranty_cost_impact(self, agent):
        """Test warranty cost impact estimation"""
        mock_pattern = {"size": 20, "common_attributes": {"avg_repair_cost": 2000, "warranty_coverage_rate": 0.7}}

        cost_impact = await agent.estimate_warranty_cost_impact(mock_pattern)

        assert isinstance(cost_impact, dict)
        assert "current_impact" in cost_impact
        assert "projected_annual_impact" in cost_impact
        assert "cost_per_failure" in cost_impact
        assert cost_impact["current_impact"] >= 0
        assert cost_impact["projected_annual_impact"] >= 0

    @pytest.mark.asyncio
    async def test_forecast_future_failures(self, agent):
        """Test failure forecasting functionality"""
        mock_pattern = {"size": 15, "common_attributes": {"avg_repair_cost": 1200}}

        current_trend = [1000, 1100, 1200, 1300]  # Mock cost trend

        forecast = await agent.forecast_future_failures(mock_pattern, current_trend)

        assert isinstance(forecast, dict)
        assert "projected_monthly_failures" in forecast
        assert "projected_total_cost" in forecast
        assert "growth_rate" in forecast
        assert len(forecast["projected_monthly_failures"]) == 12
        assert forecast["projected_total_cost"] >= 0

    @pytest.mark.asyncio
    async def test_simulate_corrective_action_impact(self, agent):
        """Test corrective action impact simulation"""
        mock_pattern = {"size": 10}

        impact = await agent.simulate_corrective_action_impact(mock_pattern, "supplier_change")

        assert isinstance(impact, dict)
        assert "expected_reduction_percent" in impact
        assert "confidence" in impact
        assert "implementation_cost" in impact
        assert 0 <= impact["confidence"] <= 1
        assert impact["expected_reduction_percent"] >= 0

    @pytest.mark.asyncio
    async def test_track_capa_status(self, agent):
        """Test CAPA status tracking"""
        # Use first CAPA from database
        capa_id = agent.capa_database[0].capa_id

        status = await agent.track_capa_status(capa_id)

        assert isinstance(status, dict)
        assert "capa_id" in status
        assert "status" in status
        assert "assigned_to" in status
        assert status["status"] in ["open", "in_progress", "completed", "verified"]

    @pytest.mark.asyncio
    async def test_measure_capa_effectiveness(self, agent):
        """Test CAPA effectiveness measurement"""
        # Use first CAPA from database
        capa_id = agent.capa_database[0].capa_id

        effectiveness = await agent.measure_capa_effectiveness(capa_id, "premature_wear")

        assert isinstance(effectiveness, dict)
        assert "failure_reduction_percent" in effectiveness
        assert "statistical_significance" in effectiveness
        assert "confidence_level" in effectiveness
        assert 0 <= effectiveness["confidence_level"] <= 1

    @pytest.mark.asyncio
    async def test_create_quality_report(self, agent):
        """Test quality report generation"""
        # Create mock insights data
        mock_insights = {
            "period": "2024 - 01 - 01 to 2024 - 01 - 31",
            "cluster_analyses": [
                {
                    "cluster": FailureCluster(
                        cluster_id="TEST_001",
                        size=25,
                        common_attributes={
                            "most_common_component": "engine",
                            "most_common_failure_type": "premature_wear",
                            "most_common_model": "ModelA",
                            "avg_repair_cost": 1500,
                        },
                        failures=[],
                        confidence_score=0.8,
                        priority="P1",
                    ),
                    "cost_impact": {"current_impact": 37500},
                    "recommendations": [
                        QualityRecommendation(
                            recommendation_id="REC_001",
                            priority="P1",
                            title="Supplier Quality Review",
                            description="Review supplier quality processes",
                            affected_components=["engine"],
                            estimated_cost_savings=30000,
                            implementation_timeline="30 days",
                            responsible_team="Quality",
                            success_metrics=["Reduced defects"],
                        )
                    ],
                }
            ],
            "total_failures": 100,
        }

        report = await agent.create_quality_report(mock_insights)

        assert isinstance(report, str)
        assert "MANUFACTURING QUALITY REPORT" in report
        assert "EXECUTIVE SUMMARY" in report
        assert "Total Field Failures: 100" in report
        assert "engine" in report.lower()

    @pytest.mark.asyncio
    async def test_complete_workflow(self, agent, sample_state):
        """Test complete manufacturing insights workflow"""
        # Initialize conversation_history to prevent KeyError
        sample_state["conversation_history"] = []
        sample_state["updated_at"] = datetime.now()

        # Execute the complete workflow
        result_state = await agent._execute_internal(sample_state)

        # Verify state updates
        assert "manufacturing_insights" in result_state
        insights = result_state["manufacturing_insights"]

        # Check all required components
        assert "analysis_period" in insights
        assert "aggregated_failures" in insights
        assert "failure_clusters" in insights
        assert "cluster_analyses" in insights
        assert "quality_report" in insights
        assert "capa_effectiveness" in insights
        assert "analysis_timestamp" in insights

        # Verify data types and structure
        assert isinstance(insights["aggregated_failures"], int)
        assert isinstance(insights["failure_clusters"], int)
        assert isinstance(insights["cluster_analyses"], list)
        assert isinstance(insights["quality_report"], str)
        assert isinstance(insights["capa_effectiveness"], dict)

    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """Test error handling in various scenarios"""
        # Test with invalid date format
        with pytest.raises(ValueError):
            await agent.aggregate_failures("invalid_date", "2024 - 01 - 31")

        # Test with empty failure list
        empty_clusters = await agent.cluster_similar_failures([])
        assert empty_clusters == []

        # Test CAPA tracking with non-existent ID
        status = await agent.track_capa_status("NON_EXISTENT")
        assert "error" in status

    @pytest.mark.asyncio
    async def test_data_model_validation(self, agent):
        """Test data model integrity and validation"""
        # Test FieldFailure data model
        for failure in agent.failure_database[:5]:
            assert isinstance(failure, FieldFailure)
            assert failure.failure_id is not None
            assert failure.vin is not None
            assert failure.component in ["engine", "transmission", "brakes", "electrical", "suspension", "hvac"]
            assert failure.severity in ["critical", "high", "medium", "low"]

        # Test ManufacturingData data model
        for mfg_data in agent.manufacturing_database.values():
            assert isinstance(mfg_data, ManufacturingData)
            assert mfg_data.supplier_id is not None
            assert 0 <= mfg_data.significance_p_value <= 1

        # Test RCAReport data model
        for rca in agent.rca_database[:5]:
            assert isinstance(rca, RCAReport)
            assert rca.rca_id is not None
            assert 0 <= rca.effectiveness_score <= 1

        # Test CAPARecord data model
        for capa in agent.capa_database[:5]:
            assert isinstance(capa, CAPARecord)
            assert capa.status in ["open", "in_progress", "completed", "verified"]
            assert 0 <= capa.failure_reduction_percent <= 100


def run_tests():
    """Run all tests"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
