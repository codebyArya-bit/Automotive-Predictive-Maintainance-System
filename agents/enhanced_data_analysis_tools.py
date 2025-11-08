"""
Enhanced Data Analysis Tools for Automotive Predictive Maintenance
Implements comprehensive telemetry processing, validation, and ML feature engineering
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
import warnings

warnings.filterwarnings("ignore")

try:
    from langchain_core.tools import tool

    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback decorator for when LangChain is not available
    def tool(func):
        func.is_tool = True
        return func

    LANGCHAIN_AVAILABLE = False

try:
    from psycopg2.extras import RealDictCursor

    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class TelemetryRecord:
    """Enhanced structure for telemetry data records"""

    timestamp: datetime
    vehicle_id: str
    engine_rpm: float
    coolant_temp: float
    battery_voltage: float
    oil_pressure: float
    fuel_level: float
    throttle_position: float
    brake_pressure: float
    transmission_temp: float
    intake_air_temp: float
    exhaust_temp: float
    turbo_boost: Optional[float]
    lambda_sensor: Optional[float]
    brake_pad_thickness: float
    tire_pressure_fl: float
    tire_pressure_fr: float
    tire_pressure_rl: float
    tire_pressure_rr: float
    transmission_fluid_level: float
    mileage: int
    error_codes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


# Import the centralized database manager
from database_manager import db_manager


@tool
def fetch_telemetry(vehicle_id: str, days: int = 30) -> List[Dict]:
    """
    Fetch telemetry data for a vehicle from TimescaleDB.

    Args:
        vehicle_id: Vehicle identifier
        days: Number of days of historical data to fetch

    Returns:
        List of telemetry records with timestamp, sensor readings, and metadata
    """
    logger.info(f"Fetching telemetry data for vehicle {vehicle_id} for {days} days")

    # Use the centralized database manager
    telemetry_data = db_manager.get_telemetry_data(vehicle_id, days)

    if not telemetry_data:
        # Fallback to simulated data
        logger.info("Using simulated telemetry data")
        return _generate_simulated_telemetry(vehicle_id, days)

    logger.info(f"Fetched {len(telemetry_data)} telemetry records")
    return telemetry_data


@tool
def enhanced_fetch_telemetry(vehicle_id: str, days: int = 30, include_predictions: bool = True) -> Dict:
    """
    Enhanced telemetry fetching with predictive analytics using SQLAlchemy ORM.

    Args:
        vehicle_id: Vehicle identifier
        days: Number of days of historical data
        include_predictions: Whether to include predictive analytics

    Returns:
        Enhanced telemetry data with analytics and predictions
    """
    try:
        # Use the centralized database manager
        telemetry_data = db_manager.get_telemetry_data(vehicle_id, days)

        if not telemetry_data:
            logger.warning(f"No telemetry data found for vehicle {vehicle_id}, using simulated data")
            telemetry_data = _generate_simulated_telemetry(vehicle_id, days)

        # Perform analytics on the data
        validation = validate_telemetry(telemetry_data)
        features = compute_features(telemetry_data)
        analytics = {**validation, **features}

        result = {
            "vehicle_id": vehicle_id,
            "data_points": len(telemetry_data),
            "time_range_days": days,
            "telemetry_data": telemetry_data,
            "analytics": analytics,
        }

        if include_predictions:
            predictions = {"status": "predictions_available", "features": features}
            result["predictions"] = predictions

        logger.info(f"Enhanced telemetry analysis completed for vehicle {vehicle_id}")
        return result

    except Exception as e:
        logger.error(f"Enhanced telemetry fetch failed: {e}")
        # Fallback to simulated data
        return {
            "vehicle_id": vehicle_id,
            "data_points": 0,
            "time_range_days": days,
            "telemetry_data": _generate_simulated_telemetry(vehicle_id, days),
            "analytics": {"status": "simulated"},
            "predictions": {"status": "unavailable", "reason": str(e)} if include_predictions else None,
        }


def _generate_simulated_telemetry(vehicle_id: str, days: int) -> List[Dict]:
    """Generate realistic simulated telemetry data"""
    records = []
    base_time = datetime.now()

    # Generate data points every hour for the specified days
    for i in range(days * 24):
        timestamp = base_time - timedelta(hours=i)

        # Simulate realistic sensor readings with some variation
        record = TelemetryRecord(
            timestamp=timestamp,
            vehicle_id=vehicle_id,
            engine_rpm=np.random.normal(2500, 300),
            coolant_temp=np.random.normal(85, 5),
            battery_voltage=np.random.normal(12.6, 0.3),
            oil_pressure=np.random.normal(45, 5),
            fuel_level=max(0, np.random.normal(60, 20)),
            throttle_position=np.random.uniform(0, 100),
            brake_pressure=np.random.uniform(0, 50),
            transmission_temp=np.random.normal(70, 8),
            intake_air_temp=np.random.normal(25, 5),
            exhaust_temp=np.random.normal(400, 50),
            turbo_boost=np.random.normal(1.2, 0.2) if np.random.random() > 0.3 else None,
            lambda_sensor=np.random.normal(1.0, 0.05) if np.random.random() > 0.2 else None,
            brake_pad_thickness=max(0, np.random.normal(8, 1)),
            tire_pressure_fl=np.random.normal(32, 2),
            tire_pressure_fr=np.random.normal(32, 2),
            tire_pressure_rl=np.random.normal(32, 2),
            tire_pressure_rr=np.random.normal(32, 2),
            transmission_fluid_level=np.random.normal(75, 5),
            mileage=50000 + i * 10,
            error_codes=[] if np.random.random() > 0.05 else [f"P{np.random.randint(100, 999)}"],
        )

        records.append(record.to_dict())

    return records


@tool
def validate_telemetry(telemetry: List[Dict]) -> Dict:
    """
    Validate telemetry data quality with comprehensive checks.

    Args:
        telemetry: List of telemetry records

    Returns:
        Dictionary with validation results, data quality score, and cleaned data
    """
    logger.info(f"Validating {len(telemetry)} telemetry records")

    if not telemetry:
        return {
            "is_valid": False,
            "data_quality_score": 0.0,
            "issues": ["No telemetry data provided"],
            "cleaned_data": [],
            "statistics": {},
        }

    df = pd.DataFrame(telemetry)
    issues = []

    # Convert timestamp to datetime if it's a string
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Define sensor ranges for validation
    sensor_ranges = {
        "engine_rpm": (0, 8000),
        "coolant_temp": (-40, 150),
        "battery_voltage": (8, 16),
        "oil_pressure": (0, 100),
        "fuel_level": (0, 100),
        "throttle_position": (0, 100),
        "brake_pressure": (0, 100),
        "transmission_temp": (-40, 150),
        "intake_air_temp": (-40, 80),
        "exhaust_temp": (0, 1000),
        "brake_pad_thickness": (0, 20),
        "tire_pressure_fl": (15, 50),
        "tire_pressure_fr": (15, 50),
        "tire_pressure_rl": (15, 50),
        "tire_pressure_rr": (15, 50),
        "transmission_fluid_level": (0, 100),
        "mileage": (0, 1000000),
    }

    # Check for missing values
    missing_percentage = (df.isnull().sum() / len(df)) * 100
    for column, percentage in missing_percentage.items():
        if percentage > 5:  # More than 5% missing
            issues.append(f"High missing values in {column}: {percentage:.1f}%")

    # Check for out-of-range values
    for column, (min_val, max_val) in sensor_ranges.items():
        if column in df.columns:
            out_of_range = ((df[column] < min_val) | (df[column] > max_val)).sum()
            if out_of_range > 0:
                issues.append(f"Out-of-range values in {column}: {out_of_range} records")

    # Check for duplicate timestamps
    if "timestamp" in df.columns:
        duplicates = df["timestamp"].duplicated().sum()
        if duplicates > 0:
            issues.append(f"Duplicate timestamps: {duplicates} records")

    # Check for anomalies using statistical methods
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for column in numeric_columns:
        if column in sensor_ranges:
            # Use IQR method for anomaly detection
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            anomalies = ((df[column] < lower_bound) | (df[column] > upper_bound)).sum()
            if anomalies > len(df) * 0.1:  # More than 10% anomalies
                issues.append(f"High anomaly rate in {column}: {anomalies} records ({anomalies / len(df) * 100:.1f}%)")

    # Clean the data
    cleaned_df = df.copy()

    # Remove duplicates
    if "timestamp" in cleaned_df.columns:
        cleaned_df = cleaned_df.drop_duplicates(subset=["timestamp"])

    # Cap out-of-range values
    for column, (min_val, max_val) in sensor_ranges.items():
        if column in cleaned_df.columns:
            cleaned_df[column] = cleaned_df[column].clip(lower=min_val, upper=max_val)

    # Fill missing values with interpolation or median
    for column in numeric_columns:
        if cleaned_df[column].isnull().sum() > 0:
            if "timestamp" in cleaned_df.columns:
                # Convert timestamp to datetime index for time-based interpolation
                try:
                    cleaned_df["timestamp"] = pd.to_datetime(cleaned_df["timestamp"])
                    cleaned_df = cleaned_df.set_index("timestamp").sort_index()
                    cleaned_df[column] = cleaned_df[column].interpolate(method="time")
                    cleaned_df = cleaned_df.reset_index()
                except Exception as e:
                    logger.warning(f"Time interpolation failed for {column}: {e}, using median fill")
                    cleaned_df[column] = cleaned_df[column].fillna(cleaned_df[column].median())
            else:
                # Fill with median
                cleaned_df[column] = cleaned_df[column].fillna(cleaned_df[column].median())

    # Calculate data quality score
    total_issues = len(issues)
    missing_score = 1 - (missing_percentage.mean() / 100)
    range_score = 1 - (total_issues / max(len(telemetry), 1))
    data_quality_score = (missing_score + range_score) / 2

    # Generate statistics
    statistics = {
        "total_records": len(telemetry),
        "cleaned_records": len(cleaned_df),
        "missing_percentage": missing_percentage.to_dict(),
        "data_quality_score": data_quality_score,
        "time_span_hours": (
            (df["timestamp"].max() - df["timestamp"].min()).total_seconds() / 3600 if "timestamp" in df.columns else 0
        ),
    }

    # Convert cleaned data back to list of dictionaries
    cleaned_data = cleaned_df.to_dict("records")
    for record in cleaned_data:
        if "timestamp" in record and isinstance(record["timestamp"], pd.Timestamp):
            record["timestamp"] = record["timestamp"].isoformat()

    result = {
        "is_valid": data_quality_score >= 0.8 and len(issues) < 5,
        "data_quality_score": data_quality_score,
        "issues": issues,
        "cleaned_data": cleaned_data,
        "statistics": statistics,
    }

    logger.info(f"Data validation complete. Quality score: {data_quality_score:.2f}")
    return result


@tool
def compute_features(telemetry: List[Dict]) -> Dict:
    """
    Compute ML features from telemetry data including rolling statistics and engineered features.

    Args:
        telemetry: List of cleaned telemetry records

    Returns:
        Dictionary with computed features ready for ML models
    """
    logger.info(f"Computing features from {len(telemetry)} telemetry records")

    if not telemetry:
        return {"error": "No telemetry data provided"}

    df = pd.DataFrame(telemetry)

    # Convert timestamp to datetime and sort
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        df.set_index("timestamp", inplace=True)

    features = {}

    # Define key sensors for feature engineering
    key_sensors = [
        "engine_rpm",
        "coolant_temp",
        "battery_voltage",
        "oil_pressure",
        "fuel_level",
        "throttle_position",
        "brake_pressure",
        "transmission_temp",
        "intake_air_temp",
        "exhaust_temp",
        "brake_pad_thickness",
    ]

    # Rolling averages (7-day and 30-day equivalents in hours)
    for sensor in key_sensors:
        if sensor in df.columns:
            # 7-day average (168 hours)
            df[f"{sensor}_7d_avg"] = df[sensor].rolling(window="168H", min_periods=1).mean()
            features[f"{sensor}_7d_avg"] = df[f"{sensor}_7d_avg"].iloc[-1] if not df[f"{sensor}_7d_avg"].empty else 0

            # 30-day average (720 hours)
            df[f"{sensor}_30d_avg"] = df[sensor].rolling(window="720H", min_periods=1).mean()
            features[f"{sensor}_30d_avg"] = df[f"{sensor}_30d_avg"].iloc[-1] if not df[f"{sensor}_30d_avg"].empty else 0

            # Rate of change (trend)
            df[f"{sensor}_trend"] = df[sensor].diff().rolling(window="24H", min_periods=1).mean()
            features[f"{sensor}_trend"] = df[f"{sensor}_trend"].iloc[-1] if not df[f"{sensor}_trend"].empty else 0

            # Volatility (standard deviation)
            df[f"{sensor}_volatility"] = df[sensor].rolling(window="168H", min_periods=1).std()
            features[f"{sensor}_volatility"] = (
                df[f"{sensor}_volatility"].iloc[-1] if not df[f"{sensor}_volatility"].empty else 0
            )

    # Interaction features
    if "engine_rpm" in df.columns and "oil_pressure" in df.columns:
        df["high_rpm_low_oil"] = (
            (df["engine_rpm"] > df["engine_rpm"].quantile(0.8))
            & (df["oil_pressure"] < df["oil_pressure"].quantile(0.2))
        ).astype(int)
        features["high_rpm_low_oil_frequency"] = (
            df["high_rpm_low_oil"].rolling(window="168H").sum().iloc[-1] if not df.empty else 0
        )

    if "coolant_temp" in df.columns and "engine_rpm" in df.columns:
        df["overheating_risk"] = ((df["coolant_temp"] > 95) & (df["engine_rpm"] > 3000)).astype(int)
        features["overheating_risk_frequency"] = (
            df["overheating_risk"].rolling(window="168H").sum().iloc[-1] if not df.empty else 0
        )

    if "battery_voltage" in df.columns:
        features["battery_health_score"] = (
            min(1.0, max(0.0, (df["battery_voltage"].iloc[-1] - 11.5) / (13.0 - 11.5))) if not df.empty else 0
        )

    # Tire pressure features
    tire_columns = ["tire_pressure_fl", "tire_pressure_fr", "tire_pressure_rl", "tire_pressure_rr"]
    available_tires = [col for col in tire_columns if col in df.columns]
    if available_tires:
        df["tire_pressure_avg"] = df[available_tires].mean(axis=1)
        df["tire_pressure_imbalance"] = df[available_tires].std(axis=1)
        features["tire_pressure_avg"] = df["tire_pressure_avg"].iloc[-1] if not df.empty else 0
        features["tire_pressure_imbalance"] = df["tire_pressure_imbalance"].iloc[-1] if not df.empty else 0

    # Mileage-based features
    if "mileage" in df.columns and len(df) > 1:
        features["mileage_rate"] = (df["mileage"].iloc[-1] - df["mileage"].iloc[0]) / max(1, len(df))
        features["current_mileage"] = df["mileage"].iloc[-1] if not df.empty else 0

    # Error code frequency
    if "error_codes" in df.columns:
        error_count = sum(len(codes) if isinstance(codes, list) else 0 for codes in df["error_codes"])
        features["error_code_frequency"] = error_count / len(df) if len(df) > 0 else 0

    # Recent vs historical comparison
    if len(df) > 24:  # At least 24 hours of data
        recent_data = df.tail(24)  # Last 24 hours
        historical_data = df.head(-24)  # All but last 24 hours

        for sensor in key_sensors:
            if sensor in df.columns:
                recent_avg = recent_data[sensor].mean()
                historical_avg = historical_data[sensor].mean()
                if historical_avg != 0:
                    features[f"{sensor}_recent_vs_historical"] = (recent_avg - historical_avg) / historical_avg
                else:
                    features[f"{sensor}_recent_vs_historical"] = 0

    # Feature summary statistics
    features["feature_count"] = len([k for k in features.keys() if not k.startswith("_")])
    features["data_span_hours"] = (df.index.max() - df.index.min()).total_seconds() / 3600 if len(df) > 1 else 0
    features["data_points"] = len(df)

    logger.info(f"Computed {len(features)} features")
    return features


@tool
def fetch_maintenance_history(vehicle_id: str) -> List[Dict]:
    """
    Fetch past maintenance records for context.

    Args:
        vehicle_id: Vehicle identifier

    Returns:
        List of maintenance events with dates, types, and details
    """
    logger.info(f"Fetching maintenance history for vehicle {vehicle_id}")

    conn = db_manager.get_connection()

    if conn is None:
        # Fallback to simulated data
        logger.info("Using simulated maintenance history")
        return _generate_simulated_maintenance_history(vehicle_id)

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
            SELECT
                maintenance_date,
                maintenance_type,
                description,
                cost,
                mileage_at_service,
                parts_replaced,
                technician_notes
            FROM maintenance_history
            WHERE vehicle_id = %s
            ORDER BY maintenance_date DESC
            LIMIT 50
            """

            cursor.execute(query, (vehicle_id,))
            records = cursor.fetchall()

            # Convert to list of dictionaries
            maintenance_data = []
            for record in records:
                data = dict(record)
                data["maintenance_date"] = data["maintenance_date"].isoformat()
                maintenance_data.append(data)

            logger.info(f"Fetched {len(maintenance_data)} maintenance records")
            return maintenance_data

    except Exception as e:
        logger.error(f"Error fetching maintenance history: {e}")
        # Fallback to simulated data
        return _generate_simulated_maintenance_history(vehicle_id)


def _generate_simulated_maintenance_history(vehicle_id: str) -> List[Dict]:
    """Generate realistic simulated maintenance history"""
    maintenance_types = [
        "Oil Change",
        "Brake Inspection",
        "Tire Rotation",
        "Battery Check",
        "Transmission Service",
        "Coolant Flush",
        "Air Filter Replacement",
        "Spark Plug Replacement",
        "Brake Pad Replacement",
        "Belt Replacement",
    ]

    records = []
    base_date = datetime.now()
    base_mileage = 50000

    # Generate 10 - 15 maintenance records over the past 2 years
    for i in range(np.random.randint(10, 16)):
        days_ago = np.random.randint(30, 730)  # 30 days to 2 years ago
        maintenance_date = base_date - timedelta(days=days_ago)

        maintenance_type = np.random.choice(maintenance_types)

        record = {
            "maintenance_date": maintenance_date.isoformat(),
            "maintenance_type": maintenance_type,
            "description": f"Routine {maintenance_type.lower()} service",
            "cost": np.random.uniform(50, 500),
            "mileage_at_service": base_mileage - (days_ago * 50),
            "parts_replaced": [maintenance_type.split()[0]] if np.random.random() > 0.5 else [],
            "technician_notes": f"Completed {maintenance_type.lower()} - vehicle in good condition",
        }

        records.append(record)

    return sorted(records, key=lambda x: x["maintenance_date"], reverse=True)


# Export all tools for easy import
__all__ = ["fetch_telemetry", "validate_telemetry", "compute_features", "fetch_maintenance_history"]
