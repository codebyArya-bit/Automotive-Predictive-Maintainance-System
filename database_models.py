"""
Database Models for AutoMind - Automotive Predictive Maintenance System
SQLAlchemy ORM models for PostgreSQL database
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    JSON,
    ForeignKey,
    Index,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class Vehicle(Base):
    """Vehicle information and registration"""

    __tablename__ = "vehicles"

    id = Column(String(50), primary_key=True)  # VIN or custom ID
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    engine_type = Column(String(50))
    transmission_type = Column(String(50))
    mileage = Column(Integer, default=0)
    registration_date = Column(DateTime, default=func.now())
    last_service_date = Column(DateTime)
    warranty_expiry = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationships
    telemetry_data = relationship("TelemetryData", back_populates="vehicle")
    maintenance_records = relationship("MaintenanceRecord", back_populates="vehicle")
    customer_vehicles = relationship("CustomerVehicle", back_populates="vehicle")

    __table_args__ = (
        Index("idx_vehicle_make_model", "make", "model"),
        Index("idx_vehicle_year", "year"),
    )


class Customer(Base):
    """Customer information and preferences"""

    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    preferred_contact_method = Column(String(20), default="app_notification")  # voice, app_notification, email, sms
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Customer preferences
    notification_preferences = Column(JSON)  # JSON field for flexible preferences
    service_history_consent = Column(Boolean, default=True)

    # Relationships
    customer_vehicles = relationship("CustomerVehicle", back_populates="customer")
    appointments = relationship("ServiceAppointment", back_populates="customer")
    feedback_records = relationship("FeedbackRecord", back_populates="customer")

    __table_args__ = (
        Index("idx_customer_email", "email"),
        Index("idx_customer_name", "last_name", "first_name"),
    )


class CustomerVehicle(Base):
    """Association table for customer-vehicle relationships"""

    __tablename__ = "customer_vehicles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    vehicle_id = Column(String(50), ForeignKey("vehicles.id"), nullable=False)
    relationship_type = Column(String(20), default="owner")  # owner, lessee, authorized_user
    start_date = Column(DateTime, default=func.now())
    end_date = Column(DateTime)
    is_primary = Column(Boolean, default=True)

    # Relationships
    customer = relationship("Customer", back_populates="customer_vehicles")
    vehicle = relationship("Vehicle", back_populates="customer_vehicles")

    __table_args__ = (
        UniqueConstraint("customer_id", "vehicle_id", name="uq_customer_vehicle"),
        Index("idx_customer_vehicle_active", "customer_id", "vehicle_id", "end_date"),
    )


class TelemetryData(Base):
    """Vehicle telemetry data from sensors"""

    __tablename__ = "telemetry_data"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_id = Column(String(50), ForeignKey("vehicles.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())

    # Engine metrics
    engine_rpm = Column(Float)
    engine_temperature = Column(Float)
    coolant_temp = Column(Float)
    oil_pressure = Column(Float)
    oil_temperature = Column(Float)

    # Electrical system
    battery_voltage = Column(Float)
    alternator_output = Column(Float)

    # Braking system
    brake_pad_thickness_fl = Column(Float)  # Front Left
    brake_pad_thickness_fr = Column(Float)  # Front Right
    brake_pad_thickness_rl = Column(Float)  # Rear Left
    brake_pad_thickness_rr = Column(Float)  # Rear Right
    brake_fluid_level = Column(Float)

    # Tires
    tire_pressure_fl = Column(Float)
    tire_pressure_fr = Column(Float)
    tire_pressure_rl = Column(Float)
    tire_pressure_rr = Column(Float)
    tire_temperature_fl = Column(Float)
    tire_temperature_fr = Column(Float)
    tire_temperature_rl = Column(Float)
    tire_temperature_rr = Column(Float)

    # Transmission
    transmission_fluid_level = Column(Float)
    transmission_temperature = Column(Float)
    gear_position = Column(String(10))

    # General
    mileage = Column(Integer)
    fuel_level = Column(Float)
    speed = Column(Float)
    location_lat = Column(Float)
    location_lng = Column(Float)

    # Error codes and diagnostics
    error_codes = Column(JSON)  # Array of error codes
    diagnostic_data = Column(JSON)  # Additional diagnostic information

    # Data quality indicators
    data_quality_score = Column(Float, default=1.0)
    sensor_status = Column(JSON)  # Status of individual sensors

    # Relationships
    vehicle = relationship("Vehicle", back_populates="telemetry_data")

    __table_args__ = (
        Index("idx_telemetry_vehicle_timestamp", "vehicle_id", "timestamp"),
        Index("idx_telemetry_timestamp", "timestamp"),
        CheckConstraint("data_quality_score >= 0 AND data_quality_score <= 1", name="chk_data_quality"),
    )


class MaintenanceRecord(Base):
    """Maintenance and repair records"""

    __tablename__ = "maintenance_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_id = Column(String(50), ForeignKey("vehicles.id"), nullable=False)
    service_date = Column(DateTime, nullable=False)
    service_type = Column(String(50), nullable=False)  # scheduled, repair, inspection, recall

    # Service details
    components_serviced = Column(JSON)  # List of components
    parts_replaced = Column(JSON)  # Parts and part numbers
    labor_hours = Column(Float)
    total_cost = Column(Float)

    # Service provider
    service_provider = Column(String(200))
    technician_id = Column(String(50))
    service_location = Column(String(200))

    # Maintenance specifics
    mileage_at_service = Column(Integer)
    next_service_due_mileage = Column(Integer)
    next_service_due_date = Column(DateTime)

    # Quality and compliance
    service_quality_rating = Column(Float)  # 1 - 10 scale
    warranty_work = Column(Boolean, default=False)
    recall_related = Column(Boolean, default=False)

    # Documentation
    service_notes = Column(Text)
    before_photos = Column(JSON)  # URLs to photos
    after_photos = Column(JSON)  # URLs to photos

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_records")

    __table_args__ = (
        Index("idx_maintenance_vehicle_date", "vehicle_id", "service_date"),
        Index("idx_maintenance_type", "service_type"),
        Index("idx_maintenance_next_due", "next_service_due_date"),
    )


class ServiceAppointment(Base):
    """Service appointments and scheduling"""

    __tablename__ = "service_appointments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    vehicle_id = Column(String(50), ForeignKey("vehicles.id"), nullable=False)

    # Appointment details
    appointment_date = Column(DateTime, nullable=False)
    estimated_duration_hours = Column(Float, default=2.0)
    service_type = Column(String(50), nullable=False)
    priority_level = Column(String(10), default="P3")  # P0, P1, P2, P3

    # Status tracking
    status = Column(String(20), default="scheduled")  # scheduled, confirmed, in_progress, completed, cancelled
    confirmation_method = Column(String(20))  # voice, app, email, sms
    confirmation_date = Column(DateTime)

    # Service details
    requested_services = Column(JSON)  # List of requested services
    estimated_cost = Column(Float)
    actual_cost = Column(Float)

    # Location and provider
    service_location = Column(String(200))
    service_provider = Column(String(200))
    assigned_technician = Column(String(100))

    # Customer communication
    reminder_sent = Column(Boolean, default=False)
    reminder_date = Column(DateTime)
    customer_notes = Column(Text)
    internal_notes = Column(Text)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="appointments")
    vehicle = relationship("Vehicle")

    __table_args__ = (
        Index("idx_appointment_date", "appointment_date"),
        Index("idx_appointment_customer", "customer_id", "appointment_date"),
        Index("idx_appointment_status", "status"),
    )


class FeedbackRecord(Base):
    """Customer feedback and satisfaction tracking"""

    __tablename__ = "feedback_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    vehicle_id = Column(String(50), ForeignKey("vehicles.id"))
    appointment_id = Column(String(36), ForeignKey("service_appointments.id"))

    # Feedback details
    feedback_type = Column(String(30), nullable=False)  # service_satisfaction, app_experience, general
    overall_rating = Column(Float)  # 1 - 10 scale
    service_quality_rating = Column(Float)
    communication_rating = Column(Float)
    timeliness_rating = Column(Float)

    # Feedback content
    feedback_text = Column(Text)
    improvement_suggestions = Column(Text)
    would_recommend = Column(Boolean)

    # Sentiment analysis
    sentiment_score = Column(Float)  # -1 to 1 scale
    sentiment_label = Column(String(20))  # positive, neutral, negative

    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_completed = Column(Boolean, default=False)
    follow_up_notes = Column(Text)

    created_at = Column(DateTime, default=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="feedback_records")
    appointment = relationship("ServiceAppointment")

    __table_args__ = (
        Index("idx_feedback_customer", "customer_id", "created_at"),
        Index("idx_feedback_rating", "overall_rating"),
        Index("idx_feedback_sentiment", "sentiment_score"),
    )


class AgentBaseline(Base):
    """Agent behavioral baselines for UEBA monitoring"""

    __tablename__ = "agent_baselines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(100), nullable=False, unique=True)
    agent_type = Column(String(50), nullable=False)

    # Behavioral patterns
    typical_actions_per_hour = Column(Float)
    typical_resources_accessed = Column(JSON)  # List of resources
    normal_workflow_sequence = Column(JSON)  # Typical workflow steps
    average_processing_time = Column(Float)

    # Performance metrics
    success_rate = Column(Float, default=1.0)
    error_rate = Column(Float, default=0.0)
    timeout_rate = Column(Float, default=0.0)

    # Security patterns
    allowed_resources = Column(JSON)  # List of allowed resources
    typical_access_hours = Column(JSON)  # Typical operating hours

    # Baseline metadata
    baseline_period_start = Column(DateTime, nullable=False)
    baseline_period_end = Column(DateTime, nullable=False)
    data_points_count = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.0)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_agent_baseline_agent_id", "agent_id"),
        Index("idx_agent_baseline_type", "agent_type"),
    )


class AgentActivity(Base):
    """Agent activity logs for monitoring and analytics"""

    __tablename__ = "agent_activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(100), nullable=False)
    agent_type = Column(String(50), nullable=False)

    # Activity details
    action_type = Column(String(50), nullable=False)
    target_resource = Column(String(200))
    payload_size = Column(Integer, default=0)
    processing_time = Column(Float)

    # Context
    vehicle_id = Column(String(50))
    customer_id = Column(String(36))
    session_id = Column(String(100))

    # Results
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    response_data = Column(JSON)

    # Timing
    timestamp = Column(DateTime, nullable=False, default=func.now())
    hour_of_day = Column(Integer)  # 0 - 23 for pattern analysis
    day_of_week = Column(Integer)  # 0 - 6 for pattern analysis

    # Security and compliance
    anomaly_detected = Column(Boolean, default=False)
    anomaly_type = Column(String(50))
    risk_score = Column(Float, default=0.0)

    __table_args__ = (
        Index("idx_agent_activity_agent_timestamp", "agent_id", "timestamp"),
        Index("idx_agent_activity_type", "action_type"),
        Index("idx_agent_activity_anomaly", "anomaly_detected", "timestamp"),
        Index("idx_agent_activity_vehicle", "vehicle_id", "timestamp"),
    )


class SystemMetrics(Base):
    """System performance and health metrics"""

    __tablename__ = "system_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(100), nullable=False)
    metric_type = Column(String(50), nullable=False)  # counter, gauge, histogram

    # Metric values
    value = Column(Float, nullable=False)
    unit = Column(String(20))

    # Context and tags
    component = Column(String(100))  # master_agent, api_server, database, etc.
    environment = Column(String(50), default="production")
    tags = Column(JSON)  # Additional metadata

    # Timing
    timestamp = Column(DateTime, nullable=False, default=func.now())

    __table_args__ = (
        Index("idx_system_metrics_name_timestamp", "metric_name", "timestamp"),
        Index("idx_system_metrics_component", "component", "timestamp"),
    )


# Create all tables function
def create_tables(engine):
    """Create all database tables"""
    Base.metadata.create_all(engine)


# Drop all tables function (for development/testing)
def drop_tables(engine):
    """Drop all database tables"""
    Base.metadata.drop_all(engine)
