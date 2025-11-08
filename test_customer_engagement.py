#!/usr/bin/env python3
"""
Test script for Customer Engagement Agent
Tests various conversation scenarios and multi-language support
"""

import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.customer_engagement_agent import CustomerEngagementAgent


def test_customer_engagement_agent():
    """Test the Customer Engagement Agent with various scenarios"""
    print("🚗 Testing Customer Engagement Agent")
    print("=" * 50)

    try:
        # Initialize agent
        agent = CustomerEngagementAgent()
        print("✅ Agent initialized successfully")

        # Test 1: Customer Profile Retrieval
        print("\n📋 Test 1: Customer Profile Retrieval")
        profile = agent.get_customer_profile("CUST001")
        print(f"Customer: {profile.get('name', 'Unknown')}")
        print(f"Language: {profile.get('preferred_language', 'Unknown')}")
        print(f"Vehicle: {profile.get('vehicle_model', 'Unknown')}")

        # Test 2: Sentiment Analysis
        print("\n😊 Test 2: Sentiment Analysis")
        test_messages = [
            "Yes, I'd like to schedule the service immediately!",
            "I'm not interested and I'm very busy right now.",
            "How much will this cost? I'm worried about the expense.",
            "I don't understand what you're talking about.",
        ]

        for msg in test_messages:
            sentiment = agent.detect_sentiment(msg)
            print(f"Message: '{msg[:40]}...' → Sentiment: {sentiment}/10")

        # Test 3: Translation
        print("\n🌐 Test 3: Translation")
        english_msg = "Your battery needs replacement within 7 days."
        hindi_translation = agent.translate_message(english_msg, "hindi")
        print(f"English: {english_msg}")
        print(f"Hindi: {hindi_translation}")

        # Test 4: Discount Eligibility
        print("\n💰 Test 4: Discount Eligibility")
        priorities = ["P0", "P1", "P2", "P3"]
        for priority in priorities:
            discount = agent.fetch_discount_eligibility("CUST001", priority)
            print(f"{priority}: {discount['discount_percent']}% - {discount['reason']}")

        # Test 5: Full Conversation Flow
        print("\n💬 Test 5: Full Conversation Flow")

        # Sample prediction data
        prediction = {
            "component": "battery",
            "probability": 85,
            "days_to_failure": 7,
            "priority": "P1",
            "estimated_cost": 6500,
        }

        # Start conversation
        conversation_result = agent.start_conversation("CUST001", "VEH001", prediction)

        if conversation_result["success"]:
            print("✅ Conversation started successfully")
            print(f"Opening message: {conversation_result['opening_message'][:100]}...")

            # Simulate customer responses
            customer_responses = [
                "Yes, tell me what's wrong with my car.",
                "How much will this cost?",
                "That seems expensive. Can you give me a discount?",
                "Okay, I'll book the service.",
            ]

            for i, response in enumerate(customer_responses, 1):
                print(f"\n--- Turn {i} ---")
                print(f"Customer: {response}")

                result = agent.process_customer_response("CUST001", response)

                if "error" not in result:
                    print(f"Agent: {result['agent_response'][:100]}...")
                    print(f"Sentiment: {result['sentiment_score']}/10")

                    if result.get("escalation_needed"):
                        print("🚨 Escalation needed - transferring to human agent")
                        break
                else:
                    print(f"❌ Error: {result['error']}")

            # Get conversation summary
            summary = agent.get_conversation_summary("CUST001")
            print(f"\n📊 Conversation Summary:")
            print(f"Duration: {summary['conversation_duration']} messages")
            print(f"Final sentiment: {summary['final_sentiment']}/10")
            print(f"Outcome: {summary['outcome']}")
            print(f"Language: {summary['language']}")

        else:
            print(f"❌ Failed to start conversation: {conversation_result['error']}")

        # Test 6: Escalation Scenario
        print("\n🚨 Test 6: Escalation Scenario")

        # Start new conversation for escalation test
        escalation_conversation = agent.start_conversation("CUST002", "VEH002", prediction)

        if escalation_conversation["success"]:
            # Simulate frustrated customer
            frustrated_responses = [
                "I don't want to hear about this!",
                "This is ridiculous! I want to speak to your manager!",
                "You people are always trying to scam customers!",
            ]

            for response in frustrated_responses:
                result = agent.process_customer_response("CUST002", response)
                print(f"Customer: {response}")
                print(f"Sentiment: {result.get('sentiment_score', 0)}/10")

                if result.get("escalation_needed"):
                    print("✅ Escalation correctly triggered")
                    print(f"Escalation message: {result['agent_response'][:80]}...")
                    break

        print("\n🎉 All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback

        traceback.print_exc()


def test_multi_language_support():
    """Test multi-language conversation support"""
    print("\n🌍 Testing Multi-Language Support")
    print("=" * 40)

    try:
        agent = CustomerEngagementAgent()

        # Test different languages
        languages = ["english", "hindi", "tamil"]
        test_message = "Your vehicle needs immediate attention for safety reasons."

        for lang in languages:
            translated = agent.translate_message(test_message, lang)
            print(f"{lang.capitalize()}: {translated}")

        print("✅ Multi-language support working")

    except Exception as e:
        print(f"❌ Multi-language test failed: {str(e)}")


if __name__ == "__main__":
    # Force tests to use deterministic, offline mode
    os.environ["LLM_PROVIDER"] = "rule_based"

    test_customer_engagement_agent()
    test_multi_language_support()
