import streamlit as st
from datetime import datetime, date
from utils import (
    load_services,
    load_users,
    save_services,
    inject_global_css
)

SERVICES_FILE = "services.json"
USERS_FILE = "users.json"

def filter_services_by_date(services, start_date, end_date):
    """Filter services by request_date range"""
    filtered = []
    for service in services:
        if 'request_date' in service:
            try:
                # Extract date from request_date (format: "2025-07-09 12:02:45")
                service_date = datetime.strptime(service['request_date'].split()[0], "%Y-%m-%d").date()
                if start_date <= service_date <= end_date:
                    filtered.append(service)
            except Exception:
                continue
    return filtered

def filter_services_by_vehicle_number(services, vehicle_number):
    """Filter services by vehicle number (case-insensitive partial match)"""
    if not vehicle_number:
        return services
    filtered = []
    vehicle_number_lower = vehicle_number.lower()
    for service in services:
        if 'vehicle_no' in service:
            if vehicle_number_lower in service['vehicle_no'].lower():
                filtered.append(service)
    return filtered

def display_service_type(service):
    """Helper to display service type(s)"""
    service_type = service.get('service_type')
    service_types = service.get('service_types')
    if service_type:
        return service_type
    elif service_types:
        return ', '.join(service_types)
    else:
        return "N/A"

def service_detail_page(service_id):
    """Display detailed view of a specific service with enhanced styling"""
    services = load_services()
    service = next((s for s in services if s["service_id"] == service_id), None)
    if not service:
        st.error("Service not found!")
        return

    # Enhanced title
    st.markdown(f"""
    <h1 class="admin-title" style="color: #2c3e50;">
        🔧 Service Details
    </h1>
    <p class="admin-subtitle" style="color: #2c3e50;">
        Service ID: {service_id}
    </p>
    """, unsafe_allow_html=True)

    # Back button with enhanced styling
    if st.button("← Back to Dashboard", key="back_button"):
        st.session_state.current_service = None
        st.rerun()

    # Get customer details from service data
    customer_name = service.get('customer_name', 'Unknown')
    customer_email = service.get('customer_email', 'N/A')
    customer_phone = service.get('customer_phone', 'N/A')

    # Service Information Cards
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="service-card">
            <h3 class="section-header" style="color: #2c3e50;">👤 Customer Information</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px; margin: 10px 0;">
            <p style="color: #2c3e50;"><strong>🧑 Customer:</strong> {customer_name}</p>
            <p style="color: #2c3e50;"><strong>📧 Email:</strong> {customer_email}</p>
            <p style="color: #2c3e50;"><strong>📱 Phone:</strong> {customer_phone}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="service-card">
            <h3 class="section-header" style="color: #2c3e50;">🚗 Vehicle Information</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px; margin: 10px 0;">
            <p style="color: #2c3e50;"><strong>🚙 Vehicle Type:</strong> {service['vehicle_type']}</p>
            <p style="color: #2c3e50;"><strong>🏭 Brand:</strong> {service['vehicle_brand']}</p>
            <p style="color: #2c3e50;"><strong>🚗 Model:</strong> {service['vehicle_model']}</p>
            <p style="color: #2c3e50;"><strong>🔢 Vehicle No:</strong> {service['vehicle_no']}</p>
            <p style="color: #2c3e50;"><strong>🔧 Service Type:</strong> {display_service_type(service)}</p>
            <p style="color: #2c3e50;"><strong>📝 Description:</strong> {service['description']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="service-card">
            <h3 class="section-header" style="color: #2c3e50;">📊 Service Status</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px; margin: 10px 0;">
            <p style="color: #2c3e50;"><strong>📈 Status:</strong> {service['status']}</p>
            <p style="color: #2c3e50;"><strong>💳 Payment:</strong> {service.get('payment_status', 'Pending')}</p>
            <p style="color: #2c3e50;"><strong>🔧 Assigned Mechanic:</strong> {service.get('assigned_mechanic', 'Not Assigned')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="service-card">
            <h3 class="section-header" style="color: #2c3e50;">💰 Cost Information</h3>
        </div>
        """, unsafe_allow_html=True)
        
        base_cost = service.get('base_cost', 0)
        extra_charges = service.get('extra_charges', 0)
        total_cost = base_cost + extra_charges
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px; margin: 10px 0;">
            <p style="color: #2c3e50;"><strong>💵 Base Cost:</strong> ₹{base_cost}</p>
            <p style="color: #2c3e50;"><strong>➕ Extra Charges:</strong> ₹{extra_charges}</p>
            <p style="color: #2c3e50;"><strong>💰 Total Cost:</strong> ₹{total_cost}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Update Service Status, Progress and Assign Mechanic
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<h3 class="section-header" style="color: #2c3e50;">📈 Update Status</h3>', unsafe_allow_html=True)
        new_status = st.selectbox(
            "Service Status",
            ["Pending", "In Progress", "Completed", "Cancelled"],
            index=["Pending", "In Progress", "Completed", "Cancelled"].index(service['status']) if service['status'] in ["Pending", "In Progress", "Completed", "Cancelled"] else 0
        )

        if st.button("🔄 Update Status"):
            for s in services:
                if s["service_id"] == service_id:
                    s["status"] = new_status
            save_services(services)
            st.success("✅ Status and progress updated!")
            st.rerun()

    with col2:
        st.markdown('<h3 class="section-header" style="color: #2c3e50;">🔧 Assign Mechanic</h3>', unsafe_allow_html=True)
        mechanic_name = st.text_input(
            "Mechanic Name",
            value=service.get('assigned_mechanic', '')
        )
        if st.button("👨‍🔧 Assign Mechanic"):
            for s in services:
                if s["service_id"] == service_id:
                    s["assigned_mechanic"] = mechanic_name
            save_services(services)
            st.success("✅ Mechanic assigned!")
            st.rerun()

    with col3:
        st.markdown('<h3 class="section-header" style="color: #2c3e50;">💸 Add Extra Charges</h3>', unsafe_allow_html=True)
        new_extra_charge = st.number_input(
            "Extra Charges (₹)",
            min_value=0,
            value=extra_charges
        )
        charge_description = st.text_input(
            "Charge Description",
            value=service.get('charge_description', '')
        )
        if st.button("💰 Update Extra Charges"):
            for s in services:
                if s["service_id"] == service_id:
                    s["extra_charges"] = new_extra_charge
                    s["charge_description"] = charge_description
                    if 'base_cost' not in s:
                        s['base_cost'] = 0
            save_services(services)
            st.success("✅ Extra charges updated!")
            st.rerun()

    # Service Work Description
    st.markdown('<h3 class="section-header" style="color: #2c3e50;">📝 Work Description</h3>', unsafe_allow_html=True)
    current_work_done = service.get('work_done', '')

    work_description = st.text_area(
        "Work Done Description",
        value=current_work_done,
        height=100,
        help="Describe what work was performed"
    )
    if st.button("💾 Save Work Description"):
        for s in services:
            if s["service_id"] == service_id:
                s["work_done"] = work_description
        save_services(services)
        st.success("✅ Work description saved!")
        st.rerun()

    # Payment Management
    st.markdown('<h3 class="section-header" style="color: #2c3e50;">💳 Payment Management</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        payment_status = st.selectbox(
            "Payment Status",
            ["Pending", "Done"],
            index=["Pending", "Done"].index(service.get('payment_status', 'Pending'))
        )
        if st.button("💳 Update Payment Status"):
            for s in services:
                if s["service_id"] == service_id:
                    s["payment_status"] = payment_status
            save_services(services)
            st.success("✅ Payment status updated!")
            st.rerun()
    with col2:
        if service.get('payment_status', 'Pending') == 'Pending':
            st.error(f"⏳ Payment Pending: ₹{total_cost}")
        else:
            st.success(f"✅ Payment Completed: ₹{total_cost}")

def main():
    inject_global_css()

    # Enhanced title
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    ">
        <h1 style="color: #2c3e50; margin: 0;">⚙️ Admin Dashboard</h1>
        <p style="color: #34495e; margin: 10px 0 0 0;">Manage your vehicle services with ease</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display admin name
    admin_email = st.session_state.get("email", "Admin")

    # Get admin's full name from users.json
    users = load_users()
    admin_user = next((u for u in users if u["email"] == admin_email), None)
    admin_name = admin_user["full_name"] if admin_user and "full_name" in admin_user else admin_email

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    ">
        <h3 style="color: #2c3e50; margin: 0;">👋 Welcome back, {admin_name}</h3>
        <p style="color: #34495e; margin: 10px 0 0 0;">Ready to manage your services today?</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'current_service' not in st.session_state:
        st.session_state.current_service = None

    # Check if viewing specific service
    if st.session_state.current_service:
        service_detail_page(st.session_state.current_service)
        return

    services = load_services()

    st.markdown('<h2 class="section-header">🔍 Filter Services</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    color = "#2c3e50"  # Your custom color

    with col1:
        st.markdown(f'<span style="color:{color}; font-weight:600;">📅 Start Date</span>', unsafe_allow_html=True)
        start_date = st.date_input(
            "Start Date",
            value=date.today().replace(day=1),
            label_visibility="collapsed"
        )
    with col2:
        st.markdown(f'<span style="color:{color}; font-weight:600;">📅 End Date</span>', unsafe_allow_html=True)
        end_date = st.date_input(
            "End Date",
            value=date.today(),
            label_visibility="collapsed"
        )
    with col3:
        st.markdown(f'<span style="color:{color}; font-weight:600;">📊 Filter by Status</span>', unsafe_allow_html=True)
        status_filter = st.multiselect(
            "Filter by Status",
            ["All", "Pending", "In Progress", "Completed", "Cancelled"],
            default=["All"],
            label_visibility="collapsed"
        )
    with col4:
        st.markdown(f'<span style="color:{color}; font-weight:600;">🔍 Search by Vehicle Number</span>', unsafe_allow_html=True)
        vehicle_number_filter = st.text_input(
            "Search by Vehicle Number",
            placeholder="Enter vehicle number...",
            help="Search for services by vehicle number (partial match)",
            label_visibility="collapsed"
        )

    # Apply filters
    filtered_services = filter_services_by_date(services, start_date, end_date)
    if status_filter and "All" not in status_filter:
        filtered_services = [s for s in filtered_services if s['status'] in status_filter]
    if vehicle_number_filter:
        filtered_services = filter_services_by_vehicle_number(filtered_services, vehicle_number_filter)



    # Display services
    if filtered_services:
        st.write(f"<span style='color: #2c3e50'>Found {len(filtered_services)} services</span>", unsafe_allow_html=True)
        for service in filtered_services:
            customer_name = service.get('customer_name', 'Unknown')
            customer_email = service.get('customer_email', 'N/A')
            customer_phone = service.get('customer_phone', 'N/A')
            with st.expander(f"Service #{service['service_id']} - {customer_name} - {service['vehicle_no']} - {service['status']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"<span style='color: #2c3e50'>**Customer:** {customer_name}</span>", unsafe_allow_html=True)
                    st.write(f"<span style='color: #2c3e50'>**Email:** {customer_email}</span>", unsafe_allow_html=True)
                    st.write(f"<span style='color: #2c3e50'>**Phone:** {customer_phone}</span>", unsafe_allow_html=True)
                    st.write(f"<span style='color: #2c3e50'>**Vehicle:** {service['vehicle_type']} {service['vehicle_brand']} {service['vehicle_model']}</span>", unsafe_allow_html=True)
                    st.write(f"<span style='color: #2c3e50'>**Vehicle No:** {service['vehicle_no']}</span>", unsafe_allow_html=True)
                    st.write(f"<span style='color: #2c3e50'>**Service Type:** {display_service_type(service)}</span>", unsafe_allow_html=True)
                with col2:
                    st.write(f"<span style='color: #2c3e50'>**Service Date:** {service['service_date']}</span>", unsafe_allow_html=True)
                    st.write(f"<span style='color: #2c3e50'>**Request Date:** {service['request_date']}</span>", unsafe_allow_html=True)
                    st.write(f"<span style='color: #2c3e50'>**Status:** {service['status']}</span>", unsafe_allow_html=True)
                with col3:
                    st.write(f"<span style='color: #2c3e50'>**Payment Status:** {service.get('payment_status', 'Pending')}</span>", unsafe_allow_html=True)
                    st.write(f"<span style='color: #2c3e50'>**Pickup Required:** {service['pickup_required']}</span>", unsafe_allow_html=True)
                    st.write(f"<span style='color: #2c3e50'>**Total Cost:** ₹{service.get('base_cost', 0)}</span>", unsafe_allow_html=True)
                    if st.button(f"View Details", key=f"view_{service['service_id']}"):
                        st.session_state.current_service = service['service_id']
                        st.rerun()
    else:
        st.info("No services found for the selected filters.") 
        
    st.markdown("---")
    st.markdown("<h3 style='color: #2c3e50'>Quick Statistics</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div style='color: #2c3e50'><strong>Total Services</strong><br><span style='font-size: 24px'>{len(services)}</span></div>", unsafe_allow_html=True)
    with col2:
        completed = len([s for s in services if s['status'] == 'Completed'])
        st.markdown(f"<div style='color: #2c3e50'><strong>Completed Services</strong><br><span style='font-size: 24px'>{completed}</span></div>", unsafe_allow_html=True)
    with col3:
        pending = len([s for s in services if s['status'] == 'Pending'])
        st.markdown(f"<div style='color: #2c3e50'><strong>Pending Services</strong><br><span style='font-size: 24px'>{pending}</span></div>", unsafe_allow_html=True)
    with col4:
        total_revenue = sum(s.get('base_cost', 0) + s.get('extra_charges', 0) for s in services if s.get('payment_status') == 'Done')
        st.markdown(f"<div style='color: #2c3e50'><strong>Total Revenue</strong><br><span style='font-size: 24px'>₹{total_revenue}</span></div>", unsafe_allow_html=True)

    # Logout button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.page = "login"
            st.session_state.logged_in = False
            st.session_state.pop("email", None)
            st.session_state.pop("user_type", None)
            st.rerun()

if __name__ == "__main__":
    main()