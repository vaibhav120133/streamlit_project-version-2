# users.py
import pymysql
from .connection import db_manager
from .exception_handler import db_exception_handler

class UserService:
    """Handles all user-related database operations."""

    @db_exception_handler
    def fetch_all_users(self):
        """Get all users ordered by name."""
        with db_manager.get_connection() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT id, full_name, email, phone, password, user_type
                FROM users
                ORDER BY full_name
            """)
            return cur.fetchall()

    @db_exception_handler
    def add_user(self, user_data):
        """Insert a new user."""
        with db_manager.get_connection() as conn, conn.cursor() as cur:
            try:
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
                    raise Exception("Email already exists.")
                else:
                    raise

    @db_exception_handler
    def get_user_by_email(self, email):
        """Retrieve a user by email."""
        with db_manager.get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cur.fetchone()
