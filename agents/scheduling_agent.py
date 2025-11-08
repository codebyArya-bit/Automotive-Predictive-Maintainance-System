"""
Enhanced Scheduling Agent - Autonomous appointment booking with geographic search and optimization
"""

import random
import math
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from .base_agent import BaseAgent
from state import State, AppointmentDetails

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ServiceCenter:
    """Service center data structure"""

    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    phone: str
    rating: float
    specialties: List[str]
    hours: Dict[str, int]
    available_slots_count: int
    distance_km: Optional[float] = None


@dataclass
class TimeSlot:
    """Available time slot data structure"""

    time_slot: str
    bay_number: int
    estimated_duration: float
    wait_time: int
    technician_id: str
    technician_name: str


@dataclass
class PartsAvailability:
    """Parts availability data structure"""

    in_stock: bool
    quantity: int
    estimated_arrival: Optional[str] = None


@dataclass
class OptimalSlot:
    """Optimal appointment slot recommendation"""

    center_id: str
    center_name: str
    date: str
    time: str
    score: float
    distance_km: float
    parts_available: bool
    estimated_duration: float


@dataclass
class BookingConfirmation:
    """Booking confirmation details"""

    booking_id: str
    confirmation_code: str
    customer_id: str
    vehicle_id: str
    center_id: str
    center_name: str
    center_address: str
    date: str
    time: str
    predicted_issue: str
    estimated_duration: float
    bay_number: int
    technician_name: str


class SchedulingAgent(BaseAgent):
    """
    Enhanced Scheduling Agent for autonomous service appointment booking.

    Features:
    - Geographic search for nearby service centers
    - Multi-factor optimization for appointment slots
    - Autonomous booking with customer confirmation
    - Parts availability checking and reservation
    - Rescheduling and cancellation handling
    - Fleet scheduling optimization
    - SMS and app notifications
    """

    def __init__(self):
        super().__init__("scheduling")

        # Mock service centers with geographic data
        self.service_centers = [
            ServiceCenter(
                id="SC001",
                name="MG Road Service Center",
                address="123 MG Road, Bangalore",
                latitude=12.9716,
                longitude=77.5946,
                phone="+91 - 80 - 12345678",
                rating=4.5,
                specialties=["engine", "brakes", "electrical", "diagnostics"],
                hours={"open": 8, "close": 18},
                available_slots_count=12,
            ),
            ServiceCenter(
                id="SC002",
                name="Indiranagar Auto Care",
                address="456 100 Feet Road, Indiranagar, Bangalore",
                latitude=12.9784,
                longitude=77.6408,
                phone="+91 - 80 - 23456789",
                rating=4.3,
                specialties=["tires", "brakes", "general", "electrical"],
                hours={"open": 7, "close": 19},
                available_slots_count=8,
            ),
            ServiceCenter(
                id="SC003",
                name="Koramangala Premium Service",
                address="789 Koramangala 4th Block, Bangalore",
                latitude=12.9352,
                longitude=77.6245,
                phone="+91 - 80 - 34567890",
                rating=4.7,
                specialties=["engine", "electrical", "diagnostics", "luxury"],
                hours={"open": 8, "close": 17},
                available_slots_count=6,
            ),
            ServiceCenter(
                id="SC004",
                name="Whitefield Express Service",
                address="321 ITPL Road, Whitefield, Bangalore",
                latitude=12.9698,
                longitude=77.7500,
                phone="+91 - 80 - 45678901",
                rating=4.2,
                specialties=["general", "tires", "brakes"],
                hours={"open": 9, "close": 18},
                available_slots_count=10,
            ),
            ServiceCenter(
                id="SC005",
                name="Electronic City Auto Hub",
                address="654 Hosur Road, Electronic City, Bangalore",
                latitude=12.8456,
                longitude=77.6603,
                phone="+91 - 80 - 56789012",
                rating=4.4,
                specialties=["engine", "electrical", "diagnostics"],
                hours={"open": 8, "close": 19},
                available_slots_count=15,
            ),
        ]

        # Mock parts inventory
        self.parts_inventory = {
            "SC001": {
                "battery": {"in_stock": True, "quantity": 25},
                "brake_pads": {"in_stock": True, "quantity": 15},
                "engine_oil": {"in_stock": True, "quantity": 50},
                "air_filter": {"in_stock": False, "quantity": 0, "estimated_arrival": "2024 - 12 - 28"},
            },
            "SC002": {
                "battery": {"in_stock": True, "quantity": 18},
                "brake_pads": {"in_stock": True, "quantity": 20},
                "tires": {"in_stock": True, "quantity": 12},
                "engine_oil": {"in_stock": True, "quantity": 30},
            },
            "SC003": {
                "battery": {"in_stock": True, "quantity": 30},
                "brake_pads": {"in_stock": True, "quantity": 25},
                "engine_oil": {"in_stock": True, "quantity": 40},
                "air_filter": {"in_stock": True, "quantity": 10},
            },
            "SC004": {
                "battery": {"in_stock": False, "quantity": 0, "estimated_arrival": "2024 - 12 - 27"},
                "brake_pads": {"in_stock": True, "quantity": 12},
                "tires": {"in_stock": True, "quantity": 20},
                "engine_oil": {"in_stock": True, "quantity": 35},
            },
            "SC005": {
                "battery": {"in_stock": True, "quantity": 22},
                "brake_pads": {"in_stock": True, "quantity": 18},
                "engine_oil": {"in_stock": True, "quantity": 45},
                "air_filter": {"in_stock": True, "quantity": 8},
            },
        }

        # Mock bookings storage
        self.bookings = {}

        logger.info("Enhanced Scheduling Agent initialized successfully")

    def find_nearby_service_centers(self, latitude: float, longitude: float, radius_km: int = 20) -> List[Dict]:
        """Find service centers near customer location using geographic search."""
        try:
            nearby_centers = []

            for center in self.service_centers:
                # Calculate distance using Haversine formula
                distance = self._calculate_distance(latitude, longitude, center.latitude, center.longitude)

                if distance <= radius_km:
                    center_dict = asdict(center)
                    center_dict["distance_km"] = round(distance, 2)
                    nearby_centers.append(center_dict)

            # Sort by distance
            nearby_centers.sort(key=lambda x: x["distance_km"])

            logger.info(f"Found {len(nearby_centers)} service centers within {radius_km}km")
            return nearby_centers

        except Exception as e:
            logger.error(f"Error finding nearby service centers: {str(e)}")
            return []

    def get_service_center_availability(self, center_id: str, date: str, issue_type: str) -> List[Dict]:
        """Get available time slots for a specific date and issue type."""
        try:
            # Find the service center
            center = next((c for c in self.service_centers if c.id == center_id), None)
            if not center:
                return []

            # Parse the date
            target_date = datetime.strptime(date, "%Y-%m-%d")

            # Skip weekends
            if target_date.weekday() >= 5:
                return []

            available_slots = []

            # Generate available slots based on business hours
            for hour in range(center.hours["open"], center.hours["close"]):
                # Simulate some slots being unavailable
                if random.random() > 0.4:  # 60% chance slot is available
                    # Estimate duration based on issue type
                    duration = self._estimate_service_duration(issue_type)

                    # Check if slot fits within business hours
                    slot_end_hour = hour + math.ceil(duration)
                    if slot_end_hour <= center.hours["close"]:
                        slot = {
                            "time_slot": f"{hour:02d}:00",
                            "bay_number": random.randint(1, 6),
                            "estimated_duration": duration,
                            "wait_time": random.randint(0, 30),
                            "technician_id": f"TECH{random.randint(1, 10):03d}",
                            "technician_name": random.choice(
                                [
                                    "Rajesh Kumar",
                                    "Priya Sharma",
                                    "Amit Singh",
                                    "Sneha Patel",
                                    "Vikram Reddy",
                                    "Anita Gupta",
                                ]
                            ),
                        }
                        available_slots.append(slot)

            logger.info(f"Found {len(available_slots)} available slots for {center_id} on {date}")
            return available_slots

        except Exception as e:
            logger.error(f"Error getting service center availability: {str(e)}")
            return []

    def check_parts_availability(self, center_id: str, component: str) -> Dict:
        """Check if required parts are in stock at the service center."""
        try:
            # Map component to parts
            component_parts_map = {
                "battery": "battery",
                "brakes": "brake_pads",
                "engine": "engine_oil",
                "electrical": "battery",
                "air_filter": "air_filter",
                "tires": "tires",
            }

            part_name = component_parts_map.get(component.lower(), "engine_oil")
            center_inventory = self.parts_inventory.get(center_id, {})
            part_info = center_inventory.get(part_name, {"in_stock": False, "quantity": 0})

            result = {
                "in_stock": part_info["in_stock"],
                "quantity": part_info["quantity"],
                "estimated_arrival": part_info.get("estimated_arrival"),
            }

            logger.info(f"Parts availability for {component} at {center_id}: {result}")
            return result

        except Exception as e:
            logger.error(f"Error checking parts availability: {str(e)}")
            return {"in_stock": False, "quantity": 0}

    def calculate_optimal_slot(
        self, customer_location: Dict, center_options: List[Dict], urgency: str, customer_preferences: Dict
    ) -> Dict:
        """Calculate optimal appointment slot using multi-factor scoring."""
        try:
            best_slot = None
            best_score = 0

            for center in center_options:
                # Get availability for next 14 days
                for days_ahead in range(14):
                    check_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
                    slots = self.get_service_center_availability(center["id"], check_date, urgency)

                    for slot in slots:
                        # Calculate multi-factor score
                        score = self._calculate_slot_score(center, slot, check_date, urgency, customer_preferences)

                        if score > best_score:
                            best_score = score
                            best_slot = {
                                "center_id": center["id"],
                                "center_name": center["name"],
                                "date": check_date,
                                "time": slot["time_slot"],
                                "score": score,
                                "distance_km": center["distance_km"],
                                "parts_available": True,  # Simplified for demo
                                "estimated_duration": slot["estimated_duration"],
                            }

            logger.info(f"Optimal slot calculated with score: {best_score}")
            return best_slot or {}

        except Exception as e:
            logger.error(f"Error calculating optimal slot: {str(e)}")
            return {}

    def book_appointment(
        self, customer_id: str, vehicle_id: str, center_id: str, date: str, time: str, predicted_issue: str
    ) -> Dict:
        """Create appointment booking with bay and technician reservation."""
        try:
            # Generate booking ID and confirmation code
            booking_id = f"APT-{datetime.now().strftime('%Y%m%d')}-{random.randint(100000, 999999)}"
            confirmation_code = f"CONF{random.randint(10000, 99999)}"

            # Find service center
            center = next((c for c in self.service_centers if c.id == center_id), None)
            if not center:
                raise ValueError(f"Service center {center_id} not found")

            # Get slot details
            slots = self.get_service_center_availability(center_id, date, predicted_issue)
            slot = next((s for s in slots if s["time_slot"] == time), None)

            if not slot:
                raise ValueError(f"Time slot {time} not available")

            # Create booking
            booking = BookingConfirmation(
                booking_id=booking_id,
                confirmation_code=confirmation_code,
                customer_id=customer_id,
                vehicle_id=vehicle_id,
                center_id=center_id,
                center_name=center.name,
                center_address=center.address,
                date=date,
                time=time,
                predicted_issue=predicted_issue,
                estimated_duration=slot["estimated_duration"],
                bay_number=slot["bay_number"],
                technician_name=slot["technician_name"],
            )

            # Store booking
            self.bookings[booking_id] = booking

            # Reserve parts (simplified)
            self._reserve_parts(center_id, predicted_issue)

            result = {
                "booking_id": booking_id,
                "confirmation_code": confirmation_code,
                "booking_details": asdict(booking),
            }

            logger.info(f"Appointment booked successfully: {booking_id}")
            return result

        except Exception as e:
            logger.error(f"Error booking appointment: {str(e)}")
            return {"error": str(e)}

    def send_confirmation(self, customer_id: str, appointment_details: Dict) -> bool:
        """Send appointment confirmation via SMS and app notification."""
        try:
            # Mock SMS sending (would use Twilio/Exotel in production)
            sms_message = f"""
Appointment Confirmed!
Date: {appointment_details['date']}
Time: {appointment_details['time']}
Location: {appointment_details['center_name']}
Booking ID: {appointment_details['booking_id']}
Confirmation Code: {appointment_details['confirmation_code']}
            """.strip()

            # Mock app notification
            # push_notification = {
            #     "title": "Appointment Confirmed",
            #     "body": f"Your service appointment is confirmed for {appointment_details['date']} at {appointment_details['time']}",
            #     "data": appointment_details,
            # }

            # Simulate sending
            logger.info(f"SMS sent to customer {customer_id}: {sms_message[:50]}...")
            logger.info(f"Push notification sent to customer {customer_id}")

            return True

        except Exception as e:
            logger.error(f"Error sending confirmation: {str(e)}")
            return False

    def reschedule_appointment(self, booking_id: str, new_date: str, new_time: str) -> Dict:
        """Reschedule existing appointment."""
        try:
            # Find existing booking
            booking = self.bookings.get(booking_id)
            if not booking:
                return {"error": "Booking not found"}

            # Check new slot availability
            slots = self.get_service_center_availability(booking.center_id, new_date, booking.predicted_issue)
            new_slot = next((s for s in slots if s["time_slot"] == new_time), None)

            if not new_slot:
                return {"error": "New time slot not available"}

            # Update booking
            old_date, old_time = booking.date, booking.time
            booking.date = new_date
            booking.time = new_time
            booking.bay_number = new_slot["bay_number"]
            booking.technician_name = new_slot["technician_name"]

            # Send updated confirmation
            self.send_confirmation(booking.customer_id, asdict(booking))

            result = {
                "booking_id": booking_id,
                "old_date": old_date,
                "old_time": old_time,
                "new_date": new_date,
                "new_time": new_time,
                "message": "Appointment rescheduled successfully",
            }

            logger.info(f"Appointment {booking_id} rescheduled from {old_date} {old_time} to {new_date} {new_time}")
            return result

        except Exception as e:
            logger.error(f"Error rescheduling appointment: {str(e)}")
            return {"error": str(e)}

    def schedule_fleet_vehicles(self, fleet_id: str, vehicles: List[str]) -> List[Dict]:
        """Schedule multiple vehicles for fleet customers with optimization."""
        try:
            fleet_bookings = []

            # Optimize scheduling to minimize total fleet downtime
            # Stagger appointments to avoid having all vehicles out of service

            base_date = datetime.now() + timedelta(days=1)

            for i, vehicle_id in enumerate(vehicles):
                # Stagger appointments across different days and times
                appointment_date = base_date + timedelta(days=i % 3)  # Spread across 3 days
                appointment_time = f"{9 + (i % 8):02d}:00"  # Spread across business hours

                # Find available service center
                customer_location = {"latitude": 12.9716, "longitude": 77.5946}  # Mock location
                nearby_centers = self.find_nearby_service_centers(
                    customer_location["latitude"], customer_location["longitude"]
                )

                if nearby_centers:
                    center = nearby_centers[0]  # Use closest center

                    # Book appointment
                    booking_result = self.book_appointment(
                        customer_id=f"FLEET_{fleet_id}",
                        vehicle_id=vehicle_id,
                        center_id=center["id"],
                        date=appointment_date.strftime("%Y-%m-%d"),
                        time=appointment_time,
                        predicted_issue="fleet_maintenance",
                    )

                    if "error" not in booking_result:
                        fleet_bookings.append(booking_result)

            logger.info(f"Scheduled {len(fleet_bookings)} vehicles for fleet {fleet_id}")
            return fleet_bookings

        except Exception as e:
            logger.error(f"Error scheduling fleet vehicles: {str(e)}")
            return []

    def get_appointment_recommendations(
        self, customer_id: str, vehicle_id: str, predicted_issue: str, customer_location: Dict, urgency: str = "P2"
    ) -> List[Dict]:
        """Get 3 - 5 optimal appointment recommendations for customer."""
        try:
            # Find nearby service centers
            nearby_centers = self.find_nearby_service_centers(
                customer_location["latitude"], customer_location["longitude"]
            )

            if not nearby_centers:
                return []

            recommendations = []

            # Get top 3 centers
            top_centers = nearby_centers[:3]

            for center in top_centers:
                # Check parts availability
                parts_info = self.check_parts_availability(center["id"], predicted_issue)

                # Get availability for next 7 days
                for days_ahead in range(7):
                    check_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
                    slots = self.get_service_center_availability(center["id"], check_date, predicted_issue)

                    if slots:
                        # Take first available slot
                        slot = slots[0]

                        recommendation = {
                            "center_id": center["id"],
                            "center_name": center["name"],
                            "center_address": center["address"],
                            "date": check_date,
                            "time": slot["time_slot"],
                            "distance_km": center["distance_km"],
                            "estimated_duration": slot["estimated_duration"],
                            "parts_available": parts_info["in_stock"],
                            "parts_arrival": parts_info.get("estimated_arrival"),
                            "technician": slot["technician_name"],
                            "bay_number": slot["bay_number"],
                        }

                        recommendations.append(recommendation)
                        break  # Take first available slot for this center

            # Sort by distance and parts availability
            recommendations.sort(key=lambda x: (x["distance_km"], not x["parts_available"]))

            logger.info(f"Generated {len(recommendations)} appointment recommendations")
            return recommendations[:5]  # Return top 5

        except Exception as e:
            logger.error(f"Error getting appointment recommendations: {str(e)}")
            return []

    # Helper methods

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        R = 6371  # Earth's radius in kilometers

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _estimate_service_duration(self, issue_type: str) -> float:
        """Estimate service duration based on issue type."""
        duration_map = {
            "battery": 0.5,
            "brakes": 2.0,
            "engine": 4.0,
            "electrical": 1.5,
            "tires": 1.0,
            "general": 1.5,
            "fleet_maintenance": 2.0,
        }
        return duration_map.get(issue_type.lower(), 1.5)

    def _calculate_slot_score(self, center: Dict, slot: Dict, date: str, urgency: str, preferences: Dict) -> float:
        """Calculate multi-factor score for appointment slot."""
        score = 0

        # Distance factor (closer is better)
        distance_score = max(0, 20 - center["distance_km"]) / 20 * 30
        score += distance_score

        # Urgency factor
        days_ahead = (datetime.strptime(date, "%Y-%m-%d") - datetime.now()).days
        if urgency == "P0" and days_ahead <= 1:
            score += 40
        elif urgency == "P1" and days_ahead <= 3:
            score += 30
        elif urgency == "P2" and days_ahead <= 7:
            score += 20

        # Service center rating
        score += center["rating"] * 10

        # Time preference (morning preferred)
        hour = int(slot["time_slot"].split(":")[0])
        if 9 <= hour <= 11:
            score += 15
        elif 14 <= hour <= 16:
            score += 10

        # Wait time (less is better)
        score += max(0, 30 - slot["wait_time"]) / 30 * 10

        return score

    def _reserve_parts(self, center_id: str, predicted_issue: str):
        """Reserve parts for the appointment (simplified mock)."""
        component_parts_map = {
            "battery": "battery",
            "brakes": "brake_pads",
            "engine": "engine_oil",
            "electrical": "battery",
        }

        part_name = component_parts_map.get(predicted_issue.lower(), "engine_oil")
        center_inventory = self.parts_inventory.get(center_id, {})

        if part_name in center_inventory and center_inventory[part_name]["quantity"] > 0:
            center_inventory[part_name]["quantity"] -= 1
            logger.info(f"Reserved {part_name} at {center_id}")

    # Legacy method for backward compatibility
    async def _execute_internal(self, state: State) -> State:
        """Legacy method for backward compatibility with existing system."""
        try:
            self.logger.info("Processing appointment scheduling request", vehicle_id=state.get("vehicle_id"))

            # Extract customer location (mock data)
            customer_location = {"latitude": 12.9716, "longitude": 77.5946}

            # Get prediction details
            prediction = state.get("prediction", {})
            predicted_issue = prediction.get("component", "general")
            urgency = str(prediction.get("priority", "P2"))

            # Get appointment recommendations
            recommendations = self.get_appointment_recommendations(
                customer_id=state.get("customer_id", "CUST001"),
                vehicle_id=state.get("vehicle_id", "VEH001"),
                predicted_issue=predicted_issue,
                customer_location=customer_location,
                urgency=urgency,
            )

            if recommendations:
                # Auto-book the best recommendation
                best_recommendation = recommendations[0]

                booking_result = self.book_appointment(
                    customer_id=state.get("customer_id", "CUST001"),
                    vehicle_id=state.get("vehicle_id", "VEH001"),
                    center_id=best_recommendation["center_id"],
                    date=best_recommendation["date"],
                    time=best_recommendation["time"],
                    predicted_issue=predicted_issue,
                )

                if "error" not in booking_result:
                    # Send confirmation
                    self.send_confirmation(state.get("customer_id", "CUST001"), booking_result["booking_details"])

                    # Update state with appointment details
                    state["appointment"] = AppointmentDetails(
                        appointment_id=booking_result["booking_id"],
                        scheduled_date=f"{best_recommendation['date']} {best_recommendation['time']}",
                        service_type=f"{predicted_issue.title()} Service",
                        estimated_duration=int(best_recommendation["estimated_duration"] * 60),
                        service_advisor=best_recommendation["technician"],
                        location=f"{best_recommendation['center_name']} - {best_recommendation['center_address']}",
                        status="confirmed",
                    )

                    state = self._add_log_message(
                        state,
                        f"Appointment confirmed for {best_recommendation['date']} at {best_recommendation['center_name']}",
                        {"booking_details": booking_result["booking_details"]},
                    )
                else:
                    state = self._add_log_message(
                        state,
                        f"Failed to book appointment: {booking_result.get('error', 'Unknown error')}",
                        {"error": booking_result.get("error")},
                    )
            else:
                state = self._add_log_message(state, "No available appointments found", {"recommendations": []})

            return state

        except Exception as e:
            logger.error(f"Error in appointment scheduling: {str(e)}")
            state = self._add_log_message(state, f"Scheduling error: {str(e)}", {"error": str(e)})
            return state
