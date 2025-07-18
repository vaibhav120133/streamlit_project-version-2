import streamlit as st
from datetime import datetime
from utils import (
    load_services,
    load_users,
    save_services,
    inject_global_css,
    display_alert,
)

SERVICE_PRICES = {
    "Oil Change": 500,
    "Engine Repair": 3000,
    "AC Service": 1500,
    "General Maintenance": 1000,
    "Chain Adjustment": 300,
    "Brake Check": 200
}

VEHICLE_CONFIG = {
    "Car": {
        "brands": ["Toyota", "Honda", "Hyundai"],
        "models": {
            "Toyota": ["Corolla", "Camry", "Fortuner"],
            "Honda": ["Civic", "Accord", "City"],
            "Hyundai": ["i20", "Creta", "Verna"],
        },
        "services": ["Oil Change", "Engine Repair", "AC Service", "General Maintenance"]
    },
    "Bike": {
        "brands": ["Yamaha", "Hero", "Bajaj"],
        "models": {
            "Yamaha": ["FZ", "R15", "MT-15"],
            "Hero": ["Splendor", "HF Deluxe", "Glamour"],
            "Bajaj": ["Pulsar", "Avenger", "Dominar"],
        },
        "services": ["Oil Change", "Chain Adjustment", "Brake Check", "General Maintenance"]
    }
}

def validate_form_data(vehicle_no, description, selected_services, pickup_required, pickup_address):
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

def render_booking_summary(service_id, selected_services, total_cost):
    vehicle_no = st.session_state.get('vehicle_no', '')
    service_date = st.session_state.get('service_date', '')
    vehicle_type = st.session_state.get('vehicle_type', '')
    vehicle_brand = st.session_state.get('vehicle_brand', '')
    vehicle_model = st.session_state.get('vehicle_model', '')
    description = st.session_state.get('description', '')

    st.success("🎉 Booking Confirmed!")
    st.markdown(f"""
**Service ID:** #{service_id}  
**Vehicle Number:** {vehicle_no}  
**Vehicle Type:** {vehicle_type}  
**Brand:** {vehicle_brand}  
**Model:** {vehicle_model}  
**Service Date:** {service_date}

**Service Description:**  
{description}
    """)
    st.markdown("### Service Charges Breakdown")
    for i, service in enumerate(selected_services):
        price = SERVICE_PRICES.get(service, 0)
        st.write(f"- {service}: ₹{price}")
    st.markdown(f"**Total Amount:** ₹{total_cost}")

def handle_payment(service_id):
    services = load_services()
    for service in services:
        if service["service_id"] == service_id:
            service["payment_status"] = "Done"
            break
    save_services(services)

def render_payment_success_page():
    service_id = st.session_state.get('pending_service_id')
    handle_payment(service_id) # Mark payment as Done

    st.title("💳 Payment Successful!")
    st.success("✅ Payment Completed Successfully! Your service booking has been confirmed and payment has been processed.")
    st.balloons()

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🏠 Home", key="payment_success_home"):
            clear_payment_and_booking_state()
            st.session_state.page = "🛠️ Service Vehicle Form"
            st.rerun()
    with col2:
        if st.button("🔙 Go Back", key="payment_success_goback"):
            clear_payment_and_booking_state()
            st.rerun()
    with col3:
        if st.button("🚪 Logout", key="payment_success_logout"):
            clear_payment_and_booking_state()
            st.session_state.page = "login"
            st.session_state.logged_in = False
            st.session_state.email = ""
            st.session_state.user_type = ""
            display_alert("👋 Successfully logged out! See you soon!", "success")
            st.rerun()

def clear_payment_and_booking_state():
    for key in [
        'booking_completed', 'payment_pending', 'payment_completed', 'current_service_id', 
        'selected_services', 'total_cost', 'vehicle_no', 'service_date', 'vehicle_type', 
        'vehicle_brand', 'vehicle_model', 'description', 'show_payment_page', 'pending_service_id'
    ]:
        if key in st.session_state:
            del st.session_state[key]

def render_service_form():
    st.header("🛠️ Request a Vehicle Service")

    if st.session_state.get('payment_completed', False):
        st.success(
            "✅ Payment Completed Successfully! Your service booking has been confirmed and payment has been processed."
        )
        st.info("You can now make a new booking below.")
        st.session_state['payment_completed'] = False

    # Show booking summary if booking done and payment pending
    if st.session_state.get('booking_completed', False) and st.session_state.get('payment_pending', False):
        service_id = st.session_state.get('current_service_id')
        selected_services = st.session_state.get('selected_services', [])
        total_cost = st.session_state.get('total_cost', 0)

        render_booking_summary(service_id, selected_services, total_cost)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💳 Proceed to Payment", key="btn_proceed_payment"):
                st.session_state['show_payment_page'] = True
                st.session_state['pending_service_id'] = service_id
                st.session_state['booking_completed'] = False
                st.session_state['payment_pending'] = False
                st.rerun()
                return

        st.markdown("---")
        with col2:
            if st.button("🆕 Create New Booking", key="btn_create_new_booking"):
                clear_payment_and_booking_state()
                st.rerun()
        return

    # Normal form display
    col1, col2 = st.columns(2)

    with col1:
        vehicle_type = st.selectbox("🚗 Vehicle Type", list(VEHICLE_CONFIG.keys()), key='select_vehicle_type')
        vehicle_brand = st.selectbox("🏭 Vehicle Brand",
                                     VEHICLE_CONFIG[vehicle_type]["brands"], key='select_vehicle_brand')
        vehicle_model = st.selectbox("🏷️ Vehicle Model",
                                    VEHICLE_CONFIG[vehicle_type]["models"][vehicle_brand], key='select_vehicle_model')
        vehicle_no = st.text_input("🔢 Vehicle Number", placeholder="Enter vehicle number", key='input_vehicle_no')
        service_date = st.date_input("📅 Preferred Service Date", key='input_service_date')

    with col2:
        pickup_required = st.radio("🚚 Pickup Required?", ["Yes", "No"], horizontal=True, key='input_pickup_required')
        selected_services = st.multiselect(
            "⚙️ Select Services",
            VEHICLE_CONFIG[vehicle_type]["services"],
            key='input_selected_services'
        )
        pickup_address = ""
        if pickup_required == "Yes":
            pickup_address = st.text_area("📍 Pickup Address", placeholder="Enter your pickup address", key='input_pickup_address')
        description = st.text_area("📝 Service Description", placeholder="Describe the issue or service required", key='input_description')

    if st.button("🎉 Confirm Booking", key="btn_confirm_booking"):
        errors = validate_form_data(vehicle_no, description, selected_services, pickup_required, pickup_address)
        if errors:
            display_alert("⚠️ Please fix the following errors:<br>• " + "<br>• ".join(errors), "error")
        else:
            process_booking(vehicle_type, vehicle_brand, vehicle_model, vehicle_no,
                           selected_services, description, pickup_required, pickup_address, service_date)

def process_booking(vehicle_type, vehicle_brand, vehicle_model, vehicle_no,
                   selected_services, description, pickup_required, pickup_address, service_date):
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
        "base_cost": base_cost,
        "work_done": "",
        "request_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    services.append(new_service)
    save_services(services)

    # Set session state to show booking summary
    st.session_state['booking_completed'] = True
    st.session_state['payment_pending'] = True
    st.session_state['current_service_id'] = service_id
    st.session_state['selected_services'] = selected_services
    st.session_state['total_cost'] = base_cost
    st.session_state['vehicle_no'] = vehicle_no
    st.session_state['service_date'] = service_date.strftime("%Y-%m-%d")
    st.session_state['vehicle_type'] = vehicle_type
    st.session_state['vehicle_brand'] = vehicle_brand
    st.session_state['vehicle_model'] = vehicle_model
    st.session_state['description'] = description

    display_alert(f"🎉 Service request #{service_id} submitted successfully!", "success")
    st.rerun()

def render_service_history():
    st.header("📋 Your Service History")
    services = load_services()
    customer_email = st.session_state.get("email", "")
    user_services = [s for s in services if s["customer_email"] == customer_email]

    if not user_services:
        st.info("📋 No service requests found. Create your first service request!")
        return

    st.write(f"### Found {len(user_services)} service request(s)")

    for service in user_services:
        render_service_card(service)

def render_service_card(service):
    total_cost = service["base_cost"]
    status_colors = {
        "Pending": "🟡",
        "In Progress": "🟠",
        "Completed": "🟢",
        "Cancelled": "🔴"
    }
    status_icon = status_colors.get(service["status"], "🟡")
    title = f"{status_icon} #{service['service_id']} — {service['vehicle_no']} — {service['status']} — ₹{total_cost}"

    with st.expander(title, expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🚗 Vehicle Info")
            st.write(f"Type: {service['vehicle_type']}")
            st.write(f"Brand: {service['vehicle_brand']}")
            st.write(f"Model: {service['vehicle_model']}")
            st.write(f"Number: {service['vehicle_no']}")

            st.subheader("📝 Service Description")
            st.write(service.get('description', 'No description provided'))

            st.subheader("🚚 Pickup Info")
            st.write(f"Pickup Required: {service['pickup_required']}")
            if service.get('pickup_address'):
                st.write(f"Pickup Address: {service['pickup_address']}")

        with col2:
            st.subheader("⏰ Timeline & Status")
            st.write(f"Requested: {service['request_date']}")
            st.write(f"Service Date: {service['service_date']}")
            st.write(f"Status: {service['status']}")
            st.write(f"Mechanic: {service.get('assigned_mechanic', 'Not assigned')}")

            if service.get('work_done'):
                st.subheader("🔧 Work Done")
                st.write(service['work_done'])

        st.subheader("⚙️ Services Requested")
        for svc in service["service_types"]:
            price = SERVICE_PRICES.get(svc, 0)
            st.write(f"- {svc}: ₹{price}")

        st.markdown("---")
        col1, col2, _ = st.columns([2, 2, 1])

        with col1:
            st.subheader("💰 Billing Details")
            st.write(f"Total Cost: ₹{total_cost}")

        with col2:
            st.subheader("💳 Payment Status")
            if service['payment_status'] == "Pending" and total_cost > 0:
                st.warning(f"⏳ Payment Pending — ₹{total_cost}")
            elif service['payment_status'] == "Done":
                st.success(f"✅ Payment Complete — ₹{total_cost}")
            else:
                st.info("⚪ No Payment Due")

def render_logout_section():
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Logout", key="logout_main_section"):
            st.session_state.page = "login"
            st.session_state.logged_in = False
            st.session_state.email = ""
            st.session_state.user_type = ""
            clear_payment_and_booking_state()
            display_alert("👋 Successfully logged out! See you soon!", "success")
            st.rerun()

def main():
    inject_global_css()  

    customer_email = st.session_state.get("email", "guest@example.com")
    users = load_users()
    customer_user = next((u for u in users if u["email"] == customer_email), None)
    customer_name = customer_user.get("full_name", "Guest") if customer_user else "Guest"

    if st.session_state.get('show_payment_page', False):
        render_payment_success_page()
        return

    st.title("🚗 Vehicle Service Dashboard")
    st.markdown(
        f"""
        <h1 style='text-align: center; font-size: 2em;'>
            Welcome {customer_name}
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.header("🎯 Menu")
    page = st.sidebar.radio("Select Option", ["🛠️ Service Vehicle Form", "📋 Service History"], key='sidebar_menu')

    if page == "🛠️ Service Vehicle Form":
        render_service_form()
    elif page == "📋 Service History":
        render_service_history()

    render_logout_section()

if __name__ == "__main__":
    main()
