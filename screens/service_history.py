import streamlit as st
from utils import display_alert
from database.services import ServiceManager
from database.payments import PaymentService


def _display_service_details(service, total_cost, paid_amount, remaining_amount, payment_status):
    """Display detailed information for a single service"""
    # Vehicle Information
    st.write(
        f"**Vehicle:** {service.get('vehicle_type', '')} - {service.get('vehicle_brand', '')} "
        f"- {service.get('vehicle_model', '')} - ({service.get('vehicle_no', '')})"
    )
    
    # Service Information
    st.write(f"**Service Types:** {', '.join(service.get('service_types', []))}")
    st.write(f"**Description:** {service.get('description', 'No description provided')}")
    st.write(f"**Service Date:** {service.get('service_date', 'Not specified')}")
    st.write(f"**Status:** {service.get('status', 'Unknown')}")
    
    # Pickup Information
    st.write(f"**Pickup Required:** {service.get('pickup_required', 'No')}")
    if service.get("pickup_address"):
        st.write(f"**Pickup Address:** {service.get('pickup_address')}")
    
    # Work Details
    work_done = service.get('work_done')
    if work_done and work_done.strip():
        st.write(f"**Work Description:** {work_done}")
    else:
        st.write(f"**Work Description:** Not updated")
    
    # Cost Breakdown
    base_cost = service.get("base_cost", 0)
    extra_charges = service.get("extra_charges", 0)
    
    st.write(f"**Base Cost:** ₹{base_cost}")
    
    if extra_charges > 0:
        st.write(f"**Extra Charges:** ₹{extra_charges}")
        charge_description = service.get('charge_description', 'No description provided')
        st.write(f"**Extra Charge Reason:** {charge_description}")
    
    st.write(f"**Total Cost:** ₹{total_cost}")
    st.write(f"**Paid Amount:** ₹{paid_amount}")
    
    if remaining_amount > 0:
        st.write(f"**Remaining Amount:** ₹{remaining_amount}")
    
    # Payment Section
    _display_payment_section(service, payment_status, remaining_amount)


def _display_payment_section(service, payment_status, remaining_amount):
    """Handle payment display and processing"""
    service_id = service['service_id']
    
    if payment_status == "Pending" and remaining_amount > 0:
        # Show payment button for pending payments
        if st.button(f"💳 Pay ₹{remaining_amount} Now", key=f"pay_{service_id}"):
            success = PaymentService().update_payment_status(service_id, remaining_amount)
            if success:
                display_alert("✅ Payment successful!", "success")
                st.rerun()
            else:
                display_alert("❌ Payment failed. Please try again.", "error")
    
    elif payment_status == "Done":
        # Show completed payment status
        st.success("✅ Payment Completed")
    
    elif payment_status == "Partial":
        # Show partial payment status (if applicable)
        st.warning(f"⚠️ Partial Payment - Remaining: ₹{remaining_amount}")
        if st.button(f"💳 Pay Remaining ₹{remaining_amount}", key=f"pay_remaining_{service_id}"):
            success = PaymentService().update_payment_status(service_id, remaining_amount)
            if success:
                display_alert("✅ Payment completed!", "success")
                st.rerun()
            else:
                display_alert("❌ Payment failed. Please try again.", "error")


def service_history_page_with_summary(user):
    """Service history page with summary statistics"""
    st.header("📋 My Service History")
    
    # Then display detailed history
    services = ServiceManager().get_services_by_customer_id(user.id)
    
    if not services:
        st.info("No service history found.")
        return
    
    # Filter options
    with st.expander("🔍 Filter Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            status_filter = st.selectbox(
                "Filter by Status", 
                ["All", "Pending", "In Progress", "Completed", "Cancelled"]
            )
        
        with col2:
            payment_filter = st.selectbox(
                "Filter by Payment", 
                ["All", "Pending", "Done", "Partial"]
            )
    
    # Apply filters
    filtered_services = services
    if status_filter != "All":
        filtered_services = [s for s in filtered_services if s.get('status') == status_filter]
    if payment_filter != "All":
        filtered_services = [s for s in filtered_services if s.get('payment_status') == payment_filter]
    
    if not filtered_services:
        st.info(f"No services found matching the selected filters.")
        return
    
    st.write(f"Showing {len(filtered_services)} of {len(services)} services")
    
    # Display filtered services
    for service in filtered_services:
        extra_charge = service.get("extra_charges", 0)
        total_cost = service.get("base_cost", 0) + extra_charge
        payment_status = service.get("payment_status", "Pending")
        paid_amount = service.get("Paid", 0)
        remaining_amount = total_cost - paid_amount
        
        expanded_title = (
            f"Service #{service['service_id']} - {service.get('vehicle_no', 'N/A')} "
            f"- Status: {service.get('status', 'Unknown')} - "
            f"Payment: {payment_status} - Total: ₹{total_cost}"
        )
        
        with st.expander(expanded_title, expanded=False):
            _display_service_details(service, total_cost, paid_amount, remaining_amount, payment_status)