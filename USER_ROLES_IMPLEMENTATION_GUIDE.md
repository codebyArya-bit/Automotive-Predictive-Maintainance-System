# 👥 User Roles Implementation Guide

**Project**: AutoMind - Multi-User Role System
**Purpose**: Support different user types as required by Challenge III

---

## 📋 Overview

The AutoMind system needs to support **5 distinct user roles** to demonstrate realistic automotive predictive maintenance operations:

1. **Vehicle Owners/Customers** 🚗
2. **Service Center Staff** 🔧
3. **Manufacturing Team** 🏭
4. **System Administrators** 👨‍💼
5. **Fleet Managers** 📊 (Bonus)

---

## 🎯 User Role Specifications

### 1. Vehicle Owner / Customer 🚗

**Profile**: Individual vehicle owner receiving AI-driven maintenance recommendations

**Use Cases**:
- Receive predictive maintenance alerts
- View their vehicle health status
- Get voice calls from AI agent for urgent issues
- Receive app notifications for routine maintenance
- Book/reschedule service appointments
- Provide feedback after service
- View maintenance history
- Track appointment status

**Dashboard Features**:
- My Vehicles (with health status)
- Upcoming Appointments
- Recent Alerts
- Maintenance History
- Notification Center (voice calls + app notifications)
- Feedback Forms

**Sample User**:
```json
{
  "name": "Rajesh Kumar",
  "role": "customer",
  "email": "rajesh.kumar@email.com",
  "phone": "+91-9876543210",
  "vehicles": ["7ALSE94T6W43T3254"],
  "preferred_language": "hindi",
  "preferred_contact": "voice_call"
}
```

---

### 2. Service Center Staff 🔧

**Profile**: Technicians and service advisors managing daily operations

**Use Cases**:
- View daily appointment schedule
- See vehicle diagnostic reports
- Update service status (in-progress, completed)
- View service bay availability
- Manage workload distribution
- Access vehicle maintenance history
- Complete service checklists
- Generate service invoices

**Dashboard Features**:
- Today's Appointments (with priority levels)
- Service Bay Status
- Workload Distribution
- Vehicle Diagnostic Reports
- Service Completion Forms
- Parts Inventory Status
- Customer Communication History

**Sample User**:
```json
{
  "name": "Priya Sharma",
  "role": "service_staff",
  "email": "priya.sharma@servicecenter.com",
  "service_center": "Metro Service Center - Delhi",
  "specialization": "brake_systems",
  "certifications": ["ASE_Certified", "OEM_Trained"]
}
```

---

### 3. Manufacturing Quality Engineer 🏭

**Profile**: Engineers analyzing defect patterns and implementing quality improvements

**Use Cases**:
- View RCA/CAPA reports
- Analyze recurring defect patterns
- Review manufacturing insights
- Track defect reduction metrics
- Generate quality improvement recommendations
- Monitor supplier quality scores
- View fleet-wide failure statistics
- Access historical CAPA effectiveness

**Dashboard Features**:
- RCA/CAPA Report Center
- Recurring Defects Dashboard
- Quality Metrics Trends
- Supplier Quality Scorecard
- Manufacturing Improvement Recommendations
- Defect Pattern Visualizations
- Impact Analysis Reports
- Manufacturing Plant Comparison

**Sample User**:
```json
{
  "name": "Amit Patel",
  "role": "manufacturing_engineer",
  "email": "amit.patel@automanufacturing.com",
  "department": "Quality Engineering",
  "plant": "Plant_APAC",
  "focus_areas": ["brake_systems", "electrical_components"]
}
```

---

### 4. System Administrator 👨‍💼

**Profile**: IT admin monitoring AI agent orchestration and system health

**Use Cases**:
- Monitor all AI agents status
- View UEBA security alerts
- Manage circuit breakers
- Review system health metrics
- Access audit trails
- Configure agent parameters
- Manage user permissions
- View compliance dashboards

**Dashboard Features**:
- Master Agent Orchestration Monitor
- 7 Worker Agents Status
- UEBA Alert Dashboard
- Circuit Breaker States
- System Performance Metrics
- Security Compliance Status (SOX, GDPR, ISO27001, NIST)
- Audit Trail Viewer
- Agent Execution History
- Error Logs & Troubleshooting

**Sample User**:
```json
{
  "name": "Sarah Johnson",
  "role": "system_admin",
  "email": "sarah.johnson@automind.com",
  "permissions": ["all"],
  "two_factor_enabled": true,
  "last_login": "2025-11-06T10:30:00Z"
}
```

---

### 5. Fleet Manager 📊 (Bonus Role)

**Profile**: Corporate fleet manager overseeing multiple vehicles

**Use Cases**:
- Manage fleet of vehicles
- Bulk operations (schedule multiple services)
- Fleet-wide health overview
- Cost analysis across fleet
- Predictive budget planning
- Vehicle utilization tracking
- Driver behavior analysis

**Dashboard Features**:
- Fleet Overview Map
- Multi-Vehicle Health Status
- Bulk Scheduling Interface
- Fleet Cost Analytics
- Maintenance Budget Forecasting
- Vehicle Utilization Reports
- Driver Performance Metrics

**Sample User**:
```json
{
  "name": "Vikram Singh",
  "role": "fleet_manager",
  "email": "vikram.singh@corpfleet.com",
  "company": "ABC Logistics",
  "fleet_size": 50,
  "vehicles": ["...50 vehicle IDs..."]
}
```

---

## 🔐 Implementation Architecture

### Database Schema

```python
# Add to database_models.py

class User(Base):
    """User accounts with role-based access"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # Hashed password
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    role = Column(String(50), nullable=False)  # customer, service_staff, manufacturing_engineer, system_admin, fleet_manager

    # Role-specific data (JSON for flexibility)
    role_data = Column(JSON)

    # Authentication
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    owned_vehicles = relationship("CustomerVehicle", back_populates="user", foreign_keys="CustomerVehicle.user_id")

    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_role", "role"),
    )


class UserSession(Base):
    """Track user sessions for security"""
    __tablename__ = "user_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token = Column(String(500), unique=True, nullable=False)  # JWT token
    ip_address = Column(String(50))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)


class Permission(Base):
    """Role-based permissions"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(50), nullable=False)
    resource = Column(String(100), nullable=False)  # e.g., "vehicles", "agents", "rca_reports"
    action = Column(String(50), nullable=False)  # e.g., "read", "write", "delete"

    __table_args__ = (
        UniqueConstraint("role", "resource", "action", name="unique_permission"),
    )
```

---

## 🔑 Authentication System

### Backend API (Python)

```python
# auth.py - Authentication service

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict

class AuthService:
    """Handle user authentication and authorization"""

    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    @staticmethod
    def create_token(user_id: str, role: str, expiry_hours: int = 24) -> str:
        """Create JWT token"""
        payload = {
            "user_id": user_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=expiry_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, AuthService.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, AuthService.SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def check_permission(role: str, resource: str, action: str) -> bool:
        """Check if role has permission for resource/action"""
        # Define role permissions
        PERMISSIONS = {
            "customer": {
                "vehicles": ["read"],
                "appointments": ["read", "create", "update"],
                "feedback": ["create"],
                "notifications": ["read"]
            },
            "service_staff": {
                "vehicles": ["read"],
                "appointments": ["read", "update"],
                "diagnostics": ["read"],
                "service_records": ["read", "create", "update"]
            },
            "manufacturing_engineer": {
                "rca_reports": ["read", "create"],
                "capa_reports": ["read", "create"],
                "manufacturing_insights": ["read"],
                "quality_metrics": ["read"]
            },
            "system_admin": {
                "*": ["*"]  # Full access
            },
            "fleet_manager": {
                "vehicles": ["read", "create"],
                "appointments": ["read", "create", "update"],
                "fleet_analytics": ["read"]
            }
        }

        role_perms = PERMISSIONS.get(role, {})
        if "*" in role_perms and "*" in role_perms["*"]:
            return True

        resource_perms = role_perms.get(resource, [])
        return action in resource_perms


# Add to api_server.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = AuthService.verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return payload


def require_role(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(func):
        async def wrapper(*args, user = Depends(get_current_user), **kwargs):
            if user["role"] not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {allowed_roles}"
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator


# API Endpoints with role protection

@app.post("/api/v1/auth/login")
async def login(email: str, password: str):
    """User login"""
    user = db.get_user_by_email(email)
    if not user or not AuthService.verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = AuthService.create_token(user.id, user.role)

    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "role": user.role
        }
    }


@app.get("/api/v1/vehicles")
@require_role("customer", "service_staff", "fleet_manager", "system_admin")
async def get_vehicles(user = Depends(get_current_user)):
    """Get vehicles (filtered by role)"""
    if user["role"] == "customer":
        # Only show user's own vehicles
        return db.get_vehicles_by_user(user["user_id"])
    elif user["role"] == "fleet_manager":
        # Show fleet vehicles
        return db.get_vehicles_by_fleet_manager(user["user_id"])
    else:
        # Show all vehicles
        return db.get_all_vehicles()


@app.get("/api/v1/rca-reports")
@require_role("manufacturing_engineer", "system_admin")
async def get_rca_reports(user = Depends(get_current_user)):
    """Get RCA/CAPA reports (manufacturing only)"""
    return db.get_rca_reports()


@app.get("/api/v1/agents/status")
@require_role("system_admin")
async def get_agent_status(user = Depends(get_current_user)):
    """Get agent orchestration status (admin only)"""
    return master_agent.get_status()
```

---

## 🎨 Frontend Implementation

### React Components

#### 1. Login Page

```typescript
// frontend/src/pages/Login.tsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('');
  const navigate = useNavigate();

  const demoUsers = [
    { name: 'Rajesh Kumar', role: 'customer', email: 'rajesh@demo.com', icon: '🚗' },
    { name: 'Priya Sharma', role: 'service_staff', email: 'priya@demo.com', icon: '🔧' },
    { name: 'Amit Patel', role: 'manufacturing_engineer', email: 'amit@demo.com', icon: '🏭' },
    { name: 'Sarah Johnson', role: 'system_admin', email: 'sarah@demo.com', icon: '👨‍💼' },
  ];

  const handleDemoLogin = async (demoUser: any) => {
    try {
      const response = await apiService.login(demoUser.email, 'demo123');
      localStorage.setItem('token', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));

      // Redirect based on role
      switch(response.user.role) {
        case 'customer':
          navigate('/customer-dashboard');
          break;
        case 'service_staff':
          navigate('/service-dashboard');
          break;
        case 'manufacturing_engineer':
          navigate('/manufacturing-dashboard');
          break;
        case 'system_admin':
          navigate('/admin-dashboard');
          break;
      }
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">AutoMind AI</h1>
          <p className="text-gray-600">Select your role to continue</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {demoUsers.map((user) => (
            <button
              key={user.role}
              onClick={() => handleDemoLogin(user)}
              className="bg-white rounded-xl p-6 shadow-lg hover:shadow-2xl transform hover:-translate-y-1 transition-all"
            >
              <div className="text-6xl mb-4">{user.icon}</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">{user.name}</h3>
              <p className="text-sm text-gray-600 mb-4 capitalize">
                {user.role.replace('_', ' ')}
              </p>
              <span className="inline-block px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold">
                Login as {user.name}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Login;
```

#### 2. Customer Dashboard

```typescript
// frontend/src/pages/CustomerDashboard.tsx

import React, { useState, useEffect } from 'react';
import { Car, Bell, Calendar, History } from 'lucide-react';
import { apiService } from '../services/api';

const CustomerDashboard: React.FC = () => {
  const [vehicles, setVehicles] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [appointments, setAppointments] = useState([]);

  useEffect(() => {
    fetchCustomerData();
  }, []);

  const fetchCustomerData = async () => {
    const vehiclesData = await apiService.getVehicles();
    const alertsData = await apiService.getAlerts();
    const appointmentsData = await apiService.getAppointments();

    setVehicles(vehiclesData);
    setAlerts(alertsData);
    setAppointments(appointmentsData);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">My Dashboard</h1>

        {/* My Vehicles */}
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <Car className="w-6 h-6 mr-2 text-blue-600" />
            My Vehicles
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {vehicles.map((vehicle) => (
              <VehicleCard key={vehicle.id} vehicle={vehicle} />
            ))}
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <Bell className="w-6 h-6 mr-2 text-yellow-600" />
            Recent Alerts
          </h2>
          <AlertList alerts={alerts} />
        </div>

        {/* Upcoming Appointments */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <Calendar className="w-6 h-6 mr-2 text-green-600" />
            Upcoming Appointments
          </h2>
          <AppointmentList appointments={appointments} />
        </div>
      </div>
    </div>
  );
};

export default CustomerDashboard;
```

#### 3. Manufacturing Dashboard

```typescript
// frontend/src/pages/ManufacturingDashboard.tsx

import React, { useState, useEffect } from 'react';
import { TrendingDown, AlertTriangle, FileText } from 'lucide-react';
import { apiService } from '../services/api';

const ManufacturingDashboard: React.FC = () => {
  const [rcaReports, setRcaReports] = useState([]);
  const [recurringDefects, setRecurringDefects] = useState([]);
  const [qualityMetrics, setQualityMetrics] = useState({});

  useEffect(() => {
    fetchManufacturingData();
  }, []);

  const fetchManufacturingData = async () => {
    const rcaData = await apiService.getRCAReports();
    const defectsData = await apiService.getRecurringDefects();
    const metricsData = await apiService.getQualityMetrics();

    setRcaReports(rcaData);
    setRecurringDefects(defectsData);
    setQualityMetrics(metricsData);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Manufacturing Quality Dashboard</h1>

        {/* Quality Metrics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <MetricCard
            title="Defect Rate"
            value={qualityMetrics.defectRate}
            trend="down"
            icon={<TrendingDown />}
          />
          {/* More metrics... */}
        </div>

        {/* RCA/CAPA Reports */}
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <FileText className="w-6 h-6 mr-2 text-purple-600" />
            RCA/CAPA Reports
          </h2>
          <RCAReportList reports={rcaReports} />
        </div>

        {/* Recurring Defects */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <AlertTriangle className="w-6 h-6 mr-2 text-red-600" />
            Recurring Defect Patterns
          </h2>
          <RecurringDefectsList defects={recurringDefects} />
        </div>
      </div>
    </div>
  );
};

export default ManufacturingDashboard;
```

---

## 🚀 Quick Implementation Steps

### Step 1: Update Database (30 minutes)
```bash
# Add User table and permissions to database_models.py
# Run migration
python database_manager.py migrate
```

### Step 2: Add Auth Service (1 hour)
```bash
# Create auth.py with AuthService class
# Install: pip install pyjwt bcrypt
# Add login endpoint to api_server.py
```

### Step 3: Create Demo Users (15 minutes)
```python
# create_demo_users.py
def create_demo_users():
    users = [
        {"email": "rajesh@demo.com", "password": "demo123", "role": "customer", ...},
        {"email": "priya@demo.com", "password": "demo123", "role": "service_staff", ...},
        {"email": "amit@demo.com", "password": "demo123", "role": "manufacturing_engineer", ...},
        {"email": "sarah@demo.com", "password": "demo123", "role": "system_admin", ...},
    ]
    for user in users:
        db.create_user(user)
```

### Step 4: Build Frontend (4-6 hours)
```bash
# Create Login.tsx page
# Create 4 role-specific dashboards
# Add auth context and protected routes
# Add logout functionality
```

### Step 5: Test & Polish (1 hour)
```bash
# Test login for each role
# Verify role-based access
# Test navigation between dashboards
```

---

## ✅ Total Estimated Time: 8-10 hours

---

## 📊 Demo Flow with User Roles

### Recommended Demo Sequence:

1. **Start at Login** (Show role selection)
2. **Login as Customer (Rajesh)** → View vehicle alerts → Receive AI call
3. **Switch to Admin (Sarah)** → Show UEBA detecting anomaly
4. **Switch to Manufacturing (Amit)** → View RCA/CAPA report
5. **Switch to Service Staff (Priya)** → Show appointment scheduling
6. **Back to Customer** → Book appointment → Provide feedback

This demonstrates **complete end-to-end workflow** with realistic user interactions!

---

**Let me know if you need the actual code implementation for any specific part!**
