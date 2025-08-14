import streamlit as st
from datetime import datetime
from utils import display_alert
from database.vehicles import VehicleService
from database.services import ServiceManager
from database.payments import PaymentService


# Pricing dictionary for each service type
SERVICE_PRICES = {
    "Oil Change": 500,
    "Engine Repair": 3000,
    "AC Service": 1500,
    "General Maintenance": 1000,
    "Chain Adjustment": 300,
    "Brake Check": 200,
}


def validate_service_booking_form(selected_vehicle, selected_services, pickup_required, pickup_address):
    """Validate the service booking form inputs"""
    errors = []
    if not selected_vehicle:
        errors.append("Please select a vehicle.")
    if not selected_services:
        errors.append("Select at least one service.")
    if pickup_required == "Yes" and not pickup_address.strip():
        errors.append("Pickup address is required if pickup is selected.")
    return errors


def calculate_cost(service_types):
    """Calculate total cost for selected services"""
    return sum(SERVICE_PRICES.get(svc, 0) for svc in service_types)


def book_service_page(user, vehicle_config):
    """Display the book service page"""
    st.header("🛠️ Book a Service")
    vehicles = VehicleService().fetch_vehicles_by_user(user.id)

    if not vehicles:
        st.info("You have no vehicles added. Please add a vehicle first.")
        return

    # Vehicle selection
    vehicle_map = {
        f"{v['vehicle_type']}-{v['vehicle_brand']}-{v['vehicle_model']}-({v['vehicle_no']})": v
        for v in vehicles
    }
    vehicle_choice = st.selectbox("Select Vehicle", list(vehicle_map.keys()))
    vehicle = vehicle_map[vehicle_choice]

    # Service selection based on vehicle type
    vtype = vehicle["vehicle_type"]
    available_services = vehicle_config.get(vtype, {}).get("services", [])
    service_labels = [
        f"{svc} (₹{SERVICE_PRICES.get(svc, 0)})" for svc in available_services
    ]
    selected_labels = st.multiselect("Select Service Types", service_labels)
    selected_services = [
        available_services[service_labels.index(lbl)]
        for lbl in selected_labels if lbl in service_labels
    ]
    
    # Service date selection
    service_date = st.date_input("Preferred Service Date", datetime.today())
    
    # Pickup options
    pickup_required = st.radio("Pickup Required?", ["Yes", "No"], horizontal=True)
    pickup_address = ""
    if pickup_required == "Yes":
        pickup_address = st.text_area("Pickup Address", placeholder="Enter pickup address here")

    # Service description
    description = st.text_area("Service Description", placeholder="Enter description here").strip()

    # Submit service request
    if st.button("Submit Service Request"):
        errors = validate_service_booking_form(
            vehicle, selected_services, description, pickup_required, pickup_address
        )
        if errors:
            for error in errors:
                display_alert(error, "error")
            return

        base_cost = calculate_cost(selected_services)
        new_service = {
            "customer_id": user.id,
            "vehicle_id": vehicle["vehicle_id"],
            "service_types": selected_services,
            "description": description,
            "pickup_required": pickup_required,
            "pickup_address": pickup_address.strip() if pickup_required == "Yes" else None,
            "service_date": service_date.strftime("%Y-%m-%d"),
            "status": "Pending",
            "payment_status": "Pending",
            "base_cost": base_cost,
            "extra_charges": 0,
            "charge_description": "",
            "work_done": "",
            "request_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        service_id = ServiceManager().save_service(new_service)

        if service_id:
            # Save individual service types
            for svc in selected_services:
                service_type_data = {
                    'service_id': service_id,
                    'service_name': svc,
                    'price': SERVICE_PRICES.get(svc, 0)
                }
                sm = ServiceManager()
                service_type_id = sm.save_service_type(service_type_data)
                if not service_type_id:
                    display_alert(f"❌ Failed to save service type '{svc}'", "error")

        if service_id:
            st.session_state["booking_service_id"] = service_id
            display_alert(f"🎉 Service request #{service_id} submitted successfully!", "success")
            st.rerun()
        else:
            display_alert("❌ Service booking failed.", "error")


def show_service_detail_and_payment(service_id):
    """Display service details and handle payment"""
    service = ServiceManager().get_services_by_customer_id(service_id)
    if not service:
        st.error("❌ Service record not found.")
        if "booking_service_id" in st.session_state:
            del st.session_state["booking_service_id"]
        return

    base_cost = service.get("base_cost", 0)
    
    # Display service confirmation details
    st.subheader(f"🎉 Booking Confirmed!")
    st.subheader(f"Service ID: #{service_id}")
    
    st.write(
        f"**Vehicle:** {service.get('vehicle_type', '')} - {service.get('vehicle_brand', '')} "
        f" - {service.get('vehicle_model', '')} - ({service.get('vehicle_no', '')})"
    )
    st.write(f"**Service Date:** {service.get('service_date')}")
    st.write(f"**Services Requested:** {', '.join(service.get('service_types', []))}")
    st.write(f"**Description:** {service.get('description')}")
    st.write(f"**Pickup Required:** {service.get('pickup_required')}")
    
    if service.get("pickup_address"):
        st.write(f"**Pickup Address:** {service.get('pickup_address')}")
    
    st.write(f"**Base Cost:** ₹{base_cost}")
    st.write(f"**Payment Status:** {service.get('payment_status')}")

    # Payment button
    if st.button(f"💳 Pay ₹{base_cost} Now"):
        success = PaymentService().update_payment_status(service_id, base_cost)
        if success:
            display_alert("✅ Payment successful!", "success")
            if "booking_service_id" in st.session_state:
                del st.session_state["booking_service_id"]
            st.rerun()
        else:
            display_alert("❌ Payment failed. Please try again.", "error")

    # Back button
    if st.button("🔙 Back"):
        if "booking_service_id" in st.session_state:
            del st.session_state["booking_service_id"]
        st.rerun()


def get_service_prices():
    """Return the service prices dictionary"""
    return SERVICE_PRICES