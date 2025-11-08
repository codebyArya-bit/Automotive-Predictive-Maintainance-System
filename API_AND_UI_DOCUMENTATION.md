# 📚 AutoMind - Complete API & UI Documentation

**Project**: AutoMind AI Predictive Maintenance Platform
**Version**: 1.0
**Last Updated**: November 6, 2025
**Backend**: http://localhost:8000
**Frontend**: http://localhost:3000

---

## 📋 Table of Contents

1. [API Endpoints](#api-endpoints)
   - [Core Endpoints](#core-endpoints)
   - [Vehicle Management](#vehicle-management)
   - [Maintenance Management](#maintenance-management)
   - [Agent Management](#agent-management)
   - [Monitoring & Metrics](#monitoring--metrics)
2. [UI Pages & Routes](#ui-pages--routes)
3. [Response Models](#response-models)
4. [Error Handling](#error-handling)
5. [Authentication](#authentication)

---

## 🔌 API Endpoints

### Base URL
```
http://localhost:8000
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Core Endpoints

### 1. Root / Landing Page

**Endpoint**: `GET /`
**Description**: Returns HTML landing page with API information
**Response**: HTML page

**Example**:
```bash
curl http://localhost:8000/
```

---

### 2. System Health Check

**Endpoint**: `GET /api/v1/health`
**Description**: Check system health and service status
**Response Model**: `SystemHealthResponse`

**Response Example**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-06T17:30:00Z",
  "version": "1.0",
  "services": {
    "api": "operational",
    "database": "connected",
    "agents": "ready"
  }
}
```

**Example Request**:
```bash
curl http://localhost:8000/api/v1/health
```

---

### 3. Process Vehicle (AI Analysis)

**Endpoint**: `POST /api/v1/process-vehicle`
**Description**: Process vehicle telemetry data using AI predictive maintenance
**Response Model**: `VehicleProcessingResponse`
**Processing Time**: ~2-5 seconds

**Request Body**:
```json
{
  "vehicle_id": "TEST_VEHICLE_001",
  "telemetry_data": {
    "speed": 65,
    "engineRpm": 2500,
    "engineTemp": 195,
    "fuelLevel": 75,
    "batteryVoltage": 12.6,
    "oilPressure": 35
  },
  "customer_info": {
    "customer_id": "CUST_001",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  }
}
```

**Response Example**:
```json
{
  "success": true,
  "vehicle_id": "TEST_VEHICLE_001",
  "processing_time": 2.49,
  "analysis": {
    "health_score": 85,
    "predictions": [
      {
        "component": "engine",
        "status": "healthy",
        "confidence": 0.92,
        "maintenance_due": "2025-12-15"
      }
    ],
    "recommendations": [
      "Schedule oil change in 2 weeks",
      "Monitor tire pressure regularly"
    ]
  },
  "timestamp": "2025-11-06T17:30:00Z"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/process-vehicle \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "TEST_001",
    "telemetry_data": {
      "speed": 65,
      "engineRpm": 2500,
      "engineTemp": 195,
      "fuelLevel": 75,
      "batteryVoltage": 12.6,
      "oilPressure": 35
    }
  }'
```

---

### 4. Dashboard Data

**Endpoint**: `GET /api/v1/dashboard`
**Description**: Get comprehensive dashboard metrics and statistics
**Response Model**: `DashboardResponse`
**Response Time**: ~150ms

**Response Example**:
```json
{
  "timestamp": "2025-11-06T17:30:00Z",
  "agent_metrics": {
    "total_agents": 7,
    "active_agents": 5,
    "failed_agents": 0,
    "avg_response_time": 1.2
  },
  "system_metrics": {
    "total_vehicles": 55,
    "healthy_vehicles": 42,
    "warning_vehicles": 10,
    "critical_vehicles": 3,
    "active_alerts": 15,
    "maintenance_scheduled": 8
  },
  "security_metrics": {
    "circuit_breakers": 2,
    "failed_requests": 0,
    "uptime_percentage": 99.9
  },
  "recent_activities": [
    {
      "type": "vehicle_processed",
      "vehicle_id": "VEH_001",
      "timestamp": "2025-11-06T17:25:00Z",
      "status": "success"
    }
  ]
}
```

**Example Request**:
```bash
curl http://localhost:8000/api/v1/dashboard
```

---

### 5. Dashboard Metrics (Alternative)

**Endpoint**: `GET /api/v1/api/dashboard/metrics`
**Description**: Alternative endpoint for dashboard metrics
**Response**: Similar to `/api/v1/dashboard`

---

### 6. Demo Scenarios

**Endpoint**: `POST /api/v1/demo`
**Description**: Run predefined demo scenarios for testing
**Request Body**:
```json
{
  "scenario": "engine_overheating",
  "vehicle_type": "sedan"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/demo \
  -H "Content-Type: application/json" \
  -d '{"scenario": "engine_overheating"}'
```

---

## 🚗 Vehicle Management

### 1. Get All Vehicles

**Endpoint**: `GET /api/v1/vehicles`
**Description**: Get paginated list of all vehicles
**Response Model**: `PaginatedVehicleResponse`

**Query Parameters**:
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum records to return (default: 50, max: 100)
- `status` (string, optional): Filter by status (healthy, warning, critical)
- `search` (string, optional): Search by VIN, license plate, or make/model

**Response Example**:
```json
{
  "total": 55,
  "skip": 0,
  "limit": 50,
  "vehicles": [
    {
      "id": "1",
      "vin": "7ALSE94T6W43T3254",
      "make": "Toyota",
      "model": "Camry",
      "year": 2022,
      "licensePlate": "ABC-1234",
      "mileage": 15000,
      "status": "healthy",
      "lastUpdated": "2025-11-06T17:30:00Z",
      "location": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "address": "San Francisco, CA"
      }
    }
  ]
}
```

**Example Requests**:
```bash
# Get all vehicles
curl http://localhost:8000/api/v1/vehicles

# Get vehicles with pagination
curl http://localhost:8000/api/v1/vehicles?skip=0&limit=10

# Filter by status
curl http://localhost:8000/api/v1/vehicles?status=warning

# Search vehicles
curl http://localhost:8000/api/v1/vehicles?search=Toyota
```

---

### 2. Get Vehicle by ID

**Endpoint**: `GET /api/v1/vehicles/{vehicle_id}`
**Description**: Get detailed information for a specific vehicle
**Response Model**: `VehicleResponse`

**Path Parameters**:
- `vehicle_id` (string, required): Vehicle ID or VIN

**Response Example**:
```json
{
  "id": "1",
  "vin": "7ALSE94T6W43T3254",
  "make": "Toyota",
  "model": "Camry",
  "year": 2022,
  "licensePlate": "ABC-1234",
  "mileage": 15000,
  "status": "healthy",
  "health_score": 85,
  "lastUpdated": "2025-11-06T17:30:00Z",
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "address": "San Francisco, CA"
  },
  "owner": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  }
}
```

**Example Request**:
```bash
curl http://localhost:8000/api/v1/vehicles/7ALSE94T6W43T3254
```

---

### 3. Create Vehicle

**Endpoint**: `POST /api/v1/vehicles`
**Description**: Register a new vehicle in the system
**Response Model**: `VehicleResponse`

**Request Body**:
```json
{
  "vin": "NEW12345678901234",
  "make": "Honda",
  "model": "Accord",
  "year": 2023,
  "licensePlate": "XYZ-5678",
  "mileage": 5000,
  "owner": {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1987654321"
  }
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "vin": "NEW12345678901234",
    "make": "Honda",
    "model": "Accord",
    "year": 2023,
    "licensePlate": "XYZ-5678"
  }'
```

---

### 4. Update Vehicle

**Endpoint**: `PUT /api/v1/vehicles/{vehicle_id}`
**Description**: Update vehicle information
**Response Model**: `VehicleResponse`

**Path Parameters**:
- `vehicle_id` (string, required): Vehicle ID

**Request Body**:
```json
{
  "mileage": 16000,
  "status": "warning",
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "address": "San Francisco, CA"
  }
}
```

**Example Request**:
```bash
curl -X PUT http://localhost:8000/api/v1/vehicles/1 \
  -H "Content-Type: application/json" \
  -d '{"mileage": 16000}'
```

---

### 5. Delete Vehicle

**Endpoint**: `DELETE /api/v1/vehicles/{vehicle_id}`
**Description**: Remove a vehicle from the system

**Path Parameters**:
- `vehicle_id` (string, required): Vehicle ID

**Response**:
```json
{
  "success": true,
  "message": "Vehicle deleted successfully"
}
```

**Example Request**:
```bash
curl -X DELETE http://localhost:8000/api/v1/vehicles/1
```

---

### 6. Get Vehicle Telemetry

**Endpoint**: `GET /api/v1/vehicles/{vehicle_id}/telemetry`
**Description**: Get telemetry data history for a vehicle
**Response Model**: `PaginatedTelemetryResponse`

**Path Parameters**:
- `vehicle_id` (string, required): Vehicle ID

**Query Parameters**:
- `skip` (integer, optional): Records to skip (default: 0)
- `limit` (integer, optional): Max records (default: 50, max: 200)
- `start_date` (string, optional): Filter from date (ISO 8601)
- `end_date` (string, optional): Filter to date (ISO 8601)

**Response Example**:
```json
{
  "total": 1500,
  "skip": 0,
  "limit": 50,
  "telemetry": [
    {
      "id": "1",
      "vehicle_id": "1",
      "timestamp": "2025-11-06T17:30:00Z",
      "speed": 65,
      "engineRpm": 2500,
      "engineTemp": 195,
      "fuelLevel": 75,
      "batteryVoltage": 12.6,
      "oilPressure": 35,
      "errorCodes": []
    }
  ]
}
```

**Example Requests**:
```bash
# Get latest telemetry
curl http://localhost:8000/api/v1/vehicles/1/telemetry?limit=10

# Get telemetry for date range
curl "http://localhost:8000/api/v1/vehicles/1/telemetry?start_date=2025-11-01&end_date=2025-11-06"
```

---

## 🔧 Maintenance Management

### 1. Get All Maintenance Records

**Endpoint**: `GET /api/v1/maintenance`
**Description**: Get paginated maintenance records
**Response Model**: `PaginatedMaintenanceResponse`

**Query Parameters**:
- `skip` (integer, optional): Records to skip (default: 0)
- `limit` (integer, optional): Max records (default: 50)
- `vehicle_id` (string, optional): Filter by vehicle
- `status` (string, optional): Filter by status (scheduled, completed, cancelled)

**Response Example**:
```json
{
  "total": 125,
  "skip": 0,
  "limit": 50,
  "maintenance_records": [
    {
      "id": "1",
      "vehicle_id": "1",
      "type": "oil_change",
      "description": "Regular oil change service",
      "status": "completed",
      "scheduledDate": "2025-11-01T10:00:00Z",
      "completedDate": "2025-11-01T11:30:00Z",
      "cost": 45.99,
      "technician": "Mike Johnson",
      "notes": "Replaced oil filter, used synthetic oil"
    }
  ]
}
```

**Example Requests**:
```bash
# Get all maintenance records
curl http://localhost:8000/api/v1/maintenance

# Filter by vehicle
curl http://localhost:8000/api/v1/maintenance?vehicle_id=1

# Filter by status
curl http://localhost:8000/api/v1/maintenance?status=scheduled
```

---

### 2. Create Maintenance Record

**Endpoint**: `POST /api/v1/maintenance`
**Description**: Schedule new maintenance
**Response Model**: `MaintenanceResponse`

**Request Body**:
```json
{
  "vehicle_id": "1",
  "type": "tire_rotation",
  "description": "Rotate all four tires",
  "scheduledDate": "2025-11-15T10:00:00Z",
  "estimatedCost": 50.00
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/maintenance \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "1",
    "type": "tire_rotation",
    "scheduledDate": "2025-11-15T10:00:00Z"
  }'
```

---

### 3. Update Maintenance Record

**Endpoint**: `PUT /api/v1/maintenance/{maintenance_id}`
**Description**: Update maintenance record
**Response Model**: `MaintenanceResponse`

**Request Body**:
```json
{
  "status": "completed",
  "completedDate": "2025-11-15T11:00:00Z",
  "cost": 52.50,
  "technician": "Sarah Williams",
  "notes": "All tires rotated and balanced"
}
```

**Example Request**:
```bash
curl -X PUT http://localhost:8000/api/v1/maintenance/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

---

### 4. Delete Maintenance Record

**Endpoint**: `DELETE /api/v1/maintenance/{maintenance_id}`
**Description**: Remove maintenance record

**Response**:
```json
{
  "success": true,
  "message": "Maintenance record deleted successfully"
}
```

**Example Request**:
```bash
curl -X DELETE http://localhost:8000/api/v1/maintenance/1
```

---

## 🤖 Agent Management

### 1. Get All Agents

**Endpoint**: `GET /api/v1/agents`
**Description**: Get list of all AI agents and their status

**Response Example**:
```json
{
  "agents": [
    {
      "id": "predictive_maintenance",
      "name": "Predictive Maintenance Agent",
      "status": "active",
      "type": "ml_analysis",
      "last_active": "2025-11-06T17:30:00Z",
      "tasks_processed": 142,
      "success_rate": 98.5
    },
    {
      "id": "diagnostic_agent",
      "name": "Diagnostic Analysis Agent",
      "status": "active",
      "type": "diagnostics",
      "last_active": "2025-11-06T17:28:00Z",
      "tasks_processed": 95,
      "success_rate": 97.2
    },
    {
      "id": "scheduling_agent",
      "name": "Smart Scheduling Agent",
      "status": "active",
      "type": "scheduling",
      "last_active": "2025-11-06T17:25:00Z",
      "tasks_processed": 67,
      "success_rate": 99.1
    }
  ],
  "total": 7,
  "active": 7,
  "inactive": 0
}
```

**Example Request**:
```bash
curl http://localhost:8000/api/v1/agents
```

---

### 2. Get Agent Status

**Endpoint**: `GET /api/v1/agents/{agent_id}/status`
**Description**: Get detailed status for specific agent

**Response Example**:
```json
{
  "agent_id": "predictive_maintenance",
  "name": "Predictive Maintenance Agent",
  "status": "active",
  "health": "healthy",
  "uptime": 86400,
  "last_heartbeat": "2025-11-06T17:30:00Z",
  "metrics": {
    "requests_total": 142,
    "requests_success": 140,
    "requests_failed": 2,
    "avg_response_time": 2.3,
    "current_queue": 0
  },
  "capabilities": [
    "failure_prediction",
    "maintenance_scheduling",
    "anomaly_detection"
  ]
}
```

**Example Request**:
```bash
curl http://localhost:8000/api/v1/agents/predictive_maintenance/status
```

---

### 3. Trigger Agent

**Endpoint**: `POST /api/v1/agents/{agent_id}/trigger`
**Description**: Manually trigger an agent to process data

**Request Body**:
```json
{
  "vehicle_id": "1",
  "priority": "high",
  "data": {
    "telemetry": {}
  }
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/agents/predictive_maintenance/trigger \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id": "1", "priority": "high"}'
```

---

## 📊 Monitoring & Metrics

### 1. Circuit Breakers Status

**Endpoint**: `GET /api/v1/circuit-breakers`
**Description**: Get status of all circuit breakers

**Response Example**:
```json
{
  "circuit_breakers": [
    {
      "name": "database_circuit",
      "state": "closed",
      "failure_count": 0,
      "success_count": 1542,
      "last_failure": null
    },
    {
      "name": "agent_circuit",
      "state": "closed",
      "failure_count": 2,
      "success_count": 298,
      "last_failure": "2025-11-05T12:30:00Z"
    }
  ]
}
```

**Example Request**:
```bash
curl http://localhost:8000/api/v1/circuit-breakers
```

---

### 2. Prometheus Metrics

**Endpoint**: `GET /api/v1/metrics/prometheus`
**Description**: Get metrics in Prometheus format for monitoring

**Response**: Plain text Prometheus metrics format

**Example Request**:
```bash
curl http://localhost:8000/api/v1/metrics/prometheus
```

**Example Response**:
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/v1/vehicles"} 1542

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 1200
http_request_duration_seconds_bucket{le="0.5"} 1480
http_request_duration_seconds_bucket{le="1.0"} 1520
```

---

## 🌐 WebSocket Endpoints

### Vehicle Real-Time Updates

**Endpoint**: `ws://localhost:8000/ws/vehicle/{vehicle_id}`
**Description**: Real-time vehicle telemetry and status updates

**Connection Example**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/vehicle/1');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

// Subscribe to telemetry updates
ws.send(JSON.stringify({
  type: 'subscribe_telemetry',
  vehicleId: '1'
}));
```

**Message Types**:
- `telemetry_update` - New telemetry data
- `alert_update` - New alert created
- `diagnostics_update` - Diagnostic data changed
- `status_change` - Vehicle status changed

---

## 🎨 UI Pages & Routes

### Frontend Base URL
```
http://localhost:3000
```

---

### 1. Dashboard

**Route**: `/dashboard` (also `/`)
**Component**: `Dashboard.tsx`
**Description**: Main dashboard with system overview and metrics

**Features**:
- System health overview
- Vehicle statistics (total, healthy, warning, critical)
- Active alerts count
- Agent status indicators
- Recent activity feed
- Quick action buttons
- Real-time metric updates

**Widgets**:
- Total Vehicles Card
- Active Alerts Card
- Maintenance Due Card
- Agent Status Grid
- Activity Timeline

**Access**:
```
http://localhost:3000/dashboard
```

---

### 2. Vehicle List

**Route**: `/vehicles`
**Component**: `VehicleList.tsx`
**Description**: Browse and manage all vehicles

**Features**:
- Paginated vehicle table
- Search by VIN, license plate, make/model
- Filter by status (healthy, warning, critical)
- Sort by various fields
- View vehicle details
- Add new vehicle button
- Export vehicle list (CSV)
- Status color coding
- Bulk actions (future)

**Columns**:
- VIN
- Make/Model/Year
- License Plate
- Mileage
- Status
- Last Updated
- Actions (View, Edit, Delete)

**Access**:
```
http://localhost:3000/vehicles
```

---

### 3. Vehicle Detail

**Route**: `/vehicles/:id`
**Component**: `VehicleDetail.tsx`
**Description**: Detailed view of a single vehicle

**Features**:
- Vehicle overview card
- Real-time telemetry monitoring
- WebSocket live updates toggle
- Connection status indicator
- Multiple tabs:
  - **Overview**: Key metrics, diagnostics, telemetry trends
  - **Telemetry**: Detailed telemetry history table
  - **Maintenance**: Maintenance history
  - **Alerts**: Active and historical alerts
- Export telemetry data (CSV)
- Interactive charts
- Diagnostic data:
  - Battery health
  - Oil pressure
  - Coolant level
  - Tire pressure (all 4 tires)
  - Active error codes

**Real-time Features**:
- Live telemetry updates every 5 seconds
- WebSocket connection (with polling fallback)
- Visual connection status
- Last update timestamp

**Access**:
```
http://localhost:3000/vehicles/7ALSE94T6W43T3254
```

---

### 4. AI Agent Monitor

**Route**: `/agents`
**Component**: `AgentMonitor.tsx`
**Description**: Monitor AI agent status and performance

**Features**:
- Agent grid view
- Real-time agent status
- Performance metrics per agent
- Task queue monitoring
- Agent health indicators
- Response time charts
- Success rate tracking
- Manual agent triggering
- Circuit breaker status

**Agent Types Displayed**:
- Predictive Maintenance Agent
- Diagnostic Analysis Agent
- Smart Scheduling Agent
- Customer Communication Agent
- Parts Inventory Agent
- Pricing Optimization Agent
- Route Planning Agent

**Metrics Shown**:
- Status (active/inactive/error)
- Tasks processed
- Success rate
- Average response time
- Last active timestamp
- Current queue size

**Access**:
```
http://localhost:3000/agents
```

---

### 5. Maintenance List

**Route**: `/maintenance`
**Component**: `MaintenanceList.tsx`
**Description**: View and manage maintenance records

**Features**:
- Maintenance records table
- Filter by status (scheduled, completed, cancelled)
- Filter by vehicle
- Date range filtering
- Sort by date, cost, status
- Create new maintenance record
- Update maintenance status
- View maintenance details
- Cost tracking
- Technician assignment

**Status Types**:
- Scheduled (upcoming maintenance)
- In Progress (currently being worked on)
- Completed (finished maintenance)
- Cancelled (cancelled appointments)

**Access**:
```
http://localhost:3000/maintenance
```

---

### 6. Alerts List

**Route**: `/alerts`
**Component**: `AlertsList.tsx`
**Description**: View and manage system alerts

**Features**:
- Alert list with priority sorting
- Filter by severity (critical, warning, info)
- Filter by status (active, acknowledged, resolved)
- Alert details modal
- Acknowledge alerts
- Resolve alerts
- Alert history
- Priority-based color coding

**Alert Severities**:
- Critical (red) - Immediate attention required
- Warning (yellow) - Action recommended
- Info (blue) - Informational only

**Alert Types**:
- Engine alerts
- Battery alerts
- Tire pressure alerts
- Maintenance due alerts
- System alerts

**Access**:
```
http://localhost:3000/alerts
```

---

### 7. Demo Interface

**Route**: `/demo`
**Component**: `DemoInterface.tsx`
**Description**: Interactive demo scenarios

**Features**:
- Predefined demo scenarios
- Quick vehicle processing demo
- Sample data visualization
- Test AI predictions
- Scenario selection:
  - Engine overheating
  - Low battery
  - Tire pressure warning
  - Fuel system issue
- Real-time demo results

**Access**:
```
http://localhost:3000/demo
```

---

### 8. Analytics

**Route**: `/analytics`
**Component**: `Analytics.tsx`
**Description**: Advanced analytics and insights

**Features**:
- Vehicle health trends
- Maintenance cost analysis
- Prediction accuracy metrics
- Agent performance analytics
- Custom date range selection
- Export reports
- Interactive charts:
  - Time series graphs
  - Bar charts
  - Pie charts
  - Heat maps

**Access**:
```
http://localhost:3000/analytics
```

---

### 9. Demo Analytics

**Route**: `/demo-analytics`
**Component**: `DemoAnalytics.tsx`
**Description**: Analytics specifically for demo data

**Features**:
- Demo data visualization
- Sample reports
- Test scenarios analytics
- Performance benchmarks

**Access**:
```
http://localhost:3000/demo-analytics
```

---

## 🎨 UI Component Features

### Common UI Elements

#### 1. Layout Component
- Responsive sidebar navigation
- AutoMind logo with gradient text
- Navigation menu items
- Mobile hamburger menu
- User profile section (future)

#### 2. Navigation Menu Items
- 📊 Dashboard
- 🚗 Vehicles
- 🤖 AI Agents
- 🔧 Maintenance
- 🔔 Alerts
- 🎯 Demo
- 📈 Analytics

#### 3. Loading States
- Spinner animations
- Skeleton loaders
- Progressive loading
- Suspense boundaries

#### 4. Error Handling
- Error boundary components
- Fallback UI
- Retry mechanisms
- Toast notifications

#### 5. Toast Notifications
- Success messages (green, 3s)
- Error messages (red, 5s)
- Info messages (blue, 4s)
- Custom positioning (top-right)

---

## 📦 Response Models

### Common Response Fields

All responses include:
```json
{
  "timestamp": "2025-11-06T17:30:00Z",
  "success": true,
  "message": "Operation completed successfully"
}
```

### Pagination Response
```json
{
  "total": 100,
  "skip": 0,
  "limit": 50,
  "has_next": true,
  "has_previous": false
}
```

---

## ⚠️ Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VEHICLE_NOT_FOUND",
    "message": "Vehicle with ID '123' not found",
    "details": {},
    "timestamp": "2025-11-06T17:30:00Z"
  }
}
```

### HTTP Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

### Common Error Codes

- `VEHICLE_NOT_FOUND` - Vehicle doesn't exist
- `INVALID_VIN` - VIN format invalid
- `DUPLICATE_VIN` - VIN already exists
- `INVALID_DATE_RANGE` - Date range invalid
- `AGENT_UNAVAILABLE` - AI agent not responding
- `DATABASE_ERROR` - Database operation failed
- `VALIDATION_ERROR` - Input validation failed

---

## 🔐 Authentication

### Current Status
- **Development**: No authentication required
- **Production**: JWT-based authentication recommended

### Future Authentication Flow

1. **Login**
   ```bash
   POST /api/v1/auth/login
   Body: {"email": "user@example.com", "password": "secure123"}
   ```

2. **Get Token**
   ```json
   {
     "access_token": "eyJhbGc...",
     "token_type": "bearer",
     "expires_in": 3600
   }
   ```

3. **Authenticated Request**
   ```bash
   curl -H "Authorization: Bearer eyJhbGc..." \
     http://localhost:8000/api/v1/vehicles
   ```

---

## 🚀 Quick Start Examples

### 1. Check System Health
```bash
curl http://localhost:8000/api/v1/health
```

### 2. Get Dashboard Data
```bash
curl http://localhost:8000/api/v1/dashboard
```

### 3. List All Vehicles
```bash
curl http://localhost:8000/api/v1/vehicles
```

### 4. Get Specific Vehicle
```bash
curl http://localhost:8000/api/v1/vehicles/1
```

### 5. Process Vehicle with AI
```bash
curl -X POST http://localhost:8000/api/v1/process-vehicle \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "TEST_001",
    "telemetry_data": {
      "speed": 65,
      "engineRpm": 2500,
      "engineTemp": 195,
      "fuelLevel": 75,
      "batteryVoltage": 12.6
    }
  }'
```

### 6. Get Vehicle Telemetry
```bash
curl "http://localhost:8000/api/v1/vehicles/1/telemetry?limit=10"
```

### 7. Get Agent Status
```bash
curl http://localhost:8000/api/v1/agents
```

### 8. Access UI Dashboard
```
Open browser: http://localhost:3000/dashboard
```

### 9. View Specific Vehicle
```
Open browser: http://localhost:3000/vehicles/1
```

### 10. Monitor AI Agents
```
Open browser: http://localhost:3000/agents
```

---

## 📝 Notes

### Performance Tips
- Use pagination for large datasets (`skip` and `limit` parameters)
- Enable WebSocket for real-time updates
- Use specific date ranges for telemetry queries
- Leverage caching for frequently accessed data

### Best Practices
- Always validate VIN format (17 characters)
- Handle pagination in UI for better UX
- Implement retry logic for network failures
- Use WebSocket with polling fallback
- Monitor circuit breaker status
- Export data before bulk operations

### Development Tools
- **API Testing**: Swagger UI at http://localhost:8000/docs
- **WebSocket Testing**: Use browser console or Postman
- **Database**: SQLite browser for direct DB access
- **Monitoring**: Prometheus metrics endpoint

---

## 🆘 Troubleshooting

### Common Issues

#### 1. Vehicle Not Found Error
```
Error: 404 - Vehicle not found
Solution: Verify vehicle ID/VIN exists in database
```

#### 2. WebSocket Connection Failed
```
Error: WebSocket connection failed
Solution: System falls back to polling mode (5-second intervals)
```

#### 3. Agent Timeout
```
Error: Agent processing timeout
Solution: Check agent status at /api/v1/agents, restart if needed
```

#### 4. CORS Error (Frontend)
```
Error: CORS policy blocked
Solution: Ensure backend CORS is configured for localhost:3000
```

---

## 📚 Additional Resources

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Frontend Dev Server**: http://localhost:3000
- **API Health Check**: http://localhost:8000/api/v1/health

---

## 📞 Support

For issues or questions:
1. Check logs in terminal/console
2. Verify both services are running (backend: 8000, frontend: 3000)
3. Review error messages in browser DevTools
4. Check API documentation at `/docs`

---

**Last Updated**: November 6, 2025
**Status**: Production Ready ✅
**Documentation Version**: 1.0
