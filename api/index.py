"""Lean Vercel API for AutoMind production demo.

The full backend remains available in the repository (api_server.py +
requirements.full.txt). This entrypoint intentionally keeps Vercel's
serverless bundle small while preserving the production demo's auth/session
contract and a real LangGraph StateGraph example.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Literal, TypedDict

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field


app = FastAPI(
    title="AutoMind Vercel API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://automind-ai-aryas-projects-6676c3c7.vercel.app",
        "http://localhost:5173",
    ],
    allow_origin_regex=r"https://automind-.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "automind-vercel-demo-secret-change-me")
ALGORITHM = "HS256"
TOKEN_HOURS = 24

DEMO_USERS: Dict[str, Dict[str, Any]] = {
    "rajesh@demo.com": {
        "id": "USR-CUST-001",
        "email": "rajesh@demo.com",
        "password": "demo123",
        "first_name": "Rajesh",
        "last_name": "Kumar",
        "role": "customer",
        "role_data": {"vehicle_ids": ["VEH001", "VEH002"]},
    },
    "priya@demo.com": {
        "id": "USR-SVC-001",
        "email": "priya@demo.com",
        "password": "demo123",
        "first_name": "Priya",
        "last_name": "Sharma",
        "role": "service_staff",
        "role_data": {"service_center": "Bengaluru Central"},
    },
    "amit@demo.com": {
        "id": "USR-MFG-001",
        "email": "amit@demo.com",
        "password": "demo123",
        "first_name": "Amit",
        "last_name": "Patel",
        "role": "manufacturing_engineer",
        "role_data": {"plant": "AutoMind Manufacturing"},
    },
    "sarah@demo.com": {
        "id": "USR-ADMIN-001",
        "email": "sarah@demo.com",
        "password": "demo123",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "role": "system_admin",
        "role_data": {"scope": "all"},
    },
}


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    token: str
    user: Dict[str, Any]


def public_user(user: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in user.items() if k != "password"}


def create_token(user: Dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": user["id"],
            "email": user["email"],
            "role": user["role"],
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=TOKEN_HOURS)).timestamp()),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def current_user(authorization: str | None = Header(default=None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc
    user = DEMO_USERS.get(email or "")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    return user


@app.get("/api/v1/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "runtime": "Vercel Python / FastAPI",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "api": "healthy",
            "auth": "healthy",
            "langgraph_demo": "healthy",
        },
    }


@app.get("/api/v1/debug/routes")
async def routes() -> Dict[str, Any]:
    rows = []
    for route in app.routes:
        path = getattr(route, "path", None)
        if path:
            rows.append({"path": path, "methods": sorted(getattr(route, "methods", []) or [])})
    return {"count": len(rows), "routes": sorted(rows, key=lambda item: item["path"])}


@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> Dict[str, Any]:
    user = DEMO_USERS.get(request.email.lower())
    if not user or request.password != user["password"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return {"token": create_token(user), "user": public_user(user)}


@app.get("/api/v1/auth/me")
async def me(user: Dict[str, Any] = Depends(current_user)) -> Dict[str, Any]:
    return {"user": public_user(user)}


@app.post("/api/v1/auth/logout")
async def logout() -> Dict[str, str]:
    return {"message": "Logged out successfully"}


def role_dashboard(user: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "user": public_user(user),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_metrics": {
            "total_vehicles": 1247,
            "active_vehicles": 1124,
            "healthy_vehicles": 1098,
            "vehicles_in_maintenance": 123,
            "critical_alerts": 23,
            "active_alerts": 23,
            "maintenance_scheduled": 156,
            "api_status": "healthy",
            "database_status": "demo",
            "cache_status": "demo",
        },
        "agent_metrics": {
            "active_agents": 12,
            "total_tasks_today": 847,
            "avg_response_time": 1.2,
        },
        "security_metrics": {"status": "healthy"},
        "recent_activities": [],
    }


@app.get("/api/v1/dashboard")
async def dashboard(user: Dict[str, Any] = Depends(current_user)) -> Dict[str, Any]:
    return role_dashboard(user)


@app.get("/api/v1/dashboard/customer")
async def customer_dashboard(user: Dict[str, Any] = Depends(current_user)) -> Dict[str, Any]:
    return role_dashboard(user)


@app.get("/api/v1/dashboard/service-staff")
async def service_dashboard(user: Dict[str, Any] = Depends(current_user)) -> Dict[str, Any]:
    return role_dashboard(user)


@app.get("/api/v1/dashboard/manufacturing")
async def manufacturing_dashboard(user: Dict[str, Any] = Depends(current_user)) -> Dict[str, Any]:
    return role_dashboard(user)


@app.get("/api/v1/dashboard/admin")
async def admin_dashboard(user: Dict[str, Any] = Depends(current_user)) -> Dict[str, Any]:
    return role_dashboard(user)


class DemoState(TypedDict, total=False):
    vehicle_id: str
    scenario: str
    temperature: float
    brake_warning: bool
    priority: str
    diagnosis: str
    workflow_step: str


def analyze(state: DemoState) -> DemoState:
    if state.get("temperature", 0) >= 110:
        state["priority"] = "P1"
        state["diagnosis"] = "High engine temperature detected"
    elif state.get("brake_warning"):
        state["priority"] = "P1"
        state["diagnosis"] = "Brake system warning detected"
    else:
        state["priority"] = "P3"
        state["diagnosis"] = "Vehicle telemetry within normal demo thresholds"
    state["workflow_step"] = "analyzed"
    return state


def route_after_analysis(state: DemoState) -> str:
    return "escalate" if state.get("priority") == "P1" else "complete"


def escalate(state: DemoState) -> DemoState:
    state["workflow_step"] = "human_escalation"
    return state


def complete(state: DemoState) -> DemoState:
    state["workflow_step"] = "complete"
    return state


workflow = StateGraph(DemoState)
workflow.add_node("analyze", analyze)
workflow.add_node("escalate", escalate)
workflow.add_node("complete", complete)
workflow.set_entry_point("analyze")
workflow.add_conditional_edges(
    "analyze",
    route_after_analysis,
    {"escalate": "escalate", "complete": "complete"},
)
workflow.add_edge("escalate", END)
workflow.add_edge("complete", END)
langgraph_app = workflow.compile()


class LangGraphDemoRequest(BaseModel):
    vehicle_id: str = Field(default="DEMO-EY-001", min_length=3, max_length=64)
    scenario: Literal["normal", "high_temperature", "brake_warning"] = "high_temperature"


@app.post("/api/v1/demo/langgraph")
async def langgraph_demo(request: LangGraphDemoRequest) -> Dict[str, Any]:
    telemetry = {
        "normal": {"temperature": 90.0, "brake_warning": False},
        "high_temperature": {"temperature": 118.0, "brake_warning": False},
        "brake_warning": {"temperature": 92.0, "brake_warning": True},
    }[request.scenario]
    initial: DemoState = {
        "vehicle_id": request.vehicle_id,
        "scenario": request.scenario,
        **telemetry,
    }
    result = await langgraph_app.ainvoke(initial)
    return {
        "success": True,
        "vehicle_id": request.vehicle_id,
        "scenario": request.scenario,
        "orchestration": "LangGraph StateGraph + conditional routing",
        "validation": "Pydantic v2 request model",
        "api_runtime": "async FastAPI on Vercel",
        "agents_executed": ["analyze", result.get("workflow_step", "complete")],
        "escalated": result.get("workflow_step") == "human_escalation",
        "prediction": {
            "priority": result.get("priority"),
            "diagnosis": result.get("diagnosis"),
        },
        "workflow_step": result.get("workflow_step"),
        "error": None,
    }
