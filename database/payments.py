# payments.py
from .connection import db_manager
from .exception_handler import db_exception_handler

class PaymentService:
    
    @db_exception_handler
    def update_payment_status(self, service_id, paid_amt):
        with db_manager.get_connection() as conn, conn.cursor() as cur:
            cur.execute("""
                UPDATE services
                SET payment_status = %s, Paid = %s
                WHERE service_id = %s
            """, ("Done", paid_amt, service_id))
            return cur.rowcount > 0
