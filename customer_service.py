import streamlit as st
from datetime import datetime
from utils import (
    load_services,
    load_users,
    save_services,
    set_background_image,
    display_alert,
)

SERVICES_FILE = "services.json"

# Service prices configuration
SERVICE_PRICES = {
    "Oil Change": 500,
    "Engine Repair": 3000,
    "AC Service": 1500,
    "General Maintenance": 1000,
    "Chain Adjustment": 300,
    "Brake Check": 200
}

# Vehicle configuration
VEHICLE_CONFIG = {
    "Car": {
        "brands": ["Toyota", "Honda", "Hyundai"],
        "models": {
            "Toyota": ["Corolla", "Camry", "Fortuner"],
            "Honda": ["Civic", "Accord", "City"],
            "Hyundai": ["i20", "Creta", "Verna"]
        },
        "services": ["Oil Change", "Engine Repair", "AC Service", "General Maintenance"]
    },
    "Bike": {
        "brands": ["Yamaha", "Hero", "Bajaj"],
        "models": {
            "Yamaha": ["FZ", "R15", "MT-15"],
            "Hero": ["Splendor", "HF Deluxe", "Glamour"],
            "Bajaj": ["Pulsar", "Avenger", "Dominar"]
        },
        "services": ["Oil Change", "Chain Adjustment", "Brake Check", "General Maintenance"]
    }
}

def apply_custom_styles():
    """Apply consolidated custom CSS styles"""
    st.markdown("""
    <style>
        /* Global Text Color Fix */
        .stApp, .stApp *, div[data-testid="stSidebar"] * {
            color: #2c3e50 !important;
        }
        
        /* Input Fields */
        input[type="text"], input[type="email"], input[type="password"], 
        textarea, .stNumberInput input, .stDateInput input, .stTimeInput input {
            color: #2c3e50 !important;
            background-color: #f4f6f7 !important;
            border: 1px solid #ccc !important;
            border-radius: 8px !important;
            padding: 10px !important;
        }
        
        /* Selectbox */
        .stSelectbox > div > div > select {
            color: #2c3e50 !important;
            background-color: #f4f6f7 !important;
            border: 2px solid #667eea !important;
            border-radius: 10px !important;
            padding: 10px !important;
        }
        
        /* Buttons */
        .stFormSubmitButton > button {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            font-size: 1.1em !important;
            font-weight: 700 !important;
            padding: 15px 30px !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button {
            background: rgba(52, 73, 94, 0.9) !important;
            color: #ecf0f1 !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            padding: 12px 20px !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
        }
        
        /* Containers */
        .stForm {
            background: rgba(255, 255, 255, 0.05) !important;
            border-radius: 15px !important;
            padding: 25px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px) !important;
        }
        
        .service-container {
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 10px !important;
            padding: 20px !important;
            margin: 10px 0 !important;
            border: 1px solid rgba(102, 126, 234, 0.2) !important;
        }
        
        /* Multiselect */
        .stMultiselect > div > div {
            background: rgba(244, 246, 247, 0.95) !important;
            border-radius: 10px !important;
            border: 2px solid #667eea !important;
        }
        
        /* Progress Bar */
        .stProgress > div > div {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%) !important;
        }
    </style>
    """, unsafe_allow_html=True)

def create_styled_header(title, icon="🔧"):
    """Create a styled section header"""
    return f"""
    <div style="
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 25px 0 15px 0;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    ">
        <h2 style="color: #2c3e50; margin: 0; font-size: 2.2em; font-weight: 700;">
            {icon} {title}
        </h2>
    </div>
    """

def create_field_label(label, icon=""):
    """Create a styled field label"""
    return f"""
    <h3 style="color: #2c3e50; margin: 15px 0 10px 0; font-size: 1.1em; font-weight: 600;">
        {icon} {label}
    </h3>
    """

def create_metric_card(value, label, color):
    """Create a styled metric card"""
    return f"""
    <div style="
        background: linear-gradient(135deg, {color}0.2) 0%, {color}0.2) 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid {color}0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    ">
        <h2 style="color: {color.replace('rgba(', '').replace(', 0.2)', '')} !important; margin: 0; font-size: 2.5em; font-weight: bold;">{value}</h2>
        <p style="color: #2c3e50 !important; margin: 5px 0 0 0; font-weight: 600;">{label}</p>
    </div>
    """

def validate_form_data(vehicle_no, description, selected_services, pickup_required, pickup_address):
    """Validate form data and return list of errors"""
    errors = []
    
    if not vehicle_no.strip():
        errors.append("Vehicle number is required")
    if not description.strip():
        errors.append("Service description is required")
    if not selected_services:
        errors.append("Please select at least one service")
    if pickup_required == "Yes" and not pickup_address.strip():
        errors.append("Pickup address is required when pickup is selected")
    
    return errors

def render_service_form():
    """Render the service booking form"""
    st.markdown(create_styled_header("Request a Vehicle Service", "🛠️"), unsafe_allow_html=True)
    
    # Vehicle selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(create_field_label("Vehicle Type", "🚗"), unsafe_allow_html=True)
        vehicle_type = st.selectbox("Select Vehicle Type", ["Car", "Bike"], key="vehicle_type")
    
    with col2:
        st.markdown(create_field_label("Vehicle Brand", "🏭"), unsafe_allow_html=True)
        vehicle_brand = st.selectbox(
            "Select Vehicle Brand", 
            VEHICLE_CONFIG[vehicle_type]["brands"], 
            key="vehicle_brand"
        )
    
    # Model selection
    st.markdown(create_field_label("Vehicle Model", "🏷️"), unsafe_allow_html=True)
    vehicle_model = st.selectbox(
        "Select Vehicle Model", 
        VEHICLE_CONFIG[vehicle_type]["models"][vehicle_brand], 
        key="vehicle_model"
    )
    
    # Main form
    with st.form("vehicle_service_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(create_field_label("Vehicle Number", "🔢"), unsafe_allow_html=True)
            vehicle_no = st.text_input("", placeholder="Enter vehicle number", key="vehicle_no")
            
            st.markdown(create_field_label("Preferred Service Date", "📅"), unsafe_allow_html=True)
            service_date = st.date_input("", key="service_date")
        
        with col2:
            st.markdown(create_field_label("Pickup Required?", "🚚"), unsafe_allow_html=True)
            pickup_required = st.radio("", ["Yes", "No"], key="pickup_required")
        
        # Services selection
        st.markdown(create_field_label("Select Services", "⚙️"), unsafe_allow_html=True)
        selected_services = st.multiselect(
            "",
            VEHICLE_CONFIG[vehicle_type]["services"],
            key="selected_services"
        )
        
        # Display pricing
        if selected_services:
            st.markdown("### 💰 Service Pricing")
            total_cost = sum(SERVICE_PRICES.get(service, 0) for service in selected_services)
            
            for service in selected_services:
                cost = SERVICE_PRICES.get(service, 0)
                st.markdown(f"**{service}**: ₹{cost}")
            st.markdown(f"**Total Estimated Cost**: ₹{total_cost}")
        
        # Conditional pickup address
        pickup_address = ""
        if pickup_required == "Yes":
            st.markdown(create_field_label("Pickup Address", "📍"), unsafe_allow_html=True)
            pickup_address = st.text_area("", placeholder="Enter your pickup address", key="pickup_address")
        
        # Description
        st.markdown(create_field_label("Service Description", "📝"), unsafe_allow_html=True)
        description = st.text_area("", placeholder="Describe the issue or service required", key="description")
        
        # Submit button
        st.markdown("<br>", unsafe_allow_html=True)
        submit_booking = st.form_submit_button("🎉 Confirm Booking")
    
    # Handle form submission
    if submit_booking:
        errors = validate_form_data(vehicle_no, description, selected_services, pickup_required, pickup_address)
        
        if errors:
            error_message = "⚠️ Please fix the following errors:<br>• " + "<br>• ".join(errors)
            display_alert(error_message, "error")
        else:
            # Process successful booking
            process_booking(vehicle_type, vehicle_brand, vehicle_model, vehicle_no, 
                          selected_services, description, pickup_required, pickup_address, service_date)

def process_booking(vehicle_type, vehicle_brand, vehicle_model, vehicle_no, 
                   selected_services, description, pickup_required, pickup_address, service_date):
    """Process the booking submission"""
    services = load_services()
    users = load_users()
    
    customer_email = st.session_state.get("email", "guest@example.com")
    customer_user = next((u for u in users if u["email"] == customer_email), None)
    customer_name = customer_user.get("full_name", "Guest") if customer_user else "Guest"
    customer_phone = customer_user.get("phone", "N/A") if customer_user else "N/A"
    
    base_cost = sum(SERVICE_PRICES[s] for s in selected_services)
    service_id = len(services) + 1
    
    new_service = {
        "service_id": service_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "customer_phone": customer_phone,
        "vehicle_type": vehicle_type,
        "vehicle_brand": vehicle_brand,
        "vehicle_model": vehicle_model,
        "vehicle_no": vehicle_no,
        "service_types": selected_services,
        "description": description,
        "pickup_required": pickup_required,
        "pickup_address": pickup_address if pickup_required == "Yes" else "",
        "service_date": service_date.strftime("%Y-%m-%d"),
        "status": "Pending",
        "assigned_mechanic": None,
        "payment_status": "Pending",
        "progress": 0,
        "base_cost": base_cost,
        "extra_charges": 0,
        "charge_description": "",
        "admin_feedback": "",
        "work_done": "",
        "request_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    services.append(new_service)
    save_services(services)
    
    display_alert(f"🎉 Service request #{service_id} submitted successfully!", "success")
    st.balloons()
    
    # Service breakdown
    st.markdown("### 🔍 Service & Price Breakdown")
    for svc in selected_services:
        st.markdown(f"**{svc}**: ₹{SERVICE_PRICES[svc]}")
    st.markdown(f"**Total Base Cost**: ₹{base_cost}")
    
    # Payment button
    st.markdown("### 💳 Payment")
    if st.button("🔗 Proceed to Payment", use_container_width=True):
        st.info("Payment system integration coming soon!")

def render_service_history():
    """Render the service history page"""
    st.markdown(create_styled_header("Your Service History", "📋"), unsafe_allow_html=True)
    
    services = load_services()
    customer_email = st.session_state.get("email", "")
    user_services = [s for s in services if s["customer_email"] == customer_email]
    
    if not user_services:
        st.markdown("""
        <div style="
            background: rgba(52, 152, 219, 0.1);
            border: 2px solid #3498db;
            border-radius: 15px;
            padding: 30px;
            margin: 30px 0;
            text-align: center;
            color: #2980b9 !important;
            font-size: 1.2em;
            font-weight: 600;
        ">
            📋 No service requests found. Create your first service request!
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown(f"### Found {len(user_services)} service request(s)")
    
    # Render service cards
    for service in user_services:
        render_service_card(service)
    
    # Render summary statistics
    render_service_summary(user_services)

def render_service_card(service):
    """Render individual service card"""
    total_cost = service["base_cost"] + service["extra_charges"]
    
    status_colors = {
        "Pending": "🟡",
        "In Progress": "🟠", 
        "Completed": "🟢",
        "Cancelled": "🔴"
    }
    status_icon = status_colors.get(service["status"], "🟡")
    
    title = f"{status_icon} #{service['service_id']} — {service['vehicle_no']} — {service['status']}"
    if total_cost:
        title += f" — ₹{total_cost}"
    
    with st.expander(title):
        st.markdown('<div class="service-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🚗 Vehicle Information**")
            st.write(f"**Type:** {service['vehicle_type']}")
            st.write(f"**Brand:** {service['vehicle_brand']}")
            st.write(f"**Model:** {service['vehicle_model']}")
            st.write(f"**Number:** {service['vehicle_no']}")
            st.write("**Services:**")
            for svc in service["service_types"]:
                st.write(f"• {svc} (₹{SERVICE_PRICES.get(svc, 0)})")
        
        with col2:
            st.markdown("**⏰ Timeline & Status**")
            st.write(f"**Requested:** {service['request_date']}")
            st.write(f"**Service Date:** {service['service_date']}")
            st.write(f"**Progress:** {service['progress']}%")
            st.write(f"**Pickup:** {service['pickup_required']}")
            if service['pickup_address']:
                st.write(f"**Address:** {service['pickup_address']}")
            st.write(f"**Mechanic:** {service.get('assigned_mechanic', 'Not assigned')}")
        
        with col3:
            st.markdown("**💰 Billing Details**")
            st.write(f"**Base Cost:** ₹{service['base_cost']}")
            st.write(f"**Extra Charges:** ₹{service['extra_charges']}")
            if service.get("charge_description"):
                st.write(f"**Notes:** {service['charge_description']}")
            st.write(f"**Total:** ₹{total_cost}")
            
            if service['payment_status'] == "Pending" and total_cost > 0:
                display_alert(f"Payment Pending: ₹{total_cost}", "warning")
            elif service['payment_status'] == "Done":
                display_alert(f"Paid: ₹{total_cost}", "success")
        
        # Additional details
        if service.get("admin_feedback") or service.get("work_done"):
            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                if service.get("admin_feedback"):
                    st.markdown("**💬 Admin Feedback**")
                    st.write(service["admin_feedback"])
            with col_b:
                if service.get("work_done"):
                    st.markdown("**✅ Work Completed**")
                    st.write(service["work_done"])
        
        # Progress bar
        progress = service.get("progress", 0)
        if progress > 0:
            st.markdown("---")
            st.markdown("**📊 Service Progress**")
            st.progress(progress / 100)
            st.write(f"Progress: {progress}%")
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_service_summary(user_services):
    """Render service summary statistics"""
    st.markdown("---")
    st.markdown(create_styled_header("Service Summary", "📊"), unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            str(len(user_services)), 
            "Total Services", 
            "rgba(102, 126, 234"
        ), unsafe_allow_html=True)
    
    with col2:
        completed = len([s for s in user_services if s["status"] == "Completed"])
        st.markdown(create_metric_card(
            str(completed), 
            "Completed", 
            "rgba(46, 204, 113"
        ), unsafe_allow_html=True)
    
    with col3:
        pending = len([s for s in user_services if s["status"] == "Pending"])
        st.markdown(create_metric_card(
            str(pending), 
            "Pending", 
            "rgba(241, 196, 15"
        ), unsafe_allow_html=True)
    
    with col4:
        total_spent = sum(
            s["base_cost"] + s["extra_charges"]
            for s in user_services
            if s.get("payment_status") == "Done"
        )
        st.markdown(create_metric_card(
            f"₹{total_spent}", 
            "Total Spent", 
            "rgba(142, 68, 173"
        ), unsafe_allow_html=True)

def main():
    """Main application function"""
    st.set_page_config(page_title="Customer Dashboard", layout="wide")
    set_background_image()
    apply_custom_styles()
    
    # Load current user
    customer_email = st.session_state.get("email", "guest@example.com")
    users = load_users()
    customer_user = next((u for u in users if u["email"] == customer_email), None)
    customer_name = customer_user.get("full_name", "Guest") if customer_user else "Guest"
    
    # Main title
    st.markdown(f"""
    <div style="
        text-align: center;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    ">
        <h1 style="color: #2c3e50; margin: 0 0 10px 0; font-size: 3em; font-weight: 800;">
            🚗 Vehicle Service Dashboard
        </h1>
        <p style="color: #34495e; margin: 0; font-size: 1.4em; font-weight: 600;">
            Welcome {customer_name}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(102, 126, 234, 0.3);
        text-align: center;
    ">
        <h3 style="color: #2c3e50; margin: 0; font-size: 1.4em; font-weight: 700;">
            🎯 Menu
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.radio("Select Option", ["🛠️ Service Vehicle Form", "📋 Service History"])
    
    # Page routing
    if page == "🛠️ Service Vehicle Form":
        render_service_form()
    elif page == "📋 Service History":
        render_service_history()
    
    # Logout section
    st.markdown("---")
    st.markdown("""
    <div style="
        background: rgba(231, 76, 60, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid rgba(231, 76, 60, 0.3);
        text-align: center;
    ">
        <h4 style="color: #c0392b !important; margin: 0 0 10px 0; font-size: 1.2em; font-weight: 600;">
            🔐 Session Management
        </h4>
        <p style="color: #e74c3c !important; margin: 0; font-size: 0.95em;">
            Click below to securely logout from your account
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.page = "login"
            st.session_state.logged_in = False
            st.session_state.email = ""
            st.session_state.user_type = ""
            display_alert("👋 Successfully logged out! See you soon!", "success")
            st.rerun()

if __name__ == "__main__":
    main()