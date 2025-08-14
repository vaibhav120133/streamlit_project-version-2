# connection.py
import pymysql
import streamlit as st

class DatabaseManager:
    """Handles MySQL connections using Streamlit secrets."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def get_connection(self):
        try:
            db = st.secrets["mysql"]
            return pymysql.connect(
                host=db["host"],
                user=db["user"],
                password=db["password"],
                database=db["database"],
                port=int(db.get("port", 3306)),
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
        except Exception as e:
            st.error(f"❌ Database connection failed: {e}")
            print(f"[DB ERROR] {e}")
            raise

db_manager = DatabaseManager()
