#!/usr/bin/env python3
"""Contract tests for read-only synthetic AutoMind API (no mutations/persistence)."""
import json
import os
from urllib.request import Request,urlopen
from urllib.error import HTTPError

base=os.getenv("AUTOMIND_BASE","https://automind-ai-git-audit-recruiter-8056e4-aryas-projects-6676c3c7.vercel.app").rstrip("/")
def call(path,token="",body=None):
    headers={"Content-Type":"application/json"}
    if token:
        headers["Authorization"]="Bearer "+token
    req=Request(base+path,data=json.dumps(body).encode() if body is not None else None,
                headers=headers,method="POST" if body is not None else "GET")
    with urlopen(req,timeout=40) as r:
        assert r.status==200, (path,r.status)
        return json.load(r)

login=call("/api/v1/auth/login",body={"email":"rajesh@demo.com","password":"demo123"})
token=login["token"]
tests=[
 ("/api/v1/vehicles",lambda d:len(d["data"])>=3 and d["pagination"]["total"]>=3 and d["demo"]),
 ("/api/v1/vehicles/VEH001",lambda d:d["id"]=="VEH001" and d["demo"]),
 ("/api/v1/vehicles/VEH001/telemetry",lambda d:len(d["data"])>0),
 ("/api/v1/maintenance",lambda d:len(d["data"])>=2 and d["demo"]),
 ("/api/v1/alerts",lambda d:len(d["data"])>=2 and d["demo"]),
 ("/api/v1/agents",lambda d:len(d["data"])>=2 and d["demo"]),
 ("/api/v1/demand-forecast?days=7",lambda d:len(d["forecast"]["daily_forecast"])==7 and d["demo"]),
 ("/api/v1/service-centers/capacity",lambda d:len(d["capacity_analysis"]["center_analysis"])>0 and d["demo"]),
 ("/api/v1/rca-reports",lambda d:len(d["rca_capa_data"]["reports"])>0 and d["demo"]),
 ("/api/v1/logs",lambda d:d["demo"]),
 ("/api/v1/logs/stats",lambda d:d["demo"]),
 ("/api/v1/logs/suggestions",lambda d:d["demo"]),
 ("/api/v1/edge-cases/scenarios",lambda d:len(d["scenarios"])>0 and d["demo"]),
 ("/api/v1/dashboard/customer",lambda d:len(d["dashboard"]["vehicles"])>0 and d["demo"]),
 ("/api/v1/dashboard/manufacturing",lambda d:len(d["dashboard"]["quality_metrics"]["metrics"])>0 and d["demo"]),
]
for path,validate in tests:
    try:
        result=call(path,token)
        assert validate(result),result
        print("PASS",path,flush=True)
    except Exception as e:
        print("FAIL",path,str(e)[:500],flush=True)
        raise
for path,body in [
    ("/api/v1/edge-cases/run/high_temperature",{}),
    ("/api/v1/voice-agent/initiate-call",{"priority":"P1","vehicle_id":"VEH001","customer_id":"DEMO"})
]:
    result=call(path,token,body)
    assert result["demo"],result
    print("PASS",path,flush=True)
try:
    call("/api/v1/vehicles")
except HTTPError as err:
    assert err.code==401,err.code
    print("PASS protected demo API without token returns 401",flush=True)
else:
    raise AssertionError("Data exposed without authentication")
print("ALL SAMPLE API CONTRACT CHECKS PASS",flush=True)
