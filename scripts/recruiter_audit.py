#!/usr/bin/env python3
"""Read-only recruiter walkthrough of the deployed AutoMind demo.

Checks visible page routing, exceptions and unexpected failed API requests.
This script intentionally does not mutate demo data.
"""
import json
import os
import re
import sys
from collections import Counter
from playwright.sync_api import sync_playwright

BASE = os.environ.get("AUTOMIND_BASE", "https://frontend-eight-brown-42.vercel.app").rstrip("/")
ROLES = [
    ("customer", "rajesh@demo.com", 0, ["/customer-dashboard", "/schedule-service", "/service-history", "/vehicles", "/maintenance", "/alerts", "/voice-agent", "/demo", "/demo-analytics", "/edge-cases"]),
    ("service", "priya@demo.com", 1, ["/demand-forecast", "/vehicles", "/maintenance", "/alerts"]),
    ("manufacturing", "amit@demo.com", 2, ["/manufacturing-dashboard", "/recurring-defects", "/quality-metrics", "/rca-reports", "/logs"]),
    ("admin", "sarah@demo.com", 3, ["/dashboard", "/agents", "/logs", "/analytics", "/vehicles", "/maintenance", "/alerts", "/demo", "/demo-analytics", "/edge-cases", "/rca-reports"]),
]

def clean_url(url):
    return url.replace(BASE, "").split("?")[0]

def report(label, obj):
    print(label + " " + json.dumps(obj, ensure_ascii=True, sort_keys=True), flush=True)

failures=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True, args=["--no-sandbox"])
    for role,email,index,pages in ROLES:
        context=browser.new_context()
        page=context.new_page()
        events={"console":[],"pageerrors":[],"api":[],"requestfailed":[]}
        page.on("pageerror",lambda e:events["pageerrors"].append(str(e)))
        page.on("console",lambda m:events["console"].append(m.text) if m.type=="error" else None)
        page.on("response",lambda r:events["api"].append((r.status,clean_url(r.url))) if r.status>=400 and "/api/" in r.url else None)
        page.on("requestfailed",lambda r:events["requestfailed"].append((clean_url(r.url),r.failure)))
        try:
            page.goto(BASE+"/login", wait_until="domcontentloaded",timeout=45000)
            page.get_by_role("heading",name="AutoMind AI").wait_for(timeout=15000)
            page.get_by_role("button", name="Quick Login").nth(index).click()
            page.get_by_role("dialog").get_by_role("button",name="Continue").click()
            page.wait_for_function("""() => location.pathname !== '/login' && !!localStorage.getItem('auth_token')""",timeout=35000)
            report("LOGIN",{"role":role,"path":page.url,"user":page.evaluate("JSON.parse(localStorage.getItem('user')).email")})
        except Exception as ex:
            report("LOGIN_FAIL",{"role":role,"message":str(ex)[:400],"url":page.url})
            failures.append(role+" login")
            context.close()
            continue
        for path in pages:
            before={k:len(v) for k,v in events.items()}
            try:
                page.goto(BASE+path,wait_until="domcontentloaded",timeout=25000)
                page.wait_for_timeout(2600)
                data=page.evaluate("""() => ({
                    pathname: location.pathname,
                    text: document.body.innerText.trim().slice(0,260),
                    title: document.title,
                    token: !!localStorage.getItem('auth_token'),
                    loadingText: /loading (your|forecast|manufacturing|vehicle|analytics|maintenance|alert)/i.test(document.body.innerText)
                })""")
                new={k:v[before[k]:] for k,v in events.items()}
                result={"role":role,"route":path,"actual":data["pathname"],"hasToken":data["token"],"loading":data["loadingText"],"apiErrors":new["api"][:7],"jsErrors":new["pageerrors"][:3],"failedNetwork":new["requestfailed"][:3],"excerpt":data["text"]}
                report("PAGE",result)
                if data["pathname"]!=path or not data["token"] or new["api"] or new["pageerrors"] or new["requestfailed"] or data["loadingText"]:
                    failures.append(role+" "+path)
            except Exception as ex:
                report("PAGE_FAIL",{"role":role,"route":path,"url":page.url,"exception":str(ex)[:500]})
                failures.append(role+" "+path)
        context.close()
    browser.close()
report("SUMMARY",{"testedPages":sum(len(r[3]) for r in ROLES),"failedPages":len(failures),"failures":failures})
if failures:
    sys.exit(1)
