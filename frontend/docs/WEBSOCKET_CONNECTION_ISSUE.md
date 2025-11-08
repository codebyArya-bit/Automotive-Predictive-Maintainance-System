# WebSocket Connection Issue — Diagnosis and Fix

This document records the investigation and resolution of a WebSocket connectivity problem in the frontend, including the root cause, changes made, and validation steps.

## Symptom
- Frontend pages were intermittently failing to establish WebSocket connections.
- Different parts of the app used different URL sources, leading to mismatched ports and inconsistent behavior.

## Root Cause
- Hardcoded WebSocket URLs existed in multiple pages (`Dashboard.tsx`, `VehicleDetail.tsx`, `AgentMonitor.tsx`).
- `.env.development` set `VITE_API_BASE_URL` and `VITE_WS_URL` to port `8001`, while backend server ran on port `8000`.
- Result: Some WebSocket connections targeted `8000` (hardcoded) and others used `8001` (from env), causing failures when the backend was not on the expected port.

## Fix Implemented
1. Standardized environment variables to the backend port:
   - `VITE_API_BASE_URL=http://localhost:8000`
   - `VITE_WS_URL=ws://localhost:8000/ws`
2. Centralized WebSocket URL usage via `frontend/src/config/index.ts`:
   - Updated pages to use `config.wsUrl` instead of hardcoded strings:
     - `frontend/src/pages/Dashboard.tsx` → `useWebSocket(`${config.wsUrl}/dashboard`)`
     - `frontend/src/pages/VehicleDetail.tsx` → `useWebSocket(`${config.wsUrl}/vehicle/${id}`)`
     - `frontend/src/pages/AgentMonitor.tsx` → `new WebSocket(`${config.wsUrl}/agents`)`

## Validation
- Backend server confirmed running on `http://0.0.0.0:8000` with WebSocket routes:
  - `/ws/dashboard`, `/ws/vehicle/{vehicle_id}`, `/ws/agents`, `/ws/system-maintenance`, `/ws/demo` in `api_server.py`.
- CORS configuration includes common local dev origins including `http://localhost:3002`, `http://localhost:3001`, `http://localhost:3000`, and `http://localhost:5173`.
- Frontend dev server launched and previewed; pages now reference the centralized `config.wsUrl` and connect successfully when the backend is up.

## How to Change Ports Safely
If you need to run the backend on a different port:
1. Update `frontend/.env.development`:
   - `VITE_API_BASE_URL=http://localhost:<your_port>`
   - `VITE_WS_URL=ws://localhost:<your_port>/ws`
2. Restart the frontend dev server.
3. Ensure backend CORS `allowed_frontend_origins` includes the frontend dev URL (e.g., `http://localhost:3001`).

## Troubleshooting Checklist
- Backend running on the expected port (`8000` by default): `python api_server.py`.
- Frontend points to the same port via `VITE_WS_URL` and `VITE_API_BASE_URL`.
- `config.wsUrl` is used consistently across all WebSocket consumers.
- CORS allows the frontend origin in `api_server.py` (`allowed_frontend_origins`).
- Browser console logs for WebSocket errors include useful hints (e.g., network blocks, invalid URL, or CORS).

## Notes
- `AgentMonitor.tsx` currently uses a manual `WebSocket` implementation. Consider migrating it to the shared `useWebSocket` hook for consistent reconnection/error handling.