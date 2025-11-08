#!/usr/bin/env python3
"""
Populate database with demo data
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
import uuid

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from database_models import Vehicle, Customer, CustomerVehicle, TelemetryData
from sqlalchemy import text


async def populate_demo_data():
    """Populate database with demo data"""
    try:
        print("Populating database with demo data...")
        dm = DatabaseManager()
        await dm.initialize()

        with dm.get_session() as session:
            # Check if data already exists
            vehicle_count = session.execute(text("SELECT COUNT(*) FROM vehicles")).fetchone()[0]
            if vehicle_count > 0:
                print(f"✓ Database already has {vehicle_count} vehicles")
                return True

            # Create demo vehicles
            vehicles = [
                Vehicle(
                    id="VIN123456789",
                    make="Toyota",
                    model="Camry",
                    year=2022,
                    engine_type="Hybrid",
                    transmission_type="CVT",
                    mileage=15000,
                ),
                Vehicle(
                    id="VIN987654321",
                    make="Honda",
                    model="Accord",
                    year=2021,
                    engine_type="Gasoline",
                    transmission_type="Automatic",
                    mileage=25000,
                ),
                Vehicle(
                    id="VIN456789123",
                    make="Tesla",
                    model="Model 3",
                    year=2023,
                    engine_type="Electric",
                    transmission_type="Single-Speed",
                    mileage=8000,
                ),
            ]

            # Create demo customers
            customers = [
                Customer(
                    id=str(uuid.uuid4()),
                    first_name="John",
                    last_name="Doe",
                    email="john.doe@email.com",
                    phone="+1 - 555 - 0101",
                    preferred_contact_method="app_notification",
                ),
                Customer(
                    id=str(uuid.uuid4()),
                    first_name="Jane",
                    last_name="Smith",
                    email="jane.smith@email.com",
                    phone="+1 - 555 - 0102",
                    preferred_contact_method="email",
                ),
                Customer(
                    id=str(uuid.uuid4()),
                    first_name="Mike",
                    last_name="Johnson",
                    email="mike.johnson@email.com",
                    phone="+1 - 555 - 0103",
                    preferred_contact_method="sms",
                ),
            ]

            # Add vehicles and customers to session
            for vehicle in vehicles:
                session.add(vehicle)
            for customer in customers:
                session.add(customer)

            # Commit to get IDs
            session.commit()

            # Create customer-vehicle relationships
            relationships = [
                CustomerVehicle(
                    id=str(uuid.uuid4()),
                    customer_id=customers[0].id,
                    vehicle_id=vehicles[0].id,
                    relationship_type="owner",
                    is_primary=True,
                ),
                CustomerVehicle(
                    id=str(uuid.uuid4()),
                    customer_id=customers[1].id,
                    vehicle_id=vehicles[1].id,
                    relationship_type="owner",
                    is_primary=True,
                ),
                CustomerVehicle(
                    id=str(uuid.uuid4()),
                    customer_id=customers[2].id,
                    vehicle_id=vehicles[2].id,
                    relationship_type="owner",
                    is_primary=True,
                ),
            ]

            for relationship in relationships:
                session.add(relationship)

            # Create some sample telemetry data
            base_time = datetime.now() - timedelta(days=7)
            for i, vehicle in enumerate(vehicles):
                for day in range(7):
                    for hour in range(0, 24, 4):  # Every 4 hours
                        timestamp = base_time + timedelta(days=day, hours=hour)
                        telemetry = TelemetryData(
                            id=str(uuid.uuid4()),
                            vehicle_id=vehicle.id,
                            timestamp=timestamp,
                            engine_rpm=800 + (i * 100) + (hour * 10),
                            engine_temperature=85 + (i * 5) + (hour * 2),
                            battery_voltage=12.5 + (i * 0.1),
                            fuel_level=50 + (i * 10) - (day * 5),
                            mileage=vehicle.mileage + (day * 50) + (hour * 2),
                        )
                        session.add(telemetry)

            session.commit()

            # Verify data was created
            vehicle_count = session.execute(text("SELECT COUNT(*) FROM vehicles")).fetchone()[0]
            customer_count = session.execute(text("SELECT COUNT(*) FROM customers")).fetchone()[0]
            telemetry_count = session.execute(text("SELECT COUNT(*) FROM telemetry_data")).fetchone()[0]

            print(f"✓ Created {vehicle_count} vehicles")
            print(f"✓ Created {customer_count} customers")
            print(f"✓ Created {telemetry_count} telemetry records")

        await dm.shutdown()
        print("✓ Demo data population completed")
        return True

    except Exception as e:
        print(f"✗ Demo data population failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(populate_demo_data())
    sys.exit(0 if success else 1)
