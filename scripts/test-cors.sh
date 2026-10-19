#!/usr/bin/env bash
# Check AutoMind public API availability and browser CORS behavior.
# Usage: bash scripts/test-cors.sh [API_BASE_URL] [FRONTEND_ORIGIN]
set -euo pipefail
BASE="${1:-https://frontend-eight-brown-42.vercel.app}"
ORIGIN="${2:-https://frontend-eight-brown-42.vercel.app}"
BASE="${BASE%/}"
ORIGIN="${ORIGIN%/}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }
pass() { printf 'PASS: %s\n' "$*"; }
request() {
  local name="$1"; shift
  curl -sS --max-time 25 -D "$TMP/$name.headers" -o "$TMP/$name.body" -w '%{http_code}' "$@" || fail "Cannot reach API (DNS, TLS or network issue)"
}
header() {
  local key="$1" file="$2"
  grep -i "^$key:" "$file" | tail -1 | cut -d: -f2- | tr -d '\r' | sed 's/^[[:space:]]*//' || true
}
echo "API: $BASE"
echo "Browser origin: $ORIGIN"
status="$(request health "$BASE/api/v1/health")"
[[ "$status" == "200" ]] || { cat "$TMP/health.body" >&2; fail "Health returned HTTP $status (API routing/deployment, not necessarily CORS)"; }
grep -q '"status"' "$TMP/health.body" || fail 'Health response not JSON health payload'
pass "Health endpoint HTTP 200"

status="$(request preflight -X OPTIONS "$BASE/api/v1/auth/login" -H "Origin: $ORIGIN" -H 'Access-Control-Request-Method: POST' -H 'Access-Control-Request-Headers: content-type,authorization')"
[[ "$status" == "200" || "$status" == "204" ]] || { cat "$TMP/preflight.body" >&2; fail "Preflight HTTP $status"; }
[[ "$(header access-control-allow-origin "$TMP/preflight.headers")" == "$ORIGIN" ]] || fail 'Preflight missing/mismatched Access-Control-Allow-Origin'
methods="$(header access-control-allow-methods "$TMP/preflight.headers")"
[[ ",${methods^^}," == *"POST"* ]] || fail 'Preflight missing POST allowed method'
headers="$(header access-control-allow-headers "$TMP/preflight.headers")"
[[ "${headers,,}" == *"content-type"* ]] || fail 'Preflight missing content-type header'
pass 'Browser preflight allows expected origin/method/headers'

# Invalid credentials are deliberate: response must not be a misleading 200.
status="$(request post -X POST "$BASE/api/v1/auth/login" -H "Origin: $ORIGIN" -H 'Content-Type: application/json' -d '{"email":"invalid@example.com","password":"invalid"}')"
[[ "$status" == "401" ]] || { cat "$TMP/post.body" >&2; fail "Invalid login expected 401, got $status"; }
[[ "$(header access-control-allow-origin "$TMP/post.headers")" == "$ORIGIN" ]] || fail 'Actual POST missing/mismatched CORS origin header'
pass 'Actual POST returns expected 401 with CORS headers'
echo 'All API and CORS smoke tests passed.'
