#!/usr/bin/env python3
"""
Enhanced Demo Data Generator for AutoMind
Generates realistic demo data using Faker library
"""
import asyncio
import sys
import os
import random
from datetime import datetime, timedelta
import uuid
from typing import List

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from faker import Faker
    from faker.providers import automotive, internet, phone_number, address, company
except ImportError:
    print("Installing required packages...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "faker"])
    from faker import Faker
    from faker.providers import automotive, internet, phone_number, address, company

from database_manager import DatabaseManager
from database_models import (
    Vehicle,
    Customer,
    CustomerVehicle,
    TelemetryData,
    MaintenanceRecord,
)
from sqlalchemy import text


class EnhancedDemoDataGenerator:
    def __init__(self):
        self.fake = Faker()
        self.fake.add_provider(automotive)
        self.fake.add_provider(internet)
        self.fake.add_provider(phone_number)
        self.fake.add_provider(address)
        self.fake.add_provider(company)

        # Vehicle data pools
        self.makes_models = {
            "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Prius", "Sienna"],
            "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Odyssey", "Ridgeline"],
            "Ford": ["F - 150", "Escape", "Explorer", "Mustang", "Edge", "Expedition"],
            "Chevrolet": ["Silverado", "Equinox", "Malibu", "Tahoe", "Traverse", "Camaro"],
            "BMW": ["3 Series", "5 Series", "X3", "X5", "i4", "iX"],
            "Mercedes-Benz": ["C-Class", "E-Class", "GLC", "GLE", "EQS", "EQC"],
            "Tesla": ["Model 3", "Model Y", "Model S", "Model X", "Cybertruck"],
            "Audi": ["A4", "A6", "Q5", "Q7", "e-tron", "Q4 e-tron"],
            "Nissan": ["Altima", "Sentra", "Rogue", "Pathfinder", "Leaf", "Ariya"],
            "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Ioniq 5", "Palisade"],
        }

        self.engine_types = {
            "Toyota": ["Gasoline", "Hybrid", "Electric"],
            "Honda": ["Gasoline", "Hybrid"],
            "Ford": ["Gasoline", "Hybrid", "Electric", "Diesel"],
            "Chevrolet": ["Gasoline", "Electric", "Diesel"],
            "BMW": ["Gasoline", "Hybrid", "Electric", "Diesel"],
            "Mercedes-Benz": ["Gasoline", "Hybrid", "Electric", "Diesel"],
            "Tesla": ["Electric"],
            "Audi": ["Gasoline", "Hybrid", "Electric", "Diesel"],
            "Nissan": ["Gasoline", "Electric"],
            "Hyundai": ["Gasoline", "Hybrid", "Electric"],
        }

        self.transmission_types = ["Automatic", "Manual", "CVT", "Single-Speed", "8-Speed Auto", "9-Speed Auto"]

        # Service and maintenance data
        self.service_types = ["scheduled", "repair", "inspection", "recall", "warranty"]
        self.maintenance_components = [
            "Engine Oil",
            "Oil Filter",
            "Air Filter",
            "Brake Pads",
            "Brake Rotors",
            "Tires",
            "Battery",
            "Spark Plugs",
            "Transmission Fluid",
            "Coolant",
            "Brake Fluid",
            "Power Steering Fluid",
            "Windshield Wipers",
            "Belts",
            "Hoses",
            "Suspension Components",
            "Exhaust System",
            "Fuel Filter",
        ]

        self.error_codes = [
            "P0300",
            "P0301",
            "P0302",
            "P0303",
            "P0304",
            "P0171",
            "P0174",
            "P0420",
            "P0430",
            "P0442",
            "P0455",
            "P0506",
            "P0507",
            "P0128",
            "B1000",
            "B1001",
            "B1002",
            "U0100",
            "U0101",
            "U0102",
        ]

    def generate_vin(self) -> str:
        """Generate a realistic VIN number"""
        return self.fake.vin()

    def generate_license_plate(self) -> str:
        """Generate a realistic license plate"""
        return self.fake.license_plate()

    def generate_vehicles(self, count: int = 50) -> List[Vehicle]:
        """Generate realistic vehicle data"""
        vehicles = []

        for _ in range(count):
            make = random.choice(list(self.makes_models.keys()))
            model = random.choice(self.makes_models[make])
            year = random.randint(2018, 2024)

            # Determine engine type based on make and year
            available_engines = self.engine_types[make]
            if year >= 2022 and "Electric" in available_engines:
                if len(available_engines) == 3:
                    engine_type = random.choices(available_engines, weights=[0.4, 0.3, 0.3])[0]
                elif len(available_engines) == 2:
                    engine_type = random.choices(available_engines, weights=[0.6, 0.4])[0]
                else:
                    engine_type = random.choice(available_engines)
            else:
                non_electric = [e for e in available_engines if e != "Electric"]
                engine_type = random.choice(non_electric if non_electric else available_engines)

            # Transmission based on engine type
            if engine_type == "Electric":
                transmission = "Single-Speed"
            elif engine_type == "Hybrid":
                transmission = random.choice(["CVT", "Automatic"])
            else:
                transmission = random.choice(self.transmission_types[:-1])  # Exclude Single-Speed

            # Mileage based on year
            current_year = datetime.now().year
            age = current_year - year
            base_mileage = age * random.randint(8000, 15000)
            mileage = max(0, base_mileage + random.randint(-5000, 10000))

            # Create registration date
            reg_start = datetime(year, 1, 1)
            reg_end = datetime(year, 12, 31)

            vehicle = Vehicle(
                id=self.generate_vin(),
                make=make,
                model=model,
                year=year,
                engine_type=engine_type,
                transmission_type=transmission,
                mileage=mileage,
                registration_date=self.fake.date_between(start_date=reg_start, end_date=reg_end),
                last_service_date=(
                    self.fake.date_between(start_date=datetime.now() - timedelta(days=180), end_date=datetime.now())
                    if random.random() > 0.1
                    else None
                ),
                warranty_expiry=(
                    self.fake.date_between(start_date=datetime.now(), end_date=datetime.now() + timedelta(days=1095))
                    if year >= 2021
                    else None
                ),
                is_active=random.random() > 0.05,  # 95% active
            )
            vehicles.append(vehicle)

        return vehicles

    def generate_customers(self, count: int = 100) -> List[Customer]:
        """Generate realistic customer data"""
        customers = []
        contact_methods = ["app_notification", "email", "sms", "voice"]

        for _ in range(count):
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()

            customer = Customer(
                id=str(uuid.uuid4()),
                first_name=first_name,
                last_name=last_name,
                email=f"{first_name.lower()}.{last_name.lower()}@{self.fake.domain_name()}",
                phone=self.fake.phone_number(),
                preferred_contact_method=random.choice(contact_methods),
                address=self.fake.street_address(),
                city=self.fake.city(),
                state=self.fake.state_abbr(),
                zip_code=self.fake.zipcode(),
                notification_preferences={
                    "maintenance_reminders": random.choice([True, False]),
                    "service_updates": True,
                    "promotional_offers": random.choice([True, False]),
                    "emergency_alerts": True,
                },
                service_history_consent=random.random() > 0.1,  # 90% consent
                is_active=random.random() > 0.02,  # 98% active
            )
            customers.append(customer)

        return customers

    def generate_telemetry_data(self, vehicles: List[Vehicle], days_back: int = 30) -> List[TelemetryData]:
        """Generate realistic telemetry data for vehicles"""
        telemetry_data = []

        for vehicle in vehicles:
            # Generate data points for the last N days
            for day in range(days_back):
                # 1 - 5 data points per day per vehicle
                daily_points = random.randint(1, 5)

                for _ in range(daily_points):
                    timestamp = datetime.now() - timedelta(
                        days=day, hours=random.randint(0, 23), minutes=random.randint(0, 59)
                    )

                    # Base values with some variation
                    base_temp = 190 if vehicle.engine_type != "Electric" else 0
                    base_rpm = 800 if vehicle.engine_type != "Electric" else 0

                    # Simulate some issues for older vehicles or high mileage
                    issue_probability = min(0.1, (vehicle.mileage or 0) / 200000 + (2024 - vehicle.year) * 0.01)
                    has_issues = random.random() < issue_probability

                    error_codes = []
                    if has_issues:
                        error_codes = random.sample(self.error_codes, random.randint(1, 3))

                    telemetry = TelemetryData(
                        id=str(uuid.uuid4()),
                        vehicle_id=vehicle.id,
                        timestamp=timestamp,
                        engine_rpm=base_rpm + random.randint(-200, 1500) if base_rpm > 0 else 0,
                        engine_temperature=(
                            base_temp + random.randint(-20, 40) if base_temp > 0 else random.randint(60, 80)
                        ),
                        coolant_temp=base_temp - 10 + random.randint(-15, 25) if base_temp > 0 else 0,
                        oil_pressure=random.randint(20, 80) if vehicle.engine_type != "Electric" else 0,
                        oil_temperature=random.randint(180, 220) if vehicle.engine_type != "Electric" else 0,
                        battery_voltage=(
                            random.uniform(12.0, 14.5)
                            if vehicle.engine_type != "Electric"
                            else random.uniform(350, 400)
                        ),
                        alternator_output=random.uniform(13.5, 14.8) if vehicle.engine_type != "Electric" else 0,
                        brake_pad_thickness_fl=random.uniform(2.0, 12.0),
                        brake_pad_thickness_fr=random.uniform(2.0, 12.0),
                        brake_pad_thickness_rl=random.uniform(2.0, 12.0),
                        brake_pad_thickness_rr=random.uniform(2.0, 12.0),
                        brake_fluid_level=random.uniform(0.3, 1.0),
                        tire_pressure_fl=random.uniform(28, 35),
                        tire_pressure_fr=random.uniform(28, 35),
                        tire_pressure_rl=random.uniform(28, 35),
                        tire_pressure_rr=random.uniform(28, 35),
                        tire_temperature_fl=random.uniform(60, 120),
                        tire_temperature_fr=random.uniform(60, 120),
                        tire_temperature_rl=random.uniform(60, 120),
                        tire_temperature_rr=random.uniform(60, 120),
                        transmission_fluid_level=(
                            random.uniform(0.4, 1.0) if vehicle.transmission_type != "Single-Speed" else 1.0
                        ),
                        transmission_temperature=(
                            random.randint(160, 200) if vehicle.transmission_type != "Single-Speed" else 0
                        ),
                        gear_position=(
                            random.choice(["P", "R", "N", "D", "1", "2", "3"])
                            if vehicle.transmission_type != "Single-Speed"
                            else "D"
                        ),
                        mileage=(vehicle.mileage or 0) + random.randint(0, 50),
                        fuel_level=random.uniform(0.1, 1.0) if vehicle.engine_type != "Electric" else 1.0,
                        speed=random.randint(0, 80),
                        location_lat=self.fake.latitude(),
                        location_lng=self.fake.longitude(),
                        error_codes=error_codes,
                        diagnostic_data={
                            "sensor_health": random.uniform(0.8, 1.0),
                            "communication_status": "OK" if random.random() > 0.05 else "DEGRADED",
                        },
                        data_quality_score=random.uniform(0.85, 1.0),
                        sensor_status={
                            "engine_sensors": "OK" if random.random() > 0.02 else "WARNING",
                            "brake_sensors": "OK" if random.random() > 0.01 else "WARNING",
                            "tire_sensors": "OK" if random.random() > 0.03 else "WARNING",
                        },
                    )
                    telemetry_data.append(telemetry)

        return telemetry_data

    def generate_maintenance_records(self, vehicles: List[Vehicle]) -> List[MaintenanceRecord]:
        """Generate realistic maintenance records"""
        maintenance_records = []

        for vehicle in vehicles:
            # Generate 1 - 5 maintenance records per vehicle
            num_records = random.randint(1, 5)

            for i in range(num_records):
                service_date = self.fake.date_between(
                    start_date=datetime.now() - timedelta(days=730), end_date=datetime.now()
                )

                service_type = random.choice(self.service_types)
                components = random.sample(self.maintenance_components, random.randint(1, 4))

                record = MaintenanceRecord(
                    id=str(uuid.uuid4()),
                    vehicle_id=vehicle.id,
                    service_date=service_date,
                    service_type=service_type,
                    components_serviced=components,
                    parts_replaced=[f"{comp} - Part #{self.fake.random_number(digits=8)}" for comp in components[:2]],
                    labor_hours=random.uniform(0.5, 8.0),
                    total_cost=random.uniform(50, 2000),
                    service_provider=self.fake.company(),
                    technician_id=f"TECH{random.randint(1000, 9999)}",
                    service_location=f"{self.fake.city()} Service Center",
                    mileage_at_service=(vehicle.mileage or 0) - random.randint(0, 10000),
                    next_service_due_mileage=(vehicle.mileage or 0) + random.randint(3000, 10000),
                    next_service_due_date=service_date + timedelta(days=random.randint(90, 365)),
                    service_quality_rating=random.uniform(7.0, 10.0),
                    warranty_work=random.random() < 0.2,  # 20% warranty work
                    recall_related=random.random() < 0.05,  # 5% recall related
                    service_notes=self.fake.text(max_nb_chars=200),
                    before_photos=[f"https://example.com/photos/before_{uuid.uuid4()}.jpg"],
                    after_photos=[f"https://example.com/photos/after_{uuid.uuid4()}.jpg"],
                )
                maintenance_records.append(record)

        return maintenance_records


async def main():
    """Main function to populate database with enhanced demo data"""
    print("🚀 Starting Enhanced Demo Data Generation...")

    generator = EnhancedDemoDataGenerator()
    dm = DatabaseManager()
    await dm.initialize()

    try:
        with dm.get_session() as session:
            # Check if data already exists
            vehicle_count = session.execute(text("SELECT COUNT(*) FROM vehicles")).fetchone()[0]
            if vehicle_count > 10:
                print(f"✓ Database already has {vehicle_count} vehicles. Skipping generation.")
                return

            print("📊 Generating vehicles...")
            vehicles = generator.generate_vehicles(50)

            print("👥 Generating customers...")
            customers = generator.generate_customers(100)

            print("💾 Saving vehicles and customers...")
            for vehicle in vehicles:
                session.add(vehicle)
            for customer in customers:
                session.add(customer)
            session.commit()

            print("🔗 Creating customer-vehicle relationships...")
            # Assign vehicles to customers (some customers may have multiple vehicles)
            for i, vehicle in enumerate(vehicles):
                customer = customers[i % len(customers)]
                relationship = CustomerVehicle(
                    id=str(uuid.uuid4()),
                    customer_id=customer.id,
                    vehicle_id=vehicle.id,
                    relationship_type=random.choice(["owner", "lessee"]),
                    is_primary=True,
                )
                session.add(relationship)
            session.commit()

            print("📡 Generating telemetry data...")
            telemetry_data = generator.generate_telemetry_data(vehicles, days_back=30)
            for telemetry in telemetry_data:
                session.add(telemetry)
            session.commit()

            print("🔧 Generating maintenance records...")
            maintenance_records = generator.generate_maintenance_records(vehicles)
            for record in maintenance_records:
                session.add(record)
            session.commit()

            print("✅ Demo data generation completed successfully!")
            print(f"   - {len(vehicles)} vehicles")
            print(f"   - {len(customers)} customers")
            print(f"   - {len(telemetry_data)} telemetry records")
            print(f"   - {len(maintenance_records)} maintenance records")

    except Exception as e:
        print(f"❌ Error generating demo data: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
