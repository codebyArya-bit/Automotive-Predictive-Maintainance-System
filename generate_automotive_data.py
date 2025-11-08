#!/usr/bin/env python3
"""
Automotive Data Generator
Generates realistic automotive data for the AI system including:
- Vehicle telemetry data
- Maintenance records
- Service appointments
- Customer feedback
- Agent activities
- System metrics
"""

import sqlite3
import random
import json
import uuid
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# Database connection
DB_PATH = "automotive_ai.db"

# Vehicle makes and models for realistic data
VEHICLE_DATA = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Prius", "Sienna"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Odyssey", "Fit"],
    "Ford": ["F - 150", "Escape", "Explorer", "Mustang", "Focus", "Edge"],
    "Chevrolet": ["Silverado", "Equinox", "Malibu", "Tahoe", "Cruze", "Traverse"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "7 Series", "i3"],
    "Mercedes-Benz": ["C-Class", "E-Class", "GLC", "GLE", "S-Class", "A-Class"],
    "Audi": ["A4", "A6", "Q5", "Q7", "A3", "Q3"],
    "Nissan": ["Altima", "Sentra", "Rogue", "Pathfinder", "Maxima", "Murano"],
    "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Accent", "Palisade"],
    "Volkswagen": ["Jetta", "Passat", "Tiguan", "Atlas", "Golf", "Arteon"],
}

# OBD-II Parameters for realistic telemetry
OBD_PARAMETERS = [
    "ENGINE_RPM",
    "VEHICLE_SPEED",
    "ENGINE_LOAD",
    "COOLANT_TEMP",
    "INTAKE_TEMP",
    "THROTTLE_POS",
    "FUEL_LEVEL",
    "MAF",
    "INTAKE_PRESSURE",
    "TIMING_ADVANCE",
    "FUEL_TRIM_BANK1",
    "BAROMETRIC_PRESSURE",
    "CATALYST_TEMP_B1S1",
    "CONTROL_MODULE_VOLTAGE",
    "ABSOLUTE_THROTTLE_B",
    "ACCELERATOR_POS_D",
    "ACCELERATOR_POS_E",
    "FUEL_RAIL_PRESSURE",
]


def connect_db():
    """Connect to the SQLite database"""
    return sqlite3.connect(DB_PATH)


def generate_telemetry_data(conn, num_records=10000):
    """Generate realistic vehicle telemetry data"""
    print(f"Generating {num_records} telemetry records...")

    # Get existing vehicles
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM vehicles")
    vehicle_ids = [row[0] for row in cursor.fetchall()]

    if not vehicle_ids:
        print("No vehicles found. Please ensure vehicles exist in the database.")
        return

    telemetry_records = []
    base_time = datetime.now() - timedelta(days=30)

    for i in range(num_records):
        vehicle_id = random.choice(vehicle_ids)
        timestamp = base_time + timedelta(minutes=random.randint(0, 43200))  # 30 days worth

        # Generate realistic driving scenario
        driving_mode = random.choice(["idle", "city", "highway", "parking"])

        if driving_mode == "idle":
            speed = 0
            rpm = random.randint(700, 900)
            engine_load = random.randint(15, 25)
        elif driving_mode == "city":
            speed = random.randint(20, 50)
            rpm = random.randint(1500, 3000)
            engine_load = random.randint(30, 60)
        elif driving_mode == "highway":
            speed = random.randint(60, 80)
            rpm = random.randint(2000, 3500)
            engine_load = random.randint(40, 70)
        else:  # parking
            speed = random.randint(0, 10)
            rpm = random.randint(700, 1200)
            engine_load = random.randint(15, 30)

        # Generate correlated parameters
        coolant_temp = random.randint(85, 105) if rpm > 800 else random.randint(70, 90)
        intake_temp = random.randint(20, 40)
        throttle_pos = min(100, max(0, engine_load + random.randint(-10, 10)))
        fuel_level = random.randint(10, 95)

        # Create telemetry parameters JSON
        parameters = {
            "ENGINE_RPM": rpm,
            "VEHICLE_SPEED": speed,
            "ENGINE_LOAD": engine_load,
            "COOLANT_TEMP": coolant_temp,
            "INTAKE_TEMP": intake_temp,
            "THROTTLE_POS": throttle_pos,
            "FUEL_LEVEL": fuel_level,
            "MAF": random.randint(2, 25),
            "INTAKE_PRESSURE": random.randint(20, 100),
            "TIMING_ADVANCE": random.randint(-10, 30),
            "FUEL_TRIM_BANK1": random.randint(-10, 10),
            "BAROMETRIC_PRESSURE": random.randint(95, 105),
            "CATALYST_TEMP_B1S1": random.randint(300, 800),
            "CONTROL_MODULE_VOLTAGE": round(random.uniform(12.0, 14.5), 1),
            "ABSOLUTE_THROTTLE_B": throttle_pos + random.randint(-5, 5),
            "ACCELERATOR_POS_D": random.randint(0, 100),
            "ACCELERATOR_POS_E": random.randint(0, 100),
            "FUEL_RAIL_PRESSURE": random.randint(300, 600),
        }

        # Generate additional realistic values for all columns
        battery_voltage = round(random.uniform(12.0, 14.5), 1)
        oil_pressure = random.randint(20, 80)
        oil_temperature = random.randint(180, 220)

        # Brake pad thickness (new pads are ~12mm, worn are ~2mm)
        brake_pad_fl = round(random.uniform(2.0, 12.0), 1)
        brake_pad_fr = round(random.uniform(2.0, 12.0), 1)
        brake_pad_rl = round(random.uniform(2.0, 12.0), 1)
        brake_pad_rr = round(random.uniform(2.0, 12.0), 1)

        # Tire pressures (typically 30 - 35 PSI)
        tire_pressure_fl = random.randint(28, 36)
        tire_pressure_fr = random.randint(28, 36)
        tire_pressure_rl = random.randint(28, 36)
        tire_pressure_rr = random.randint(28, 36)

        # Tire temperatures
        tire_temp_fl = random.randint(80, 120)
        tire_temp_fr = random.randint(80, 120)
        tire_temp_rl = random.randint(80, 120)
        tire_temp_rr = random.randint(80, 120)

        # Transmission
        trans_fluid_level = round(random.uniform(0.7, 1.0), 2)
        trans_temp = random.randint(160, 200)
        gear_pos = random.choice(["P", "R", "N", "D", "1", "2", "3", "4", "5"])

        mileage = random.randint(10000, 150000)
        location_lat = round(random.uniform(25.0, 49.0), 6)  # US latitude range
        location_lng = round(random.uniform(-125.0, -66.0), 6)  # US longitude range

        # Error codes (occasionally present)
        error_codes = []
        if random.random() < 0.05:  # 5% chance of error codes
            error_codes = [f"P{random.randint(100, 999)}" for _ in range(random.randint(1, 3))]

        telemetry_records.append(
            (
                str(uuid.uuid4()),  # id
                vehicle_id,
                timestamp.isoformat(),
                rpm,
                coolant_temp,
                coolant_temp,  # engine_temperature (similar to coolant)
                oil_pressure,
                oil_temperature,
                battery_voltage,
                round(random.uniform(13.5, 14.8), 1),  # alternator_output
                brake_pad_fl,
                brake_pad_fr,
                brake_pad_rl,
                brake_pad_rr,
                round(random.uniform(0.8, 1.0), 2),  # brake_fluid_level
                tire_pressure_fl,
                tire_pressure_fr,
                tire_pressure_rl,
                tire_pressure_rr,
                tire_temp_fl,
                tire_temp_fr,
                tire_temp_rl,
                tire_temp_rr,
                trans_fluid_level,
                trans_temp,
                gear_pos,
                mileage,
                fuel_level,
                speed,
                location_lat,
                location_lng,
                json.dumps(error_codes),
                json.dumps(parameters),
            )
        )

        if i % 1000 == 0:
            print(f"Generated {i} telemetry records...")

    # Insert telemetry data
    cursor.executemany(
        """
        INSERT INTO telemetry_data
        (id, vehicle_id, timestamp, engine_rpm, engine_temperature, coolant_temp, oil_pressure,
         oil_temperature, battery_voltage, alternator_output, brake_pad_thickness_fl,
         brake_pad_thickness_fr, brake_pad_thickness_rl, brake_pad_thickness_rr,
         brake_fluid_level, tire_pressure_fl, tire_pressure_fr, tire_pressure_rl,
         tire_pressure_rr, tire_temperature_fl, tire_temperature_fr, tire_temperature_rl,
         tire_temperature_rr, transmission_fluid_level, transmission_temperature,
         gear_position, mileage, fuel_level, speed, location_lat, location_lng,
         error_codes, diagnostic_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        telemetry_records,
    )

    conn.commit()
    print(f"Successfully inserted {len(telemetry_records)} telemetry records")


def generate_maintenance_records(conn, num_records=500):
    """Generate realistic maintenance records"""
    print(f"Generating {num_records} maintenance records...")

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM vehicles")
    vehicle_ids = [row[0] for row in cursor.fetchall()]

    if not vehicle_ids:
        print("No vehicles found.")
        return

    maintenance_types = [
        "Oil Change",
        "Tire Rotation",
        "Brake Inspection",
        "Battery Check",
        "Air Filter Replacement",
        "Transmission Service",
        "Coolant Flush",
        "Spark Plug Replacement",
        "Brake Pad Replacement",
        "Wheel Alignment",
        "Engine Tune-up",
        "Timing Belt Replacement",
        "Fuel System Cleaning",
        "AC Service",
        "Power Steering Service",
    ]

    maintenance_records = []

    for i in range(num_records):
        vehicle_id = random.choice(vehicle_ids)
        service_date = fake.date_between(start_date="-2y", end_date="today")
        service_type = random.choice(maintenance_types)

        # Generate realistic costs based on service type
        cost_ranges = {
            "Oil Change": (30, 80),
            "Tire Rotation": (20, 50),
            "Brake Inspection": (50, 100),
            "Battery Check": (20, 40),
            "Air Filter Replacement": (25, 60),
            "Transmission Service": (150, 300),
            "Coolant Flush": (80, 150),
            "Spark Plug Replacement": (100, 200),
            "Brake Pad Replacement": (200, 400),
            "Wheel Alignment": (75, 150),
            "Engine Tune-up": (300, 600),
            "Timing Belt Replacement": (500, 1000),
            "Fuel System Cleaning": (100, 200),
            "AC Service": (150, 300),
            "Power Steering Service": (100, 200),
        }

        cost_range = cost_ranges.get(service_type, (50, 200))
        cost = round(random.uniform(cost_range[0], cost_range[1]), 2)

        mileage = random.randint(10000, 150000)
        description = f"{service_type} performed. " + fake.sentence()

        maintenance_records.append(
            (
                str(uuid.uuid4()),  # id
                vehicle_id,
                service_date.isoformat(),
                service_type,
                json.dumps([f"Component_{i}" for i in range(1, random.randint(2, 5))]),  # components_serviced
                json.dumps(
                    [f"Part_{random.randint(1000, 9999)}" for _ in range(random.randint(1, 3))]
                ),  # parts_replaced
                round(random.uniform(0.5, 8.0), 1),  # labor_hours
                cost,
                fake.company(),  # service_provider
                f"TECH_{random.randint(100, 999)}",  # technician_id
                fake.address(),  # service_location
                mileage,  # mileage_at_service
                mileage + random.randint(3000, 10000),  # next_service_due_mileage
                (service_date + timedelta(days=random.randint(90, 365))).isoformat(),  # next_service_due_date
                round(random.uniform(6.0, 10.0), 1),  # service_quality_rating
                random.choice([True, False]),  # warranty_work
                random.choice([True, False]),  # recall_related
                description,  # service_notes
                json.dumps([]),  # before_photos
                json.dumps([]),  # after_photos
            )
        )

    cursor.executemany(
        """
        INSERT INTO maintenance_records
        (id, vehicle_id, service_date, service_type, components_serviced, parts_replaced,
         labor_hours, total_cost, service_provider, technician_id, service_location,
         mileage_at_service, next_service_due_mileage, next_service_due_date,
         service_quality_rating, warranty_work, recall_related, service_notes,
         before_photos, after_photos)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        maintenance_records,
    )

    conn.commit()
    print(f"Successfully inserted {len(maintenance_records)} maintenance records")


def generate_service_appointments(conn, num_appointments=200):
    """Generate service appointments"""
    print(f"Generating {num_appointments} service appointments...")

    cursor = conn.cursor()

    # Get existing customer and vehicle IDs
    cursor.execute("SELECT id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM vehicles")
    vehicle_ids = [row[0] for row in cursor.fetchall()]

    if not vehicle_ids:
        print("No vehicles found.")
        return

    if not customer_ids:
        print("No customers found.")
        return

    service_types = [
        "Regular Maintenance",
        "Oil Change",
        "Brake Service",
        "Tire Service",
        "Engine Diagnostic",
        "Transmission Service",
        "AC Repair",
        "Battery Service",
        "Electrical Repair",
        "Suspension Service",
    ]

    priorities = ["P0", "P1", "P2", "P3"]

    service_appointments = []

    for i in range(num_appointments):
        vehicle_id = random.choice(vehicle_ids)
        customer_id = random.choice(customer_ids)

        # Mix of past and future appointments
        if random.random() < 0.7:  # 70% past appointments
            appointment_date = fake.date_time_between(start_date="-6m", end_date="now")
            status = random.choice(["completed", "cancelled"])
        else:  # 30% future appointments
            appointment_date = fake.date_time_between(start_date="now", end_date="+3m")
            status = random.choice(["scheduled", "confirmed"])

        service_type = random.choice(service_types)
        priority = random.choice(priorities)
        estimated_cost = round(random.uniform(50, 500), 2)
        actual_cost = round(random.uniform(50, 500), 2) if status == "completed" else None
        notes = fake.text(max_nb_chars=200)

        service_appointments.append(
            (
                str(uuid.uuid4()),  # id
                customer_id,  # customer_id
                vehicle_id,
                appointment_date.isoformat(),
                round(random.uniform(1.0, 6.0), 1),  # estimated_duration_hours
                service_type,
                priority,
                status,
                random.choice(["voice", "app", "email", "sms"]),  # confirmation_method
                (
                    (appointment_date - timedelta(days=random.randint(1, 7))).isoformat()
                    if status in ["confirmed", "completed"]
                    else None
                ),  # confirmation_date
                json.dumps([service_type, "Inspection"]),  # requested_services
                estimated_cost,
                actual_cost,  # actual_cost
                fake.address(),  # service_location
                fake.company(),  # service_provider
                f"TECH_{random.randint(100, 999)}",  # assigned_technician
                random.choice([True, False]),  # reminder_sent
                (
                    (appointment_date - timedelta(days=1)).isoformat() if random.choice([True, False]) else None
                ),  # reminder_date
                fake.text(max_nb_chars=100),  # customer_notes
                notes,  # internal_notes
            )
        )

    cursor.executemany(
        """
        INSERT INTO service_appointments
        (id, customer_id, vehicle_id, appointment_date, estimated_duration_hours,
         service_type, priority_level, status, confirmation_method, confirmation_date,
         requested_services, estimated_cost, actual_cost, service_location,
         service_provider, assigned_technician, reminder_sent, reminder_date,
         customer_notes, internal_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        service_appointments,
    )

    conn.commit()
    print(f"Successfully inserted {len(service_appointments)} service appointments")


def generate_feedback_records(conn, num_records=300):
    """Generate customer feedback records"""
    print(f"Generating {num_records} feedback records...")

    cursor = conn.cursor()

    # Get existing customer, vehicle, and appointment IDs
    cursor.execute("SELECT id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM vehicles")
    vehicle_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM service_appointments")
    appointment_ids = [row[0] for row in cursor.fetchall()]

    if not customer_ids:
        print("Warning: No customers found. Skipping feedback records.")
        return

    feedback_types = ["service_satisfaction", "app_experience", "general"]

    feedback_records = []

    for i in range(num_records):
        customer_id = random.choice(customer_ids)
        vehicle_id = random.choice(vehicle_ids) if vehicle_ids and random.choice([True, False]) else None
        appointment_id = random.choice(appointment_ids) if appointment_ids and random.choice([True, False]) else None

        feedback_type = random.choice(feedback_types)
        overall_rating = round(random.uniform(1.0, 10.0), 1)
        service_quality_rating = round(random.uniform(1.0, 10.0), 1)
        communication_rating = round(random.uniform(1.0, 10.0), 1)
        timeliness_rating = round(random.uniform(1.0, 10.0), 1)

        feedback_text = fake.text(max_nb_chars=500)
        improvement_suggestions = fake.text(max_nb_chars=200) if random.choice([True, False]) else None
        would_recommend = random.choice([True, False])

        # Generate sentiment based on overall rating
        if overall_rating >= 7:
            sentiment_score = round(random.uniform(0.3, 1.0), 2)
            sentiment_label = "positive"
        elif overall_rating >= 4:
            sentiment_score = round(random.uniform(-0.3, 0.3), 2)
            sentiment_label = "neutral"
        else:
            sentiment_score = round(random.uniform(-1.0, -0.3), 2)
            sentiment_label = "negative"

        follow_up_required = overall_rating < 5
        follow_up_completed = follow_up_required and random.choice([True, False])
        follow_up_notes = fake.text(max_nb_chars=200) if follow_up_completed else None

        feedback_records.append(
            (
                str(uuid.uuid4()),  # id
                customer_id,
                vehicle_id,
                appointment_id,
                feedback_type,
                overall_rating,
                service_quality_rating,
                communication_rating,
                timeliness_rating,
                feedback_text,
                improvement_suggestions,
                would_recommend,
                sentiment_score,
                sentiment_label,
                follow_up_required,
                follow_up_completed,
                follow_up_notes,
            )
        )

    cursor.executemany(
        """
        INSERT INTO feedback_records
        (id, customer_id, vehicle_id, appointment_id, feedback_type, overall_rating,
         service_quality_rating, communication_rating, timeliness_rating, feedback_text,
         improvement_suggestions, would_recommend, sentiment_score, sentiment_label,
         follow_up_required, follow_up_completed, follow_up_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        feedback_records,
    )

    conn.commit()
    print(f"Successfully inserted {len(feedback_records)} feedback records")


def generate_agent_activities(conn, num_records=1000):
    """Generate AI agent activity records"""
    print(f"Generating {num_records} agent activity records...")
    cursor = conn.cursor()

    # Get existing vehicle and customer IDs
    cursor.execute("SELECT id FROM vehicles")
    vehicle_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]

    agent_types = [
        "data_analysis",
        "diagnosis",
        "customer_engagement",
        "scheduling",
        "feedback",
        "manufacturing_insights",
        "ueba_monitoring",
    ]

    action_types = [
        "data_processing",
        "analysis_request",
        "diagnosis_run",
        "customer_interaction",
        "appointment_scheduling",
        "feedback_analysis",
        "anomaly_detection",
        "report_generation",
    ]

    anomaly_types = ["data_anomaly", "performance_anomaly", "security_anomaly", "behavioral_anomaly"]

    agent_activities = []

    for i in range(num_records):
        agent_type = random.choice(agent_types)
        agent_id = f"{agent_type}_agent_{random.randint(1, 5)}"
        action_type = random.choice(action_types)

        # Generate timestamp (past 30 days)
        base_date = datetime.now()
        days_offset = random.randint(-30, 0)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        timestamp = base_date + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)

        vehicle_id = random.choice(vehicle_ids) if vehicle_ids and random.choice([True, False]) else None
        customer_id = random.choice(customer_ids) if customer_ids and random.choice([True, False]) else None

        success = random.choices([True, False], weights=[0.9, 0.1])[0]
        processing_time = round(random.uniform(0.1, 5.0), 3)
        payload_size = random.randint(100, 10000)

        # Anomaly detection (5% chance)
        anomaly_detected = random.choices([True, False], weights=[0.05, 0.95])[0]
        anomaly_type = random.choice(anomaly_types) if anomaly_detected else None
        risk_score = round(random.uniform(0.7, 1.0), 2) if anomaly_detected else round(random.uniform(0.0, 0.3), 2)

        error_message = fake.sentence() if not success else None
        response_data = json.dumps({"status": "success" if success else "error", "data_points": random.randint(1, 100)})

        agent_activities.append(
            (
                str(uuid.uuid4()),  # id
                agent_id,
                agent_type,
                action_type,
                f"resource_{random.randint(1000, 9999)}",  # target_resource
                payload_size,
                processing_time,
                vehicle_id,
                customer_id,
                f"session_{random.randint(10000, 99999)}",  # session_id
                success,
                error_message,
                response_data,
                timestamp.isoformat(),
                timestamp.hour,  # hour_of_day
                timestamp.weekday(),  # day_of_week
                anomaly_detected,
                anomaly_type,
                risk_score,
            )
        )

    cursor.executemany(
        """
        INSERT INTO agent_activities
        (id, agent_id, agent_type, action_type, target_resource, payload_size,
         processing_time, vehicle_id, customer_id, session_id, success, error_message,
         response_data, timestamp, hour_of_day, day_of_week, anomaly_detected,
         anomaly_type, risk_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        agent_activities,
    )

    conn.commit()
    print(f"Successfully inserted {len(agent_activities)} agent activity records")


def generate_system_metrics(conn, num_records=500):
    """Generate system performance metrics"""
    print(f"Generating {num_records} system metrics...")
    cursor = conn.cursor()

    metric_names = [
        "cpu_usage_percent",
        "memory_usage_percent",
        "disk_usage_percent",
        "network_throughput_mbps",
        "response_time_ms",
        "error_rate_percent",
        "active_connections",
        "queue_length",
        "cache_hit_rate",
        "database_connections",
    ]

    metric_types = ["gauge", "counter", "histogram"]
    components = ["master_agent", "api_server", "database", "frontend", "agents", "monitoring"]
    units = ["%", "ms", "MB", "count", "rate", "connections"]

    system_metrics = []

    for i in range(num_records):
        metric_name = random.choice(metric_names)
        metric_type = random.choice(metric_types)
        component = random.choice(components)

        # Generate realistic values based on metric name
        if "percent" in metric_name or "rate" in metric_name:
            value = round(random.uniform(0, 100), 2)
            unit = "%"
        elif "time" in metric_name:
            value = round(random.uniform(10, 1000), 2)
            unit = "ms"
        elif "throughput" in metric_name:
            value = round(random.uniform(1, 100), 2)
            unit = "mbps"
        elif "connections" in metric_name or "length" in metric_name:
            value = random.randint(1, 1000)
            unit = "count"
        else:
            value = round(random.uniform(0, 100), 2)
            unit = random.choice(units)

        # Generate timestamp (past 7 days)
        base_date = datetime.now()
        days_offset = random.randint(-7, 0)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        timestamp = base_date + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)

        tags = json.dumps(
            {
                "environment": "production",
                "region": random.choice(["us-east - 1", "us-west - 2", "eu-west - 1"]),
                "instance_id": f"i-{random.randint(100000, 999999)}",
            }
        )

        system_metrics.append(
            (
                str(uuid.uuid4()),  # id
                metric_name,
                metric_type,
                value,
                unit,
                component,
                "production",  # environment
                tags,
                timestamp.isoformat(),
            )
        )

    cursor.executemany(
        """
        INSERT INTO system_metrics
        (id, metric_name, metric_type, value, unit, component, environment, tags, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        system_metrics,
    )

    conn.commit()
    print(f"Successfully inserted {len(system_metrics)} system metrics")


def generate_agent_baselines(conn):
    """Generate AI agent baseline configurations"""
    print("Generating agent baselines...")

    agent_types = [
        "DiagnosticAgent",
        "MaintenanceAgent",
        "PredictiveAgent",
        "CustomerServiceAgent",
        "InventoryAgent",
        "SchedulingAgent",
        "QualityAgent",
        "SafetyAgent",
        "PerformanceAgent",
    ]

    baselines = []

    for i, agent_type in enumerate(agent_types):
        agent_id = f"{agent_type.lower()}_{i + 1}"

        # Generate realistic behavioral patterns
        typical_actions_per_hour = random.uniform(10, 100)
        typical_resources = [
            "customer_database",
            "vehicle_database",
            "maintenance_records",
            "diagnostic_tools",
            "scheduling_system",
            "inventory_system",
        ]

        # Select random subset of resources for this agent
        agent_resources = random.sample(typical_resources, random.randint(2, 4))

        normal_workflow = ["authenticate", "query_data", "process_request", "update_records", "respond"]

        # Generate baseline period (last 30 days)
        baseline_end = datetime.now()
        baseline_start = baseline_end - timedelta(days=30)

        # Generate allowed resources and typical access hours
        allowed_resources = agent_resources + ["system_logs", "configuration"]
        typical_hours = list(range(8, 18))  # 8 AM to 6 PM

        baselines.append(
            (
                str(uuid.uuid4()),  # id
                agent_id,
                agent_type,
                typical_actions_per_hour,
                json.dumps(agent_resources),  # typical_resources_accessed
                json.dumps(normal_workflow),  # normal_workflow_sequence
                round(random.uniform(50, 500), 2),  # average_processing_time
                round(random.uniform(0.95, 0.99), 3),  # success_rate
                round(random.uniform(0.01, 0.05), 3),  # error_rate
                round(random.uniform(0.001, 0.01), 3),  # timeout_rate
                json.dumps(allowed_resources),  # allowed_resources
                json.dumps(typical_hours),  # typical_access_hours
                baseline_start.isoformat(),  # baseline_period_start
                baseline_end.isoformat(),  # baseline_period_end
                random.randint(1000, 5000),  # data_points_count
                round(random.uniform(0.8, 0.95), 2),  # confidence_score
                datetime.now().isoformat(),  # created_at
                datetime.now().isoformat(),  # updated_at
            )
        )

    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO agent_baselines
        (id, agent_id, agent_type, typical_actions_per_hour, typical_resources_accessed,
         normal_workflow_sequence, average_processing_time, success_rate, error_rate,
         timeout_rate, allowed_resources, typical_access_hours, baseline_period_start,
         baseline_period_end, data_points_count, confidence_score, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        baselines,
    )

    conn.commit()
    print(f"Successfully inserted {len(baselines)} agent baselines")


def main():
    """Main function to generate all automotive data"""
    print("Starting automotive data generation...")
    print("=" * 50)

    conn = connect_db()

    try:
        # Generate data in order of dependencies
        generate_telemetry_data(conn, 10000)
        generate_maintenance_records(conn, 500)
        generate_service_appointments(conn, 200)
        generate_feedback_records(conn, 300)
        generate_agent_activities(conn, 1000)
        generate_system_metrics(conn, 500)
        generate_agent_baselines(conn)

        print("=" * 50)
        print("Data generation completed successfully!")

        # Print summary
        cursor = conn.cursor()
        tables = [
            "telemetry_data",
            "maintenance_records",
            "service_appointments",
            "feedback_records",
            "agent_activities",
            "system_metrics",
            "agent_baselines",
        ]

        print("\nData Summary:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} records")

    except Exception as e:
        print(f"Error generating data: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
