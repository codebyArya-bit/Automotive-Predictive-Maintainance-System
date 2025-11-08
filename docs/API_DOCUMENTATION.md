# AutoMind API Documentation

This document provides comprehensive documentation for the AutoMind REST API, including endpoints, request/response formats, authentication, and usage examples.

## Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Error Handling](#error-handling)
5. [API Endpoints](#api-endpoints)
6. [Data Models](#data-models)
7. [WebSocket API](#websocket-api)
8. [SDK and Libraries](#sdk-and-libraries)

## API Overview

### Base URL
- **Production**: `https://api.automind.com`
- **Staging**: `https://api-staging.automind.com`
- **Development**: `http://localhost:8000`

### API Version
Current API version: `v1`

All API endpoints are prefixed with `/api/v1/`

### Content Type
The API accepts and returns JSON data. All requests should include:
```
Content-Type: application/json
Accept: application/json
```

### OpenAPI Specification
Interactive API documentation is available at:
- **Swagger UI**: `https://api.automind.com/docs`
- **ReDoc**: `https://api.automind.com/redoc`
- **OpenAPI JSON**: `https://api.automind.com/openapi.json`

## Authentication

### JWT Token Authentication

The AutoMind API uses JWT (JSON Web Token) for authentication. Tokens must be included in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token

#### Login Endpoint
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Token Refresh
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### API Key Authentication (Alternative)

For server-to-server communication, API keys can be used:

```
X-API-Key: your-api-key
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Authenticated requests**: 1000 requests per hour per user
- **Unauthenticated requests**: 100 requests per hour per IP
- **Bulk operations**: 50 requests per hour per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request successful, no content returned |
| 400 | Bad Request - Invalid request parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "request_id": "req_123456789"
  }
}
```

## API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/login
Authenticate user and obtain access token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "fleet_manager"
  }
}
```

#### POST /api/v1/auth/refresh
Refresh access token using refresh token.

#### POST /api/v1/auth/logout
Invalidate current token.

### User Management

#### GET /api/v1/users/me
Get current user profile.

**Response:**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "fleet_manager",
  "organization": "ACME Fleet Services",
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-20T14:22:00Z"
}
```

#### PUT /api/v1/users/me
Update current user profile.

**Request:**
```json
{
  "name": "John Smith",
  "phone": "+1-555-0123",
  "preferences": {
    "notifications": {
      "email": true,
      "sms": false,
      "push": true
    },
    "timezone": "America/New_York"
  }
}
```

### Vehicle Management

#### GET /api/v1/vehicles
List all vehicles accessible to the user.

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)
- `make` (string): Filter by vehicle make
- `model` (string): Filter by vehicle model
- `year` (integer): Filter by vehicle year
- `status` (string): Filter by status (active, inactive, maintenance)

**Response:**
```json
{
  "vehicles": [
    {
      "id": "vehicle_123",
      "vin": "1HGBH41JXMN109186",
      "make": "Honda",
      "model": "Civic",
      "year": 2022,
      "license_plate": "ABC-1234",
      "status": "active",
      "owner": {
        "id": "user_456",
        "name": "Jane Doe",
        "email": "jane@example.com"
      },
      "location": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "address": "San Francisco, CA"
      },
      "last_telemetry": "2024-01-20T14:30:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

#### POST /api/v1/vehicles
Register a new vehicle.

**Request:**
```json
{
  "vin": "1HGBH41JXMN109186",
  "make": "Honda",
  "model": "Civic",
  "year": 2022,
  "license_plate": "ABC-1234",
  "owner_id": "user_456",
  "metadata": {
    "color": "Blue",
    "engine_type": "Gasoline",
    "transmission": "Automatic"
  }
}
```

#### GET /api/v1/vehicles/{vehicle_id}
Get detailed information about a specific vehicle.

**Response:**
```json
{
  "id": "vehicle_123",
  "vin": "1HGBH41JXMN109186",
  "make": "Honda",
  "model": "Civic",
  "year": 2022,
  "license_plate": "ABC-1234",
  "status": "active",
  "owner": {
    "id": "user_456",
    "name": "Jane Doe",
    "email": "jane@example.com"
  },
  "specifications": {
    "engine_size": "2.0L",
    "fuel_type": "Gasoline",
    "transmission": "CVT",
    "drivetrain": "FWD"
  },
  "insurance": {
    "provider": "State Farm",
    "policy_number": "SF123456789",
    "expires_at": "2024-12-31"
  },
  "maintenance_schedule": {
    "next_oil_change": "2024-02-15",
    "next_inspection": "2024-06-01"
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-20T10:15:00Z"
}
```

#### PUT /api/v1/vehicles/{vehicle_id}
Update vehicle information.

#### DELETE /api/v1/vehicles/{vehicle_id}
Remove a vehicle from the system.

### Telemetry Data

#### GET /api/v1/vehicles/{vehicle_id}/telemetry
Get telemetry data for a specific vehicle.

**Query Parameters:**
- `start_date` (ISO 8601): Start date for data range
- `end_date` (ISO 8601): End date for data range
- `metrics` (array): Specific metrics to retrieve
- `interval` (string): Data aggregation interval (1m, 5m, 1h, 1d)

**Response:**
```json
{
  "vehicle_id": "vehicle_123",
  "time_range": {
    "start": "2024-01-20T00:00:00Z",
    "end": "2024-01-20T23:59:59Z"
  },
  "data_points": [
    {
      "timestamp": "2024-01-20T14:30:00Z",
      "location": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "altitude": 52.5
      },
      "engine": {
        "rpm": 2500,
        "temperature": 195.5,
        "oil_pressure": 35.2,
        "coolant_temperature": 180.0
      },
      "vehicle": {
        "speed": 45.5,
        "odometer": 25847.3,
        "fuel_level": 0.75,
        "battery_voltage": 12.6
      },
      "diagnostics": {
        "dtc_codes": [],
        "mil_status": false,
        "readiness_status": "complete"
      }
    }
  ],
  "summary": {
    "total_points": 1440,
    "distance_traveled": 125.7,
    "average_speed": 32.4,
    "max_speed": 65.2,
    "fuel_consumed": 8.5
  }
}
```

#### POST /api/v1/telemetry
Submit telemetry data for a vehicle.

**Request:**
```json
{
  "vehicle_id": "vehicle_123",
  "timestamp": "2024-01-20T14:30:00Z",
  "data": {
    "location": {
      "latitude": 37.7749,
      "longitude": -122.4194
    },
    "engine_rpm": 2500,
    "speed": 45.5,
    "fuel_level": 0.75,
    "engine_temperature": 195.5,
    "oil_pressure": 35.2,
    "battery_voltage": 12.6
  }
}
```

#### POST /api/v1/telemetry/batch
Submit multiple telemetry data points in batch.

**Request:**
```json
{
  "data_points": [
    {
      "vehicle_id": "vehicle_123",
      "timestamp": "2024-01-20T14:30:00Z",
      "data": { /* telemetry data */ }
    },
    {
      "vehicle_id": "vehicle_124",
      "timestamp": "2024-01-20T14:30:00Z",
      "data": { /* telemetry data */ }
    }
  ]
}
```

### Maintenance Management

#### GET /api/v1/vehicles/{vehicle_id}/maintenance
Get maintenance history for a vehicle.

**Response:**
```json
{
  "vehicle_id": "vehicle_123",
  "maintenance_records": [
    {
      "id": "maint_456",
      "type": "oil_change",
      "description": "Regular oil change and filter replacement",
      "performed_at": "2024-01-15T10:00:00Z",
      "odometer_reading": 25000,
      "cost": 45.99,
      "service_provider": {
        "name": "Quick Lube Plus",
        "location": "123 Main St, Anytown, USA"
      },
      "parts_used": [
        {
          "part_number": "OIL-5W30-5QT",
          "description": "5W-30 Motor Oil (5 quarts)",
          "cost": 29.99
        },
        {
          "part_number": "FILTER-123",
          "description": "Oil Filter",
          "cost": 12.99
        }
      ],
      "next_due": {
        "date": "2024-04-15",
        "odometer": 28000
      }
    }
  ],
  "upcoming_maintenance": [
    {
      "type": "tire_rotation",
      "due_date": "2024-02-01",
      "due_odometer": 26000,
      "priority": "medium"
    }
  ]
}
```

#### POST /api/v1/vehicles/{vehicle_id}/maintenance
Record new maintenance activity.

**Request:**
```json
{
  "type": "brake_service",
  "description": "Front brake pad replacement",
  "performed_at": "2024-01-20T14:00:00Z",
  "odometer_reading": 25847,
  "cost": 299.99,
  "service_provider": {
    "name": "Brake Masters",
    "location": "456 Oak Ave, Anytown, USA"
  },
  "parts_used": [
    {
      "part_number": "BP-FRONT-SET",
      "description": "Front Brake Pad Set",
      "cost": 89.99
    }
  ]
}
```

### Predictive Analytics

#### GET /api/v1/vehicles/{vehicle_id}/predictions
Get predictive maintenance recommendations.

**Response:**
```json
{
  "vehicle_id": "vehicle_123",
  "predictions": [
    {
      "id": "pred_789",
      "component": "brake_pads",
      "prediction_type": "wear_prediction",
      "confidence": 0.87,
      "predicted_failure_date": "2024-03-15",
      "estimated_remaining_miles": 2500,
      "severity": "medium",
      "recommendations": [
        "Schedule brake inspection within 2 weeks",
        "Monitor brake performance closely",
        "Consider replacement before predicted failure date"
      ],
      "cost_estimate": {
        "parts": 150.00,
        "labor": 120.00,
        "total": 270.00
      },
      "created_at": "2024-01-20T12:00:00Z"
    }
  ],
  "risk_score": {
    "overall": 0.23,
    "categories": {
      "engine": 0.15,
      "transmission": 0.08,
      "brakes": 0.45,
      "electrical": 0.12
    }
  }
}
```

#### GET /api/v1/analytics/fleet-summary
Get fleet-wide analytics and insights.

**Query Parameters:**
- `date_range` (string): Time period (7d, 30d, 90d, 1y)
- `metrics` (array): Specific metrics to include

**Response:**
```json
{
  "fleet_summary": {
    "total_vehicles": 150,
    "active_vehicles": 142,
    "vehicles_in_maintenance": 8,
    "total_miles_driven": 125000,
    "average_fuel_efficiency": 28.5,
    "total_maintenance_cost": 15750.00
  },
  "performance_metrics": {
    "uptime_percentage": 98.7,
    "average_utilization": 0.73,
    "maintenance_compliance": 0.94
  },
  "alerts": {
    "critical": 2,
    "warning": 15,
    "info": 8
  },
  "trends": {
    "fuel_efficiency": {
      "current": 28.5,
      "previous_period": 27.8,
      "change_percentage": 2.5
    },
    "maintenance_cost": {
      "current": 15750.00,
      "previous_period": 16200.00,
      "change_percentage": -2.8
    }
  }
}
```

### Alerts and Notifications

#### GET /api/v1/alerts
Get alerts for the current user.

**Query Parameters:**
- `severity` (string): Filter by severity (critical, warning, info)
- `status` (string): Filter by status (active, acknowledged, resolved)
- `vehicle_id` (string): Filter by specific vehicle

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert_123",
      "vehicle_id": "vehicle_456",
      "type": "engine_temperature_high",
      "severity": "critical",
      "status": "active",
      "title": "High Engine Temperature",
      "message": "Engine temperature has exceeded safe operating limits",
      "created_at": "2024-01-20T14:45:00Z",
      "data": {
        "current_temperature": 220.5,
        "threshold": 210.0,
        "location": {
          "latitude": 37.7749,
          "longitude": -122.4194
        }
      },
      "actions": [
        {
          "type": "acknowledge",
          "label": "Acknowledge Alert"
        },
        {
          "type": "contact_driver",
          "label": "Contact Driver"
        }
      ]
    }
  ],
  "summary": {
    "total": 23,
    "critical": 1,
    "warning": 15,
    "info": 7
  }
}
```

#### POST /api/v1/alerts/{alert_id}/acknowledge
Acknowledge an alert.

#### POST /api/v1/notifications/preferences
Update notification preferences.

**Request:**
```json
{
  "channels": {
    "email": {
      "enabled": true,
      "address": "user@example.com"
    },
    "sms": {
      "enabled": false,
      "phone": "+1-555-0123"
    },
    "push": {
      "enabled": true
    }
  },
  "alert_types": {
    "critical_alerts": ["email", "sms", "push"],
    "maintenance_reminders": ["email"],
    "performance_reports": ["email"]
  }
}
```

## Data Models

### Vehicle Model
```json
{
  "id": "string",
  "vin": "string (17 characters)",
  "make": "string",
  "model": "string",
  "year": "integer",
  "license_plate": "string",
  "status": "enum (active, inactive, maintenance)",
  "owner_id": "string",
  "specifications": {
    "engine_size": "string",
    "fuel_type": "string",
    "transmission": "string",
    "drivetrain": "string"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Telemetry Data Model
```json
{
  "vehicle_id": "string",
  "timestamp": "datetime",
  "location": {
    "latitude": "float",
    "longitude": "float",
    "altitude": "float"
  },
  "engine": {
    "rpm": "integer",
    "temperature": "float",
    "oil_pressure": "float",
    "coolant_temperature": "float"
  },
  "vehicle": {
    "speed": "float",
    "odometer": "float",
    "fuel_level": "float (0-1)",
    "battery_voltage": "float"
  },
  "diagnostics": {
    "dtc_codes": ["string"],
    "mil_status": "boolean",
    "readiness_status": "string"
  }
}
```

### Maintenance Record Model
```json
{
  "id": "string",
  "vehicle_id": "string",
  "type": "string",
  "description": "string",
  "performed_at": "datetime",
  "odometer_reading": "float",
  "cost": "float",
  "service_provider": {
    "name": "string",
    "location": "string",
    "contact": "string"
  },
  "parts_used": [
    {
      "part_number": "string",
      "description": "string",
      "cost": "float"
    }
  ],
  "next_due": {
    "date": "date",
    "odometer": "float"
  }
}
```

## WebSocket API

For real-time updates, the AutoMind API provides WebSocket connections.

### Connection
```javascript
const ws = new WebSocket('wss://api.automind.com/ws/v1/vehicles/{vehicle_id}');

// Authentication
ws.onopen = function() {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your-jwt-token'
  }));
};

// Receive real-time updates
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```

### Message Types

#### Telemetry Updates
```json
{
  "type": "telemetry_update",
  "vehicle_id": "vehicle_123",
  "timestamp": "2024-01-20T14:30:00Z",
  "data": {
    "speed": 45.5,
    "location": {
      "latitude": 37.7749,
      "longitude": -122.4194
    }
  }
}
```

#### Alert Notifications
```json
{
  "type": "alert",
  "alert_id": "alert_456",
  "vehicle_id": "vehicle_123",
  "severity": "critical",
  "message": "Engine temperature critical"
}
```

## SDK and Libraries

### Python SDK

```python
from automind import AutoMindClient

# Initialize client
client = AutoMindClient(
    api_key='your-api-key',
    base_url='https://api.automind.com'
)

# Get vehicles
vehicles = client.vehicles.list()

# Get telemetry data
telemetry = client.telemetry.get(
    vehicle_id='vehicle_123',
    start_date='2024-01-20',
    end_date='2024-01-21'
)

# Submit telemetry data
client.telemetry.create(
    vehicle_id='vehicle_123',
    data={
        'speed': 45.5,
        'engine_rpm': 2500,
        'fuel_level': 0.75
    }
)
```

### JavaScript SDK

```javascript
import { AutoMindClient } from '@automind/sdk';

const client = new AutoMindClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.automind.com'
});

// Get vehicles
const vehicles = await client.vehicles.list();

// Real-time telemetry
const stream = client.telemetry.stream('vehicle_123');
stream.on('data', (telemetry) => {
  console.log('New telemetry:', telemetry);
});
```

### cURL Examples

#### Get Vehicles
```bash
curl -X GET "https://api.automind.com/api/v1/vehicles" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json"
```

#### Submit Telemetry
```bash
curl -X POST "https://api.automind.com/api/v1/telemetry" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "vehicle_123",
    "timestamp": "2024-01-20T14:30:00Z",
    "data": {
      "speed": 45.5,
      "engine_rpm": 2500,
      "fuel_level": 0.75
    }
  }'
```

## Support and Resources

- **API Status**: https://status.automind.com
- **Developer Portal**: https://developers.automind.com
- **Support**: support@automind.com
- **Community Forum**: https://community.automind.com

---

**API Version**: 1.0  
**Last Updated**: $(date)  
**Maintained By**: API Team