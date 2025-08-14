# mechanics.py
import streamlit as st
from .connection import db_manager
from .exception_handler import db_exception_handler

class MechanicService:

    @db_exception_handler
    def fetch_all_mechanics(self):
        with db_manager.get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM mechanics ORDER BY mechanic_name")
            return cur.fetchall()
