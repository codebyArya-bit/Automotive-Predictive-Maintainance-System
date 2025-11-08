#!/usr/bin/env python3
"""
Comprehensive API Test Script for Automotive AI System
Tests all endpoints and validates error handling
"""

import requests
import time
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000/api/v1"


def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False


def test_process_vehicle_endpoint():
    """Test the vehicle processing endpoint with valid data"""
    print("\n🔍 Testing Process Vehicle Endpoint...")

    # Test data for different scenarios
    test_cases = [
        {
            "name": "Healthy Vehicle",
            "data": {
                "vehicle_id": "VIN123456789HEALTHY",
                "telemetry": {
                    "engine_temperature": 85,
                    "oil_pressure": 45,
                    "oil_life_remaining": 75,
                    "tire_pressure_fl": 32,
                    "tire_pressure_fr": 32,
                    "tire_pressure_rl": 30,
                    "tire_pressure_rr": 30,
                    "battery_voltage": 12.6,
                    "brake_pad_thickness": 8,
                    "coolant_level": 90,
                    "mileage": 25000,
                    "last_service": "2024 - 08 - 15",
                    "timestamp": datetime.now().isoformat(),
                },
            },
        },
        {
            "name": "Critical Vehicle",
            "data": {
                "vehicle_id": "VIN987654321CRITICAL",
                "telemetry": {
                    "engine_temperature": 120,
                    "oil_pressure": 15,
                    "oil_life_remaining": 5,
                    "tire_pressure_fl": 20,
                    "tire_pressure_fr": 22,
                    "tire_pressure_rl": 18,
                    "tire_pressure_rr": 19,
                    "battery_voltage": 11.8,
                    "brake_pad_thickness": 2,
                    "coolant_level": 30,
                    "mileage": 85000,
                    "last_service": "2023 - 12 - 01",
                    "timestamp": datetime.now().isoformat(),
                },
            },
        },
    ]

    success_count = 0
    for test_case in test_cases:
        print(f"\n  Testing: {test_case['name']}")
        try:
            response = requests.post(
                f"{BASE_URL}/process-vehicle",
                json={"vehicle_id": test_case["data"]["vehicle_id"], "telemetry_data": test_case["data"]["telemetry"]},
                headers={"Content-Type": "application/json"},
            )
            print(f"  Status Code: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"  Vehicle ID: {result.get('vehicle_id', 'N/A')}")
                print(f"  Status: {result.get('status', 'N/A')}")
                print(f"  Priority: {result.get('priority', 'N/A')}")
                print(f"  Agents Executed: {result.get('total_agents_executed', 0)}")
                success_count += 1
            else:
                print(f"  Error: {response.text}")

        except Exception as e:
            print(f"  ❌ Test failed: {e}")

    return success_count == len(test_cases)


def test_invalid_data_handling():
    """Test API error handling with invalid data"""
    print("\n🔍 Testing Invalid Data Handling...")

    invalid_test_cases = [
        {
            "name": "Missing vehicle_id",
            "data": {"telemetry": {"engine_temperature": 85, "timestamp": datetime.now().isoformat()}},
        },
        {"name": "Missing telemetry", "data": {"vehicle_id": "VIN123456789TEST"}},
        {"name": "Invalid telemetry format", "data": {"vehicle_id": "VIN123456789TEST", "telemetry": "invalid_format"}},
    ]

    success_count = 0
    for test_case in invalid_test_cases:
        print(f"\n  Testing: {test_case['name']}")
        try:
            response = requests.post(
                f"{BASE_URL}/process-vehicle", json=test_case["data"], headers={"Content-Type": "application/json"}
            )
            print(f"  Status Code: {response.status_code}")

            # We expect 4xx status codes for invalid data
            if 400 <= response.status_code < 500:
                print(f"  ✅ Properly handled invalid data")
                success_count += 1
            else:
                print(f"  ❌ Unexpected status code for invalid data")

        except Exception as e:
            print(f"  ❌ Test failed: {e}")

    return success_count == len(invalid_test_cases)


def test_get_vehicle_status():
    """Test the vehicle status retrieval endpoint"""
    print("\n🔍 Testing Get Vehicle Status Endpoint...")

    # First process a vehicle to have data to retrieve
    vehicle_id = "VIN123456789STATUS"
    telemetry_data = {
        "vehicle_id": vehicle_id,
        "telemetry_data": {
            "engine_temperature": 90,
            "oil_pressure": 40,
            "oil_life_remaining": 60,
            "tire_pressure_fl": 32,
            "tire_pressure_fr": 32,
            "tire_pressure_rl": 30,
            "tire_pressure_rr": 30,
            "battery_voltage": 12.4,
            "brake_pad_thickness": 6,
            "coolant_level": 80,
            "mileage": 45000,
            "last_service": "2024 - 06 - 01",
            "timestamp": datetime.now().isoformat(),
        },
    }

    try:
        # Process the vehicle first
        process_response = requests.post(
            f"{BASE_URL}/process-vehicle", json=telemetry_data, headers={"Content-Type": "application/json"}
        )

        if process_response.status_code == 200:
            print("  ✅ Vehicle processed successfully")

            # Now try to get the status
            status_response = requests.get(f"{BASE_URL}/vehicle/{vehicle_id}/status")
            print(f"  Status Code: {status_response.status_code}")

            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"  Vehicle ID: {status_data.get('vehicle_id', 'N/A')}")
                print(f"  Status: {status_data.get('status', 'N/A')}")
                print(f"  Priority: {status_data.get('priority', 'N/A')}")
                return True
            else:
                print(f"  ❌ Failed to get status: {status_response.text}")
                return False
        else:
            print(f"  ❌ Failed to process vehicle: {process_response.text}")
            return False

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False


def test_nonexistent_vehicle_status():
    """Test getting status for a non-existent vehicle"""
    print("\n🔍 Testing Non-existent Vehicle Status...")

    try:
        response = requests.get(f"{BASE_URL}/vehicle/NONEXISTENT123/status")
        print(f"  Status Code: {response.status_code}")

        # We expect a 404 for non-existent vehicles
        if response.status_code == 404:
            print("  ✅ Properly handled non-existent vehicle")
            return True
        else:
            print(f"  ❌ Unexpected status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False


def run_comprehensive_tests():
    """Run all API tests"""
    print("🚀 Starting Comprehensive API Tests")
    print("=" * 50)

    test_results = []

    # Run all tests
    test_results.append(("Health Endpoint", test_health_endpoint()))
    test_results.append(("Process Vehicle", test_process_vehicle_endpoint()))
    test_results.append(("Invalid Data Handling", test_invalid_data_handling()))

    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1

    print(f"\n📈 Overall Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the API implementation.")

    return passed == total


if __name__ == "__main__":
    # Wait a moment for the server to be ready
    print("⏳ Waiting for API server to be ready...")
    time.sleep(2)

    success = run_comprehensive_tests()
    exit(0 if success else 1)
