import pymysql
import streamlit as st
import json


def get_connection():
    """Get database connection with proper error handling"""
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
    """Create tables if they don't exist"""
    try:
        connection = get_connection()
        with connection:
            with connection.cursor() as cursor:
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        full_name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) NOT NULL UNIQUE,
                        phone VARCHAR(20) NOT NULL,
                        password VARCHAR(100) NOT NULL,
                        user_type VARCHAR(20) NOT NULL DEFAULT 'Customer'
                    )
                """)
                
                # Create services table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS services (
                        service_id INT PRIMARY KEY AUTO_INCREMENT,
                        customer_name VARCHAR(100),
                        customer_email VARCHAR(100),
                        customer_phone VARCHAR(20),
                        vehicle_type VARCHAR(20),
                        vehicle_brand VARCHAR(100),
                        vehicle_model VARCHAR(100),
                        vehicle_no VARCHAR(30),
                        service_types JSON,
                        description TEXT,
                        pickup_required VARCHAR(10),
                        pickup_address VARCHAR(250),
                        service_date DATE,
                        status VARCHAR(20) DEFAULT 'Pending',
                        assigned_mechanic VARCHAR(100),
                        payment_status VARCHAR(20) DEFAULT 'Pending',
                        base_cost INT DEFAULT 0,
                        extra_charges INT DEFAULT 0,
                        charge_description TEXT,
                        work_done TEXT,
                        request_date DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
    except Exception as e:
        st.error(f"❌ Failed to create tables: {e}")


# Create tables at import
try:
    create_tables()
except Exception as e:
    st.error(f"❌ Database initialization failed: {e}")


def fetch_all_services():
    """Fetch all services with proper error handling"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM services ORDER BY request_date DESC;")
                services = cur.fetchall()
                
                # Process service_types JSON field
                for s in services:
                    if isinstance(s.get('service_types'), str):
                        try:
                            s['service_types'] = json.loads(s['service_types'])
                        except json.JSONDecodeError as e:
                            st.warning(f"⚠️ JSON decode error for service {s.get('service_id')}: {e}")
                            s['service_types'] = []
                    elif s.get('service_types') is None:
                        s['service_types'] = []
                return services
                
    except Exception as e:
        st.error(f"❌ Failed to fetch services: {e}")
        # Return empty list instead of crashing
        return []


def save_service(service_data):
    """Save a new service with proper error handling"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Ensure service_types is properly formatted
                service_types_json = json.dumps(service_data.get("service_types", []))
                
                cur.execute("""
                    INSERT INTO services (
                        customer_name, customer_email, customer_phone, vehicle_type,
                        vehicle_brand, vehicle_model, vehicle_no, service_types,
                        description, pickup_required, pickup_address, service_date,
                        status, assigned_mechanic, payment_status, base_cost,
                        extra_charges, charge_description, work_done, request_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    service_data.get("customer_name"),
                    service_data.get("customer_email"),
                    service_data.get("customer_phone"),
                    service_data.get("vehicle_type"),
                    service_data.get("vehicle_brand"),
                    service_data.get("vehicle_model"),
                    service_data.get("vehicle_no"),
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
                
                service_id = cur.lastrowid
                return service_id
                
    except Exception as e:
        st.error(f"❌ Failed to save service: {e}")
        return None


def fetch_all_users():
    """Fetch all users with proper error handling"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, full_name, email, phone, password, user_type FROM users ORDER BY full_name;")
                users = cur.fetchall()
                return users
    except Exception as e:
        st.error(f"❌ Failed to fetch users: {e}")
        return []


def add_user(user_data):
    """Add a new user with proper error handling"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (full_name, email, phone, password, user_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    user_data['full_name'],
                    user_data['email'],
                    user_data['phone'],
                    user_data['password'],
                    user_data.get('user_type', 'Customer')
                ))
                
                user_id = cursor.lastrowid
                return user_id
                
    except pymysql.IntegrityError as e:
        if "Duplicate entry" in str(e) and "email" in str(e):
            st.error("❌ Email already exists. Please use a different email address.")
        else:
            st.error(f"❌ Database integrity error: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Failed to add user: {e}")
        return None


def get_user_by_email(email):
    """Get user by email with proper error handling"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cur.fetchone()
                return user
    except Exception as e:
        st.error(f"❌ Failed to fetch user by email: {e}")
        return None


def authenticate_user(email, password):
    """Authenticate user with proper error handling"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
                user = cur.fetchone()
                if user:
                    st.success("✅ User authenticated successfully")
                    return user
                else:
                    st.error("❌ Invalid email or password")
                    return None
    except Exception as e:
        st.error(f"❌ Authentication failed: {e}")
        return None


def update_payment_status(service_id):
    """Update payment status with proper error handling"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE services SET payment_status = %s WHERE service_id = %s",
                    ("Done", service_id)
                )
                
                if cur.rowcount > 0:
                    st.success(f"✅ Payment status updated for service ID: {service_id}")
                    return True
                else:
                    st.warning(f"⚠️ No service found with ID: {service_id}")
                    return False
                    
    except Exception as e:
        st.error(f"❌ Failed to update payment status: {e}")
        return False


def update_service(service_id, field_values: dict):
    """Update specific fields of a service by ID with proper error handling"""
    try:
        if not field_values:
            st.warning("⚠️ No fields to update")
            return False
            
        with get_connection() as conn:
            with conn.cursor() as cur:
                set_clauses = []
                params = []
                
                for field, value in field_values.items():
                    set_clauses.append(f"{field} = %s")
                    # Convert lists to JSON strings if needed
                    if field == "service_types" and isinstance(value, (list, dict)):
                        params.append(json.dumps(value))
                    else:
                        params.append(value)
                        
                params.append(service_id)

                sql = f"UPDATE services SET {', '.join(set_clauses)} WHERE service_id = %s"
                cur.execute(sql, tuple(params))
                
                if cur.rowcount > 0:
                    st.success(f"✅ Service {service_id} updated successfully")
                    return True
                else:
                    st.warning(f"⚠️ No service found with ID: {service_id}")
                    return False
                    
    except Exception as e:
        st.error(f"❌ Failed to update service: {e}")
        return False


def get_service_by_id(service_id):
    """Get a specific service by ID with proper error handling"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM services WHERE service_id = %s", (service_id,))
                service = cur.fetchone()
                
                if service:
                    # Process service_types JSON field
                    if isinstance(service.get('service_types'), str):
                        try:
                            service['service_types'] = json.loads(service['service_types'])
                        except json.JSONDecodeError:
                            service['service_types'] = []
                    elif service.get('service_types') is None:
                        service['service_types'] = []
                        
                return service
                
    except Exception as e:
        st.error(f"❌ Failed to fetch service by ID: {e}")
        return None


def delete_service(service_id):
    """Delete a service with proper error handling"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM services WHERE service_id = %s", (service_id,))
                
                if cur.rowcount > 0:
                    st.success(f"✅ Service {service_id} deleted successfully")
                    return True
                else:
                    st.warning(f"⚠️ No service found with ID: {service_id}")
                    return False
                    
    except Exception as e:
        st.error(f"❌ Failed to delete service: {e}")
        return False


def delete_user(user_id):
    """Delete a user with proper error handling"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
                
                if cur.rowcount > 0:
                    st.success(f"✅ User {user_id} deleted successfully")
                    return True
                else:
                    st.warning(f"⚠️ No user found with ID: {user_id}")
                    return False
                    
    except Exception as e:
        st.error(f"❌ Failed to delete user: {e}")
        return False


def update_user(user_id, field_values: dict):
    """Update specific fields of a user by ID with proper error handling"""
    try:
        if not field_values:
            st.warning("⚠️ No fields to update")
            return False
            
        with get_connection() as conn:
            with conn.cursor() as cur:
                set_clauses = []
                params = []
                
                for field, value in field_values.items():
                    set_clauses.append(f"{field} = %s")
                    params.append(value)
                        
                params.append(user_id)

                sql = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s"
                cur.execute(sql, tuple(params))
                
                if cur.rowcount > 0:
                    st.success(f"✅ User {user_id} updated successfully")
                    return True
                else:
                    st.warning(f"⚠️ No user found with ID: {user_id}")
                    return False
                    
    except pymysql.IntegrityError as e:
        if "Duplicate entry" in str(e) and "email" in str(e):
            st.error("❌ Email already exists. Please use a different email address.")
        else:
            st.error(f"❌ Database integrity error: {e}")
        return False
    except Exception as e:
        st.error(f"❌ Failed to update user: {e}")
        return False


def get_services_by_customer_email(customer_email):
    """Get all services for a specific customer by email with proper error handling"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM services WHERE customer_email = %s ORDER BY request_date DESC", 
                    (customer_email,)
                )
                services = cur.fetchall()
                
                # Process service_types JSON field for each service
                for service in services:
                    if isinstance(service.get('service_types'), str):
                        try:
                            service['service_types'] = json.loads(service['service_types'])
                        except json.JSONDecodeError:
                            service['service_types'] = []
                    elif service.get('service_types') is None:
                        service['service_types'] = []
                        
                return services
                
    except Exception as e:
        st.error(f"❌ Failed to fetch services for customer: {e}")
        return []


def get_service_statistics():
    """Get service statistics with proper error handling"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Total services
                cur.execute("SELECT COUNT(*) as total FROM services")
                total_services = cur.fetchone()['total']
                
                # Services by status
                cur.execute("SELECT status, COUNT(*) as count FROM services GROUP BY status")
                status_counts = cur.fetchall()
                
                # Total revenue (only completed payments)
                cur.execute("""
                    SELECT SUM(COALESCE(base_cost, 0) + COALESCE(extra_charges, 0)) as total_revenue 
                    FROM services WHERE payment_status = 'Done'
                """)
                revenue_result = cur.fetchone()
                total_revenue = revenue_result['total_revenue'] or 0
                
                # Pending revenue
                cur.execute("""
                    SELECT SUM(COALESCE(base_cost, 0) + COALESCE(extra_charges, 0)) as pending_revenue 
                    FROM services WHERE payment_status = 'Pending'
                """)
                pending_result = cur.fetchone()
                pending_revenue = pending_result['pending_revenue'] or 0
                
                return {
                    'total_services': total_services,
                    'status_counts': {item['status']: item['count'] for item in status_counts},
                    'total_revenue': total_revenue,
                    'pending_revenue': pending_revenue
                }
                
    except Exception as e:
        st.error(f"❌ Failed to fetch service statistics: {e}")
        return {
            'total_services': 0,
            'status_counts': {},
            'total_revenue': 0,
            'pending_revenue': 0
        }


def test_connection():
    """Test database connection"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                if result:
                    st.success("✅ Database connection test successful")
                    return True
                else:
                    st.error("❌ Database connection test failed")
                    return False
    except Exception as e:
        st.error(f"❌ Database connection test failed: {e}")
        return False