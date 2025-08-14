# services.py
import json
from .connection import db_manager
from .exception_handler import db_exception_handler

class ServiceManager:

    @db_exception_handler
    def save_service(self, service_data):
        with db_manager.get_connection() as conn, conn.cursor() as cur:
            service_types_json = json.dumps(service_data.get("service_types", []))
            cur.execute("""
                INSERT INTO services (
                    customer_id, vehicle_id, service_types,
                    description, pickup_required, pickup_address,
                    service_date, status, assigned_mechanic,
                    payment_status, base_cost, extra_charges,
                    charge_description, work_done, request_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                service_data["customer_id"],
                service_data["vehicle_id"],
                service_types_json,
                service_data.get("description"),
                service_data.get("pickup_required"),
                service_data.get("pickup_address"),
                service_data.get("service_date"),
                service_data.get("status", "Pending"),
                service_data.get("assigned_mechanic"),
                service_data.get("payment_status", "Pending"),
                service_data.get("base_cost", 0),
                service_data.get("extra_charges", 0),
                service_data.get("charge_description"),
                service_data.get("work_done"),
                service_data.get("request_date")
            ))
            return cur.lastrowid

    @db_exception_handler
    def fetch_all_services(self):
        with db_manager.get_connection() as conn, conn.cursor() as cur:
            query = """
                SELECT s.*, u.full_name AS customer_name, u.email AS customer_email, u.phone AS customer_phone,
                       v.vehicle_type, v.vehicle_brand, v.vehicle_model, v.vehicle_no
                FROM services s
                JOIN users u ON s.customer_id = u.id
                JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                ORDER BY s.request_date DESC
            """
            cur.execute(query)
            services = cur.fetchall()
            for s in services:
                if isinstance(s.get('service_types'), str):
                    try:
                        s['service_types'] = json.loads(s['service_types'])
                    except:
                        s['service_types'] = []
            return services

    @db_exception_handler
    def get_services_by_customer_id(self, customer_id):
        """Fetch all services for a specific customer_id."""
        with db_manager.get_connection() as conn, conn.cursor() as cur:
            query = """
                SELECT s.*, v.vehicle_type, v.vehicle_brand, v.vehicle_model, v.vehicle_no
                FROM services s
                JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                WHERE s.customer_id = %s
                ORDER BY s.request_date DESC
            """
            cur.execute(query, (customer_id,))
            services = cur.fetchall()
            for s in services:
                if isinstance(s.get('service_types'), str):
                    try:
                        s['service_types'] = json.loads(s['service_types'])
                    except:
                        s['service_types'] = []
            return services

    @db_exception_handler
    def save_service_type(self, service_type_data):
        """Insert a new service type entry for a service."""
        with db_manager.get_connection() as conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO service_types (service_id, service_name, price)
                VALUES (%s, %s, %s)
            """, (
                service_type_data["service_id"],
                service_type_data["service_name"],
                service_type_data.get("price", 0)
            ))
            return cur.lastrowid
