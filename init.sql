-- AutoMind Database Initialization Script
-- PostgreSQL database setup for Automotive Predictive Maintenance System

-- Create database (run this separately if needed)
-- CREATE DATABASE automind_db;

-- Connect to the database
\c automind_db;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "timescaledb" CASCADE;

-- Create schemas for organization
CREATE SCHEMA IF NOT EXISTS automind;
CREATE SCHEMA IF NOT EXISTS monitoring;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Set default schema
SET search_path TO automind, public;

-- Create custom types
CREATE TYPE contact_method AS ENUM ('voice', 'app_notification', 'email', 'sms');
CREATE TYPE appointment_status AS ENUM ('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled');
CREATE TYPE priority_level AS ENUM ('P0', 'P1', 'P2', 'P3');
CREATE TYPE service_type AS ENUM ('scheduled', 'repair', 'inspection', 'recall');
CREATE TYPE feedback_type AS ENUM ('service_satisfaction', 'app_experience', 'general');
CREATE TYPE sentiment_label AS ENUM ('positive', 'neutral', 'negative');

-- Vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    id VARCHAR(50) PRIMARY KEY,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL CHECK (year >= 1900 AND year <= EXTRACT(YEAR FROM CURRENT_DATE) + 2),
    engine_type VARCHAR(50),
    transmission_type VARCHAR(50),
    mileage INTEGER DEFAULT 0 CHECK (mileage >= 0),
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_service_date TIMESTAMP WITH TIME ZONE,
    warranty_expiry TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    preferred_contact_method contact_method DEFAULT 'app_notification',
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    notification_preferences JSONB,
    service_history_consent BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Customer-Vehicle association table
CREATE TABLE IF NOT EXISTS customer_vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    vehicle_id VARCHAR(50) NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    relationship_type VARCHAR(20) DEFAULT 'owner' CHECK (relationship_type IN ('owner', 'lessee', 'authorized_user')),
    start_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP WITH TIME ZONE,
    is_primary BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id, vehicle_id)
);

-- Telemetry data table (TimescaleDB hypertable)
CREATE TABLE IF NOT EXISTS telemetry_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id VARCHAR(50) NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Engine metrics
    engine_rpm REAL CHECK (engine_rpm >= 0),
    engine_temperature REAL,
    coolant_temp REAL,
    oil_pressure REAL CHECK (oil_pressure >= 0),
    oil_temperature REAL,
    
    -- Electrical system
    battery_voltage REAL CHECK (battery_voltage >= 0),
    alternator_output REAL CHECK (alternator_output >= 0),
    
    -- Braking system
    brake_pad_thickness_fl REAL CHECK (brake_pad_thickness_fl >= 0),
    brake_pad_thickness_fr REAL CHECK (brake_pad_thickness_fr >= 0),
    brake_pad_thickness_rl REAL CHECK (brake_pad_thickness_rl >= 0),
    brake_pad_thickness_rr REAL CHECK (brake_pad_thickness_rr >= 0),
    brake_fluid_level REAL CHECK (brake_fluid_level >= 0 AND brake_fluid_level <= 100),
    
    -- Tires
    tire_pressure_fl REAL CHECK (tire_pressure_fl >= 0),
    tire_pressure_fr REAL CHECK (tire_pressure_fr >= 0),
    tire_pressure_rl REAL CHECK (tire_pressure_rl >= 0),
    tire_pressure_rr REAL CHECK (tire_pressure_rr >= 0),
    tire_temperature_fl REAL,
    tire_temperature_fr REAL,
    tire_temperature_rl REAL,
    tire_temperature_rr REAL,
    
    -- Transmission
    transmission_fluid_level REAL CHECK (transmission_fluid_level >= 0 AND transmission_fluid_level <= 100),
    transmission_temperature REAL,
    gear_position VARCHAR(10),
    
    -- General
    mileage INTEGER CHECK (mileage >= 0),
    fuel_level REAL CHECK (fuel_level >= 0 AND fuel_level <= 100),
    speed REAL CHECK (speed >= 0),
    location_lat REAL CHECK (location_lat >= -90 AND location_lat <= 90),
    location_lng REAL CHECK (location_lng >= -180 AND location_lng <= 180),
    
    -- Diagnostics
    error_codes JSONB,
    diagnostic_data JSONB,
    data_quality_score REAL DEFAULT 1.0 CHECK (data_quality_score >= 0 AND data_quality_score <= 1),
    sensor_status JSONB
);

-- Convert telemetry_data to TimescaleDB hypertable
SELECT create_hypertable('telemetry_data', 'timestamp', if_not_exists => TRUE);

-- Maintenance records table
CREATE TABLE IF NOT EXISTS maintenance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id VARCHAR(50) NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    service_date TIMESTAMP WITH TIME ZONE NOT NULL,
    service_type service_type NOT NULL,
    
    -- Service details
    components_serviced JSONB,
    parts_replaced JSONB,
    labor_hours REAL CHECK (labor_hours >= 0),
    total_cost REAL CHECK (total_cost >= 0),
    
    -- Service provider
    service_provider VARCHAR(200),
    technician_id VARCHAR(50),
    service_location VARCHAR(200),
    
    -- Maintenance specifics
    mileage_at_service INTEGER CHECK (mileage_at_service >= 0),
    next_service_due_mileage INTEGER CHECK (next_service_due_mileage >= 0),
    next_service_due_date TIMESTAMP WITH TIME ZONE,
    
    -- Quality and compliance
    service_quality_rating REAL CHECK (service_quality_rating >= 1 AND service_quality_rating <= 10),
    warranty_work BOOLEAN DEFAULT FALSE,
    recall_related BOOLEAN DEFAULT FALSE,
    
    -- Documentation
    service_notes TEXT,
    before_photos JSONB,
    after_photos JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Service appointments table
CREATE TABLE IF NOT EXISTS service_appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    vehicle_id VARCHAR(50) NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    
    -- Appointment details
    appointment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    estimated_duration_hours REAL DEFAULT 2.0 CHECK (estimated_duration_hours > 0),
    service_type VARCHAR(50) NOT NULL,
    priority_level priority_level DEFAULT 'P3',
    
    -- Status tracking
    status appointment_status DEFAULT 'scheduled',
    confirmation_method contact_method,
    confirmation_date TIMESTAMP WITH TIME ZONE,
    
    -- Service details
    requested_services JSONB,
    estimated_cost REAL CHECK (estimated_cost >= 0),
    actual_cost REAL CHECK (actual_cost >= 0),
    
    -- Location and provider
    service_location VARCHAR(200),
    service_provider VARCHAR(200),
    assigned_technician VARCHAR(100),
    
    -- Customer communication
    reminder_sent BOOLEAN DEFAULT FALSE,
    reminder_date TIMESTAMP WITH TIME ZONE,
    customer_notes TEXT,
    internal_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Feedback records table
CREATE TABLE IF NOT EXISTS feedback_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    vehicle_id VARCHAR(50) REFERENCES vehicles(id) ON DELETE SET NULL,
    appointment_id UUID REFERENCES service_appointments(id) ON DELETE SET NULL,
    
    -- Feedback details
    feedback_type feedback_type NOT NULL,
    overall_rating REAL CHECK (overall_rating >= 1 AND overall_rating <= 10),
    service_quality_rating REAL CHECK (service_quality_rating >= 1 AND service_quality_rating <= 10),
    communication_rating REAL CHECK (communication_rating >= 1 AND communication_rating <= 10),
    timeliness_rating REAL CHECK (timeliness_rating >= 1 AND timeliness_rating <= 10),
    
    -- Feedback content
    feedback_text TEXT,
    improvement_suggestions TEXT,
    would_recommend BOOLEAN,
    
    -- Sentiment analysis
    sentiment_score REAL CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    sentiment_label sentiment_label,
    
    -- Follow-up
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_completed BOOLEAN DEFAULT FALSE,
    follow_up_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Agent baselines table (for UEBA monitoring)
CREATE TABLE IF NOT EXISTS agent_baselines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    
    -- Behavioral patterns
    typical_actions_per_hour REAL CHECK (typical_actions_per_hour >= 0),
    typical_resources_accessed JSONB,
    normal_workflow_sequence JSONB,
    average_processing_time REAL CHECK (average_processing_time >= 0),
    
    -- Performance metrics
    success_rate REAL DEFAULT 1.0 CHECK (success_rate >= 0 AND success_rate <= 1),
    error_rate REAL DEFAULT 0.0 CHECK (error_rate >= 0 AND error_rate <= 1),
    timeout_rate REAL DEFAULT 0.0 CHECK (timeout_rate >= 0 AND timeout_rate <= 1),
    
    -- Security patterns
    allowed_resources JSONB,
    typical_access_hours JSONB,
    
    -- Baseline metadata
    baseline_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    baseline_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    data_points_count INTEGER DEFAULT 0 CHECK (data_points_count >= 0),
    confidence_score REAL DEFAULT 0.0 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Agent activities table (for monitoring and analytics)
CREATE TABLE IF NOT EXISTS agent_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    
    -- Activity details
    action_type VARCHAR(50) NOT NULL,
    target_resource VARCHAR(200),
    payload_size INTEGER DEFAULT 0 CHECK (payload_size >= 0),
    processing_time REAL CHECK (processing_time >= 0),
    
    -- Context
    vehicle_id VARCHAR(50),
    customer_id UUID,
    session_id VARCHAR(100),
    
    -- Results
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    response_data JSONB,
    
    -- Timing
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hour_of_day INTEGER CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
    day_of_week INTEGER CHECK (day_of_week >= 0 AND day_of_week <= 6),
    
    -- Security and compliance
    anomaly_detected BOOLEAN DEFAULT FALSE,
    anomaly_type VARCHAR(50),
    risk_score REAL DEFAULT 0.0 CHECK (risk_score >= 0 AND risk_score <= 1)
);

-- Convert agent_activities to TimescaleDB hypertable
SELECT create_hypertable('agent_activities', 'timestamp', if_not_exists => TRUE);

-- System metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL CHECK (metric_type IN ('counter', 'gauge', 'histogram')),
    
    -- Metric values
    value REAL NOT NULL,
    unit VARCHAR(20),
    
    -- Context and tags
    component VARCHAR(100),
    environment VARCHAR(50) DEFAULT 'production',
    tags JSONB,
    
    -- Timing
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Convert system_metrics to TimescaleDB hypertable
SELECT create_hypertable('system_metrics', 'timestamp', if_not_exists => TRUE);

-- Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_vehicles_make_model ON vehicles(make, model);
CREATE INDEX IF NOT EXISTS idx_vehicles_year ON vehicles(year);
CREATE INDEX IF NOT EXISTS idx_vehicles_active ON vehicles(is_active) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_customers_active ON customers(is_active) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_customer_vehicles_customer ON customer_vehicles(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_vehicles_vehicle ON customer_vehicles(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_customer_vehicles_active ON customer_vehicles(customer_id, vehicle_id) WHERE end_date IS NULL;

CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle_timestamp ON telemetry_data(vehicle_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_quality ON telemetry_data(data_quality_score) WHERE data_quality_score < 0.8;

CREATE INDEX IF NOT EXISTS idx_maintenance_vehicle_date ON maintenance_records(vehicle_id, service_date DESC);
CREATE INDEX IF NOT EXISTS idx_maintenance_type ON maintenance_records(service_type);
CREATE INDEX IF NOT EXISTS idx_maintenance_next_due ON maintenance_records(next_service_due_date) WHERE next_service_due_date IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_appointments_date ON service_appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_customer ON service_appointments(customer_id, appointment_date DESC);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON service_appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_vehicle ON service_appointments(vehicle_id, appointment_date DESC);

CREATE INDEX IF NOT EXISTS idx_feedback_customer ON feedback_records(customer_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback_records(overall_rating);
CREATE INDEX IF NOT EXISTS idx_feedback_sentiment ON feedback_records(sentiment_score);

CREATE INDEX IF NOT EXISTS idx_agent_baselines_agent_id ON agent_baselines(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_baselines_type ON agent_baselines(agent_type);

CREATE INDEX IF NOT EXISTS idx_agent_activities_agent_timestamp ON agent_activities(agent_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_agent_activities_type ON agent_activities(action_type);
CREATE INDEX IF NOT EXISTS idx_agent_activities_anomaly ON agent_activities(anomaly_detected, timestamp DESC) WHERE anomaly_detected = TRUE;
CREATE INDEX IF NOT EXISTS idx_agent_activities_vehicle ON agent_activities(vehicle_id, timestamp DESC) WHERE vehicle_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_system_metrics_name_timestamp ON system_metrics(metric_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_metrics_component ON system_metrics(component, timestamp DESC);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_vehicles_updated_at BEFORE UPDATE ON vehicles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maintenance_records_updated_at BEFORE UPDATE ON maintenance_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_appointments_updated_at BEFORE UPDATE ON service_appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_baselines_updated_at BEFORE UPDATE ON agent_baselines
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE OR REPLACE VIEW active_vehicles AS
SELECT v.*, cv.customer_id, c.first_name, c.last_name, c.email
FROM vehicles v
JOIN customer_vehicles cv ON v.id = cv.vehicle_id
JOIN customers c ON cv.customer_id = c.id
WHERE v.is_active = TRUE AND c.is_active = TRUE AND cv.end_date IS NULL;

CREATE OR REPLACE VIEW recent_telemetry AS
SELECT DISTINCT ON (vehicle_id) 
    vehicle_id, timestamp, engine_rpm, engine_temperature, battery_voltage,
    fuel_level, mileage, error_codes, data_quality_score
FROM telemetry_data
ORDER BY vehicle_id, timestamp DESC;

CREATE OR REPLACE VIEW maintenance_due AS
SELECT v.id as vehicle_id, v.make, v.model, v.year, v.mileage,
       mr.next_service_due_date, mr.next_service_due_mileage,
       c.first_name, c.last_name, c.email, c.preferred_contact_method
FROM vehicles v
JOIN customer_vehicles cv ON v.id = cv.vehicle_id
JOIN customers c ON cv.customer_id = c.id
LEFT JOIN maintenance_records mr ON v.id = mr.vehicle_id
WHERE v.is_active = TRUE 
  AND c.is_active = TRUE 
  AND cv.end_date IS NULL
  AND (mr.next_service_due_date <= CURRENT_DATE + INTERVAL '30 days' 
       OR v.mileage >= mr.next_service_due_mileage - 1000);

-- Insert sample data for testing
INSERT INTO vehicles (id, make, model, year, engine_type, transmission_type, mileage) VALUES
('VIN123456789', 'Toyota', 'Camry', 2022, 'Hybrid', 'CVT', 15000),
('VIN987654321', 'Honda', 'Accord', 2021, 'Gasoline', 'Automatic', 25000),
('VIN456789123', 'Tesla', 'Model 3', 2023, 'Electric', 'Single-Speed', 8000)
ON CONFLICT (id) DO NOTHING;

INSERT INTO customers (first_name, last_name, email, phone, preferred_contact_method) VALUES
('John', 'Doe', 'john.doe@email.com', '+1-555-0101', 'app_notification'),
('Jane', 'Smith', 'jane.smith@email.com', '+1-555-0102', 'email'),
('Mike', 'Johnson', 'mike.johnson@email.com', '+1-555-0103', 'sms')
ON CONFLICT (email) DO NOTHING;

-- Link customers to vehicles
INSERT INTO customer_vehicles (customer_id, vehicle_id, relationship_type, is_primary)
SELECT c.id, 'VIN123456789', 'owner', TRUE
FROM customers c WHERE c.email = 'john.doe@email.com'
ON CONFLICT (customer_id, vehicle_id) DO NOTHING;

INSERT INTO customer_vehicles (customer_id, vehicle_id, relationship_type, is_primary)
SELECT c.id, 'VIN987654321', 'owner', TRUE
FROM customers c WHERE c.email = 'jane.smith@email.com'
ON CONFLICT (customer_id, vehicle_id) DO NOTHING;

INSERT INTO customer_vehicles (customer_id, vehicle_id, relationship_type, is_primary)
SELECT c.id, 'VIN456789123', 'owner', TRUE
FROM customers c WHERE c.email = 'mike.johnson@email.com'
ON CONFLICT (customer_id, vehicle_id) DO NOTHING;

-- Create database user for the application
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'automind_app') THEN
        CREATE ROLE automind_app WITH LOGIN PASSWORD 'secure_password_change_in_production';
    END IF;
END
$$;

-- Grant permissions
GRANT USAGE ON SCHEMA automind TO automind_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA automind TO automind_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA automind TO automind_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA automind TO automind_app;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA automind GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO automind_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA automind GRANT USAGE, SELECT ON SEQUENCES TO automind_app;

-- Create retention policies for TimescaleDB (optional)
-- Keep telemetry data for 2 years
SELECT add_retention_policy('telemetry_data', INTERVAL '2 years', if_not_exists => TRUE);

-- Keep agent activities for 1 year
SELECT add_retention_policy('agent_activities', INTERVAL '1 year', if_not_exists => TRUE);

-- Keep system metrics for 6 months
SELECT add_retention_policy('system_metrics', INTERVAL '6 months', if_not_exists => TRUE);

-- Create continuous aggregates for analytics (TimescaleDB feature)
CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) AS hour,
    vehicle_id,
    AVG(engine_rpm) as avg_engine_rpm,
    AVG(engine_temperature) as avg_engine_temp,
    AVG(battery_voltage) as avg_battery_voltage,
    AVG(fuel_level) as avg_fuel_level,
    COUNT(*) as data_points
FROM telemetry_data
GROUP BY hour, vehicle_id;

-- Add refresh policy for continuous aggregate
SELECT add_continuous_aggregate_policy('telemetry_hourly',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE);

-- Final message
SELECT 'AutoMind database initialization completed successfully!' as status;