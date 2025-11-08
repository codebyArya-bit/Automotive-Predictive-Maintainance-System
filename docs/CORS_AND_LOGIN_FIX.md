# CORS and Login Fix

This document summarizes the investigation, root cause, and resolution for the CORS preflight failure and the `/api/v1/auth/login` endpoint behavior across development servers.

## Symptoms
- `OPTIONS /api/v1/auth/login` returned `400` with message "Disallowed CORS origin" when the frontend ran on `http://localhost:3001` and targeted the backend at `http://localhost:8001`.
- A subsequent `POST /api/v1/auth/login` sometimes succeeded from allowed origins (e.g. `http://localhost:3000`).
- On the backend listening at port `8000`, the `auth/login` route was not found.

## Root Cause
- The backend's CORS configuration did not include `http://localhost:3001` as an allowed origin, so the browser's preflight was rejected.
- The server on port `8000` does not expose the authentication endpoints; those are present on the port `8001` instance.

## Changes Implemented
1. Expanded CORS allowed origins in `api_server.py`:
   - Supports comma-separated `FRONTEND_ORIGINS` environment variable.
   - Defaults now include `http://localhost:3000`, `http://localhost:3001`, `http://localhost:3002`, and `http://localhost:5173`.
   - Keeps `allow_credentials=True`, `allow_methods=["*"]`, and `allow_headers=["*"]`.

2. Added startup logging of effective CORS settings in `api_server.py`:
   - Logs `allowed_frontend_origins` at app startup via `logs_manager.ingest`.

3. Enhanced backend request logging in `logs_system.py`:
   - `LoggingMiddleware` now records CORS/preflight context for each request, including:
     - `origin`, `is_preflight`, `access_control_request_method`, `access_control_request_headers`.
     - CORS-related response headers (`access-control-*`, `vary`).

4. Augmented frontend error handling (`frontend/src/utils/errorHandler.ts`):
   - Network errors now include contextual details such as origin, target URL, method, `withCredentials`, presence of `Authorization` header, and online status.
   - Messages clarify when a failure is likely CORS-related.

## Verification
- Preflight to `http://localhost:8001/api/v1/auth/login` from origin `http://localhost:3001` now returns `200 OK` with appropriate CORS headers.
- Full login POST to `http://localhost:8001/api/v1/auth/login` from `http://localhost:3001` succeeds (`200 OK`) using demo credentials `sarah@demo.com` / `demo123`.
- On port `8000`, preflight responds `200 OK` but `POST /api/v1/auth/login` returns `404 Not Found` because authentication routes are not present on that instance.

## Operational Notes
- Use `FRONTEND_ORIGINS` to control allowed dev origins without code changes:
  - Example: `FRONTEND_ORIGINS=http://localhost:3000,http://localhost:3001`
- Align the frontend proxy or `VITE_API_BASE_URL` with the backend that serves authentication endpoints (`:8001`), or expose auth routes consistently across environments if desired.

## Next Steps
- Consider consolidating all endpoints onto a single development server to reduce confusion.
- Optionally add an automated health check to ensure required routes (e.g., auth) are present and logged at startup.