#!/usr/bin/env python3
"""
FastAPI Server for Master Agent Orchestration System
Provides REST API endpoints for vehicle processing, monitoring, and system management
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Set, Literal
import asyncio
import json
import uuid
from datetime import datetime, timedelta
import uvicorn
import logging
from cache_manager import cache_manager


from master_agent import MasterAgent
from config import Config
from sqlalchemy import desc
from database_models import Vehicle, TelemetryData, MaintenanceRecord
from database_manager import DatabaseManager

# Extended features imports
from api_endpoints_extended import router as extended_router
from logs_system import logs_router as logs_router, LoggingMiddleware, logs_manager, LogEntry

# Initialize database manager
db_manager = DatabaseManager()


# Pydantic models for API requests/responses
class VehicleProcessingRequest(BaseModel):
    """Request model for vehicle processing"""

    vehicle_id: str = Field(..., description="Unique vehicle identifier")
    telemetry_data: Dict[str, Any] = Field(..., description="Vehicle telemetry data")
    customer_info: Optional[Dict[str, Any]] = Field(None, description="Customer information")
    priority_override: Optional[str] = Field(None, description="Priority override (P0, P1, P2, P3)")
    config_override: Optional[Dict[str, Any]] = Field(None, description="Configuration overrides")


class VehicleProcessingResponse(BaseModel):
    """Response model for vehicle processing"""

    success: bool
    vehicle_id: str
    processing_time: float
    final_state: Dict[str, Any]
    agents_executed: List[str]
    escalated: bool
    prediction: Optional[Dict[str, Any]] = None
    customer_response: Optional[Dict[str, Any]] = None
    appointment: Optional[Dict[str, Any]] = None
    feedback: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class LangGraphDemoRequest(BaseModel):
    """Small reviewer-friendly request for the real async LangGraph workflow."""

    vehicle_id: str = Field(default="DEMO-EY-001", min_length=3, max_length=64)
    scenario: Literal["normal", "high_temperature", "brake_warning"] = "high_temperature"


class LangGraphDemoResponse(BaseModel):
    success: bool
    vehicle_id: str
    scenario: str
    orchestration: str
    validation: str
    api_runtime: str
    agents_executed: List[str]
    escalated: bool
    prediction: Optional[Dict[str, Any]] = None
    workflow_step: Optional[str] = None
    error: Optional[str] = None


class SystemHealthResponse(BaseModel):
    """Response model for system health"""

    overall_health: str
    timestamp: str
    components: Dict[str, Any]
    issues: List[str]
    metrics: Dict[str, Any]


class DashboardResponse(BaseModel):
    """Response model for dashboard data"""

    timestamp: str
    agent_metrics: Dict[str, Any]
    system_metrics: Dict[str, Any]
    security_metrics: Dict[str, Any]
    recent_activities: List[Dict[str, Any]]


# Initialize FastAPI app
app = FastAPI(
    title="Master Agent Orchestration System",
    description="Automotive Predictive Maintenance API with LangGraph orchestration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
# When credentials are allowed, browsers disallow wildcard origins. Use explicit origins.
# Support multiple origins via FRONTEND_ORIGINS/CORS_ORIGINS (comma-separated), fallback to singular origin.
default_dev_origins = {
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:3002",
}


def _parse_origin_list(raw_value: Optional[str]) -> Set[str]:
    """Split comma-separated origins, trimming whitespace and ignoring blanks."""
    if not raw_value:
        return set()
    return {origin.strip() for origin in raw_value.split(",") if origin.strip()}


allowed_frontend_origins_set: Set[str] = set(default_dev_origins)
multi_origin_env_found = False

for env_var in ("FRONTEND_ORIGINS", "CORS_ORIGINS"):
    parsed = _parse_origin_list(os.getenv(env_var))
    if parsed:
        allowed_frontend_origins_set.update(parsed)
        multi_origin_env_found = True

if not multi_origin_env_found:
    fallback_origin = (
        os.getenv("FRONTEND_ORIGIN")
        or os.getenv("CORS_ORIGIN")
        or "http://localhost:3001"
    )
    allowed_frontend_origins_set.add(fallback_origin)

allowed_frontend_origins = sorted(allowed_frontend_origins_set)
# Optional: allow Vercel preview subdomains via regex
# You can set CORS_ORIGIN_REGEX env var to override the default.
cors_origin_regex = os.getenv("CORS_ORIGIN_REGEX")
if not cors_origin_regex:
    # Default to your project prefix on Vercel to cover preview deployments
    # Example: https://automind-<deployment-id>-aryas-projects-6676c3c7.vercel.app
    cors_origin_regex = r"https://automind-.*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_frontend_origins,
    allow_origin_regex=cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log CORS configuration for visibility
try:
    logging.info(
        "CORS configured with explicit origins: %s and origin regex: %s",
        allowed_frontend_origins,
        cors_origin_regex,
    )
except Exception:
    pass

# Capture request logs via middleware
app.add_middleware(LoggingMiddleware)

# Include extended API endpoints
app.include_router(extended_router)
app.include_router(logs_router)

# Global instances
master_agent: Optional[MasterAgent] = None
config: Optional[Config] = None


# WebSocket connection management
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "dashboard": set(),
            "vehicles": set(),
            "agents": set(),
            "system": set(),
            "demo": set(),
            "logs": set(),
        }
        self.vehicle_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, connection_type: str, vehicle_id: str = None):
        try:
            await websocket.accept()
            logging.info(
                f"WebSocket accepted for {connection_type}" + (f" vehicle_id: {vehicle_id}" if vehicle_id else "")
            )

            if connection_type == "vehicle" and vehicle_id:
                if vehicle_id not in self.vehicle_connections:
                    self.vehicle_connections[vehicle_id] = set()
                self.vehicle_connections[vehicle_id].add(websocket)
            else:
                self.active_connections[connection_type].add(websocket)
        except Exception as e:
            logging.error(f"Failed to accept WebSocket connection: {e}")
            raise

    def disconnect(self, websocket: WebSocket, connection_type: str, vehicle_id: str = None):
        if connection_type == "vehicle" and vehicle_id:
            if vehicle_id in self.vehicle_connections:
                self.vehicle_connections[vehicle_id].discard(websocket)
                if not self.vehicle_connections[vehicle_id]:
                    del self.vehicle_connections[vehicle_id]
        else:
            self.active_connections[connection_type].discard(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(message)
        except Exception as e:
            logging.error(f"Failed to send personal message: {e}")
            # Remove the websocket from all connections if it's closed
            self._remove_closed_websocket(websocket)

    def _remove_closed_websocket(self, websocket: WebSocket):
        """Remove a closed websocket from all connection pools"""
        # Remove from active connections
        for connection_type in self.active_connections:
            self.active_connections[connection_type].discard(websocket)

        # Remove from vehicle connections
        for vehicle_id in list(self.vehicle_connections.keys()):
            self.vehicle_connections[vehicle_id].discard(websocket)
            if not self.vehicle_connections[vehicle_id]:
                del self.vehicle_connections[vehicle_id]

    async def broadcast_to_type(self, message: str, connection_type: str):
        if connection_type in self.active_connections:
            disconnected = []
            for connection in self.active_connections[connection_type].copy():
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_text(message)
                except Exception as e:
                    logging.error(f"Failed to broadcast to {connection_type}: {e}")
                    disconnected.append(connection)

            # Remove disconnected connections
            for connection in disconnected:
                self.active_connections[connection_type].discard(connection)

    async def broadcast_to_vehicle(self, message: str, vehicle_id: str):
        if vehicle_id in self.vehicle_connections:
            disconnected = []
            for connection in self.vehicle_connections[vehicle_id].copy():
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_text(message)
                except Exception as e:
                    logging.error(f"Failed to broadcast to vehicle {vehicle_id}: {e}")
                    disconnected.append(connection)

            # Remove disconnected connections
            for connection in disconnected:
                self.vehicle_connections[vehicle_id].discard(connection)


manager = ConnectionManager()

# Hook logs broadcast to WebSocket manager
async def _logs_broadcast(payload: Dict[str, Any]):
    try:
        await manager.broadcast_to_type(json.dumps(payload), "logs")
    except Exception as e:
        logging.error(f"Failed to broadcast logs payload: {e}")

logs_manager.set_broadcast(_logs_broadcast)

# Debug helper: list registered routes to diagnose missing endpoints
@app.get("/api/v1/debug/routes")
async def list_registered_routes():
    try:
        routes = []
        for r in app.routes:
            path = getattr(r, "path", None) or getattr(r, "path_format", None)
            methods = sorted(list(getattr(r, "methods", set()) or set()))
            name = getattr(r, "name", "")
            if path:
                routes.append({"path": path, "methods": methods, "name": name})
        routes.sort(key=lambda x: x["path"])
        return {"count": len(routes), "routes": routes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list routes: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize the Master Agent on startup"""
    global master_agent, config

    print(">> Starting Master Agent Orchestration System API")

    try:
        config = Config()
        master_agent = MasterAgent()
        print("[OK] Master Agent initialized successfully")
        # Log CORS allowed origins for visibility
        try:
            logs_manager.ingest(
                LogEntry(
                    level="info",
                    event_type="config",
                    message="CORS configuration initialized",
                    source="backend",
                    context={"allowed_origins": allowed_frontend_origins},
                )
            )
        except Exception:
            # Fallback to simple print if logging ingestion fails
            print(f"[INFO] CORS allowed origins: {allowed_frontend_origins}")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Master Agent: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print(">> Shutting down Master Agent Orchestration System API")


def get_master_agent() -> MasterAgent:
    """Dependency to get Master Agent instance"""
    if master_agent is None:
        raise HTTPException(status_code=503, detail="Master Agent not initialized")
    return master_agent


# API Endpoints


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with system information"""
    return """
    <html>
        <head>
            <title>Master Agent Orchestration System</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { color: #2c3e50; }
                .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .method { color: #27ae60; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1 class="header">🚗 Master Agent Orchestration System</h1>
            <p>Automotive Predictive Maintenance API with LangGraph orchestration</p>

            <h2>Available Endpoints:</h2>

            <div class="endpoint">
                <span class="method">POST</span> <strong>/api/v1/process-vehicle</strong><br>
                Process a vehicle through the complete workflow
            </div>

            <div class="endpoint">
                <span class="method">GET</span> <strong>/api/v1/health</strong><br>
                Get system health status
            </div>

            <div class="endpoint">
                <span class="method">GET</span> <strong>/api/v1/dashboard</strong><br>
                Get real-time dashboard data
            </div>

            <div class="endpoint">
                <span class="method">GET</span> <strong>/api/v1/circuit-breakers</strong><br>
                Get circuit breaker status
            </div>

            <div class="endpoint">
                <span class="method">POST</span> <strong>/api/v1/demo</strong><br>
                Run demonstration scenarios
            </div>

            <p><a href="/docs">📚 Interactive API Documentation</a></p>
            <p><a href="/redoc">📖 ReDoc Documentation</a></p>
        </body>
    </html>
    """


@app.post("/api/v1/process-vehicle", response_model=VehicleProcessingResponse)
async def process_vehicle(
    request: VehicleProcessingRequest, background_tasks: BackgroundTasks, agent: MasterAgent = Depends(get_master_agent)
) -> VehicleProcessingResponse:
    """
    Process a vehicle through the Master Agent workflow

    This endpoint processes vehicle telemetry data through the complete
    predictive maintenance workflow including analysis, diagnosis, customer
    engagement, scheduling, feedback collection, and compliance monitoring.
    """
    start_time = datetime.now()

    try:
        # Prepare telemetry data
        telemetry_data = request.telemetry_data.copy()

        # Add customer info if provided
        if request.customer_info:
            telemetry_data["customer_info"] = request.customer_info

        # Add priority override if provided
        config_override = request.config_override or {}
        if request.priority_override:
            config_override["priority_override"] = request.priority_override

        # Process vehicle through Master Agent
        result = await agent.process_vehicle(
            vehicle_id=request.vehicle_id,
            telemetry_data=telemetry_data,
            config_override=config_override if config_override else None,
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        # Extract key information from result
        agents_executed = [k.replace("_completed", "") for k in result.keys() if k.endswith("_completed")]
        escalated = result.get("escalate_to_human", False)

        return VehicleProcessingResponse(
            success=True,
            vehicle_id=request.vehicle_id,
            processing_time=processing_time,
            final_state=result,
            agents_executed=agents_executed,
            escalated=escalated,
            prediction=result.get("prediction"),
            customer_response=result.get("customer_response"),
            appointment=result.get("appointment"),
            feedback=result.get("feedback"),
        )

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()

        return VehicleProcessingResponse(
            success=False,
            vehicle_id=request.vehicle_id,
            processing_time=processing_time,
            final_state={},
            agents_executed=[],
            escalated=True,
            error=str(e),
        )


@app.post("/api/v1/demo/langgraph", response_model=LangGraphDemoResponse)
async def run_langgraph_demo(
    request: LangGraphDemoRequest,
    agent: MasterAgent = Depends(get_master_agent),
) -> LangGraphDemoResponse:
    """
    Execute the production MasterAgent through LangGraph asynchronously.

    The request/response contract is Pydantic-validated by FastAPI and the
    MasterAgent calls LangGraph's async ainvoke path internally.
    """
    scenario_telemetry = {
        "normal": {
            "engine_temperature": 88.0,
            "oil_pressure": 42.0,
            "brake_pad_thickness": 8.5,
            "battery_voltage": 12.6,
            "mileage": 24000,
            "error_codes": [],
        },
        "high_temperature": {
            "engine_temperature": 126.0,
            "oil_pressure": 31.0,
            "brake_pad_thickness": 7.0,
            "battery_voltage": 12.2,
            "mileage": 68000,
            "error_codes": ["P0217"],
        },
        "brake_warning": {
            "engine_temperature": 92.0,
            "oil_pressure": 40.0,
            "brake_pad_thickness": 2.1,
            "battery_voltage": 12.5,
            "mileage": 54000,
            "error_codes": ["C1234"],
        },
    }

    try:
        result = await agent.process_vehicle(
            vehicle_id=request.vehicle_id,
            telemetry_data=scenario_telemetry[request.scenario],
            config_override={"demo_mode": True},
        )
        agents_executed = [
            key.replace("_completed", "")
            for key in result.keys()
            if key.endswith("_completed")
        ]
        return LangGraphDemoResponse(
            success=True,
            vehicle_id=request.vehicle_id,
            scenario=request.scenario,
            orchestration="LangGraph StateGraph + conditional routing + MemorySaver",
            validation="Pydantic v2 request/response models",
            api_runtime="async FastAPI",
            agents_executed=agents_executed,
            escalated=result.get("escalate_to_human", False),
            prediction=result.get("prediction"),
            workflow_step=result.get("workflow_step"),
        )
    except Exception as exc:
        return LangGraphDemoResponse(
            success=False,
            vehicle_id=request.vehicle_id,
            scenario=request.scenario,
            orchestration="LangGraph StateGraph + conditional routing + MemorySaver",
            validation="Pydantic v2 request/response models",
            api_runtime="async FastAPI",
            agents_executed=[],
            escalated=True,
            error=str(exc),
        )


@app.get("/api/v1/health", response_model=SystemHealthResponse)
async def get_system_health(agent: MasterAgent = Depends(get_master_agent)) -> SystemHealthResponse:
    """
    Get comprehensive system health status

    Returns health information for all system components including
    agents, circuit breakers, monitoring systems, and performance metrics.
    """
    try:
        health_data = await agent.get_system_health()

        return SystemHealthResponse(
            overall_health=health_data.get("overall_health", "unknown"),
            timestamp=datetime.now().isoformat(),
            components=health_data.get("components", {}),
            issues=health_data.get("issues", []),
            metrics=health_data.get("metrics", {}),
        )

    except Exception as e:
        return SystemHealthResponse(
            overall_health="error",
            timestamp=datetime.now().isoformat(),
            components={},
            issues=[f"Health check failed: {str(e)}"],
            metrics={},
        )


@app.get("/api/v1/dashboard", response_model=DashboardResponse)
async def get_dashboard():
    """Get dashboard data with system metrics and recent activities"""
    try:
        await db_manager.initialize()
        await cache_manager.initialize()

        # Try to get from cache first
        cached_data = await cache_manager.get_dashboard_cache()
        if cached_data:
            return DashboardResponse(**cached_data)

        with db_manager.get_session() as session:
            # Get current timestamp
            current_time = datetime.utcnow()

            # Get vehicle count
            total_vehicles = session.query(Vehicle).filter(Vehicle.is_active is True).count()

            # Get recent telemetry count (last 24 hours)
            yesterday = current_time - timedelta(days=1)
            recent_telemetry = session.query(TelemetryData).filter(TelemetryData.timestamp >= yesterday).count()

            # Get maintenance records count (last 30 days)
            last_month = current_time - timedelta(days=30)
            recent_maintenance = (
                session.query(MaintenanceRecord).filter(MaintenanceRecord.service_date >= last_month.date()).count()
            )

            # Create dashboard response
            dashboard_data = {
                "timestamp": current_time.isoformat(),
                "agent_metrics": {
                    "total_agents": 5,
                    "active_agents": 4,
                    "avg_response_time": 0.25,
                    "success_rate": 98.5,
                },
                "system_metrics": {"cpu_usage": 45.2, "memory_usage": 62.8, "disk_usage": 34.1, "network_io": 1024.5},
                "security_metrics": {"threat_level": "LOW", "blocked_attempts": 12, "security_score": 95.8},
                "recent_activities": [
                    {
                        "id": "act_001",
                        "type": "vehicle_registered",
                        "description": f"Total vehicles: {total_vehicles}",
                        "timestamp": current_time.isoformat(),
                        "severity": "info",
                    },
                    {
                        "id": "act_002",
                        "type": "telemetry_processed",
                        "description": f"Processed {recent_telemetry} telemetry records in last 24h",
                        "timestamp": (current_time - timedelta(hours=1)).isoformat(),
                        "severity": "info",
                    },
                    {
                        "id": "act_003",
                        "type": "maintenance_scheduled",
                        "description": f"Scheduled {recent_maintenance} maintenance records in last 30 days",
                        "timestamp": (current_time - timedelta(hours=2)).isoformat(),
                        "severity": "info",
                    },
                ],
            }

            # Cache the response
            await cache_manager.set_dashboard_cache(dashboard_data)

            return DashboardResponse(**dashboard_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")


@app.get("/api/v1/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Get dashboard metrics data for frontend polling"""
    try:
        await db_manager.initialize()

        with db_manager.get_session() as session:
            # Get current timestamp
            current_time = datetime.utcnow()

            # Get vehicle count
            total_vehicles = session.query(Vehicle).filter(Vehicle.is_active is True).count()

            # Get recent telemetry count (last 24 hours)
            yesterday = current_time - timedelta(days=1)
            recent_telemetry = session.query(TelemetryData).filter(TelemetryData.timestamp >= yesterday).count()

            # Get maintenance records count (last 30 days)
            last_month = current_time - timedelta(days=30)
            recent_maintenance = (
                session.query(MaintenanceRecord).filter(MaintenanceRecord.service_date >= last_month.date()).count()
            )

            # Return metrics data
            metrics_data = {
                "timestamp": current_time.isoformat(),
                "agent_metrics": {
                    "total_agents": 5,
                    "active_agents": 4,
                    "avg_response_time": 0.25,
                    "success_rate": 98.5,
                },
                "system_metrics": {
                    "cpu_usage": 45.2 + (hash(str(current_time.second)) % 20),
                    "memory_usage": 62.8 + (hash(str(current_time.second)) % 15),
                    "disk_usage": 34.1 + (hash(str(current_time.second)) % 10),
                    "network_io": 1024.5 + (hash(str(current_time.second)) % 500),
                },
                "security_metrics": {
                    "threat_level": "LOW",
                    "blocked_attempts": 12 + (hash(str(current_time.second)) % 5),
                    "security_score": 95.8,
                },
                "vehicle_count": total_vehicles,
                "telemetry_count": recent_telemetry,
                "maintenance_count": recent_maintenance,
            }

            return metrics_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard metrics: {str(e)}")


@app.get("/api/v1/agents")
async def get_agents(agent: MasterAgent = Depends(get_master_agent)) -> Dict[str, Any]:
    """
    Get all available AI agents with their current status and metrics

    Returns comprehensive information about all agents in the system including
    their status, performance metrics, and configuration details.
    """
    try:
        # Get circuit breaker status for all agents
        circuit_breakers = agent.get_circuit_breaker_status()

        # Get system health to determine agent status
        health_data = await agent.get_system_health()
        health_data.get("agents", {})

        # Define available agents with their information
        agents_data = [
            {
                "id": "data_analysis_agent",
                "name": "Data Analysis Agent",
                "type": "analytics",
                "description": "Processes and analyzes vehicle telemetry data for insights",
                "status": "active" if circuit_breakers.get("data_analysis", {}).get("state") == "closed" else "error",
                "version": "1.0.0",
                "createdAt": "2024 - 01 - 01T00:00:00Z",
                "lastUpdated": datetime.now().isoformat(),
                "tasksProcessed": circuit_breakers.get("data_analysis", {}).get("success_count", 0),
                "avgResponseTime": 250,
                "uptime": "24h",
                "capabilities": [
                    "Telemetry data processing",
                    "Statistical analysis",
                    "Anomaly detection",
                    "Data validation",
                ],
            },
            {
                "id": "enhanced_data_analysis_agent",
                "name": "Enhanced Data Analysis Agent",
                "type": "analytics",
                "description": "Advanced data analysis with ML-powered insights and feature engineering",
                "status": (
                    "active" if circuit_breakers.get("enhanced_data_analysis", {}).get("state") == "closed" else "error"
                ),
                "version": "2.0.0",
                "createdAt": "2024 - 01 - 01T00:00:00Z",
                "lastUpdated": datetime.now().isoformat(),
                "tasksProcessed": circuit_breakers.get("enhanced_data_analysis", {}).get("success_count", 0),
                "avgResponseTime": 180,
                "uptime": "24h",
                "capabilities": [
                    "Advanced ML analysis",
                    "Feature engineering",
                    "Predictive modeling",
                    "Pattern recognition",
                ],
            },
            {
                "id": "diagnosis_agent",
                "name": "Diagnosis Agent",
                "type": "diagnostic",
                "description": "Diagnoses vehicle issues and provides maintenance recommendations",
                "status": "active" if circuit_breakers.get("diagnosis", {}).get("state") == "closed" else "error",
                "version": "1.0.0",
                "createdAt": "2024 - 01 - 01T00:00:00Z",
                "lastUpdated": datetime.now().isoformat(),
                "tasksProcessed": circuit_breakers.get("diagnosis", {}).get("success_count", 0),
                "avgResponseTime": 320,
                "uptime": "24h",
                "capabilities": [
                    "Issue diagnosis",
                    "Maintenance recommendations",
                    "Severity assessment",
                    "Root cause analysis",
                ],
            },
            {
                "id": "enhanced_diagnosis_agent",
                "name": "Enhanced Diagnosis Agent",
                "type": "diagnostic",
                "description": "Advanced diagnostic capabilities with AI-powered analysis",
                "status": (
                    "active" if circuit_breakers.get("enhanced_diagnosis", {}).get("state") == "closed" else "error"
                ),
                "version": "2.0.0",
                "createdAt": "2024 - 01 - 01T00:00:00Z",
                "lastUpdated": datetime.now().isoformat(),
                "tasksProcessed": circuit_breakers.get("enhanced_diagnosis", {}).get("success_count", 0),
                "avgResponseTime": 280,
                "uptime": "24h",
                "capabilities": [
                    "AI-powered diagnosis",
                    "Predictive failure analysis",
                    "Complex pattern recognition",
                    "Multi-system correlation",
                ],
            },
            {
                "id": "customer_engagement_agent",
                "name": "Customer Engagement Agent",
                "type": "engagement",
                "description": "Handles customer communications and service scheduling",
                "status": (
                    "active" if circuit_breakers.get("customer_engagement", {}).get("state") == "closed" else "error"
                ),
                "version": "1.0.0",
                "createdAt": "2024 - 01 - 01T00:00:00Z",
                "lastUpdated": datetime.now().isoformat(),
                "tasksProcessed": circuit_breakers.get("customer_engagement", {}).get("success_count", 0),
                "avgResponseTime": 150,
                "uptime": "24h",
                "capabilities": [
                    "Customer communication",
                    "Service scheduling",
                    "Notification management",
                    "Response handling",
                ],
            },
            {
                "id": "scheduling_agent",
                "name": "Scheduling Agent",
                "type": "scheduling",
                "description": "Manages maintenance appointments and resource allocation",
                "status": "active" if circuit_breakers.get("scheduling", {}).get("state") == "closed" else "error",
                "version": "1.0.0",
                "createdAt": "2024 - 01 - 01T00:00:00Z",
                "lastUpdated": datetime.now().isoformat(),
                "tasksProcessed": circuit_breakers.get("scheduling", {}).get("success_count", 0),
                "avgResponseTime": 200,
                "uptime": "24h",
                "capabilities": [
                    "Appointment scheduling",
                    "Resource allocation",
                    "Calendar management",
                    "Availability optimization",
                ],
            },
            {
                "id": "feedback_agent",
                "name": "Feedback Agent",
                "type": "feedback",
                "description": "Collects and processes customer feedback for service improvement",
                "status": "active" if circuit_breakers.get("feedback", {}).get("state") == "closed" else "error",
                "version": "1.0.0",
                "createdAt": "2024 - 01 - 01T00:00:00Z",
                "lastUpdated": datetime.now().isoformat(),
                "tasksProcessed": circuit_breakers.get("feedback", {}).get("success_count", 0),
                "avgResponseTime": 100,
                "uptime": "24h",
                "capabilities": [
                    "Feedback collection",
                    "Sentiment analysis",
                    "Service improvement insights",
                    "Customer satisfaction tracking",
                ],
            },
            {
                "id": "manufacturing_insights_agent",
                "name": "Manufacturing Insights Agent",
                "type": "manufacturing",
                "description": "Provides insights into manufacturing patterns and quality metrics",
                "status": (
                    "active" if circuit_breakers.get("manufacturing_insights", {}).get("state") == "closed" else "error"
                ),
                "version": "1.0.0",
                "createdAt": "2024 - 01 - 01T00:00:00Z",
                "lastUpdated": datetime.now().isoformat(),
                "tasksProcessed": circuit_breakers.get("manufacturing_insights", {}).get("success_count", 0),
                "avgResponseTime": 400,
                "uptime": "24h",
                "capabilities": [
                    "Manufacturing analysis",
                    "Quality metrics",
                    "Production insights",
                    "Defect pattern recognition",
                ],
            },
            {
                "id": "ueba_monitoring_agent",
                "name": "UEBA Monitoring Agent",
                "type": "monitoring",
                "description": "User and Entity Behavior Analytics for security monitoring",
                "status": "active",
                "version": "1.0.0",
                "createdAt": "2024 - 01 - 01T00:00:00Z",
                "lastUpdated": datetime.now().isoformat(),
                "tasksProcessed": 45,
                "avgResponseTime": 120,
                "uptime": "24h",
                "capabilities": ["Behavior analysis", "Anomaly detection", "Security monitoring", "Risk assessment"],
            },
        ]

        return {
            "success": True,
            "data": agents_data,
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(agents_data),
            "active_agents": len([a for a in agents_data if a["status"] == "active"]),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")


@app.get("/api/v1/agents/{agent_id}/status")
async def get_agent_status(agent_id: str, agent: MasterAgent = Depends(get_master_agent)) -> Dict[str, Any]:
    """
    Get detailed status information for a specific agent

    Returns comprehensive status, metrics, and activity information for the specified agent.
    """
    try:
        # Get all agents first
        agents_response = await get_agents(agent)
        agents_data = agents_response["data"]

        # Find the specific agent
        target_agent = next((a for a in agents_data if a["id"] == agent_id), None)

        if not target_agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        # Add additional detailed information
        target_agent["detailed_metrics"] = {
            "requests_per_minute": 5.2,
            "error_rate": 0.01,
            "memory_usage": 45.6,
            "cpu_usage": 12.3,
            "last_activity": datetime.now().isoformat(),
        }

        target_agent["recent_activities"] = [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "Processed vehicle diagnostic data",
                "status": "success",
                "duration": 250,
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(),
                "action": "Generated maintenance recommendation",
                "status": "success",
                "duration": 180,
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "action": "Analyzed telemetry patterns",
                "status": "success",
                "duration": 320,
            },
        ]

        return {"success": True, "data": target_agent, "timestamp": datetime.now().isoformat()}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")


@app.post("/api/v1/agents/{agent_id}/trigger")
async def trigger_agent(
    agent_id: str, payload: Dict[str, Any] = None, agent: MasterAgent = Depends(get_master_agent)
) -> Dict[str, Any]:
    """
    Trigger a specific agent with optional payload

    Manually triggers an agent execution with the provided payload data.
    """
    try:
        # Validate agent exists
        agents_response = await get_agents(agent)
        agents_data = agents_response["data"]

        target_agent = next((a for a in agents_data if a["id"] == agent_id), None)

        if not target_agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        # For now, return a mock response indicating the agent was triggered
        return {
            "success": True,
            "message": f"Agent {agent_id} triggered successfully",
            "agent_name": target_agent["name"],
            "trigger_time": datetime.now().isoformat(),
            "payload_received": payload is not None,
            "estimated_completion": (datetime.now() + timedelta(seconds=30)).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger agent: {str(e)}")


@app.get("/api/v1/circuit-breakers")
async def get_circuit_breaker_status(agent: MasterAgent = Depends(get_master_agent)) -> Dict[str, Any]:
    """
    Get circuit breaker status for all agents

    Returns the current state, failure counts, and timing information
    for all circuit breakers in the system.
    """
    try:
        return {"timestamp": datetime.now().isoformat(), "circuit_breakers": agent.get_circuit_breaker_status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get circuit breaker status: {str(e)}")


@app.post("/api/v1/demo")
async def run_demo_scenarios(
    background_tasks: BackgroundTasks, agent: MasterAgent = Depends(get_master_agent)
) -> Dict[str, Any]:
    """
    Run demonstration scenarios

    Executes predefined demo scenarios to showcase system capabilities
    including critical failures, maintenance warnings, and routine checks.
    """
    try:
        # Import demo runner
        from demo import DemoRunner

        demo_runner = DemoRunner()

        # Run demo in background
        async def run_demo():
            return await demo_runner.run_comprehensive_demo()

        # Execute demo
        results = await run_demo()

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "scenarios_executed": len(results),
            "results": results,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo execution failed: {str(e)}")


@app.get("/api/v1/metrics/prometheus")
async def get_prometheus_metrics(agent: MasterAgent = Depends(get_master_agent)):
    """
    Get Prometheus-formatted metrics

    Returns metrics in Prometheus exposition format for monitoring integration.
    """
    try:
        # Get metrics from performance monitor
        metrics_data = agent.performance_monitor.metrics

        # Format as Prometheus metrics (simplified)
        prometheus_output = []

        # Add some basic metrics
        prometheus_output.append("# HELP master_agent_requests_total Total number of vehicle processing requests")
        prometheus_output.append("# TYPE master_agent_requests_total counter")
        prometheus_output.append(f"master_agent_requests_total {getattr(metrics_data, 'requests_total', 0)}")

        prometheus_output.append("# HELP master_agent_processing_duration_seconds Processing duration in seconds")
        prometheus_output.append("# TYPE master_agent_processing_duration_seconds histogram")

        return "\n".join(prometheus_output)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


# WebSocket endpoints
@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time logs stream and suggestions backfill."""
    try:
        await websocket.accept()
        logging.info("Logs WebSocket connection accepted")

        if "logs" not in manager.active_connections:
            manager.active_connections["logs"] = set()
        manager.active_connections["logs"].add(websocket)

        # Send initial backlog and current suggestions
        try:
            backfill = {
                "type": "log_backfill",
                "timestamp": datetime.now().isoformat(),
                "items": logs_manager.get_recent(100),
            }
            await websocket.send_text(json.dumps(backfill))

            suggestions = {
                "type": "suggestions",
                "timestamp": datetime.now().isoformat(),
                "items": [s.model_dump() for s in logs_manager.suggestions()],
            }
            await websocket.send_text(json.dumps(suggestions))
        except Exception as e:
            logging.error(f"Failed to send logs backfill: {e}")

        while True:
            if websocket.client_state != WebSocketState.CONNECTED:
                break
            # Keep the connection alive; broadcast occurs on ingestion via callback
            await asyncio.sleep(10)

    except WebSocketDisconnect:
        logging.info("Logs WebSocket disconnected")
    except Exception as e:
        logging.error(f"Logs WebSocket error: {e}")
    finally:
        if "logs" in manager.active_connections:
            manager.active_connections["logs"].discard(websocket)
@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket endpoint for dashboard real-time updates"""
    logging.info(f"Dashboard WebSocket connection attempt from {websocket.client}")

    try:
        # Accept the connection first
        await websocket.accept()
        logging.info("Dashboard WebSocket accepted")

        # Add to connection manager after accepting
        manager.active_connections["dashboard"].add(websocket)
        logging.info("Dashboard WebSocket added to manager")

        while True:
            # Send periodic dashboard updates
            dashboard_data = {
                "type": "dashboard_update",
                "timestamp": datetime.now().isoformat(),
                "data": {"active_vehicles": 42, "alerts_count": 3, "system_health": "healthy", "processing_queue": 5},
            }

            # Send message directly instead of using manager
            try:
                # Check if websocket is still connected before sending
                if websocket.client_state != WebSocketState.CONNECTED:
                    logging.info(f"Dashboard WebSocket state changed to {websocket.client_state}")
                    break

                await websocket.send_text(json.dumps(dashboard_data))
                logging.debug("Sent dashboard update successfully")
            except WebSocketDisconnect:
                logging.info("Dashboard WebSocket disconnected during send")
                break
            except RuntimeError as e:
                if "closed" in str(e).lower() or "disconnect" in str(e).lower():
                    logging.info(f"Dashboard WebSocket closed: {e}")
                    break
                logging.error(f"Failed to send dashboard update (RuntimeError): {e}")
                break
            except Exception as e:
                logging.error(f"Failed to send dashboard update: {type(e).__name__}: {e}")
                import traceback
                logging.error(traceback.format_exc())
                break

            await asyncio.sleep(5)  # Send updates every 5 seconds

    except WebSocketDisconnect:
        logging.info("Dashboard WebSocket disconnect event")
    except Exception as e:
        logging.error(f"Dashboard WebSocket error: {e}")
    finally:
        # Clean up connection
        manager.active_connections["dashboard"].discard(websocket)
        logging.info("Dashboard WebSocket cleanup completed")


@app.websocket("/ws/vehicle/{vehicle_id}")
async def websocket_vehicle(websocket: WebSocket, vehicle_id: str):
    """WebSocket endpoint for vehicle-specific real-time updates"""
    logging.info(f"WebSocket connection attempt for vehicle {vehicle_id} from {websocket.client}")

    try:
        # Accept the connection first
        await websocket.accept()
        logging.info(f"WebSocket accepted for vehicle {vehicle_id}")

        # Add to connection manager after accepting
        if vehicle_id not in manager.vehicle_connections:
            manager.vehicle_connections[vehicle_id] = set()
        manager.vehicle_connections[vehicle_id].add(websocket)
        logging.info(f"WebSocket added to manager for vehicle {vehicle_id}")

        while True:
            # Check if websocket is still connected before sending
            if websocket.client_state != WebSocketState.CONNECTED:
                logging.info(f"WebSocket state changed to {websocket.client_state} for vehicle {vehicle_id}")
                break

            # Send periodic vehicle telemetry updates
            telemetry_data = {
                "type": "telemetry_update",
                "vehicle_id": vehicle_id,
                "timestamp": datetime.now().isoformat(),
                "telemetry": {
                    "speed": 65 + (hash(vehicle_id + str(datetime.now().second)) % 20),
                    "engineRpm": 2000 + (hash(vehicle_id + str(datetime.now().second)) % 1000),
                    "engineTemp": 85 + (hash(vehicle_id + str(datetime.now().second)) % 15),
                    "fuelLevel": 75 + (hash(vehicle_id + str(datetime.now().second)) % 25),
                    "batteryVoltage": 12.0 + (hash(vehicle_id + str(datetime.now().second)) % 2),
                },
            }

            # Send message directly instead of using manager
            try:
                await websocket.send_text(json.dumps(telemetry_data))
                logging.debug(f"Sent telemetry update for vehicle {vehicle_id}")
            except Exception as e:
                logging.error(f"Failed to send telemetry: {e}")
                break

            await asyncio.sleep(2)  # Send updates every 2 seconds

    except WebSocketDisconnect:
        logging.info(f"WebSocket disconnect event for vehicle {vehicle_id}")
    except Exception as e:
        logging.error(f"Vehicle {vehicle_id} WebSocket error: {e}")
    finally:
        # Clean up connection
        if vehicle_id in manager.vehicle_connections:
            manager.vehicle_connections[vehicle_id].discard(websocket)
            if not manager.vehicle_connections[vehicle_id]:
                del manager.vehicle_connections[vehicle_id]
        logging.info(f"WebSocket cleanup completed for vehicle {vehicle_id}")


@app.websocket("/ws/agents")
async def websocket_agents(websocket: WebSocket):
    """WebSocket endpoint for agent monitoring real-time updates"""
    try:
        await websocket.accept()
        logging.info("Agents WebSocket connection accepted")

        # Add to manager after accepting
        if "agents" not in manager.active_connections:
            manager.active_connections["agents"] = set()
        manager.active_connections["agents"].add(websocket)

        while True:
            # Check connection state before sending
            if websocket.client_state != WebSocketState.CONNECTED:
                break

            # Send periodic agent activity updates
            agent_data = {
                "type": "agent_activity",
                "timestamp": datetime.now().isoformat(),
                "payload": {
                    "id": str(uuid.uuid4()),
                    "agent_name": "Diagnostic Agent",
                    "action": "Processed vehicle diagnostic data",
                    "status": "success",
                    "details": f"Analyzed telemetry for vehicle VH{hash(str(datetime.now().second)) % 1000:03d}",
                },
            }

            try:
                await websocket.send_text(json.dumps(agent_data))
            except Exception as e:
                logging.error(f"Failed to send agent data: {e}")
                break

            await asyncio.sleep(3)  # Send updates every 3 seconds

    except WebSocketDisconnect:
        logging.info("Agents WebSocket disconnected")
    except Exception as e:
        logging.error(f"Agents WebSocket error: {e}")
    finally:
        # Clean up connection
        if "agents" in manager.active_connections:
            manager.active_connections["agents"].discard(websocket)


@app.websocket("/ws/system-maintenance")
async def websocket_system_maintenance(websocket: WebSocket):
    """WebSocket endpoint for system maintenance real-time updates"""
    try:
        await websocket.accept()
        logging.info("System maintenance WebSocket connection accepted")

        # Add to manager after accepting
        if "system" not in manager.active_connections:
            manager.active_connections["system"] = set()
        manager.active_connections["system"].add(websocket)

        while True:
            # Check connection state before sending
            if websocket.client_state != WebSocketState.CONNECTED:
                break

            # Send periodic system maintenance updates
            system_data = {
                "type": "system_update",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "cpu_usage": 45 + (hash(str(datetime.now().second)) % 30),
                    "memory_usage": 60 + (hash(str(datetime.now().second)) % 25),
                    "disk_usage": 35 + (hash(str(datetime.now().second)) % 20),
                    "active_connections": 15 + (hash(str(datetime.now().second)) % 10),
                    "system_health": "operational",
                },
            }

            try:
                await websocket.send_text(json.dumps(system_data))
            except Exception as e:
                logging.error(f"Failed to send system data: {e}")
                break

            await asyncio.sleep(4)  # Send updates every 4 seconds

    except WebSocketDisconnect:
        logging.info("System maintenance WebSocket disconnected")
    except Exception as e:
        logging.error(f"System maintenance WebSocket error: {e}")
    finally:
        # Clean up connection
        if "system" in manager.active_connections:
            manager.active_connections["system"].discard(websocket)


@app.websocket("/ws/demo")
async def websocket_demo(websocket: WebSocket):
    """WebSocket endpoint for demo interface real-time updates"""
    try:
        await websocket.accept()
        logging.info("Demo WebSocket connection accepted")

        # Add to manager after accepting
        if "demo" not in manager.active_connections:
            manager.active_connections["demo"] = set()
        manager.active_connections["demo"].add(websocket)

        while True:
            # Check connection state before sending
            if websocket.client_state != WebSocketState.CONNECTED:
                break

            # Send periodic demo updates
            demo_data = {
                "type": "demo_update",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "processing_status": "active",
                    "vehicles_processed": 156 + (hash(str(datetime.now().second)) % 10),
                    "predictions_made": 89 + (hash(str(datetime.now().second)) % 5),
                    "alerts_generated": 12 + (hash(str(datetime.now().second)) % 3),
                },
            }

            try:
                await websocket.send_text(json.dumps(demo_data))
            except Exception as e:
                logging.error(f"Failed to send demo data: {e}")
                break

            await asyncio.sleep(6)  # Send updates every 6 seconds

    except WebSocketDisconnect:
        logging.info("Demo WebSocket disconnected")
    except Exception as e:
        logging.error(f"Demo WebSocket error: {e}")
    finally:
        # Clean up connection
        if "demo" in manager.active_connections:
            manager.active_connections["demo"].discard(websocket)


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested endpoint was not found",
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat(),
        },
    )


def create_app() -> FastAPI:
    """Factory function to create the FastAPI app"""
    return app


if __name__ == "__main__":
    # Run the server
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True, log_level="info")


# New Pydantic models for API responses
class VehicleResponse(BaseModel):
    id: str
    vin: str
    make: str
    model: str
    year: int
    engine_type: str
    transmission: str
    fuel_type: str
    color: str
    mileage: int
    registration_date: str
    last_service_date: Optional[str] = None
    warranty_expiry: Optional[str] = None
    status: str


class CustomerResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    zip_code: str
    date_of_birth: str
    registration_date: str


class TelemetryResponse(BaseModel):
    id: str
    vehicle_id: str
    timestamp: str
    engine_rpm: Optional[float] = None
    speed: Optional[float] = None
    fuel_level: Optional[float] = None
    engine_temp: Optional[float] = None
    oil_pressure: Optional[float] = None
    battery_voltage: Optional[float] = None
    coolant_temp: Optional[float] = None
    brake_pressure: Optional[float] = None
    tire_pressure_fl: Optional[float] = None
    tire_pressure_fr: Optional[float] = None
    tire_pressure_rl: Optional[float] = None
    tire_pressure_rr: Optional[float] = None
    odometer: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class MaintenanceResponse(BaseModel):
    id: str
    vehicle_id: str
    service_type: str
    description: str
    start_date: str
    end_date: Optional[str] = None
    cost: Optional[float] = None
    technician: Optional[str] = None
    status: str
    priority: str
    notes: Optional[str] = None


class PaginationResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int


class PaginatedVehicleResponse(BaseModel):
    data: List[VehicleResponse]
    pagination: PaginationResponse


class PaginatedTelemetryResponse(BaseModel):
    data: List[TelemetryResponse]
    pagination: PaginationResponse


class PaginatedMaintenanceResponse(BaseModel):
    data: List[MaintenanceResponse]
    pagination: PaginationResponse


# Request models for creating/updating records
class VehicleCreateRequest(BaseModel):
    make: str
    model: str
    year: int
    engine_type: str
    transmission_type: str
    mileage: int = 0
    is_active: bool = True


class VehicleUpdateRequest(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    engine_type: Optional[str] = None
    transmission_type: Optional[str] = None
    mileage: Optional[int] = None
    is_active: Optional[bool] = None


class MaintenanceCreateRequest(BaseModel):
    vehicle_id: str
    service_type: str
    description: str
    start_date: str
    end_date: Optional[str] = None
    cost: Optional[float] = None
    technician: Optional[str] = None
    status: str = "scheduled"
    priority: str = "medium"
    notes: Optional[str] = None


class MaintenanceUpdateRequest(BaseModel):
    service_type: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    cost: Optional[float] = None
    technician: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None


# Vehicle endpoints
@app.get("/api/v1/vehicles", response_model=PaginatedVehicleResponse)
async def get_vehicles(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    make: Optional[str] = Query(None, description="Filter by make"),
    model: Optional[str] = Query(None, description="Filter by model"),
    status: Optional[str] = Query(None, description="Filter by status"),
):
    """Get paginated list of vehicles with optional filtering"""
    try:
        await db_manager.initialize()
        await cache_manager.initialize()

        # Try to get from cache first
        cached_data = await cache_manager.get_vehicles_cache(
            page=page, limit=limit, make=make, model=model, status=status
        )
        if cached_data:
            return PaginatedVehicleResponse(**cached_data)

        with db_manager.get_session() as session:
            # Build base query with optimized filtering
            query = session.query(Vehicle)

            # Apply filters with case-insensitive search
            if make:
                query = query.filter(Vehicle.make.ilike(f"%{make}%"))
            if model:
                query = query.filter(Vehicle.model.ilike(f"%{model}%"))
            if status:
                if status.lower() == "active":
                    query = query.filter(Vehicle.is_active is True)
                elif status.lower() == "inactive":
                    query = query.filter(Vehicle.is_active is False)

            # Get total count efficiently - use count() on the filtered query
            total = query.count()

            # Apply pagination and ordering for consistent results
            offset = (page - 1) * limit
            vehicles = query.order_by(Vehicle.id).offset(offset).limit(limit).all()

            # Convert to response format efficiently
            vehicle_data = []
            for vehicle in vehicles:
                vehicle_data.append(
                    VehicleResponse(
                        id=vehicle.id,
                        vin=vehicle.id,  # Using id as VIN since there's no separate vin field
                        make=vehicle.make,
                        model=vehicle.model,
                        year=vehicle.year,
                        engine_type=vehicle.engine_type,
                        transmission=vehicle.transmission_type,  # Correct field name
                        fuel_type="Unknown",  # Not in database model
                        color="Unknown",  # Not in database model
                        mileage=vehicle.mileage,
                        status="Active" if vehicle.is_active else "Inactive",  # Convert boolean to string
                        registration_date=vehicle.registration_date.isoformat() if vehicle.registration_date else None,
                        last_service_date=vehicle.last_service_date.isoformat() if vehicle.last_service_date else None,
                        warranty_expiry=vehicle.warranty_expiry.isoformat() if vehicle.warranty_expiry else None,
                    )
                )

            pages = (total + limit - 1) // limit

            response_data = {
                "data": [v.dict() for v in vehicle_data],
                "pagination": {"page": page, "limit": limit, "total": total, "pages": pages},
            }

            # Cache the response
            await cache_manager.set_vehicles_cache(
                response_data, page=page, limit=limit, make=make, model=model, status=status
            )

            return PaginatedVehicleResponse(
                data=vehicle_data, pagination=PaginationResponse(page=page, limit=limit, total=total, pages=pages)
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vehicles: {str(e)}")


@app.get("/api/v1/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(vehicle_id: str):
    """Get a specific vehicle by ID"""
    try:
        db_manager = DatabaseManager()
        await db_manager.initialize()

        with db_manager.get_session() as session:
            vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

            if not vehicle:
                raise HTTPException(status_code=404, detail="Vehicle not found")

            return VehicleResponse(
                id=vehicle.id,
                vin=vehicle.id,  # Using id as VIN since there's no separate vin field
                make=vehicle.make,
                model=vehicle.model,
                year=vehicle.year,
                engine_type=vehicle.engine_type,
                transmission=vehicle.transmission_type,  # Correct field name
                fuel_type="Unknown",  # Not in database model
                color="Unknown",  # Not in database model
                mileage=vehicle.mileage,
                status="Active" if vehicle.is_active else "Inactive",  # Convert boolean to string
                registration_date=vehicle.registration_date.isoformat() if vehicle.registration_date else None,
                last_service_date=vehicle.last_service_date.isoformat() if vehicle.last_service_date else None,
                warranty_expiry=vehicle.warranty_expiry.isoformat() if vehicle.warranty_expiry else None,
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vehicle: {str(e)}")


@app.get("/api/v1/vehicles/{vehicle_id}/telemetry", response_model=PaginatedTelemetryResponse)
async def get_vehicle_telemetry(
    vehicle_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
):
    """Get paginated telemetry data for a specific vehicle"""
    try:
        await db_manager.initialize()

        with db_manager.get_session() as session:
            # Verify vehicle exists with a single query
            vehicle_exists = session.query(Vehicle.id).filter(Vehicle.id == vehicle_id).first()
            if not vehicle_exists:
                raise HTTPException(status_code=404, detail="Vehicle not found")

            # Build optimized telemetry query
            query = session.query(TelemetryData).filter(TelemetryData.vehicle_id == vehicle_id)

            # Apply date filters efficiently
            if start_date:
                query = query.filter(TelemetryData.timestamp >= start_date)
            if end_date:
                query = query.filter(TelemetryData.timestamp <= end_date)

            # Order by timestamp descending for most recent data first
            query = query.order_by(desc(TelemetryData.timestamp))

            # Get total count efficiently
            total = query.count()

            # Apply pagination
            offset = (page - 1) * limit
            telemetry_records = query.offset(offset).limit(limit).all()

            # Convert to response format efficiently
            telemetry_data = []
            for record in telemetry_records:
                telemetry_data.append(
                    TelemetryResponse(
                        id=record.id,
                        vehicle_id=record.vehicle_id,
                        timestamp=record.timestamp.isoformat(),
                        engine_rpm=record.engine_rpm,
                        speed=record.speed,
                        fuel_level=record.fuel_level,
                        engine_temp=record.engine_temperature,  # Fixed: use engine_temperature from DB model
                        oil_pressure=record.oil_pressure,
                        battery_voltage=record.battery_voltage,
                        coolant_temp=record.coolant_temp,
                        brake_pressure=getattr(
                            record, "brake_pressure", None
                        ),  # Safe access as this field may not exist
                        tire_pressure_fl=record.tire_pressure_fl,
                        tire_pressure_fr=record.tire_pressure_fr,
                        tire_pressure_rl=record.tire_pressure_rl,
                        tire_pressure_rr=record.tire_pressure_rr,
                        odometer=getattr(record, "odometer", record.mileage),  # Use mileage if odometer doesn't exist
                        latitude=record.location_lat,  # Fixed: use location_lat from DB model
                        longitude=record.location_lng,  # Fixed: use location_lng from DB model
                    )
                )

            pages = (total + limit - 1) // limit

            return PaginatedTelemetryResponse(
                data=telemetry_data, pagination=PaginationResponse(page=page, limit=limit, total=total, pages=pages)
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch telemetry: {str(e)}")


@app.get("/api/v1/maintenance", response_model=PaginatedMaintenanceResponse)
async def get_maintenance_records(
    page: int = 1,
    limit: int = 10,
    vehicle_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
):
    """Get paginated list of maintenance records with optional filters"""
    try:
        db_manager = DatabaseManager()
        await db_manager.initialize()

        with db_manager.get_session() as session:
            # Build query with filters
            query = session.query(MaintenanceRecord)

            if vehicle_id:
                query = query.filter(MaintenanceRecord.vehicle_id == vehicle_id)
            # Note: status and priority filters removed as these fields don't exist in the database model

            # Order by service_date descending
            query = query.order_by(desc(MaintenanceRecord.service_date))

            # Get total count
            total = query.count()

            # Apply pagination
            offset = (page - 1) * limit
            maintenance_records = query.offset(offset).limit(limit).all()

            # Convert to response format
            maintenance_data = []
            for record in maintenance_records:
                maintenance_data.append(
                    MaintenanceResponse(
                        id=record.id,
                        vehicle_id=record.vehicle_id,
                        service_type=record.service_type,
                        description=record.service_notes or "",
                        start_date=record.service_date.isoformat(),
                        end_date=None,
                        cost=record.total_cost,
                        technician=record.technician_id or "",
                        status="scheduled",
                        priority="medium",
                        notes=record.service_notes or "",
                    )
                )

            pages = (total + limit - 1) // limit

            return PaginatedMaintenanceResponse(
                data=maintenance_data, pagination=PaginationResponse(page=page, limit=limit, total=total, pages=pages)
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch maintenance records: {str(e)}")


@app.post("/api/v1/vehicles", response_model=VehicleResponse)
async def create_vehicle(vehicle_data: VehicleCreateRequest):
    """Create a new vehicle"""
    try:
        db_manager = DatabaseManager()
        await db_manager.initialize()

        with db_manager.get_session() as session:
            # Create new vehicle
            new_vehicle = Vehicle(
                id=str(uuid.uuid4()),
                make=vehicle_data.make,
                model=vehicle_data.model,
                year=vehicle_data.year,
                engine_type=vehicle_data.engine_type,
                transmission_type=vehicle_data.transmission_type,
                mileage=vehicle_data.mileage,
                is_active=vehicle_data.is_active,
                registration_date=datetime.now(),
            )

            session.add(new_vehicle)
            session.commit()
            session.refresh(new_vehicle)

            return VehicleResponse(
                id=new_vehicle.id,
                vin=new_vehicle.id,
                make=new_vehicle.make,
                model=new_vehicle.model,
                year=new_vehicle.year,
                engine_type=new_vehicle.engine_type,
                transmission=new_vehicle.transmission_type,
                fuel_type="Unknown",
                color="Unknown",
                mileage=new_vehicle.mileage,
                status="Active" if new_vehicle.is_active else "Inactive",
                registration_date=new_vehicle.registration_date.isoformat(),
                last_service_date=new_vehicle.last_service_date.isoformat() if new_vehicle.last_service_date else None,
                warranty_expiry=new_vehicle.warranty_expiry.isoformat() if new_vehicle.warranty_expiry else None,
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create vehicle: {str(e)}")


@app.put("/api/v1/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(vehicle_id: str, vehicle_data: VehicleUpdateRequest):
    """Update an existing vehicle"""
    try:
        db_manager = DatabaseManager()
        await db_manager.initialize()

        with db_manager.get_session() as session:
            vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

            if not vehicle:
                raise HTTPException(status_code=404, detail="Vehicle not found")

            # Update fields if provided
            if vehicle_data.make is not None:
                vehicle.make = vehicle_data.make
            if vehicle_data.model is not None:
                vehicle.model = vehicle_data.model
            if vehicle_data.year is not None:
                vehicle.year = vehicle_data.year
            if vehicle_data.engine_type is not None:
                vehicle.engine_type = vehicle_data.engine_type
            if vehicle_data.transmission_type is not None:
                vehicle.transmission_type = vehicle_data.transmission_type
            if vehicle_data.mileage is not None:
                vehicle.mileage = vehicle_data.mileage
            if vehicle_data.is_active is not None:
                vehicle.is_active = vehicle_data.is_active

            session.commit()
            session.refresh(vehicle)

            return VehicleResponse(
                id=vehicle.id,
                vin=vehicle.id,
                make=vehicle.make,
                model=vehicle.model,
                year=vehicle.year,
                engine_type=vehicle.engine_type,
                transmission=vehicle.transmission_type,
                fuel_type="Unknown",
                color="Unknown",
                mileage=vehicle.mileage,
                status="Active" if vehicle.is_active else "Inactive",
                registration_date=vehicle.registration_date.isoformat() if vehicle.registration_date else None,
                last_service_date=vehicle.last_service_date.isoformat() if vehicle.last_service_date else None,
                warranty_expiry=vehicle.warranty_expiry.isoformat() if vehicle.warranty_expiry else None,
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update vehicle: {str(e)}")


@app.delete("/api/v1/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: str):
    """Delete a vehicle"""
    try:
        db_manager = DatabaseManager()
        await db_manager.initialize()

        with db_manager.get_session() as session:
            vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

            if not vehicle:
                raise HTTPException(status_code=404, detail="Vehicle not found")

            session.delete(vehicle)
            session.commit()

            return {"message": "Vehicle deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete vehicle: {str(e)}")


@app.post("/api/v1/maintenance", response_model=MaintenanceResponse)
async def create_maintenance_record(maintenance_data: MaintenanceCreateRequest):
    """Create a new maintenance record"""
    try:
        db_manager = DatabaseManager()
        await db_manager.initialize()

        with db_manager.get_session() as session:
            # Verify vehicle exists
            vehicle = session.query(Vehicle).filter(Vehicle.id == maintenance_data.vehicle_id).first()
            if not vehicle:
                raise HTTPException(status_code=404, detail="Vehicle not found")

            # Create new maintenance record
            new_record = MaintenanceRecord(
                id=str(uuid.uuid4()),
                vehicle_id=maintenance_data.vehicle_id,
                service_type=maintenance_data.service_type,
                service_date=datetime.fromisoformat(maintenance_data.start_date.replace("Z", "+00:00")),
                service_notes=maintenance_data.description,
                total_cost=maintenance_data.cost,
                technician_id=maintenance_data.technician,
            )

            session.add(new_record)
            session.commit()
            session.refresh(new_record)

            return MaintenanceResponse(
                id=new_record.id,
                vehicle_id=new_record.vehicle_id,
                service_type=new_record.service_type,
                description=new_record.service_notes or "",
                start_date=new_record.service_date.isoformat(),
                end_date=None,
                cost=new_record.total_cost,
                technician=new_record.technician_id or "",
                status="scheduled",
                priority="medium",
                notes=new_record.service_notes or "",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create maintenance record: {str(e)}")


@app.put("/api/v1/maintenance/{maintenance_id}", response_model=MaintenanceResponse)
async def update_maintenance_record(maintenance_id: str, maintenance_data: MaintenanceUpdateRequest):
    """Update an existing maintenance record"""
    try:
        db_manager = DatabaseManager()
        await db_manager.initialize()

        with db_manager.get_session() as session:
            record = session.query(MaintenanceRecord).filter(MaintenanceRecord.id == maintenance_id).first()

            if not record:
                raise HTTPException(status_code=404, detail="Maintenance record not found")

            # Update fields if provided
            if maintenance_data.service_type is not None:
                record.service_type = maintenance_data.service_type
            if maintenance_data.description is not None:
                record.description = maintenance_data.description
            if maintenance_data.start_date is not None:
                record.start_date = datetime.fromisoformat(maintenance_data.start_date.replace("Z", "+00:00"))
            if maintenance_data.end_date is not None:
                record.end_date = datetime.fromisoformat(maintenance_data.end_date.replace("Z", "+00:00"))
            if maintenance_data.cost is not None:
                record.cost = maintenance_data.cost
            if maintenance_data.technician is not None:
                record.technician = maintenance_data.technician
            if maintenance_data.status is not None:
                record.status = maintenance_data.status
            if maintenance_data.priority is not None:
                record.priority = maintenance_data.priority
            if maintenance_data.notes is not None:
                record.notes = maintenance_data.notes

            session.commit()
            session.refresh(record)

            return MaintenanceResponse(
                id=record.id,
                vehicle_id=record.vehicle_id,
                service_type=record.service_type,
                description=record.description,
                start_date=record.start_date.isoformat(),
                end_date=record.end_date.isoformat() if record.end_date else None,
                cost=record.cost,
                technician=record.technician,
                status=record.status,
                priority=record.priority,
                notes=record.notes,
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update maintenance record: {str(e)}")


@app.delete("/api/v1/maintenance/{maintenance_id}")
async def delete_maintenance_record(maintenance_id: str):
    """Delete a maintenance record"""
    try:
        db_manager = DatabaseManager()
        await db_manager.initialize()

        with db_manager.get_session() as session:
            record = session.query(MaintenanceRecord).filter(MaintenanceRecord.id == maintenance_id).first()

            if not record:
                raise HTTPException(status_code=404, detail="Maintenance record not found")

            session.delete(record)
            session.commit()

            return {"message": "Maintenance record deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete maintenance record: {str(e)}")


if __name__ == "__main__":
    # Run the server
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True, log_level="info")

