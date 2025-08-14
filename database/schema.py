# schema.py
from .connection import db_manager
from .exception_handler import db_exception_handler

class SchemaManager:
    """Handles creation and initialization of database tables."""

    @db_exception_handler
    def create_tables(self):
        with db_manager.get_connection() as conn, conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    full_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    phone VARCHAR(20) NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    user_type VARCHAR(20) NOT NULL DEFAULT 'Customer'
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS vehicles (
                    vehicle_id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    vehicle_type VARCHAR(20),
                    vehicle_brand VARCHAR(100),
                    vehicle_model VARCHAR(100),
                    vehicle_no VARCHAR(30) UNIQUE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS mechanics (
                    mechanic_id INT PRIMARY KEY AUTO_INCREMENT,
                    mechanic_name VARCHAR(100) NOT NULL,
                    contact VARCHAR(20)
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    service_id INT PRIMARY KEY AUTO_INCREMENT,
                    customer_id INT NOT NULL,
                    vehicle_id INT NOT NULL,
                    service_types JSON,
                    description TEXT,
                    pickup_required VARCHAR(10),
                    pickup_address VARCHAR(250),
                    service_date DATE,
                    status VARCHAR(20) DEFAULT 'Pending',
                    assigned_mechanic INT,
                    payment_status VARCHAR(20) DEFAULT 'Pending',
                    base_cost INT DEFAULT 0,
                    extra_charges INT DEFAULT 0,
                    charge_description TEXT,
                    work_done TEXT,
                    Paid INT DEFAULT 0,
                    request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
                    FOREIGN KEY (assigned_mechanic) REFERENCES mechanics(mechanic_id) ON DELETE SET NULL
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS service_types(
                    service_type_id INT PRIMARY KEY AUTO_INCREMENT,
                    service_id INT NOT NULL,
                    service_name VARCHAR(100) NOT NULL,
                    price INT DEFAULT 0,
                    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE
                );
            """)
