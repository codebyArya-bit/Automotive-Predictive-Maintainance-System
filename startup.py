#!/usr/bin/env python3
"""
Startup Script for Automotive AI System
Provides easy initialization, testing, and management of the system
"""

import sys
import time
import subprocess
import requests
from datetime import datetime
from pathlib import Path


class SystemStartup:
    """System startup and management utility"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.api_url = "http://localhost:8000"
        self.server_process = None

    def print_banner(self):
        """Print system banner"""
        print("=" * 60)
        print("🚗 AUTOMOTIVE AI PREDICTIVE MAINTENANCE SYSTEM")
        print("   Master Agent Orchestration with LangGraph")
        print("=" * 60)
        print(f"📁 Working Directory: {self.base_dir}")
        print(f"🌐 API URL: {self.api_url}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("\n🔍 Checking Dependencies...")

        required_packages = ["fastapi", "uvicorn", "pydantic", "requests", "structlog", "langgraph", "langchain"]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package} (missing)")
                missing_packages.append(package)

        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print("   Run: pip install -r requirements.txt")
            return False

        print("✅ All dependencies satisfied")
        return True

    def check_configuration(self):
        """Check system configuration"""
        print("\n🔧 Checking Configuration...")

        config_files = ["config.py", "master_agent.py", "api_server.py"]

        for config_file in config_files:
            file_path = self.base_dir / config_file
            if file_path.exists():
                print(f"  ✅ {config_file}")
            else:
                print(f"  ❌ {config_file} (missing)")
                return False

        # Check agents directory
        agents_dir = self.base_dir / "agents"
        if agents_dir.exists():
            agent_files = list(agents_dir.glob("*.py"))
            print(f"  ✅ agents/ ({len(agent_files)} agent files)")
        else:
            print("  ❌ agents/ directory (missing)")
            return False

        print("✅ Configuration check passed")
        return True

    def start_api_server(self):
        """Start the API server"""
        print("\n🚀 Starting API Server...")

        try:
            # Check if server is already running
            try:
                response = requests.get(f"{self.api_url}/health", timeout=2)
                if response.status_code == 200:
                    print("  ✅ API Server already running")
                    return True
            except requests.exceptions.RequestException:
                pass

            # Start the server
            print("  🔄 Launching API server...")

            # Use subprocess to start the server
            cmd = [sys.executable, "api_server.py"]
            self.server_process = subprocess.Popen(
                cmd, cwd=self.base_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Wait for server to start
            print("  ⏳ Waiting for server to initialize...")

            for attempt in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{self.api_url}/health", timeout=1)
                    if response.status_code == 200:
                        print("  ✅ API Server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    pass

                time.sleep(1)
                print(f"    Attempt {attempt + 1}/30...")

            print("  ❌ Failed to start API server")
            return False

        except Exception as e:
            print(f"  ❌ Error starting server: {e}")
            return False

    def run_health_check(self):
        """Run system health check"""
        print("\n🏥 Running Health Check...")

        try:
            response = requests.get(f"{self.api_url}/api/v1/health", timeout=10)

            if response.status_code == 200:
                health_data = response.json()
                print(f"  ✅ System Health: {health_data.get('overall_health', 'unknown')}")

                # Show any issues
                issues = health_data.get("issues", [])
                if issues:
                    print("  ⚠️  Issues found:")
                    for issue in issues:
                        print(f"    - {issue}")
                else:
                    print("  ✅ No issues detected")

                return True
            else:
                print(f"  ❌ Health check failed: HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"  ❌ Health check error: {e}")
            return False

    def run_demo_test(self):
        """Run a quick demo test"""
        print("\n🧪 Running Demo Test...")

        try:
            # Test data
            test_data = {
                "vehicle_id": "VIN123456789STARTUP",
                "telemetry_data": {
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
            }

            response = requests.post(
                f"{self.api_url}/api/v1/process-vehicle",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Demo test successful")
                print(f"    Vehicle ID: {result.get('vehicle_id', 'N/A')}")
                print(f"    Processing Time: {result.get('processing_time', 0):.2f}s")
                print(f"    Success: {result.get('success', False)}")
                return True
            else:
                print(f"  ❌ Demo test failed: HTTP {response.status_code}")
                print(f"    Response: {response.text}")
                return False

        except Exception as e:
            print(f"  ❌ Demo test error: {e}")
            return False

    def show_endpoints(self):
        """Show available API endpoints"""
        print("\n📚 Available API Endpoints:")
        print(f"  🌐 API Documentation: {self.api_url}/docs")
        print(f"  📖 ReDoc Documentation: {self.api_url}/redoc")
        print(f"  🏥 Health Check: {self.api_url}/api/v1/health")
        print(f"  🚗 Process Vehicle: {self.api_url}/api/v1/process-vehicle")
        print(f"  📊 Dashboard: {self.api_url}/api/v1/dashboard")
        print(f"  🔧 Circuit Breakers: {self.api_url}/api/v1/circuit-breakers")
        print(f"  🎯 Demo: {self.api_url}/api/v1/demo")

    def cleanup(self):
        """Cleanup resources"""
        if self.server_process:
            print("\n🛑 Stopping API server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("  ✅ Server stopped")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("  ⚠️  Server force killed")

    def run_full_startup(self):
        """Run complete system startup sequence"""
        try:
            self.print_banner()

            # Check dependencies
            if not self.check_dependencies():
                return False

            # Check configuration
            if not self.check_configuration():
                return False

            # Start API server
            if not self.start_api_server():
                return False

            # Run health check
            if not self.run_health_check():
                print("  ⚠️  Health check failed, but continuing...")

            # Run demo test
            if not self.run_demo_test():
                print("  ⚠️  Demo test failed, but system is running...")

            # Show endpoints
            self.show_endpoints()

            print("\n🎉 System startup completed successfully!")
            print("\n💡 Tips:")
            print("  - Visit /docs for interactive API documentation")
            print("  - Use Ctrl+C to stop the system")
            print("  - Check logs for detailed information")

            return True

        except KeyboardInterrupt:
            print("\n\n⏹️  Startup interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Startup failed: {e}")
            return False


def main():
    """Main startup function"""
    startup = SystemStartup()

    try:
        success = startup.run_full_startup()

        if success:
            print("\n⏳ System is running. Press Ctrl+C to stop...")

            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n🛑 Shutting down system...")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        startup.cleanup()
        print("👋 Goodbye!")


if __name__ == "__main__":
    main()
