"""
Authentication Service for AutoMind
Handles user authentication, JWT tokens, and role-based access control
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from functools import wraps
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


class AuthService:
    """Handle user authentication and authorization"""

    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "automind-secret-key-change-in-production-2025")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS = 24

    # Role-based permissions
    PERMISSIONS = {
        "customer": {
            "vehicles": ["read"],
            "appointments": ["read", "create", "update"],
            "alerts": ["read"],
            "feedback": ["create"],
            "notifications": ["read"],
        },
        "service_staff": {
            "vehicles": ["read"],
            "appointments": ["read", "update"],
            "diagnostics": ["read"],
            "service_records": ["read", "create", "update"],
            "workload": ["read"],
        },
        "manufacturing_engineer": {
            "rca_reports": ["read", "create"],
            "capa_reports": ["read", "create"],
            "manufacturing_insights": ["read"],
            "quality_metrics": ["read"],
            "defect_patterns": ["read"],
        },
        "system_admin": {
            "*": ["*"]  # Full access to everything
        },
        "fleet_manager": {
            "vehicles": ["read", "create", "update"],
            "appointments": ["read", "create", "update"],
            "fleet_analytics": ["read"],
            "bulk_operations": ["create"],
        }
    }

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    @staticmethod
    def create_token(user_id: str, role: str, email: str) -> str:
        """Create JWT token"""
        payload = {
            "user_id": user_id,
            "role": role,
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=AuthService.ACCESS_TOKEN_EXPIRE_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, AuthService.SECRET_KEY, algorithm=AuthService.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, AuthService.SECRET_KEY, algorithms=[AuthService.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    @staticmethod
    def check_permission(role: str, resource: str, action: str) -> bool:
        """Check if role has permission for resource/action"""
        role_perms = AuthService.PERMISSIONS.get(role, {})

        # Admin has full access
        if "*" in role_perms and "*" in role_perms["*"]:
            return True

        resource_perms = role_perms.get(resource, [])
        return action in resource_perms or "*" in resource_perms


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Dependency to get current user from JWT token"""
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    return payload


def require_role(*allowed_roles):
    """Decorator to require specific roles for endpoint access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: Dict = Depends(get_current_user), **kwargs):
            if user["role"] not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {allowed_roles}"
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator


def require_permission(resource: str, action: str):
    """Decorator to require specific permission for endpoint access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: Dict = Depends(get_current_user), **kwargs):
            if not AuthService.check_permission(user["role"], resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required permission: {action} on {resource}"
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator


# Demo users for quick testing
DEMO_USERS = [
    {
        "id": "user_customer_1",
        "email": "rajesh@demo.com",
        "password_hash": AuthService.hash_password("demo123"),
        "first_name": "Rajesh",
        "last_name": "Kumar",
        "role": "customer",
        "phone": "+91-9876543210",
        "role_data": {
            "vehicles": ["7ALSE94T6W43T3254"],
            "preferred_language": "hindi",
            "preferred_contact": "voice_call"
        }
    },
    {
        "id": "user_service_1",
        "email": "priya@demo.com",
        "password_hash": AuthService.hash_password("demo123"),
        "first_name": "Priya",
        "last_name": "Sharma",
        "role": "service_staff",
        "phone": "+91-9876543211",
        "role_data": {
            "service_center": "Metro Service Center - Delhi",
            "specialization": "brake_systems",
            "certifications": ["ASE_Certified", "OEM_Trained"]
        }
    },
    {
        "id": "user_mfg_1",
        "email": "amit@demo.com",
        "password_hash": AuthService.hash_password("demo123"),
        "first_name": "Amit",
        "last_name": "Patel",
        "role": "manufacturing_engineer",
        "phone": "+91-9876543212",
        "role_data": {
            "department": "Quality Engineering",
            "plant": "Plant_APAC",
            "focus_areas": ["brake_systems", "electrical_components"]
        }
    },
    {
        "id": "user_admin_1",
        "email": "sarah@demo.com",
        "password_hash": AuthService.hash_password("demo123"),
        "first_name": "Sarah",
        "last_name": "Johnson",
        "role": "system_admin",
        "phone": "+1-5551234567",
        "role_data": {
            "permissions": ["all"],
            "department": "IT Operations"
        }
    }
]


def get_demo_user_by_email(email: str) -> Optional[Dict]:
    """Get demo user by email"""
    for user in DEMO_USERS:
        if user["email"] == email:
            return user
    return None


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user by email and password"""
    user = get_demo_user_by_email(email)
    if not user:
        return None

    if not AuthService.verify_password(password, user["password_hash"]):
        return None

    # Return user without password hash
    user_data = user.copy()
    del user_data["password_hash"]
    return user_data
