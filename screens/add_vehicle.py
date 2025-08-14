import streamlit as st
from utils import display_alert
from database.vehicles import VehicleService

# Vehicle configuration data
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


def validate_vehicle_form(vehicle_no, vtype, brand, model):
    """Validate the vehicle form inputs"""
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


def add_vehicle_page(user):
    """Display the add vehicle page"""
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.header("➕ Add New Vehicle")
        # Vehicle type selection
        vtype = st.selectbox("Select Vehicle Type", list(VEHICLE_CONFIG.keys()))
        
        # Brand selection based on vehicle type
        brand = st.selectbox("Select Brand", VEHICLE_CONFIG[vtype]["brands"])
        
        # Model selection based on brand
        model = st.selectbox("Select Model", VEHICLE_CONFIG[vtype]["models"][brand])
        
        # Vehicle number input
        vehicle_no = st.text_input("Vehicle Number")

        # Add vehicle button
        if st.button("Add Vehicle"):
            errors = validate_vehicle_form(vehicle_no, vtype, brand, model)
            if errors:
                for error in errors:
                    display_alert(error, "error")
            else:
                vehicle_data = {
                    "user_id": user.id,
                    "vehicle_type": vtype,
                    "vehicle_brand": brand,
                    "vehicle_model": model,
                    "vehicle_no": vehicle_no.strip().upper(),
                }
                
                vehicle_id = VehicleService().add_users_vehicle(vehicle_data)
                
                if vehicle_id:
                    display_alert("🚗 Vehicle added successfully!", "success")
                    # Redirect to Book Service page
                    st.session_state["sidebar_choice"] = "Book Service"
                    st.rerun()
                else:
                    display_alert("❌ Failed to add vehicle. Vehicle number might already exist.", "error")


def get_vehicle_config():
    """Return the vehicle configuration dictionary"""
    return VEHICLE_CONFIG
