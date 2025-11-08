"""
Centralized Logging System with JSONL persistence, in-memory ring buffer,
query/filter endpoints, suggestions engine, and WebSocket broadcasting hook.

Exposes:
- logs_router: FastAPI APIRouter with /api/v1/logs endpoints
- LoggingMiddleware: ASGI middleware to capture HTTP request/response logs
- logs_manager: singleton LogsManager for ingestion, querying, and suggestions

This module is lightweight and avoids DB dependencies; it writes to logs/logs.jsonl
and keeps a bounded in-memory deque for performance.
"""

from __future__ import annotations

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from collections import deque, defaultdict

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

try:
    # Reuse structured logging config if available
    from monitoring import StructuredLogger
    _structured_logger = StructuredLogger()
    _logger = _structured_logger.logger
except Exception:
    # Fallback to simple print-like logger
    import logging
    _logger = logging.getLogger(__name__)


class LogEntry(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    level: str = Field(default="info")  # debug|info|warning|error|critical
    event_type: str = Field(default="event")
    message: str = Field(default="")
    source: str = Field(default="backend")
    context: Dict[str, Any] = Field(default_factory=dict)


class Suggestion(BaseModel):
    id: str
    title: str
    description: str
    priority: str  # high|medium|low
    category: str  # auth|websocket|api|performance|security|compliance|other
    actions: List[str] = Field(default_factory=list)
    score: float = 0.0
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class LogsManager:
    def __init__(self, ring_size: int = 5000, file_path: str = "logs/logs.jsonl"):
        self.ring: deque[LogEntry] = deque(maxlen=ring_size)
        self.file_path = file_path
        self._broadcast: Optional[Callable[[Dict[str, Any]], Any]] = None
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def set_broadcast(self, callback: Callable[[Dict[str, Any]], Any]):
        """Set async or sync broadcast callback for real-time streaming."""
        self._broadcast = callback

    def ingest(self, entry: LogEntry):
        # Append to in-memory ring
        self.ring.append(entry)

        # Persist to JSONL (simple append; fast enough for moderate volumes)
        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(entry.model_dump_json() + "\n")
        except Exception as e:
            _logger.error("Failed to persist log entry", error=str(e))

        # Broadcast real-time update if available
        if self._broadcast:
            try:
                payload = {"type": "log_event", "data": entry.model_dump()}
                result = self._broadcast(payload)
                # Support async callbacks
                if asyncio.iscoroutine(result):
                    asyncio.create_task(result)
            except Exception as e:
                _logger.error("Failed to broadcast log entry", error=str(e))

    def get_recent(self, limit: int = 200) -> List[Dict[str, Any]]:
        items = list(self.ring)[-limit:]
        return [i.model_dump() for i in items]

    def query(
        self,
        level: Optional[str] = None,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
        since: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        since_dt: Optional[datetime] = None
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            except Exception:
                since_dt = None

        def match(e: LogEntry) -> bool:
            if level and e.level.lower() != level.lower():
                return False
            if event_type and e.event_type != event_type:
                return False
            if source and e.source != source:
                return False
            if since_dt:
                try:
                    if datetime.fromisoformat(e.timestamp.replace("Z", "+00:00")) < since_dt:
                        return False
                except Exception:
                    pass
            if search:
                hay = (e.message or "") + json.dumps(e.context, ensure_ascii=False)
                if search.lower() not in hay.lower():
                    return False
            return True

        filtered = [i for i in self.ring if match(i)]
        return [i.model_dump() for i in filtered[-limit:]]

    def stats(self, window_minutes: int = 60) -> Dict[str, Any]:
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=window_minutes)
        level_counts = defaultdict(int)
        type_counts = defaultdict(int)
        errors: List[LogEntry] = []

        for e in self.ring:
            try:
                ts = datetime.fromisoformat(e.timestamp.replace("Z", "+00:00"))
            except Exception:
                ts = now
            if ts < cutoff:
                continue
            level_counts[e.level] += 1
            type_counts[e.event_type] += 1
            if e.level in ("error", "critical"):
                errors.append(e)

        return {
            "levels": level_counts,
            "types": type_counts,
            "errors": [e.model_dump() for e in errors[-50:]],
            "window_minutes": window_minutes,
            "timestamp": now.isoformat(),
        }

    def suggestions(self, recent_n: int = 300) -> List[Suggestion]:
        recent = list(self.ring)[-recent_n:]

        # Simple pattern detection
        counts = defaultdict(int)
        ws_disconnects = 0
        auth_401 = 0
        http_500 = 0
        slow_requests = 0

        for e in recent:
            counts[(e.event_type, e.level)] += 1
            if e.context.get("status_code") == 401 or "401" in e.message:
                auth_401 += 1
            if e.context.get("status_code") and int(e.context["status_code"]) >= 500:
                http_500 += 1
            if e.event_type == "websocket" and "close" in (e.message or "").lower():
                ws_disconnects += 1
            # naive slow request detection
            dur = e.context.get("duration_ms")
            if isinstance(dur, (int, float)) and dur > 1000:
                slow_requests += 1

        suggestions: List[Suggestion] = []

        if auth_401 >= 3:
            suggestions.append(
                Suggestion(
                    id="auth-verify-token",
                    title="Repeated 401 responses detected",
                    description="Authenticated requests are failing. Verify token storage and Authorization header injection.",
                    priority="high",
                    category="auth",
                    actions=[
                        "Confirm login POST path is /api/v1/auth/login",
                        "Ensure localStorage 'auth_token' is set on login",
                        "Check Axios interceptor sets 'Authorization: Bearer <token>'",
                    ],
                    score=min(1.0, auth_401 / 10.0),
                )
            )

        if ws_disconnects >= 3:
            suggestions.append(
                Suggestion(
                    id="ws-stability",
                    title="Frequent WebSocket disconnects",
                    description="Live updates disconnect often. Align ws URL and enable keepalive/retry.",
                    priority="medium",
                    category="websocket",
                    actions=[
                        "Use centralized config.wsUrl for all sockets",
                        "Send periodic pings or use built-in reconnection hook",
                    ],
                    score=min(1.0, ws_disconnects / 10.0),
                )
            )

        if http_500 >= 1:
            suggestions.append(
                Suggestion(
                    id="backend-500",
                    title="Server errors observed",
                    description="Investigate recent 5xx responses and review backend traces.",
                    priority="high",
                    category="api",
                    actions=[
                        "Check uvicorn error logs for stack traces",
                        "Validate request payloads and database connections",
                    ],
                    score=min(1.0, http_500 / 5.0),
                )
            )

        if slow_requests >= 5:
            suggestions.append(
                Suggestion(
                    id="perf-slow-req",
                    title="Potential API performance issue",
                    description="Many requests exceed 1s. Consider indexing, caching, or batching.",
                    priority="medium",
                    category="performance",
                    actions=[
                        "Profile endpoints with high latency",
                        "Add caching for repeated reads and optimize DB queries",
                    ],
                    score=min(1.0, slow_requests / 20.0),
                )
            )

        # Sort by score and priority
        priority_rank = {"high": 3, "medium": 2, "low": 1}
        suggestions.sort(key=lambda s: (priority_rank.get(s.priority, 0), s.score), reverse=True)
        return suggestions


# Singleton manager
logs_manager = LogsManager()


class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = datetime.utcnow()
        request = Request(scope)

        async def send_wrapper(message):
            if message.get("type") == "http.response.start":
                status_code = message.get("status")
                duration_ms = (datetime.utcnow() - start).total_seconds() * 1000.0
                level = "error" if status_code and status_code >= 500 else "info"

                # Extract request-side CORS/preflight context
                origin = request.headers.get("origin")
                acr_method = request.headers.get("access-control-request-method")
                acr_headers = request.headers.get("access-control-request-headers")
                is_preflight = (request.method.upper() == "OPTIONS") and (acr_method is not None)

                # Extract response CORS headers (if present)
                resp_headers_raw = message.get("headers") or []
                cors_resp_headers: Dict[str, Any] = {}
                try:
                    for k_bytes, v_bytes in resp_headers_raw:
                        k = k_bytes.decode("latin-1").lower()
                        if k.startswith("access-control-") or k in ("vary",):
                            cors_resp_headers[k] = v_bytes.decode("latin-1")
                except Exception:
                    # Ignore header decoding issues; continue without response header context
                    pass

                entry = LogEntry(
                    level=level,
                    event_type="api_request",
                    message=f"{request.method} {request.url.path}",
                    source="backend",
                    context={
                        "method": request.method,
                        "path": request.url.path,
                        "query": str(request.url.query),
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                        # Helpful CORS/preflight context for troubleshooting
                        "origin": origin,
                        "is_preflight": is_preflight,
                        "access_control_request_method": acr_method,
                        "access_control_request_headers": acr_headers,
                        "cors_response_headers": cors_resp_headers,
                    },
                )
                logs_manager.ingest(entry)
            await send(message)

        await self.app(scope, receive, send_wrapper)


class IngestPayload(BaseModel):
    logs: List[LogEntry]


logs_router = APIRouter(prefix="/api/v1", tags=["logs"])


@logs_router.get("/logs")
async def get_logs(
    level: Optional[str] = None,
    event_type: Optional[str] = None,
    source: Optional[str] = None,
    since: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 200,
):
    try:
        data = logs_manager.query(level, event_type, source, since, search, limit)
        return JSONResponse(content={"items": data, "count": len(data)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@logs_router.get("/logs/stats")
async def get_log_stats(window_minutes: int = 60):
    try:
        return logs_manager.stats(window_minutes=window_minutes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@logs_router.get("/logs/suggestions")
async def get_log_suggestions(recent_n: int = 300):
    try:
        suggestions = logs_manager.suggestions(recent_n=recent_n)
        return {"items": [s.model_dump() for s in suggestions], "count": len(suggestions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@logs_router.post("/logs/ingest")
async def ingest_logs(payload: IngestPayload):
    try:
        for entry in payload.logs:
            logs_manager.ingest(entry)
        return {"status": "ok", "ingested": len(payload.logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))