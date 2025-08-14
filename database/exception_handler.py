# exception_handler.py
import streamlit as st
import traceback
import sys

def db_exception_handler(func):
    """Decorator to handle database exceptions and log them."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"❌ Error in {func.__name__}: {e}")
            
            print("\n" + "="*40)
            print(f"[ERROR] Function: {func.__name__}")
            print("Exception Type:", type(e).__name__)
            print("Error Message:", str(e))
            print("Traceback:")
            traceback.print_exc(file=sys.stdout)
            print("="*40 + "\n")
            return None
    return wrapper
