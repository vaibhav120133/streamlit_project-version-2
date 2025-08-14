# vehicles.py
import pymysql
from .connection import db_manager
from .exception_handler import db_exception_handler

class VehicleService:
    """Handles vehicle-related database operations."""

    @db_exception_handler
    def fetch_vehicles_by_user(self, user_id):
        """Get all vehicles for a specific user."""
        with db_manager.get_connection() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM vehicles
                WHERE user_id = %s
                ORDER BY vehicle_type ASC, vehicle_brand ASC, vehicle_model ASC, vehicle_no ASC
            """, (user_id,))
            return cur.fetchall()

    @db_exception_handler
    def add_users_vehicle(self, vehicle_data):
        """Insert a new vehicle for a user."""
        with db_manager.get_connection() as conn, conn.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO vehicles (user_id, vehicle_type, vehicle_brand, vehicle_model, vehicle_no)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    vehicle_data["user_id"],
                    vehicle_data["vehicle_type"],
                    vehicle_data["vehicle_brand"],
                    vehicle_data["vehicle_model"],
                    vehicle_data["vehicle_no"].upper()
                ))
                return cur.lastrowid
            except pymysql.IntegrityError as e:
                if "Duplicate entry" in str(e):
                    raise Exception("Vehicle number already exists.")
                else:
                    raise
