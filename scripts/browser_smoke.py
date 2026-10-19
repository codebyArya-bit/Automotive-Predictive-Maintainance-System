#!/usr/bin/env python3
"""End-to-end AutoMind smoke checks in real headless Chromium.

Install: pip install playwright && python -m playwright install chromium
Run: python scripts/browser_smoke.py
"""
import json
import re
import sys

from playwright.sync_api import sync_playwright

SITES = {
    "production": "https://frontend-eight-brown-42.vercel.app",
    "preview": "https://automind-mafb5ffbx-aryas-projects-6676c3c7.vercel.app",
}
ROLES = [
    (0, "rajesh@demo.com", "customer", "/customer-dashboard"),
    (1, "priya@demo.com", "service_staff", "/demand-forecast"),
    (2, "amit@demo.com", "manufacturing_engineer", "/manufacturing-dashboard"),
    (3, "sarah@demo.com", "system_admin", "/dashboard"),
]


def main():
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        for label, base in SITES.items():
            for index, email, role, destination in ROLES:
                context = browser.new_context()
                page = context.new_page()
                js_errors = []
                page.on("pageerror", lambda error: js_errors.append(str(error)))
                try:
                    page.goto(base + "/login", wait_until="domcontentloaded", timeout=45000)
                    page.get_by_role("heading", name="AutoMind AI").wait_for(timeout=20000)
                    cards = page.get_by_role("button", name="Quick Login")
                    assert cards.count() == 4, f"Expected four separate demo login buttons; got {cards.count()}"
                    cards.nth(index).click()
                    dialog = page.get_by_role("dialog")
                    dialog.wait_for(timeout=5000)
                    assert dialog.locator("#demo-email").input_value() == email
                    assert dialog.locator("#demo-password").input_value() == "demo123"
                    dialog.get_by_role("button", name="Continue").click()
                    page.wait_for_url(re.compile(re.escape(destination) + r"(?:[/?#].*)?$"), timeout=11000)
                    page.locator("#root").wait_for(timeout=15000)
                    session = page.evaluate("""() => ({
                        token: localStorage.getItem('auth_token'),
                        user: JSON.parse(localStorage.getItem('user') || 'null')
                    })""")
                    assert session["token"], "No token stored after login"
                    assert session["user"]["email"] == email and session["user"]["role"] == role
                    probe = page.evaluate("""async () => {
                        const r = await fetch('/api/v1/dashboard', {
                            headers: {Authorization: 'Bearer ' + localStorage.getItem('auth_token')}
                        });
                        return {status:r.status, payload:await r.json()};
                    }""")
                    assert probe["status"] == 200 and "system_metrics" in probe["payload"], str(probe)
                    assert not page.get_by_text("Something went wrong", exact=False).is_visible(), "UI error boundary visible"
                    assert not js_errors, "Unhandled browser errors: " + " | ".join(js_errors[:3])
                    print(f"PASS {label}: Chromium {email} quick-login, {destination}, session and dashboard")
                except Exception as exc:
                    diagnostic = page.evaluate("""() => ({
                        url:location.href,
                        storedEmail:(JSON.parse(localStorage.getItem('user') || 'null') || {}).email || null,
                        hasToken:!!localStorage.getItem('auth_token'),
                        visibleText:document.body.innerText.slice(0,800)
                    })""")
                    print(f"FAIL {label}: Chromium {email}: {type(exc).__name__}: {exc}; diagnostics={json.dumps(diagnostic)}; pageErrors={js_errors[:3]}")
                    failures.append(f"{label} {email}")
                finally:
                    context.close()

        # Real browser cross-origin preflight must make the error response readable.
        # Fetching preview from the production page verifies the preview's production allowlist.
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto(SITES["production"] + "/login", wait_until="domcontentloaded", timeout=45000)
            page.get_by_role("heading", name="AutoMind AI").wait_for(timeout=20000)
            result = page.evaluate("""async (url) => {
                try {
                    const r = await fetch(url + '/api/v1/auth/login', {
                        method:'POST',
                        headers:{'Content-Type':'application/json'},
                        body:JSON.stringify({email:'invalid@example.com',password:'invalid'})
                    });
                    return {status:r.status, text:(await r.text()).slice(0,150)};
                } catch (e) { return {error:String(e)}; }
            }""", SITES["preview"])
            assert result.get("status") == 401, f"Browser cross-origin preview POST failed: {result}"
            print("PASS Chromium: production origin -> preview login CORS preflight + readable 401")
        except Exception as exc:
            print("FAIL Chromium cross-origin request:", repr(exc))
            failures.append("cross-origin")
        finally:
            context.close()
            browser.close()

    if failures:
        print("FAILED tests:", ", ".join(failures))
        sys.exit(1)
    print("PASS: all Chromium smoke tests")


if __name__ == "__main__":
    main()
