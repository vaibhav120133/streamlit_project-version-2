import streamlit as st
from datetime import datetime
from utils import inject_global_css, display_alert
from database import (
    fetch_all_users,
    fetch_vehicles_by_user,
    add_vehicle,
    save_service,
    get_services_by_customer_id,
    update_payment_status,
    get_service_by_id,
)

# Pricing dictionary for each service type
SERVICE_PRICES = {
    "Oil Change": 500,
    "Engine Repair": 3000,
    "AC Service": 1500,
    "General Maintenance": 1000,
    "Chain Adjustment": 300,
    "Brake Check": 200,
}

VEHICLE_CONFIG = {
    "Car": {
        "brands": ["Toyota", "Honda", "Hyundai"],
        "models": {
            "Toyota": ["Corolla", "Camry", "Fortuner"],
            "Honda": ["Civic", "Accord", "City"],
            "Hyundai": ["i20", "Creta", "Verna"],
        },
        "services": ["Oil Change", "Engine Repair", "AC Service", "General Maintenance"],
    },
    "Bike": {
        "brands": ["Yamaha", "Hero", "Bajaj"],
        "models": {
            "Yamaha": ["FZ", "R15", "MT-15"],
            "Hero": ["Splendor", "HF Deluxe", "Glamour"],
            "Bajaj": ["Pulsar", "Avenger", "Dominar"],
        },
        "services": ["Oil Change", "Chain Adjustment", "Brake Check", "General Maintenance"],
    }
}

class User:
    def __init__(self, data):
        self.id = data.get("id")
        self.full_name = data.get("full_name") or ""
        self.email = data.get("email") or ""
        self.phone = data.get("phone") or ""
        self.user_type = data.get("user_type", "Customer")


def validate_vehicle_form(vehicle_no, vtype, brand, model):
    errors = []
    if not vehicle_no.strip():
        errors.append("Vehicle number is required.")
    if vtype not in VEHICLE_CONFIG:
        errors.append("Invalid vehicle type selected.")
    if brand not in VEHICLE_CONFIG.get(vtype, {}).get("brands", []):
        errors.append("Invalid brand selected.")
    if model not in VEHICLE_CONFIG.get(vtype, {}).get("models", {}).get(brand, []):
        errors.append("Invalid model selected.")
    return errors


def validate_service_booking_form(selected_vehicle, selected_services, description, pickup_required, pickup_address):
    errors = []
    if not selected_vehicle:
        errors.append("Please select a vehicle.")
    if not selected_services:
        errors.append("Select at least one service.")
    if pickup_required == "Yes" and not pickup_address.strip():
        errors.append("Pickup address is required if pickup is selected.")
    return errors


def calculate_cost(service_types):
    return sum(SERVICE_PRICES.get(svc, 0) for svc in service_types)


class CustomerDashboard:
    def __init__(self, user):
        self.user = user

    def run(self):
        inject_global_css()
        st.title("🚗 Vehicle Service Dashboard")

        options = ["Add Vehicle", "Book Service", "Service History", "My Vehicles"]
        default_choice = st.session_state.get("sidebar_choice", "Add Vehicle")
        choice = st.sidebar.radio("Options", options, index=options.index(default_choice))
        st.session_state["sidebar_choice"] = choice

        if choice == "Add Vehicle":
            self.add_vehicle_page()
        elif choice == "Book Service":
            if st.session_state.get("booking_service_id"):
                self.show_service_detail_and_payment(st.session_state["booking_service_id"])
            else:
                self.book_service_page()
        elif choice == "Service History":
            self.service_history_page()
        elif choice == "My Vehicles":
            self.my_vehicles_page()

        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()

    def add_vehicle_page(self):
        st.header("➕ Add New Vehicle")
        vtype = st.selectbox("Select Vehicle Type", list(VEHICLE_CONFIG.keys()))
        brand = st.selectbox("Select Brand", VEHICLE_CONFIG[vtype]["brands"])
        model = st.selectbox("Select Model", VEHICLE_CONFIG[vtype]["models"][brand])
        vehicle_no = st.text_input("Vehicle Number")

        if st.button("Add Vehicle"):
            errors = validate_vehicle_form(vehicle_no, vtype, brand, model)
            if errors:
                for e in errors:
                    display_alert(e, "error")
            else:
                vehicle_data = {
                    "user_id": self.user.id,
                    "vehicle_type": vtype,
                    "vehicle_brand": brand,
                    "vehicle_model": model,
                    "vehicle_no": vehicle_no.strip().upper(),
                }
                vid = add_vehicle(vehicle_data)
                if vid:
                    display_alert("🚗 Vehicle added successfully!", "success")
                    # Redirect to Book Service page
                    st.session_state["sidebar_choice"] = "Book Service"
                    st.rerun()
                else:
                    display_alert("❌ Failed to add vehicle. Vehicle number might already exist.", "error")

    def book_service_page(self):
        st.header("🛠️ Book a Service")
        vehicles = fetch_vehicles_by_user(self.user.id)

        if not vehicles:
            st.info("You have no vehicles added. Please add a vehicle first.")
            return

        vehicle_map = {
            f"{v['vehicle_type']}-{v['vehicle_brand']}-{v['vehicle_model']}-({v['vehicle_no']})": v
            for v in vehicles
        }
        vehicle_choice = st.selectbox("Select Vehicle", list(vehicle_map.keys()))
        vehicle = vehicle_map[vehicle_choice]

        vtype = vehicle["vehicle_type"]
        available_services = VEHICLE_CONFIG.get(vtype, {}).get("services", [])
        selected_services = st.multiselect("Select Service Types", available_services)
        service_date = st.date_input("Preferred Service Date", datetime.today())
        pickup_required = st.radio("Pickup Required?", ["Yes", "No"], horizontal=True)
        pickup_address = ""
        if pickup_required == "Yes":
            pickup_address = st.text_area("Pickup Address", placeholder="Enter pickup address here")

        description = st.text_area("Service Description", placeholder="Enter description here").strip()

        if st.button("Submit Service Request"):
            errors = validate_service_booking_form(
                vehicle, selected_services, description, pickup_required, pickup_address
            )
            if errors:
                for e in errors:
                    display_alert(e, "error")
                return

            base_cost = calculate_cost(selected_services)
            new_service = {
                "customer_id": self.user.id,
                "vehicle_id": vehicle["vehicle_id"],
                "service_types": selected_services,
                "description": description.strip(),
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
            service_id = save_service(new_service)

            if service_id:
                st.session_state["booking_service_id"] = service_id
                st.session_state["booking_selected_services"] = selected_services
                st.session_state["booking_total_cost"] = base_cost
                st.session_state["booking_vehicle_no"] = vehicle["vehicle_no"]
                st.session_state["booking_vehicle_type"] = vehicle["vehicle_type"]
                st.session_state["booking_vehicle_brand"] = vehicle["vehicle_brand"]
                st.session_state["booking_vehicle_model"] = vehicle["vehicle_model"]
                st.session_state["booking_service_date"] = service_date.strftime("%Y-%m-%d")
                st.session_state["booking_description"] = description.strip()
                display_alert(f"🎉 Service request #{service_id} submitted successfully!", "success")
                st.rerun()
            else:
                display_alert("❌ Service booking failed.", "error")

    def show_service_detail_and_payment(self, service_id):
        service = get_service_by_id(service_id)
        if not service:
            st.error("❌ Service record not found.")
            del st.session_state["booking_service_id"]
            return
        base_c = service.get("base_cost", 0)
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
        st.write(f"**Base Cost:** ₹{base_c}")
        st.write(f"**Payment Status:** {service.get('payment_status')}")

        if st.button(f"💳 Pay ₹{base_c} Now"):
            success = update_payment_status(service_id, base_c)
            if success:
                display_alert("✅ Payment successful!", "success")
                del st.session_state["booking_service_id"]
                st.rerun()
            else:
                display_alert("❌ Payment failed. Please try again.", "error")

        if st.button("🔙 Back"):
            del st.session_state["booking_service_id"]
            st.rerun()

    def service_history_page(self):
        st.header("📋 My Service History")
        services = get_services_by_customer_id(self.user.id)

        if not services:
            st.info("No service history found.")
            return

        for s in services:
            extra_charge = s.get("extra_charges", 0)
            total_cost = s.get("base_cost", 0) + extra_charge
            payment_status = s.get("payment_status", "Pending")
            remain_amt = total_cost - s.get("Paid", 0)
            expanded_title = (
                f"Service #{s['service_id']} - {s.get('vehicle_no', 'N/A')} "
                f"- Status: {s.get('status', 'Unknown')} - "
                f"Payment: {payment_status} - Total: ₹{total_cost}"
            )
            with st.expander(expanded_title, expanded=False):
                st.write(
                    f"**Vehicle:** {s.get('vehicle_type', '')} - {s.get('vehicle_brand', '')} "
                    f" - {s.get('vehicle_model', '')} - ({s.get('vehicle_no', '')})"
                )
                st.write(f"**Service Types:** {', '.join(s.get('service_types', []))}")
                st.write(f"**Description:** {s.get('description')}")
                st.write(f"**Pickup Required:** {s.get('pickup_required')}")
                if s.get("pickup_address"):
                    st.write(f"**Pickup Address:** {s.get('pickup_address')}")
                st.write(f"**Service Date:** {s.get('service_date')}")
                st.write(f"**Status:** {s.get('status')}")
                st.write(f"**Work Description:** {s.get('work_done') or 'Not updated'}")
                if extra_charge > 0:
                    st.write(f"**Extra Cost:** ₹{extra_charge}")
                    st.write(f"**Extra charge reason:** {s.get('charge_description')}")
                st.write(f"**Total Cost:** ₹{total_cost}")
                st.write(f"**Paid Amount:** ₹{s.get('Paid')}")

                if payment_status == "Pending":
                    if st.button(f"💳 Pay ₹{remain_amt} Now", key=f"pay_{s['service_id']}"):
                        if update_payment_status(s["service_id"], total_cost):
                            display_alert("✅ Payment successful!", "success")
                            st.rerun()
                        else:
                            display_alert("❌ Payment failed. Please try again.", "error")
                elif payment_status == "Done":
                    st.success("✅ Payment Completed")

    def my_vehicles_page(self):
        st.header("🚗 My Vehicles")
        vehicles = fetch_vehicles_by_user(self.user.id)
        if not vehicles:
            st.info("You have no vehicles registered.")
            return
        for v in vehicles:
            st.write(f"- {v['vehicle_type']} - {v['vehicle_brand']} - {v['vehicle_model']} - {v['vehicle_no']}")


def main():
    inject_global_css()
    users = fetch_all_users()
    email = st.session_state.get("email")
    user_data = next((u for u in users if u["email"] == email), None)
    if not user_data:
        st.error("User not found. Please log in again.")
        return
    user = User(user_data)

    dashboard = CustomerDashboard(user)
    dashboard.run()


if __name__ == "__main__":
    main()
