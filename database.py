import pymysql
import streamlit as st
import json


def get_connection():
    """Get a database connection from Streamlit secrets."""
    try:
        db = st.secrets["mysql"]
        connection = pymysql.connect(
            host=db["host"],
            user=db["user"],
            password=db["password"],
            database=db["database"],
            port=int(db.get("port", 3306)),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return connection
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        raise


def create_tables():
    """Create database tables if they don't exist, using normalized users, vehicles, service_types, mechanics."""
    try:
        connection = get_connection()
        with connection:
            with connection.cursor() as cur:
                # USERS table
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

                # VEHICLES table: one user can have multiple vehicles
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

                # MECHANICS table
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
                        request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
                        FOREIGN KEY (assigned_mechanic) REFERENCES mechanics(mechanic_id) ON DELETE SET NULL
                    );
                """)

        st.success("✅ Database tables created or verified successfully.")
    except Exception as e:
        st.error(f"❌ Failed to create tables: {e}")


# Create tables on import
try:
    create_tables()
except Exception as e:
    st.error(f"❌ Database initialization failed: {e}")


# ----------- CRUD & Fetch Functions -----------


# Users
def fetch_all_users():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, full_name, email, phone, password, user_type FROM users ORDER BY full_name;")
                return cur.fetchall()
    except Exception as e:
        st.error(f"❌ Failed to fetch users: {e}")
        return []


def add_user(user_data):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (full_name, email, phone, password, user_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    user_data['full_name'],
                    user_data['email'],
                    user_data['phone'],
                    user_data['password'],
                    user_data.get('user_type', 'Customer')
                ))
                return cur.lastrowid
    except pymysql.IntegrityError as e:
        if "Duplicate entry" in str(e) and "email" in str(e):
            st.error("❌ Email already exists.")
        else:
            st.error(f"❌ Database error: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Failed to add user: {e}")
        return None


def get_user_by_email(email):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                return cur.fetchone()
    except Exception as e:
        st.error(f"❌ Failed to fetch user by email: {e}")
        return None


# Vehicles
def fetch_vehicles_by_user(user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM vehicles WHERE user_id = %s", (user_id,))
                return cur.fetchall()
    except Exception as e:
        st.error(f"❌ Failed to fetch user vehicles: {e}")
        return []


def add_vehicle(vehicle_data):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
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
            st.error("❌ Vehicle number already exists.")
        else:
            st.error(f"❌ Database error: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Failed to add vehicle: {e}")
        return None


# Mechanics
def fetch_all_mechanics():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM mechanics ORDER BY mechanic_name")
                return cur.fetchall()
    except Exception as e:
        st.error(f"❌ Failed to fetch mechanics: {e}")
        return []

# Services
def save_service(service_data):
    """
    Save a new service; service_types stored as JSON array of selected service_type names or IDs.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
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
    except Exception as e:
        st.error(f"❌ Failed to save service: {e}")
        return None


def fetch_all_services():
    """Fetch all service records joined with customer and vehicle details."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                SELECT 
                    s.*,
                    u.full_name AS customer_name,
                    u.email AS customer_email,
                    u.phone AS customer_phone,
                    v.vehicle_type,
                    v.vehicle_brand,
                    v.vehicle_model,
                    v.vehicle_no
                FROM services s
                JOIN users u ON s.customer_id = u.id
                JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                ORDER BY s.request_date DESC;
                """
                cur.execute(query)
                services = cur.fetchall()

                # Parse JSON service_types into list objects for each service
                for s in services:
                    if isinstance(s.get('service_types'), str):
                        try:
                            s['service_types'] = json.loads(s['service_types'])
                        except json.JSONDecodeError:
                            s['service_types'] = []
                    elif s.get('service_types') is None:
                        s['service_types'] = []

                return services
    except Exception as e:
        st.error(f"❌ Failed to fetch services: {e}")
        return []


def get_service_by_id(service_id):
    """Fetch a single service by ID joined with customer and vehicle details."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                SELECT 
                    s.*,
                    u.full_name AS customer_name,
                    u.email AS customer_email,
                    u.phone AS customer_phone,
                    v.vehicle_type,
                    v.vehicle_brand,
                    v.vehicle_model,
                    v.vehicle_no
                FROM services s
                JOIN users u ON s.customer_id = u.id
                JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                WHERE s.service_id = %s;
                """
                cur.execute(query, (service_id,))
                service = cur.fetchone()
                if service:
                    if isinstance(service.get('service_types'), str):
                        try:
                            service['service_types'] = json.loads(service['service_types'])
                        except json.JSONDecodeError:
                            service['service_types'] = []
                    elif service.get('service_types') is None:
                        service['service_types'] = []
                return service
    except Exception as e:
        st.error(f"❌ Failed to fetch service: {e}")
        return None


def get_services_by_customer_id(customer_id):
    """Fetch services for a specific customer ID."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                query = '''SELECT
                             s.*, v.* 
                             FROM services s 
                             JOIN vehicles v ON s.vehicle_id = v.vehicle_id 
                             WHERE customer_id = %s 
                             ORDER BY request_date DESC;
                            '''
                cur.execute(query, (customer_id,))
                services = cur.fetchall()
                for s in services:
                    if isinstance(s.get('service_types'), str):
                        try:
                            s['service_types'] = json.loads(s['service_types'])
                        except:
                            s['service_types'] = []
                    elif s.get('service_types') is None:
                        s['service_types'] = []
                return services
    except Exception as e:
        st.error(f"❌ Failed to fetch customer services: {e}")
        return []


def update_payment_status(service_id, paid_amt):
    """Customer-only payment status update to done."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE services SET payment_status = %s, Paid = %s WHERE service_id = %s", ("Done", paid_amt, service_id))
                return cur.rowcount > 0
    except Exception as e:
        st.error(f"❌ Failed to update payment status: {e}")
        return False


def update_service(service_id, updates):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                sets = []
                params = []
                for k, v in updates.items():
                    sets.append(f"{k} = %s")
                    params.append(v)
                params.append(service_id)
                sql = f"UPDATE services SET {', '.join(sets)} WHERE service_id = %s"
                cur.execute(sql, tuple(params))
                return cur.rowcount > 0
    except Exception as e:
        st.error(f"❌ Failed to update service: {e}")
        return False
