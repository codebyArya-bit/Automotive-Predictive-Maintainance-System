"""
Data Analysis Tools for Automotive Predictive Maintenance
Provides tools for telemetry processing, validation, and feature engineering
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
import logging
from langchain.tools import tool
from psycopg2.extras import RealDictCursor
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class TelemetryRecord:
    """Structure for telemetry data records"""

    timestamp: datetime
    vehicle_id: str
    engine_rpm: float
    coolant_temp: float
    battery_voltage: float
    oil_pressure: float
    brake_pad_thickness: float
    tire_pressure_fl: float
    tire_pressure_fr: float
    tire_pressure_rl: float
    tire_pressure_rr: float
    transmission_fluid_level: float
    mileage: int
    error_codes: List[str]


# Import the centralized database manager
from database_manager import db_manager


@tool
def fetch_telemetry(vehicle_id: str, days: int = 30) -> List[Dict]:
    """
    Fetch telemetry data for a vehicle from TimescaleDB using SQLAlchemy ORM.

    Args:
        vehicle_id: Vehicle identifier
        days: Number of days of historical data to fetch

    Returns:
        List of telemetry records with timestamp, sensor readings, etc.
    """
    try:
        # Use the centralized database manager with ORM
        telemetry_data = db_manager.get_telemetry_data(vehicle_id, days)

        if not telemetry_data:
            logger.warning(f"No telemetry data found for vehicle {vehicle_id}, returning simulated data")
            return _generate_simulated_telemetry(vehicle_id, days)

        logger.info(f"Fetched {len(telemetry_data)} telemetry records for vehicle {vehicle_id}")
        return telemetry_data

    except Exception as e:
        logger.error(f"Failed to fetch telemetry data: {e}")
        # Fallback to simulated data
        logger.warning("Falling back to simulated telemetry data")
        return _generate_simulated_telemetry(vehicle_id, days)


def _generate_simulated_telemetry(vehicle_id: str, days: int) -> List[Dict]:
    """Generate simulated telemetry data for demo purposes"""
    import random

    telemetry_data = []
    end_date = datetime.now()

    # Generate hourly data points
    for i in range(days * 24):
        timestamp = end_date - timedelta(hours=i)

        # Base values with some realistic variation
        record = {
            "timestamp": timestamp.isoformat(),
            "vehicle_id": vehicle_id,
            "engine_rpm": 2000 + random.normalvariate(0, 300),
            "coolant_temp": 90 + random.normalvariate(0, 5),
            "battery_voltage": 13.2 + random.normalvariate(0, 0.3),
            "oil_pressure": 45 + random.normalvariate(0, 5),
            "brake_pad_thickness": 8.0 + random.normalvariate(0, 0.5),
            "tire_pressure_fl": 32.0 + random.normalvariate(0, 1),
            "tire_pressure_fr": 32.0 + random.normalvariate(0, 1),
            "tire_pressure_rl": 30.0 + random.normalvariate(0, 1),
            "tire_pressure_rr": 30.0 + random.normalvariate(0, 1),
            "transmission_fluid_level": 0.85 + random.normalvariate(0, 0.05),
            "mileage": 50000 + i,  # Incremental mileage
            "error_codes": [],
        }

        # Occasionally add error codes
        if random.random() < 0.05:  # 5% chance
            error_codes = ["P0300", "P0420", "P0171", "B1234", "C1201"]
            record["error_codes"] = [random.choice(error_codes)]

        telemetry_data.append(record)

    return telemetry_data


@tool
def validate_telemetry(telemetry: List[Dict]) -> Dict:
    """
    Validate telemetry data quality.

    Args:
        telemetry: List of telemetry records

    Returns:
        Dictionary with validation results: {is_valid: bool, issues: List[str], cleaned_data: List[Dict]}
    """
    if not telemetry:
        return {
            "is_valid": False,
            "issues": ["No telemetry data provided"],
            "cleaned_data": [],
            "data_quality_score": 0.0,
        }

    issues = []
    cleaned_data = []
    total_records = len(telemetry)
    valid_records = 0

    # Define valid ranges for sensors
    sensor_ranges = {
        "engine_rpm": (0, 8000),
        "coolant_temp": (-40, 150),
        "battery_voltage": (10.0, 16.0),
        "oil_pressure": (0, 100),
        "brake_pad_thickness": (0, 15),
        "tire_pressure_fl": (15, 50),
        "tire_pressure_fr": (15, 50),
        "tire_pressure_rl": (15, 50),
        "tire_pressure_rr": (15, 50),
        "transmission_fluid_level": (0.0, 1.0),
        "mileage": (0, 1000000),
    }

    required_fields = ["timestamp", "vehicle_id", "engine_rpm", "coolant_temp", "battery_voltage"]

    for i, record in enumerate(telemetry):
        record_issues = []

        # Check for missing required fields
        for field in required_fields:
            if field not in record or record[field] is None:
                record_issues.append(f"Missing required field: {field}")

        # Check sensor value ranges
        for sensor, (min_val, max_val) in sensor_ranges.items():
            if sensor in record and record[sensor] is not None:
                try:
                    value = float(record[sensor])
                    if not (min_val <= value <= max_val):
                        record_issues.append(f"{sensor} out of range: {value} (expected {min_val}-{max_val})")
                        # Clean the data by clamping to valid range
                        record[sensor] = max(min_val, min(max_val, value))
                except (ValueError, TypeError):
                    record_issues.append(f"Invalid {sensor} value: {record[sensor]}")
                    # Set to None for invalid values
                    record[sensor] = None

        # Validate timestamp
        if "timestamp" in record:
            try:
                if isinstance(record["timestamp"], str):
                    datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
            except ValueError:
                record_issues.append(f"Invalid timestamp format: {record['timestamp']}")

        if len(record_issues) == 0:
            valid_records += 1
            cleaned_data.append(record)
        elif len(record_issues) <= 2:  # Minor issues, include with fixes
            cleaned_data.append(record)
            issues.extend([f"Record {i}: {issue}" for issue in record_issues])
        else:  # Too many issues, exclude record
            issues.extend([f"Record {i} excluded: {issue}" for issue in record_issues])

    # Calculate data quality metrics
    data_quality_score = valid_records / total_records if total_records > 0 else 0.0
    missing_percentage = (total_records - len(cleaned_data)) / total_records * 100 if total_records > 0 else 0

    # Determine if data is valid (>80% good records, <20% missing)
    is_valid = data_quality_score >= 0.8 and missing_percentage < 20

    if missing_percentage > 20:
        issues.append(f"High missing data percentage: {missing_percentage:.1f}%")

    logger.info(f"Telemetry validation completed: {len(cleaned_data)}/{total_records} records valid")

    return {
        "is_valid": is_valid,
        "issues": issues,
        "cleaned_data": cleaned_data,
        "data_quality_score": data_quality_score,
        "missing_percentage": missing_percentage,
        "total_records": total_records,
        "valid_records": len(cleaned_data),
    }


@tool
def compute_features(telemetry: List[Dict]) -> Dict:
    """
    Compute ML features from telemetry data.

    Args:
        telemetry: List of cleaned telemetry records

    Returns:
        Dictionary of computed features for ML model
    """
    if not telemetry:
        return {"error": "No telemetry data provided for feature computation"}

    try:
        # Convert to pandas DataFrame for easier manipulation
        df = pd.DataFrame(telemetry)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")

        # Ensure numeric columns
        numeric_columns = [
            "engine_rpm",
            "coolant_temp",
            "battery_voltage",
            "oil_pressure",
            "brake_pad_thickness",
            "tire_pressure_fl",
            "tire_pressure_fr",
            "tire_pressure_rl",
            "tire_pressure_rr",
            "transmission_fluid_level",
            "mileage",
        ]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        features = {}

        # Rolling averages (7-day and 30-day)
        for col in numeric_columns:
            if col in df.columns and not df[col].isna().all():
                # 7-day rolling average (168 hours)
                df[f"{col}_7d_avg"] = df[col].rolling(window=min(168, len(df)), min_periods=1).mean()
                features[f"{col}_7d_avg"] = (
                    float(df[f"{col}_7d_avg"].iloc[-1]) if not df[f"{col}_7d_avg"].isna().iloc[-1] else None
                )

                # 30-day rolling average (720 hours)
                df[f"{col}_30d_avg"] = df[col].rolling(window=min(720, len(df)), min_periods=1).mean()
                features[f"{col}_30d_avg"] = (
                    float(df[f"{col}_30d_avg"].iloc[-1]) if not df[f"{col}_30d_avg"].isna().iloc[-1] else None
                )

                # Rate of change (trend)
                if len(df) > 1:
                    recent_values = df[col].tail(min(24, len(df)))  # Last 24 hours
                    if len(recent_values) > 1 and not recent_values.isna().all():
                        trend = np.polyfit(range(len(recent_values)), recent_values.fillna(method="ffill"), 1)[0]
                        features[f"{col}_trend"] = float(trend)

                # Standard deviation (volatility)
                recent_std = df[col].tail(min(168, len(df))).std()
                features[f"{col}_volatility"] = float(recent_std) if not pd.isna(recent_std) else None

        # Interaction features
        if all(col in df.columns for col in ["engine_rpm", "oil_pressure"]):
            # High RPM + Low oil pressure risk
            high_rpm_low_oil = (
                (df["engine_rpm"] > df["engine_rpm"].quantile(0.8))
                & (df["oil_pressure"] < df["oil_pressure"].quantile(0.2))
            ).sum()
            features["high_rpm_low_oil_events"] = int(high_rpm_low_oil)

        if all(col in df.columns for col in ["coolant_temp", "engine_rpm"]):
            # Temperature vs RPM correlation
            temp_rpm_corr = df["coolant_temp"].corr(df["engine_rpm"])
            features["temp_rpm_correlation"] = float(temp_rpm_corr) if not pd.isna(temp_rpm_corr) else None

        # Tire pressure imbalance
        tire_cols = ["tire_pressure_fl", "tire_pressure_fr", "tire_pressure_rl", "tire_pressure_rr"]
        if all(col in df.columns for col in tire_cols):
            tire_pressures = df[tire_cols].iloc[-1]
            tire_pressure_std = tire_pressures.std()
            features["tire_pressure_imbalance"] = float(tire_pressure_std) if not pd.isna(tire_pressure_std) else None

        # Battery health indicators
        if "battery_voltage" in df.columns:
            battery_data = df["battery_voltage"].dropna()
            if len(battery_data) > 0:
                features["battery_voltage_min_7d"] = float(battery_data.tail(min(168, len(battery_data))).min())
                features["battery_voltage_max_7d"] = float(battery_data.tail(min(168, len(battery_data))).max())
                features["battery_voltage_range_7d"] = (
                    features["battery_voltage_max_7d"] - features["battery_voltage_min_7d"]
                )

        # Error code frequency
        if "error_codes" in df.columns:
            error_count = sum(len(codes) if isinstance(codes, list) else 0 for codes in df["error_codes"])
            features["error_code_frequency"] = error_count / len(df) if len(df) > 0 else 0

        # Mileage-based features
        if "mileage" in df.columns and len(df) > 1:
            mileage_data = df["mileage"].dropna()
            if len(mileage_data) > 1:
                daily_mileage = mileage_data.diff().dropna()
                features["avg_daily_mileage"] = float(daily_mileage.mean()) if len(daily_mileage) > 0 else None
                features["max_daily_mileage"] = float(daily_mileage.max()) if len(daily_mileage) > 0 else None

        # Add metadata
        features["feature_computation_timestamp"] = datetime.now().isoformat()
        features["data_points_used"] = len(df)
        features["data_time_span_hours"] = (df["timestamp"].max() - df["timestamp"].min()).total_seconds() / 3600

        logger.info(f"Computed {len(features)} features from {len(df)} telemetry records")
        return features

    except Exception as e:
        logger.error(f"Error computing features: {e}")
        return {"error": f"Feature computation failed: {str(e)}"}


@tool
def fetch_maintenance_history(vehicle_id: str) -> List[Dict]:
    """
    Fetch past maintenance records for a vehicle.

    Args:
        vehicle_id: Vehicle identifier

    Returns:
        List of maintenance events with dates, types, and details
    """
    try:
        conn = db_manager.get_connection()

        # If no database connection, return simulated data for demo
        if conn is None:
            logger.warning("No database connection, returning simulated maintenance data")
            return _generate_simulated_maintenance(vehicle_id)

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
            SELECT
                maintenance_date,
                maintenance_type,
                description,
                cost,
                mileage_at_service,
                parts_replaced,
                technician_notes,
                next_service_due
            FROM maintenance_history
            WHERE vehicle_id = %s
            ORDER BY maintenance_date DESC
            LIMIT 50
            """

            cursor.execute(query, (vehicle_id,))
            results = cursor.fetchall()

            # Convert to list of dictionaries
            maintenance_data = []
            for row in results:
                record = dict(row)
                if record["maintenance_date"]:
                    record["maintenance_date"] = record["maintenance_date"].isoformat()
                if record["next_service_due"]:
                    record["next_service_due"] = record["next_service_due"].isoformat()
                maintenance_data.append(record)

            logger.info(f"Fetched {len(maintenance_data)} maintenance records for vehicle {vehicle_id}")
            return maintenance_data

    except Exception as e:
        logger.error(f"Error fetching maintenance history: {e}")
        # Return simulated data as fallback
        return _generate_simulated_maintenance(vehicle_id)

    finally:
        if conn:
            conn.close()


def _generate_simulated_maintenance(vehicle_id: str) -> List[Dict]:
    """Generate simulated maintenance history for demo purposes"""
    import random

    maintenance_types = [
        "Oil Change",
        "Brake Inspection",
        "Tire Rotation",
        "Battery Check",
        "Transmission Service",
        "Coolant Flush",
        "Air Filter Replacement",
        "Brake Pad Replacement",
        "Tire Replacement",
        "Engine Tune-up",
    ]

    maintenance_history = []
    current_date = datetime.now()

    # Generate 5 - 15 maintenance records over the past 2 years
    num_records = random.randint(5, 15)
    for i in range(num_records):
        days_ago = random.randint(30, 730)  # 30 days to 2 years ago
        maintenance_date = current_date - timedelta(days=days_ago)

        maintenance_type = random.choice(maintenance_types)

        record = {
            "maintenance_date": maintenance_date.isoformat(),
            "maintenance_type": maintenance_type,
            "description": f"Routine {maintenance_type.lower()} service",
            "cost": round(random.uniform(50, 500), 2),
            "mileage_at_service": 50000 - (days_ago * random.randint(20, 50)),
            "parts_replaced": [],
            "technician_notes": f"Completed {maintenance_type.lower()} without issues",
            "next_service_due": (maintenance_date + timedelta(days=random.randint(90, 180))).isoformat(),
        }

        # Add parts for certain maintenance types
        if "replacement" in maintenance_type.lower():
            if "brake" in maintenance_type.lower():
                record["parts_replaced"] = ["brake pads", "brake fluid"]
            elif "tire" in maintenance_type.lower():
                record["parts_replaced"] = ["tires"]
            elif "filter" in maintenance_type.lower():
                record["parts_replaced"] = ["air filter"]

        maintenance_history.append(record)

    # Sort by date (most recent first)
    maintenance_history.sort(key=lambda x: x["maintenance_date"], reverse=True)

    return maintenance_history
