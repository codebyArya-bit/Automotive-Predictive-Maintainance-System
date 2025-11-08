"""
Centralized Database Manager for AutoMind
Handles PostgreSQL, Redis connections, SQLAlchemy ORM, and database migrations
"""

import os
import redis
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager, contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
import structlog
from datetime import datetime, timedelta
import json

from database_models import Base, Vehicle, Customer, TelemetryData, MaintenanceRecord
from config import Config

logger = structlog.get_logger(__name__)


class DatabaseManager:
    """
    Centralized database manager for AutoMind system
    Handles PostgreSQL with SQLAlchemy ORM and Redis connections
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._redis_client: Optional[redis.Redis] = None
        self._initialized = False

        # Connection parameters
        self.db_url = self._build_database_url()
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379 / 0")

    def _build_database_url(self) -> str:
        """Build database connection URL from environment variables"""
        # Check if DATABASE_URL is set (for SQLite fallback)
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return database_url

        # Otherwise build PostgreSQL URL
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "automind_db")
        user = os.getenv("DB_USER", "automind_app")
        password = os.getenv("DB_PASSWORD", "secure_password_change_in_production")

        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

    async def initialize(self):
        """Initialize database connections and create tables if needed"""
        if self._initialized:
            return

        try:
            # Determine if we're using SQLite or PostgreSQL
            is_sqlite = self.db_url.startswith("sqlite")

            if is_sqlite:
                # Initialize SQLite connection
                self._engine = create_engine(self.db_url, echo=False)  # Set to True for SQL debugging
            else:
                # Initialize PostgreSQL connection
                self._engine = create_engine(
                    self.db_url,
                    poolclass=QueuePool,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    pool_recycle=3600,  # Recycle connections every hour
                    echo=False,  # Set to True for SQL debugging
                )

            # Create session factory
            self._session_factory = sessionmaker(bind=self._engine, autocommit=False, autoflush=False)

            # Test database connection
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                db_type = "SQLite" if is_sqlite else "PostgreSQL"
                logger.info(f"{db_type} connection established successfully")

            # Create tables if they don't exist (for SQLite)
            if is_sqlite:
                from database_models import Base

                Base.metadata.create_all(self._engine)
                logger.info("Database tables created/verified")

            # Initialize Redis connection (optional for development)
            try:
                self._redis_client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )

                # Test Redis connection
                self._redis_client.ping()
                logger.info("Redis connection established successfully")
            except Exception as redis_error:
                logger.warning(f"Redis connection failed (optional): {redis_error}")
                self._redis_client = None

            self._initialized = True
            logger.info("Database manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            raise

    async def shutdown(self):
        """Shutdown database connections"""
        try:
            if self._redis_client:
                (
                    await self._redis_client.aclose()
                    if hasattr(self._redis_client, "aclose")
                    else self._redis_client.close()
                )
                logger.info("Redis connection closed")

            if self._engine:
                self._engine.dispose()
                logger.info("PostgreSQL connection pool disposed")

            self._initialized = False
            logger.info("Database manager shutdown completed")

        except Exception as e:
            logger.error(f"Error during database manager shutdown: {e}")

    @contextmanager
    def get_session(self) -> Session:
        """Get a database session with automatic cleanup"""
        if not self._initialized:
            raise RuntimeError("Database manager not initialized")

        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    @asynccontextmanager
    async def get_async_session(self):
        """Get an async database session (for future async support)"""
        # For now, use sync session in async context
        # TODO: Implement proper async SQLAlchemy when needed
        with self.get_session() as session:
            yield session

    def get_redis(self) -> redis.Redis:
        """Get Redis client"""
        if not self._initialized:
            raise RuntimeError("Database manager not initialized")
        return self._redis_client

    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(self._engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise

    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        try:
            Base.metadata.drop_all(self._engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on database connections"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "postgresql": {"status": "unknown", "error": None},
            "redis": {"status": "unknown", "error": None},
        }

        # Check PostgreSQL
        try:
            with self._engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
                if result == 1:
                    health_status["postgresql"]["status"] = "healthy"
                else:
                    health_status["postgresql"]["status"] = "unhealthy"
        except Exception as e:
            health_status["postgresql"]["status"] = "unhealthy"
            health_status["postgresql"]["error"] = str(e)

        # Check Redis
        try:
            self._redis_client.ping()
            health_status["redis"]["status"] = "healthy"
        except Exception as e:
            health_status["redis"]["status"] = "unhealthy"
            health_status["redis"]["error"] = str(e)

        return health_status

    # Telemetry Data Methods
    def insert_telemetry_data(self, telemetry_records: List[Dict[str, Any]]) -> int:
        """Insert telemetry data records"""
        try:
            with self.get_session() as session:
                inserted_count = 0
                for record in telemetry_records:
                    telemetry = TelemetryData(**record)
                    session.add(telemetry)
                    inserted_count += 1

                session.commit()
                logger.info(f"Inserted {inserted_count} telemetry records")
                return inserted_count

        except Exception as e:
            logger.error(f"Failed to insert telemetry data: {e}")
            raise

    def get_telemetry_data(self, vehicle_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get telemetry data for a vehicle"""
        try:
            with self.get_session() as session:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                telemetry_records = (
                    session.query(TelemetryData)
                    .filter(
                        TelemetryData.vehicle_id == vehicle_id,
                        TelemetryData.timestamp >= start_date,
                        TelemetryData.timestamp <= end_date,
                    )
                    .order_by(TelemetryData.timestamp.asc())
                    .all()
                )

                # Convert to dictionaries
                result = []
                for record in telemetry_records:
                    data = {
                        "id": record.id,
                        "vehicle_id": record.vehicle_id,
                        "timestamp": record.timestamp.isoformat(),
                        "engine_rpm": record.engine_rpm,
                        "engine_temperature": record.engine_temperature,
                        "battery_voltage": record.battery_voltage,
                        "oil_pressure": record.oil_pressure,
                        "brake_pad_thickness_fl": record.brake_pad_thickness_fl,
                        "tire_pressure_fl": record.tire_pressure_fl,
                        "tire_pressure_fr": record.tire_pressure_fr,
                        "tire_pressure_rl": record.tire_pressure_rl,
                        "tire_pressure_rr": record.tire_pressure_rr,
                        "fuel_level": record.fuel_level,
                        "mileage": record.mileage,
                        "error_codes": record.error_codes,
                        "data_quality_score": record.data_quality_score,
                    }
                    result.append(data)

                logger.info(f"Retrieved {len(result)} telemetry records for vehicle {vehicle_id}")
                return result

        except Exception as e:
            logger.error(f"Failed to get telemetry data: {e}")
            raise

    # Vehicle Methods
    def get_vehicle(self, vehicle_id: str) -> Optional[Dict[str, Any]]:
        """Get vehicle information"""
        try:
            with self.get_session() as session:
                vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
                if vehicle:
                    return {
                        "id": vehicle.id,
                        "make": vehicle.make,
                        "model": vehicle.model,
                        "year": vehicle.year,
                        "engine_type": vehicle.engine_type,
                        "transmission_type": vehicle.transmission_type,
                        "mileage": vehicle.mileage,
                        "registration_date": (
                            vehicle.registration_date.isoformat() if vehicle.registration_date else None
                        ),
                        "last_service_date": (
                            vehicle.last_service_date.isoformat() if vehicle.last_service_date else None
                        ),
                        "is_active": vehicle.is_active,
                    }
                return None

        except Exception as e:
            logger.error(f"Failed to get vehicle {vehicle_id}: {e}")
            raise

    def get_active_vehicles(self) -> List[Dict[str, Any]]:
        """Get all active vehicles"""
        try:
            with self.get_session() as session:
                vehicles = session.query(Vehicle).filter(Vehicle.is_active is True).all()
                result = []
                for vehicle in vehicles:
                    result.append(
                        {
                            "id": vehicle.id,
                            "make": vehicle.make,
                            "model": vehicle.model,
                            "year": vehicle.year,
                            "mileage": vehicle.mileage,
                            "last_service_date": (
                                vehicle.last_service_date.isoformat() if vehicle.last_service_date else None
                            ),
                        }
                    )

                logger.info(f"Retrieved {len(result)} active vehicles")
                return result

        except Exception as e:
            logger.error(f"Failed to get active vehicles: {e}")
            raise

    # Customer Methods
    def get_customer_by_vehicle(self, vehicle_id: str) -> Optional[Dict[str, Any]]:
        """Get customer information by vehicle ID"""
        try:
            with self.get_session() as session:
                # Query using the relationship
                result = (
                    session.query(Customer, Vehicle)
                    .join(Customer.customer_vehicles)
                    .join(Vehicle)
                    .filter(Vehicle.id == vehicle_id, Customer.is_active is True)
                    .first()
                )

                if result:
                    customer, vehicle = result
                    return {
                        "id": customer.id,
                        "first_name": customer.first_name,
                        "last_name": customer.last_name,
                        "email": customer.email,
                        "phone": customer.phone,
                        "preferred_contact_method": customer.preferred_contact_method,
                        "notification_preferences": customer.notification_preferences,
                    }
                return None

        except Exception as e:
            logger.error(f"Failed to get customer for vehicle {vehicle_id}: {e}")
            raise

    # Maintenance Methods
    def get_maintenance_history(self, vehicle_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get maintenance history for a vehicle"""
        try:
            with self.get_session() as session:
                records = (
                    session.query(MaintenanceRecord)
                    .filter(MaintenanceRecord.vehicle_id == vehicle_id)
                    .order_by(MaintenanceRecord.service_date.desc())
                    .limit(limit)
                    .all()
                )

                result = []
                for record in records:
                    result.append(
                        {
                            "id": record.id,
                            "service_date": record.service_date.isoformat(),
                            "service_type": record.service_type,
                            "components_serviced": record.components_serviced,
                            "total_cost": record.total_cost,
                            "service_provider": record.service_provider,
                            "next_service_due_date": (
                                record.next_service_due_date.isoformat() if record.next_service_due_date else None
                            ),
                            "service_notes": record.service_notes,
                        }
                    )

                logger.info(f"Retrieved {len(result)} maintenance records for vehicle {vehicle_id}")
                return result

        except Exception as e:
            logger.error(f"Failed to get maintenance history: {e}")
            raise

    # Cache Methods (Redis)
    def cache_set(self, key: str, value: Any, expire_seconds: int = 3600):
        """Set a value in Redis cache"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            self._redis_client.setex(key, expire_seconds, value)
            logger.debug(f"Cached value for key: {key}")
        except Exception as e:
            logger.error(f"Failed to set cache for key {key}: {e}")

    def cache_get(self, key: str) -> Optional[Any]:
        """Get a value from Redis cache"""
        try:
            value = self._redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Failed to get cache for key {key}: {e}")
            return None

    def cache_delete(self, key: str):
        """Delete a value from Redis cache"""
        try:
            self._redis_client.delete(key)
            logger.debug(f"Deleted cache for key: {key}")
        except Exception as e:
            logger.error(f"Failed to delete cache for key {key}: {e}")

    def cache_exists(self, key: str) -> bool:
        """Check if a key exists in Redis cache"""
        try:
            return bool(self._redis_client.exists(key))
        except Exception as e:
            logger.error(f"Failed to check cache existence for key {key}: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions for backward compatibility
def get_db_session():
    """Get database session (backward compatibility)"""
    return db_manager.get_session()


def get_redis_client():
    """Get Redis client (backward compatibility)"""
    return db_manager.get_redis()


async def initialize_database():
    """Initialize database connections"""
    await db_manager.initialize()


async def shutdown_database():
    """Shutdown database connections"""
    await db_manager.shutdown()
