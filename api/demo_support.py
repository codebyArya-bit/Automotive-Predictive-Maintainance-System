"""Deterministic read-only demonstration API for the Vercel showcase.

These responses are SYNTHETIC, not live telemetry or real vehicle data.
Mutations require a persistent backend and are intentionally not exposed here.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable
from fastapi import APIRouter, Depends, HTTPException, Query

VEHICLES = [
    {"id":"VEH001","vin":"5YJ3E1EA7KF000001","make":"Tesla","model":"Model 3","year":2023,"status":"active","mileage":18300,"registration_date":"2023-04-01T00:00:00Z"},
    {"id":"VEH002","vin":"1HGCM82633A000002","make":"Honda","model":"Civic","year":2022,"status":"maintenance","mileage":42000,"registration_date":"2022-05-01T00:00:00Z"},
    {"id":"VEH003","vin":"JTNB11HK6K3000003","make":"Toyota","model":"Camry","year":2024,"status":"warning","mileage":12900,"registration_date":"2024-02-01T00:00:00Z"},
]
MAINTENANCE = [
    {"id":"MAINT001","vehicle_id":"VEH001","service_type":"Battery Inspection","description":"Routine battery inspection (sample)","start_date":"2026-11-03T10:00:00Z","end_date":None,"cost":120,"technician":"Demo Technician","status":"scheduled","priority":"medium","notes":"Synthetic demonstration record"},
    {"id":"MAINT002","vehicle_id":"VEH002","service_type":"Brake Service","description":"Brake pad evaluation (sample)","start_date":"2026-10-12T08:00:00Z","end_date":"2026-10-12T13:00:00Z","cost":290,"technician":"Demo Technician","status":"completed","priority":"high","notes":"Synthetic demonstration record"},
    {"id":"MAINT003","vehicle_id":"VEH003","service_type":"Engine Inspection","description":"Temperature anomaly follow-up (sample)","start_date":"2026-10-27T09:00:00Z","end_date":None,"cost":150,"technician":"Demo Technician","status":"scheduled","priority":"high","notes":"Synthetic demonstration record"},
]
ALERTS = [
    {"id":"ALERT001","vehicleId":"VEH002","vehicle_id":"VEH002","severity":"high","status":"open","type":"maintenance","title":"Brake Inspection Due","description":"Sample brake inspection alert","message":"Sample brake inspection alert","acknowledged":False,"resolved":False,"createdAt":"2026-10-18T10:00:00Z","timestamp":"2026-10-18T10:00:00Z"},
    {"id":"ALERT002","vehicleId":"VEH003","vehicle_id":"VEH003","severity":"critical","status":"open","type":"diagnostic","title":"Temperature Warning","description":"Simulated engine temperature anomaly","message":"Simulated engine temperature anomaly","acknowledged":False,"resolved":False,"createdAt":"2026-10-18T12:00:00Z","timestamp":"2026-10-18T12:00:00Z"},
]
AGENTS = [
    {"id":"agent-diagnostics","name":"Diagnosis Agent","type":"diagnostic","status":"active","description":"Illustrative diagnostic agent","lastActivity":"2026-10-19T10:00:00Z","tasksCompleted":128,"successRate":97.0},
    {"id":"agent-forecast","name":"Forecasting Agent","type":"predictive","status":"active","description":"Illustrative forecasting agent","lastActivity":"2026-10-19T10:00:00Z","tasksCompleted":94,"successRate":95.0},
    {"id":"agent-support","name":"Engagement Agent","type":"support","status":"idle","description":"Illustrative customer agent","lastActivity":"2026-10-19T10:00:00Z","tasksCompleted":61,"successRate":99.0},
]
SCENARIOS = [
    {"scenario_name":"high_temperature","description":"Simulated high engine temperature escalated for review","category":"vehicle_safety","priority":"high","icon":"🌡️"},
    {"scenario_name":"brake_warning","description":"Simulated brake warning routed to service","category":"maintenance","priority":"high","icon":"🛞"},
    {"scenario_name":"normal","description":"Simulated normal telemetry monitoring","category":"vehicle_safety","priority":"low","icon":"🚗"},
]


def page_of(items: list[dict[str, Any]], page: int, limit: int) -> dict[str, Any]:
    page=max(1,page)
    limit=max(1,min(limit,100))
    total=len(items)
    return {"data":items[(page-1)*limit:page*limit],"pagination":{"page":page,"limit":limit,"total":total,"pages":(total+limit-1)//limit},"demo":True}


def create_demo_router(auth_dependency: Callable[..., Any]) -> APIRouter:
    router=APIRouter(prefix="/api/v1",dependencies=[Depends(auth_dependency)])

    @router.get("/vehicles")
    async def vehicles(page:int=1,limit:int=10,status:str|None=None,search:str|None=None):
        items=VEHICLES
        if status and status!="all":
            items=[v for v in items if v["status"]==status]
        if search:
            items=[v for v in items if search.lower() in (v["make"]+" "+v["model"]+" "+v["vin"]).lower()]
        return page_of(items,page,limit)

    @router.get("/vehicles/{vehicle_id}")
    async def vehicle_detail(vehicle_id:str):
        for vehicle in VEHICLES:
            if vehicle_id in (vehicle["id"],vehicle["vin"]):
                return {**vehicle,"demo":True}
        raise HTTPException(status_code=404,detail="No such sample vehicle")

    @router.get("/vehicles/{vehicle_id}/telemetry")
    async def telemetry(vehicle_id:str,limit:int=30):
        if not any(v["id"]==vehicle_id for v in VEHICLES):
            raise HTTPException(status_code=404,detail="No such sample vehicle")
        now=datetime.now(timezone.utc)
        items=[{"vehicle_id":vehicle_id,"engine_temp":84+(i%7),"oil_pressure":36+(i%3),"coolant_temp":82+(i%5),"engine_rpm":1400+(i%10)*55,"speed":50+(i%8),"fuel_level":70-i%10,"battery_voltage":12.4,"odometer":18300+i,"timestamp":(now-timedelta(minutes=i*5)).isoformat()} for i in range(min(max(limit,1),100))]
        return page_of(items,1,min(max(limit,1),100))

    @router.get("/maintenance")
    async def maintenance(page:int=1,limit:int=10,status:str|None=None,vehicle_id:str|None=None):
        items=MAINTENANCE
        if status and status!="all": items=[x for x in items if x["status"]==status]
        if vehicle_id: items=[x for x in items if x["vehicle_id"]==vehicle_id]
        return page_of(items,page,limit)

    @router.get("/alerts")
    async def alerts(page:int=1,limit:int=20,severity:str|None=None,status:str|None=None,vehicle_id:str|None=None):
        items=ALERTS
        if severity and severity!="all": items=[x for x in items if x["severity"]==severity]
        if status and status!="all": items=[x for x in items if x["status"]==status]
        if vehicle_id: items=[x for x in items if x["vehicle_id"]==vehicle_id]
        return page_of(items,page,limit)

    @router.get("/agents")
    async def agents():
        return {"data":AGENTS,"demo":True}

    @router.get("/agents/{agent_id}/status")
    async def agent_status(agent_id:str):
        for agent in AGENTS:
            if agent["id"]==agent_id: return {"data":agent,"demo":True}
        raise HTTPException(status_code=404,detail="Unknown sample agent")

    @router.get("/demand-forecast")
    async def demand_forecast(days:int=30):
        days=max(1,min(days,90))
        demand=[8+(i%7)*2 for i in range(days)]
        return {"status":"demo","demo":True,"forecast":{"daily_forecast":demand,"forecast_period_days":days},"generated_at":datetime.now(timezone.utc).isoformat()}

    @router.get("/service-centers/capacity")
    async def capacity():
        return {"status":"demo","demo":True,"capacity_analysis":{"center_analysis":{
            "Bengaluru_Central":{"capacity":24,"forecasted_demand":19,"forecasted_utilization":79},
            "Bengaluru_North":{"capacity":18,"forecasted_demand":14,"forecasted_utilization":78}},
            "capacity_warnings":[{"severity":"low","message":"Synthetic demand projection, for demonstration only","recommendation":"Review staffing before any real deployment"}]}}

    @router.get("/rca-reports")
    async def rca_reports():
        report={"defect_id":"RCA-DEMO-001","defect_type":"Brake wear variation","component":"Brake Assembly","vehicles_affected":12,
        "recurring_pattern":{"frequency":3,"trend":"stable","severity":"medium"},
        "root_cause_analysis":{"problem_statement":"Synthetic recurring brake wear example","rca_method":"5 Whys (illustration)","five_why_analysis":["Variable wear","Uneven brake contact","Calibration variation","Inspection timing","Review maintenance process"],"root_cause":"Illustrative calibration variation"},
        "corrective_actions":[{"action_id":"CA1","description":"Inspect sample calibration","responsible_party":"Demo QC","timeline":"7 days","status":"planned"}],
        "preventive_actions":[{"action_id":"PA1","description":"Add scheduled inspection","responsible_party":"Demo QA","implementation_date":"2026-11-01","status":"planned"}],
        "manufacturing_feedback":{"process_improvements":["Review process parameters"],"quality_control_updates":["Add inspection checkpoint"],"supplier_actions":["Review sample part specifications"]},
        "impact_analysis":{"expected_defect_reduction":"Illustrative only","estimated_cost_savings":"Not estimated","implementation_cost":"Not estimated","roi":"N/A","quality_improvement_score":84}}
        return {"rca_capa_data":{"reports":[report]},"demo":True}

    @router.get("/logs")
    async def logs():
        return {"items":[],"total":0,"demo":True,"message":"Live WebSocket logs are unavailable in this serverless demonstration."}

    @router.get("/logs/stats")
    async def logs_stats():
        return {"total":0,"errors":0,"warnings":0,"infos":0,"demo":True}

    @router.get("/logs/suggestions")
    async def logs_suggestions():
        return {"items":[],"demo":True}

    @router.get("/edge-cases/scenarios")
    async def edge_scenarios():
        return {"scenarios":SCENARIOS,"demo":True}

    @router.post("/edge-cases/run/{scenario_name}")
    async def run_edge_case(scenario_name:str):
        chosen=next((x for x in SCENARIOS if x["scenario_name"]==scenario_name),None)
        if chosen is None:
            raise HTTPException(status_code=404,detail="Unknown demo scenario")
        return {"demo":True,"scenario":{"scenario_name":scenario_name,"description":chosen["description"],
        "steps":[{"step":1,"action":"Classify sample telemetry","details":{"source":"synthetic input"},"outcome":"Scenario classified"},
                 {"step":2,"action":"Route to simulated diagnostic agent","details":{"severity":chosen["priority"]},"outcome":"Sample diagnosis generated"},
                 {"step":3,"action":"Produce illustrative recommendation","details":{"review_required":True},"outcome":"Review suggested"}],
        "business_impact":{"customer_satisfaction":"Not measured","cost_impact":"Not measured","time_saved":"Not measured"},
        "key_learnings":["This is a scenario simulation, not real sensor monitoring."]}}

    @router.post("/voice-agent/initiate-call")
    async def voice_call(payload:dict[str,Any]):
        priority=str(payload.get("priority","P2"))
        return {"demo":True,"call":{"call_id":"DEMO-CALL-001","status":"active","priority":priority,
        "vehicle_id":payload.get("vehicle_id","VEH001"),"customer_id":payload.get("customer_id","demo"),
        "conversation_script":{"priority":priority,"urgency_level":"high" if priority in ("P0","P1") else "normal",
        "conversation":[{"speaker":"agent","text":"Hello, this is a simulated AutoMind service call."},{"speaker":"customer","text":"What do you recommend?"},{"speaker":"agent","text":"Please arrange a qualified technician inspection."}],
        "key_points":["Demonstration only; no real call is placed"],"expected_outcome":"human_review"}}}

    @router.get("/voice-agent/call-history")
    async def voice_history():
        return {"calls":[],"demo":True}

    @router.post("/agents/{agent_id}/restart")
    @router.post("/agents/{agent_id}/pause")
    async def deny_agent_mutation(agent_id:str):
        raise HTTPException(status_code=409,detail="Demo is read-only: live agents cannot be controlled")

    return router
