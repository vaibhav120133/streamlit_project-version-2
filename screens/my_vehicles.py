import streamlit as st
from database.vehicles import VehicleService

def my_vehicles_page(user):
    """Enhanced My Vehicles page with filtering and search capabilities"""
    st.header("🚗 My Vehicles")
    
    # Fetch all vehicles for the user, assumed sorted by DB query
    vehicles = VehicleService().fetch_vehicles_by_user(user.id)
    
    if not vehicles:
        st.info("You have no vehicles registered.")
        st.markdown("---")
        st.info("💡 **Tip:** Add your first vehicle using the 'Add Vehicle' option in the sidebar.")
        return
    
    # Display vehicle summary
    _display_vehicle_summary(vehicles)
    
    # Filter and search options
    filtered_vehicles = _apply_filters_and_search(vehicles)
    
    if not filtered_vehicles:
        st.warning("No vehicles found matching your search criteria.")
        return
    
    # Display vehicles in one-line format without dropdown
    _display_vehicles_inline(filtered_vehicles)


def _display_vehicle_summary(vehicles):
    """Display summary statistics of user's vehicles"""
    total_vehicles = len(vehicles)
    bikes = [v for v in vehicles if v['vehicle_type'] == 'Bike']
    cars = [v for v in vehicles if v['vehicle_type'] == 'Car']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Vehicles", total_vehicles)
    with col2:
        st.metric("🏍️ Bikes", len(bikes))
    with col3:
        st.metric("🚗 Cars", len(cars))
    
    st.markdown("---")


def _apply_filters_and_search(vehicles):
    """Apply filtering and search functionality"""
    st.subheader("🔍 Filter & Search")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Vehicle type filter
        vehicle_types = ["All"] + sorted(set(v['vehicle_type'] for v in vehicles))
        selected_type = st.selectbox("Filter by Vehicle Type", vehicle_types)
    
    with col2:
        # Search by vehicle number
        search_query = st.text_input("Search by Vehicle Number", placeholder="Enter vehicle number...")
    
    # Apply filters
    filtered_vehicles = vehicles
    
    # Filter by vehicle type
    if selected_type != "All":
        filtered_vehicles = [v for v in filtered_vehicles if v['vehicle_type'] == selected_type]
    
    # Search by vehicle number
    if search_query.strip():
        q = search_query.strip().upper()
        filtered_vehicles = [v for v in filtered_vehicles if q in v['vehicle_no'].upper()]
    
    # If filtered by specific type, sort by brand/model/vehicle_no
    if selected_type != "All":
        filtered_vehicles = sorted(
            filtered_vehicles,
            key=lambda x: (x['vehicle_brand'], x['vehicle_model'], x['vehicle_no'])
        )
    
    # If "All" selected, assume DB returns sorted list, so no sorting here
    
    return filtered_vehicles


def _display_vehicles_inline(vehicles):
    """Display vehicles in one line with white background for each row, entire line bold"""
    st.subheader(f"📋 Your Vehicles ({len(vehicles)} found)")
    
    for vehicle in vehicles:
        emoji = _get_vehicle_emoji(vehicle['vehicle_type'])
        vehicle_info = f"{emoji} {vehicle['vehicle_brand']} - {vehicle['vehicle_model']} - {vehicle['vehicle_no']}"
        
        st.markdown(
            f"""
            <div style="
                background-color: white;
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            ">
                <strong>{vehicle_info}</strong>
            </div>
            """, unsafe_allow_html=True
        )

def _get_vehicle_emoji(vehicle_type):
    """Get emoji based on vehicle type"""
    return "🏍️" if vehicle_type == "Bike" else "🚗"
