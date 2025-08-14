import streamlit as st
from utils import global_css
from database.users import UserService
from screens.add_vehicle import add_vehicle_page, get_vehicle_config
from screens.book_service import book_service_page, show_service_detail_and_payment
from screens.service_history import service_history_page_with_summary
from screens.my_vehicles import my_vehicles_page

# Get vehicle configuration from the add_vehicle module
VEHICLE_CONFIG = get_vehicle_config()


class User:
    def __init__(self, data):
        self.id = data.get("id")
        self.full_name = data.get("full_name") or ""
        self.email = data.get("email") or ""
        self.phone = data.get("phone") or ""
        self.user_type = data.get("user_type", "Customer")


class CustomerDashboard:
    def __init__(self, user):
        self.user = user

    def run(self):
        global_css()
        st.title("🚗 Vehicle Service Dashboard")

        options = ["Add Vehicle", "Book Service", "Service History", "My Vehicles"]
        default_choice = st.session_state.get("sidebar_choice", "Add Vehicle")
        choice = st.sidebar.radio("Options", options, index=options.index(default_choice))
        st.session_state["sidebar_choice"] = choice

        if choice == "Add Vehicle":
            add_vehicle_page(self.user)
        elif choice == "Book Service":
            if st.session_state.get("booking_service_id"):
                # Show service detail and payment page
                show_service_detail_and_payment(st.session_state["booking_service_id"])
            else:
                # Show book service page
                book_service_page(self.user, VEHICLE_CONFIG)
        elif choice == "Service History":
            service_history_page_with_summary(self.user)
        elif choice == "My Vehicles":
            my_vehicles_page(self.user)
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            print(f"[LOGOUT] {st.session_state.get('user_type', 'Unknown')} logged out: {st.session_state.get('email', 'Unknown')}")
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()


def main():
    global_css()
    users = UserService().fetch_all_users()
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