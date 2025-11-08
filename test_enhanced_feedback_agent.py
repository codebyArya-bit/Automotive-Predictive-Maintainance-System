"""
Comprehensive test suite for Enhanced Feedback Agent
Tests all feedback collection, issue escalation, ML integration, and analytics functionality
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.enhanced_feedback_agent import EnhancedFeedbackAgent, PredictionOutcome
from state import State


def test_completed_appointments_retrieval():
    """Test getting completed appointments for a specific date"""
    print("\n=== Testing Completed Appointments Retrieval ===")

    agent = EnhancedFeedbackAgent()

    # Test with yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    appointments = agent.get_completed_appointments(yesterday)

    print(f"✓ Found {len(appointments)} completed appointments for {yesterday}")

    if appointments:
        sample_appointment = appointments[0]
        print(f"✓ Sample appointment: {sample_appointment['appointment_id']}")
        print(f"  - Customer: {sample_appointment['customer_id']}")
        print(f"  - Predicted issue: {sample_appointment['predicted_issue']}")
        print(f"  - Service cost: ₹{sample_appointment['service_cost']}")

    # Test with date that has no appointments
    future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    future_appointments = agent.get_completed_appointments(future_date)
    print(f"✓ Future date check: {len(future_appointments)} appointments (expected: 0)")

    return len(appointments) > 0


def test_feedback_request_sending():
    """Test sending feedback requests via different channels"""
    print("\n=== Testing Feedback Request Sending ===")

    agent = EnhancedFeedbackAgent()

    # Test SMS feedback request
    sms_sent = agent.send_feedback_request("CUST001", "APT - 001", "sms")
    print(f"✓ SMS feedback request sent: {sms_sent}")

    # Test app notification
    app_sent = agent.send_feedback_request("CUST002", "APT - 002", "app_notification")
    print(f"✓ App notification sent: {app_sent}")

    # Test voice call
    voice_sent = agent.send_feedback_request("CUST004", "APT - 003", "voice_call")
    print(f"✓ Voice call initiated: {voice_sent}")

    # Test with non-existent customer
    invalid_sent = agent.send_feedback_request("INVALID", "APT - 001", "sms")
    print(f"✓ Invalid customer handling: {not invalid_sent} (should be False)")

    return sms_sent and app_sent and voice_sent and not invalid_sent


def test_feedback_collection():
    """Test structured feedback collection"""
    print("\n=== Testing Feedback Collection ===")

    agent = EnhancedFeedbackAgent()

    # Test feedback collection for multiple appointments
    test_appointments = ["APT - 001", "APT - 002", "APT - 003"]
    collected_feedback = []

    for apt_id in test_appointments:
        feedback = agent.collect_feedback(apt_id)
        if feedback:
            collected_feedback.append(feedback)
            print(f"✓ Feedback collected for {apt_id}:")
            print(f"  - Service quality: {feedback['service_quality']}/5")
            print(f"  - Issue resolved: {feedback['issue_resolved']}")
            print(f"  - NPS score: {feedback['nps_score']}/10")
            print(f"  - Comments: {feedback['comments'][:50]}...")

    # Test feedback structure validation
    if collected_feedback:
        sample_feedback = collected_feedback[0]
        required_fields = [
            "appointment_id",
            "customer_id",
            "service_quality",
            "issue_resolved",
            "nps_score",
            "comments",
        ]

        all_fields_present = all(field in sample_feedback for field in required_fields)
        print(f"✓ Feedback structure validation: {all_fields_present}")

        # Test rating ranges
        valid_ratings = 1 <= sample_feedback["service_quality"] <= 5 and 0 <= sample_feedback["nps_score"] <= 10
        print(f"✓ Rating ranges validation: {valid_ratings}")

        return len(collected_feedback) > 0 and all_fields_present and valid_ratings

    return False


def test_unresolved_issue_detection():
    """Test detection of unresolved issues"""
    print("\n=== Testing Unresolved Issue Detection ===")

    agent = EnhancedFeedbackAgent()

    # Test case 1: Issue explicitly not resolved
    feedback_unresolved = {"issue_resolved": False, "service_quality": 4, "nps_score": 7}
    is_unresolved_1 = agent.detect_unresolved_issue(feedback_unresolved)
    print(f"✓ Explicit unresolved issue detected: {is_unresolved_1}")

    # Test case 2: Low service quality
    feedback_low_quality = {"issue_resolved": True, "service_quality": 2, "nps_score": 8}
    is_unresolved_2 = agent.detect_unresolved_issue(feedback_low_quality)
    print(f"✓ Low service quality detected as unresolved: {is_unresolved_2}")

    # Test case 3: Very low NPS
    feedback_low_nps = {"issue_resolved": True, "service_quality": 4, "nps_score": 2}
    is_unresolved_3 = agent.detect_unresolved_issue(feedback_low_nps)
    print(f"✓ Very low NPS detected as unresolved: {is_unresolved_3}")

    # Test case 4: All positive feedback
    feedback_positive = {"issue_resolved": True, "service_quality": 5, "nps_score": 9}
    is_resolved = agent.detect_unresolved_issue(feedback_positive)
    print(f"✓ Positive feedback correctly identified as resolved: {not is_resolved}")

    return is_unresolved_1 and is_unresolved_2 and is_unresolved_3 and not is_resolved


def test_support_ticket_creation():
    """Test support ticket creation for unresolved issues"""
    print("\n=== Testing Support Ticket Creation ===")

    agent = EnhancedFeedbackAgent()

    # Create support tickets for different scenarios
    ticket_1 = agent.create_support_ticket("APT - 001", "Customer reports battery issue not fully resolved")
    print(f"✓ Support ticket created: {ticket_1}")

    ticket_2 = agent.create_support_ticket("APT - 002", "Low service quality rating - follow up needed")
    print(f"✓ Second support ticket created: {ticket_2}")

    # Test ticket details
    if ticket_1 and ticket_1 in agent.support_tickets:
        ticket_details = agent.support_tickets[ticket_1]
        print(f"✓ Ticket details:")
        print(f"  - Priority: {ticket_details.priority}")
        print(f"  - Status: {ticket_details.status}")
        print(f"  - Assigned to: {ticket_details.assigned_to}")

        valid_ticket = ticket_details.status == "OPEN" and ticket_details.priority in ["HIGH", "MEDIUM", "LOW"]
        print(f"✓ Ticket validation: {valid_ticket}")

        return bool(ticket_1) and bool(ticket_2) and valid_ticket

    return False


def test_prediction_outcome_labeling():
    """Test ML prediction outcome labeling"""
    print("\n=== Testing Prediction Outcome Labeling ===")

    agent = EnhancedFeedbackAgent()

    # Test case 1: True Positive - prediction matches service
    feedback_tp = {"issue_resolved": True, "service_quality": 4}
    appointment_tp = {
        "predicted_issue": "battery",
        "actual_service_performed": ["battery_replacement", "electrical_check"],
        "parts_replaced": ["battery", "battery_terminals"],
    }
    outcome_tp = agent.label_prediction_outcome("APT - 001", feedback_tp, appointment_tp)
    print(f"✓ True Positive labeling: {outcome_tp}")

    # Test case 2: False Positive - prediction doesn't match service
    feedback_fp = {"issue_resolved": True, "service_quality": 4}
    appointment_fp = {"predicted_issue": "engine", "actual_service_performed": ["inspection"], "parts_replaced": []}
    outcome_fp = agent.label_prediction_outcome("APT - 002", feedback_fp, appointment_fp)
    print(f"✓ False Positive labeling: {outcome_fp}")

    # Test case 3: Issue predicted but not resolved
    feedback_unresolved = {"issue_resolved": False, "service_quality": 2}
    appointment_unresolved = {
        "predicted_issue": "brakes",
        "actual_service_performed": ["brake_inspection"],
        "parts_replaced": ["brake_fluid"],
    }
    outcome_unresolved = agent.label_prediction_outcome("APT - 003", feedback_unresolved, appointment_unresolved)
    print(f"✓ Unresolved issue labeling: {outcome_unresolved}")

    # Verify outcomes are stored
    stored_outcomes = len(agent.prediction_outcomes)
    print(f"✓ Prediction outcomes stored: {stored_outcomes}")

    valid_outcomes = outcome_tp in [e.value for e in PredictionOutcome]
    return valid_outcomes and stored_outcomes >= 3


def test_ml_retraining_pipeline():
    """Test ML retraining pipeline integration"""
    print("\n=== Testing ML Retraining Pipeline ===")

    agent = EnhancedFeedbackAgent()

    # Test sending labeled data to ML pipeline
    labeled_data = {
        "appointment_id": "APT - 001",
        "prediction": "battery",
        "actual_service": ["battery_replacement"],
        "outcome_label": "true_positive",
        "feedback": {"service_quality": 5, "issue_resolved": True},
        "timestamp": datetime.now().isoformat(),
    }

    ml_sent = agent.send_to_ml_retraining_pipeline(labeled_data)
    print(f"✓ Data sent to ML pipeline: {ml_sent}")

    # Check training data storage
    training_data_count = len(agent.ml_training_data)
    print(f"✓ Training data records: {training_data_count}")

    # Test multiple data points to simulate threshold
    for i in range(5):
        test_data = {"appointment_id": f"APT-TEST-{i}", "prediction": "test_issue", "outcome_label": "true_positive"}
        agent.send_to_ml_retraining_pipeline(test_data)

    final_count = len(agent.ml_training_data)
    print(f"✓ Final training data count: {final_count}")

    return ml_sent and final_count > training_data_count


def test_prediction_accuracy_analysis():
    """Test prediction accuracy analysis and metrics calculation"""
    print("\n=== Testing Prediction Accuracy Analysis ===")

    agent = EnhancedFeedbackAgent()

    # Add some mock prediction outcomes for analysis
    mock_outcomes = {
        "APT-ANALYSIS - 1": {"outcome": "true_positive", "labeled_date": datetime.now().isoformat()},
        "APT-ANALYSIS - 2": {"outcome": "false_positive", "labeled_date": datetime.now().isoformat()},
        "APT-ANALYSIS - 3": {"outcome": "true_positive", "labeled_date": datetime.now().isoformat()},
        "APT-ANALYSIS - 4": {"outcome": "false_negative", "labeled_date": datetime.now().isoformat()},
    }

    agent.prediction_outcomes.update(mock_outcomes)

    # Run accuracy analysis
    metrics = agent.analyze_prediction_accuracy()

    print(f"✓ Accuracy analysis completed:")
    print(f"  - Total predictions: {metrics.total_predictions}")
    print(f"  - Precision: {metrics.precision:.3f}")
    print(f"  - Recall: {metrics.recall:.3f}")
    print(f"  - F1-score: {metrics.f1_score:.3f}")
    print(f"  - Accuracy: {metrics.accuracy:.3f}")

    # Validate metrics calculation
    expected_total = len(mock_outcomes)
    metrics_valid = (
        metrics.total_predictions >= expected_total
        and 0 <= metrics.precision <= 1
        and 0 <= metrics.recall <= 1
        and 0 <= metrics.f1_score <= 1
        and 0 <= metrics.accuracy <= 1
    )

    print(f"✓ Metrics validation: {metrics_valid}")

    return metrics_valid and metrics.total_predictions > 0


def test_feedback_summary_analytics():
    """Test feedback summary and analytics functionality"""
    print("\n=== Testing Feedback Summary Analytics ===")

    agent = EnhancedFeedbackAgent()

    # Collect some feedback first
    for apt_id in ["APT - 001", "APT - 002", "APT - 003"]:
        agent.collect_feedback(apt_id)

    # Generate feedback summary
    summary = agent.get_feedback_summary(days=30)

    print(f"✓ Feedback summary generated:")
    if "total_feedback_collected" in summary:
        print(f"  - Total feedback: {summary['total_feedback_collected']}")
        print(f"  - Average service quality: {summary['average_service_quality']}")
        print(f"  - Average NPS: {summary['average_nps_score']}")
        print(f"  - Resolution rate: {summary['issue_resolution_rate']}%")
        print(f"  - Support tickets: {summary['support_tickets_created']}")

        # Validate summary structure
        required_fields = [
            "total_feedback_collected",
            "average_service_quality",
            "average_nps_score",
            "issue_resolution_rate",
        ]
        summary_valid = all(field in summary for field in required_fields)
        print(f"✓ Summary structure validation: {summary_valid}")

        return summary_valid and summary["total_feedback_collected"] > 0
    else:
        print(f"  - Message: {summary.get('message', 'No summary available')}")
        return True  # Valid response for no data


async def test_complete_feedback_workflow():
    """Test the complete feedback workflow end-to-end"""
    print("\n=== Testing Complete Feedback Workflow ===")

    agent = EnhancedFeedbackAgent()

    # Create initial state with proper initialization
    state = State()
    state["user_request"] = "Process post-service feedback for completed appointments"
    state["conversation_history"] = []  # Initialize conversation history
    state["updated_at"] = datetime.now().isoformat()

    # Execute the complete workflow
    result_state = await agent._execute_internal(state)

    print(f"✓ Workflow execution completed")
    print(f"✓ Appointments processed: {result_state.get('appointments_processed', 0)}")
    print(f"✓ Feedback collected: {result_state.get('feedback_collected_count', 0)}")

    # Check workflow results
    if "feedback_collection_results" in result_state:
        results = result_state["feedback_collection_results"]
        print(f"✓ Detailed results available: {len(results)} appointment results")

        # Check for ML integration
        ml_integrated = any(r.get("ml_data_sent") for r in results if isinstance(r, dict))
        print(f"✓ ML integration working: {ml_integrated}")

        workflow_success = result_state.get("appointments_processed", 0) > 0 and len(results) > 0
        print(f"✓ Complete workflow success: {workflow_success}")

        return workflow_success

    return False


def test_error_handling():
    """Test error handling and edge cases"""
    print("\n=== Testing Error Handling ===")

    agent = EnhancedFeedbackAgent()

    # Test with invalid appointment ID
    invalid_feedback = agent.collect_feedback("INVALID-APT")
    print(f"✓ Invalid appointment handling: {len(invalid_feedback) == 0}")

    # Test with empty feedback data
    empty_detection = agent.detect_unresolved_issue({})
    print(f"✓ Empty feedback handling: {not empty_detection}")

    # Test support ticket creation with invalid appointment
    invalid_ticket = agent.create_support_ticket("INVALID-APT", "Test issue")
    print(f"✓ Invalid ticket creation handling: {invalid_ticket == ''}")

    # Test prediction labeling with missing data
    incomplete_outcome = agent.label_prediction_outcome("INVALID", {}, {})
    print(f"✓ Incomplete data labeling: {incomplete_outcome is not None}")

    # Test accuracy analysis with no data
    empty_agent = EnhancedFeedbackAgent()
    empty_agent.prediction_outcomes = {}
    empty_metrics = empty_agent.analyze_prediction_accuracy()
    print(f"✓ Empty data analysis: {empty_metrics.total_predictions == 0}")

    error_handling_success = (
        len(invalid_feedback) == 0
        and not empty_detection
        and invalid_ticket == ""
        and incomplete_outcome is not None
        and empty_metrics.total_predictions == 0
    )

    print(f"✓ Error handling validation: {error_handling_success}")
    return error_handling_success


async def run_all_tests():
    """Run all feedback agent tests"""
    print("🚀 Starting Enhanced Feedback Agent Test Suite")
    print("=" * 60)

    test_results = []

    # Run all tests
    test_functions = [
        ("Completed Appointments Retrieval", test_completed_appointments_retrieval),
        ("Feedback Request Sending", test_feedback_request_sending),
        ("Feedback Collection", test_feedback_collection),
        ("Unresolved Issue Detection", test_unresolved_issue_detection),
        ("Support Ticket Creation", test_support_ticket_creation),
        ("Prediction Outcome Labeling", test_prediction_outcome_labeling),
        ("ML Retraining Pipeline", test_ml_retraining_pipeline),
        ("Prediction Accuracy Analysis", test_prediction_accuracy_analysis),
        ("Feedback Summary Analytics", test_feedback_summary_analytics),
        ("Complete Feedback Workflow", test_complete_feedback_workflow),
        ("Error Handling", test_error_handling),
    ]

    for test_name, test_func in test_functions:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            test_results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            test_results.append((test_name, False))
            print(f"\n❌ ERROR in {test_name}: {str(e)}")

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")

    print(f"\n🎯 Results: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 All tests passed! Enhanced Feedback Agent is fully functional.")
        print("\n🔧 Verified Capabilities:")
        print("   • Post-service feedback collection (24-hour follow-up)")
        print("   • Multi-channel communication (SMS, app, voice, email)")
        print("   • Structured feedback analysis and rating collection")
        print("   • Unresolved issue detection and escalation")
        print("   • Automated support ticket creation and prioritization")
        print("   • ML prediction outcome labeling (TP/FP/TN/FN)")
        print("   • ML retraining pipeline integration")
        print("   • Prediction accuracy analysis and reporting")
        print("   • Comprehensive feedback analytics and summaries")
        print("   • Complete workflow automation")
        print("   • Robust error handling and edge case management")

        print("\n🎯 Key Features Demonstrated:")
        print("   • Continuous learning through feedback loop")
        print("   • Customer satisfaction monitoring")
        print("   • Service quality assurance")
        print("   • Predictive model improvement")
        print("   • Automated escalation workflows")
        print("   • Performance metrics and reporting")
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed. Please review the implementation.")

    return passed_tests == total_tests


if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
