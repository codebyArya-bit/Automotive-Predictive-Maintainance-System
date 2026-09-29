"""
Extended API Endpoints for Enhanced Features
Authentication, Service Demand Forecasting, RCA/CAPA, Edge Cases, Voice Agent
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import auth and agents
from auth import AuthService, get_current_user, authenticate_user, get_demo_user_by_email, require_role, require_permission
from agents.service_demand_forecasting_agent import ServiceDemandForecastingAgent
from agents.rca_capa_agent import RCACAPAAgent
from edge_case_scenarios import EdgeCaseScenarios

# Create router
router = APIRouter(prefix="/api/v1", tags=["extended"])

# Initialize agents
demand_forecasting_agent = ServiceDemandForecastingAgent()
rca_capa_agent = RCACAPAAgent()
edge_case_scenarios = EdgeCaseScenarios()


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: Dict[str, Any]


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    User login endpoint
    Returns JWT token and user information
    """
    user = authenticate_user(request.email, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT token
    token = AuthService.create_token(user["id"], user["role"], user["email"])

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "role": user["role"],
            "role_data": user.get("role_data", {})
        }
    }


@router.get("/auth/me")
async def get_current_user_info(user: Dict = Depends(get_current_user)):
    """
    Get the currently authenticated user.

    Keep the response shape identical to /auth/login so the React auth
    provider can safely restore a session after refresh.
    """
    demo_user = get_demo_user_by_email(user["email"]) or {}
    return {
        "user": {
            "id": user["user_id"],
            "email": user["email"],
            "first_name": demo_user.get("first_name", ""),
            "last_name": demo_user.get("last_name", ""),
            "role": user["role"],
            "phone": demo_user.get("phone"),
            "role_data": demo_user.get("role_data", {})
        }
    }


@router.post("/auth/logout")
async def logout():
    """
    Idempotent logout for the stateless JWT demo.

    The browser clears its token locally. Keeping this endpoint independent
    of token validity prevents an expired token from breaking logout.
    """
    return {"message": "Logged out successfully"}


# ============================================================================
# SERVICE DEMAND FORECASTING ENDPOINTS
# ============================================================================

@router.get("/demand-forecast")
@require_role("service_staff", "system_admin", "fleet_manager")
async def get_demand_forecast(
    days: int = 30,
    user: Dict = Depends(get_current_user)
):
    """
    Get service demand forecast for specified number of days
    """
    from state import StateManager

    # Create full initial state for forecast generation
    state = StateManager.create_initial_state(vehicle_id="FORECAST_REQUEST", session_id="demand_forecast")
    state["current_agent"] = "service_demand_forecasting"
    state["workflow_step"] = "forecasting"

    # Run forecasting agent
    result_state = await demand_forecasting_agent.execute(state)

    if "demand_forecast" not in result_state:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate forecast"
        )

    return {
        "status": "success",
        "forecast": result_state["demand_forecast"],
        "generated_at": datetime.now().isoformat()
    }


@router.get("/demand-forecast/summary")
async def get_forecast_summary():
    """
    Get quick forecast summary (no auth required for demo)
    """
    summary = await demand_forecasting_agent.get_forecast_summary()
    return {
        "status": "success",
        "summary": summary
    }


@router.get("/service-centers/capacity")
@require_role("service_staff", "system_admin")
async def get_service_center_capacity(user: Dict = Depends(get_current_user)):
    """
    Get current service center capacity and utilization
    """
    # Get forecast to access capacity analysis
    from state import StateManager

    state = StateManager.create_initial_state(vehicle_id="CAPACITY_REQUEST", session_id="service_center_capacity")
    state["current_agent"] = "service_demand_forecasting"

    result_state = await demand_forecasting_agent.execute(state)

    capacity_analysis = result_state.get("demand_forecast", {}).get("capacity_analysis", {})

    return {
        "status": "success",
        "capacity_analysis": capacity_analysis,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# RCA/CAPA ENDPOINTS
# ============================================================================

@router.get("/rca-reports")
@require_role("manufacturing_engineer", "system_admin")
async def get_rca_reports(user: Dict = Depends(get_current_user)):
    """
    Get all RCA/CAPA reports (Manufacturing team only)
    """
    from state import StateManager

    # Generate RCA/CAPA analysis with complete initial state
    state = StateManager.create_initial_state(vehicle_id="RCA_REQUEST", session_id="rca_reports")
    state["current_agent"] = "rca_capa"

    result_state = await rca_capa_agent.execute(state)

    if "rca_capa" not in result_state:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate RCA/CAPA reports"
        )

    return {
        "status": "success",
        "rca_capa_data": result_state["rca_capa"],
        "generated_at": datetime.now().isoformat()
    }


@router.get("/rca-reports/{defect_id}")
@require_role("manufacturing_engineer", "system_admin")
async def get_rca_report_by_id(
    defect_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    Get specific RCA/CAPA report by defect ID
    """
    # Generate full analysis first with complete initial state
    from state import StateManager

    state = StateManager.create_initial_state(vehicle_id="RCA_REQUEST", session_id="rca_reports_detail")
    state["current_agent"] = "rca_capa"

    result_state = await rca_capa_agent.execute(state)
    rca_capa_data = result_state.get("rca_capa", {})

    # Find specific report
    for report in rca_capa_data.get("rca_reports", []):
        if report.get("defect_id") == defect_id:
            # Find corresponding CAPA
            capa = next(
                (c for c in rca_capa_data.get("capa_actions", []) if c.get("defect_id") == defect_id),
                None
            )
            return {
                "status": "success",
                "rca_report": report,
                "capa_actions": capa
            }

    raise HTTPException(
        status_code=404,
        detail=f"RCA report not found for defect_id: {defect_id}"
    )


@router.get("/recurring-defects")
@require_role("manufacturing_engineer", "system_admin", "service_staff")
async def get_recurring_defects(user: Dict = Depends(get_current_user)):
    """
    Get list of recurring defects across fleet
    """
    from state import StateManager

    state = StateManager.create_initial_state(vehicle_id="DEFECT_REQUEST", session_id="recurring_defects")
    state["current_agent"] = "rca_capa"

    result_state = await rca_capa_agent.execute(state)
    rca_capa_data = result_state.get("rca_capa", {})

    return {
        "status": "success",
        "recurring_defects": rca_capa_data.get("recurring_defects", []),
        "total_count": len(rca_capa_data.get("recurring_defects", []))
    }


@router.get("/manufacturing-feedback")
@require_role("manufacturing_engineer", "system_admin")
async def get_manufacturing_feedback(user: Dict = Depends(get_current_user)):
    """
    Get manufacturing feedback and improvement recommendations
    """
    from state import StateManager

    state = StateManager.create_initial_state(vehicle_id="FEEDBACK_REQUEST", session_id="manufacturing_feedback")
    state["current_agent"] = "rca_capa"

    result_state = await rca_capa_agent.execute(state)
    rca_capa_data = result_state.get("rca_capa", {})

    return {
        "status": "success",
        "manufacturing_feedback": rca_capa_data.get("manufacturing_feedback", {}),
        "impact_analysis": rca_capa_data.get("impact_analysis", {})
    }


# ============================================================================
# EDGE CASE SCENARIOS ENDPOINTS
# ============================================================================

@router.get("/edge-cases/scenarios")
async def list_edge_case_scenarios():
    """
    List all available edge case scenarios
    """
    scenarios = edge_case_scenarios.get_scenario_descriptions()
    return {
        "status": "success",
        "scenarios": scenarios
    }


@router.post("/edge-cases/run/{scenario_name}")
async def run_edge_case_scenario(scenario_name: str):
    """
    Run a specific edge case scenario for demonstration
    """
    try:
        result = await edge_case_scenarios.run_scenario(scenario_name)
        return {
            "status": "success",
            "result": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run scenario: {str(e)}"
        )


# ============================================================================
# VOICE AGENT ENDPOINTS
# ============================================================================

class VoiceCallRequest(BaseModel):
    vehicle_id: str
    customer_id: str
    priority: str  # P0, P1, P2, P3


@router.post("/voice-agent/initiate-call")
@require_role("customer", "service_staff", "system_admin")
async def initiate_voice_call(
    request: VoiceCallRequest,
    user: Dict = Depends(get_current_user)
):
    """
    Simulate voice agent call initiation
    Returns pre-scripted conversation flow
    """
    # Generate conversation based on priority
    if request.priority in ["P0", "P1"]:
        conversation_type = "urgent"
        opening = "URGENT: This is AutoMind Emergency System."
    else:
        conversation_type = "routine"
        opening = "Hello, this is Maya from AutoMind."

    conversation = {
        "call_id": f"CALL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "vehicle_id": request.vehicle_id,
        "customer_id": request.customer_id,
        "priority": request.priority,
        "conversation_type": conversation_type,
        "initiated_at": datetime.now().isoformat(),
        "status": "in_progress",
        "conversation_script": _generate_conversation_script(request.priority),
    }

    return {
        "status": "success",
        "call": conversation
    }


def _generate_conversation_script(priority: str) -> List[Dict]:
    """Generate conversation script based on priority"""

    if priority == "P0":
        return [
            {"speaker": "agent", "text": "URGENT: This is AutoMind Emergency System. Your vehicle has a critical engine failure!", "timestamp": 0, "emotion": "urgent"},
            {"speaker": "customer", "text": "What? What should I do?", "timestamp": 3, "emotion": "concerned"},
            {"speaker": "agent", "text": "Pull over IMMEDIATELY and turn off the engine. Towing service is being dispatched to your location now.", "timestamp": 6, "emotion": "urgent"},
            {"speaker": "customer", "text": "Okay, I'm pulling over now!", "timestamp": 10, "emotion": "alarmed"},
            {"speaker": "agent", "text": "Good. Stay safe. Tow truck ETA is 20 minutes. You'll receive live tracking via SMS.", "timestamp": 12, "emotion": "reassuring"},
        ]

    elif priority == "P1":
        return [
            {"speaker": "agent", "text": "Hello, this is Maya from AutoMind. I'm calling regarding an important maintenance alert for your vehicle.", "timestamp": 0, "emotion": "professional"},
            {"speaker": "customer", "text": "Yes, what's the issue?", "timestamp": 3, "emotion": "neutral"},
            {"speaker": "agent", "text": "Our system detected that your brake pads are wearing critically and need immediate replacement within 3 days to ensure your safety.", "timestamp": 5, "emotion": "concerned"},
            {"speaker": "customer", "text": "That sounds serious. When can I bring it in?", "timestamp": 10, "emotion": "concerned"},
            {"speaker": "agent", "text": "I can book you for tomorrow morning at 9 AM at Metro Service Center. The service will take about 45 minutes. Does this work for you?", "timestamp": 12, "emotion": "helpful"},
            {"speaker": "customer", "text": "Yes, that works. Please book it.", "timestamp": 17, "emotion": "agreeing"},
            {"speaker": "agent", "text": "Perfect! Your appointment is confirmed. You'll receive a confirmation SMS with all details. Drive safely!", "timestamp": 19, "emotion": "friendly"},
        ]

    else:  # P2, P3
        return [
            {"speaker": "agent", "text": "Hello Mr. Kumar, this is Maya from AutoMind. How are you today?", "timestamp": 0, "emotion": "friendly"},
            {"speaker": "customer", "text": "I'm good, thanks. What's this about?", "timestamp": 3, "emotion": "curious"},
            {"speaker": "agent", "text": "I'm calling regarding your Honda Civic. Our predictive system analyzed your vehicle's health and detected that brake pad replacement will be needed within 2 weeks.", "timestamp": 5, "emotion": "informative"},
            {"speaker": "customer", "text": "Oh, is it urgent?", "timestamp": 12, "emotion": "curious"},
            {"speaker": "agent", "text": "Not urgent, but we recommend scheduling within 2 weeks for optimal safety. This is routine maintenance based on your 75,000 miles.", "timestamp": 14, "emotion": "reassuring"},
            {"speaker": "customer", "text": "I see. What are my options?", "timestamp": 20, "emotion": "interested"},
            {"speaker": "agent", "text": "We have weekend slots available. Would Saturday morning at 9 AM work for you? The service takes only 45 minutes and costs approximately $180.", "timestamp": 22, "emotion": "helpful"},
            {"speaker": "customer", "text": "Saturday morning works. Let's book it.", "timestamp": 28, "emotion": "agreeing"},
            {"speaker": "agent", "text": "Excellent! Your appointment is confirmed for Saturday 9 AM. You'll receive a confirmation SMS and calendar invite. Thank you for choosing AutoMind!", "timestamp": 30, "emotion": "friendly"},
        ]


@router.get("/voice-agent/call-history")
@require_role("customer", "service_staff", "system_admin")
async def get_call_history(
    customer_id: Optional[str] = None,
    user: Dict = Depends(get_current_user)
):
    """
    Get voice call history
    """
    # Mock call history
    calls = [
        {
            "call_id": "CALL-20251106001",
            "vehicle_id": "7ALSE94T6W43T3254",
            "customer_id": "user_customer_1",
            "priority": "P2",
            "outcome": "appointment_booked",
            "duration_seconds": 120,
            "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            "call_id": "CALL-20251105002",
            "vehicle_id": "1TS0ANPS9KCNX8996",
            "customer_id": "user_customer_1",
            "priority": "P0",
            "outcome": "emergency_handled",
            "duration_seconds": 45,
            "timestamp": (datetime.now() - timedelta(days=2)).isoformat()
        }
    ]

    # Filter by customer_id if provided and user is customer
    if user["role"] == "customer" or customer_id:
        filter_customer_id = customer_id or user["user_id"]
        calls = [c for c in calls if c["customer_id"] == filter_customer_id]

    return {
        "status": "success",
        "calls": calls,
        "total_count": len(calls)
    }


# ============================================================================
# ROLE-SPECIFIC DASHBOARD ENDPOINTS
# ============================================================================

@router.get("/dashboard/customer")
@require_role("customer")
async def get_customer_dashboard(user: Dict = Depends(get_current_user)):
    """
    Get customer-specific dashboard data
    """
    return {
        "status": "success",
        "dashboard": {
            "user": {
                "name": "Rajesh Kumar",
                "vehicles_count": 1
            },
            "alerts": {
                "total": 2,
                "critical": 0,
                "warning": 1,
                "info": 1
            },
            "appointments": {
                "upcoming": 1,
                "completed": 5
            },
            "recent_activity": [
                {"type": "alert", "message": "Brake pad maintenance recommended", "date": "2025-11-05"},
                {"type": "appointment", "message": "Oil change completed", "date": "2025-10-15"}
            ]
        }
    }


@router.get("/dashboard/service-staff")
@require_role("service_staff")
async def get_service_staff_dashboard(user: Dict = Depends(get_current_user)):
    """
    Get service staff dashboard data
    """
    return {
        "status": "success",
        "dashboard": {
            "today_appointments": 12,
            "pending_services": 3,
            "completed_today": 9,
            "service_bays": {
                "total": 8,
                "occupied": 5,
                "available": 3
            },
            "workload_status": "normal"
        }
    }


@router.get("/dashboard/manufacturing")
@require_role("manufacturing_engineer", "system_admin")
async def get_manufacturing_dashboard(user: Dict = Depends(get_current_user)):
    """
    Get manufacturing engineer dashboard data
    """
    from state import StateManager

    # Initialize complete state to avoid missing keys
    state = StateManager.create_initial_state(vehicle_id="DASHBOARD_REQUEST", session_id="manufacturing_dashboard")
    state["current_agent"] = "rca_capa"

    result_state = await rca_capa_agent.execute(state)
    rca_capa_data = result_state.get("rca_capa", {})

    return {
        "status": "success",
        "dashboard": {
            "recurring_defects_count": len(rca_capa_data.get("recurring_defects", [])),
            "open_rca_reports": len(rca_capa_data.get("rca_reports", [])),
            "pending_capa_actions": sum(
                len(c.get("corrective_actions", [])) + len(c.get("preventive_actions", []))
                for c in rca_capa_data.get("capa_actions", [])
            ),
            "impact_analysis": rca_capa_data.get("impact_analysis", {}),
            "quality_metrics": {
                "current_defect_rate": rca_capa_data.get("impact_analysis", {}).get("current_defect_rate_pct", 0),
                "target_defect_rate": rca_capa_data.get("impact_analysis", {}).get("target_defect_rate_pct", 0),
                "improvement_target": rca_capa_data.get("impact_analysis", {}).get("defect_rate_reduction_target_pct", 0)
            }
        }
    }


@router.get("/dashboard/admin")
@require_role("system_admin")
async def get_admin_dashboard(user: Dict = Depends(get_current_user)):
    """
    Get system admin dashboard data
    """
    return {
        "status": "success",
        "dashboard": {
            "system_health": "healthy",
            "agents_status": {
                "total": 7,
                "active": 7,
                "errors": 0
            },
            "ueba_alerts": {
                "total_today": 0,
                "critical": 0,
                "warning": 0
            },
            "circuit_breakers": {
                "total": 9,
                "open": 0,
                "half_open": 0,
                "closed": 9
            },
            "performance_metrics": {
                "avg_response_time_ms": 245,
                "requests_today": 1247,
                "success_rate_pct": 99.8
            }
        }
    }
