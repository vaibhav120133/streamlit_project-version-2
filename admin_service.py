import streamlit as st
from datetime import datetime, date
from utils import (
    load_services,
    save_services,
    load_users,
    inject_global_css
)

SERVICES_FILE = "services.json"
USERS_FILE = "users.json"

# ----------- DATA MODEL CLASSES -----------

class Service:
    def __init__(self, data):
        self.data = data

    @property
    def service_id(self):
        return self.data.get('service_id')

    @property
    def status(self):
        return self.data.get('status', 'Pending')

    @status.setter
    def status(self, val):
        self.data['status'] = val

    @property
    def request_date(self):
        return self.data.get('request_date', '')

    @property
    def payment_status(self):
        return self.data.get('payment_status', 'Pending')

    @payment_status.setter
    def payment_status(self, val):
        self.data['payment_status'] = val

    def update_status(self, new_status):
        self.status = new_status

    def assign_mechanic(self, mechanic_name):
        self.data['assigned_mechanic'] = mechanic_name

    def add_extra_charges(self, extra_charges, desc):
        self.data['extra_charges'] = extra_charges
        self.data['charge_description'] = desc

    def save_work_description(self, description):
        self.data['work_done'] = description

    def to_dict(self):
        return self.data

    def matches_vehicle_number(self, vehicle_number):
        return vehicle_number.lower() in self.data.get('vehicle_no', '').lower()

    def matches_status(self, status_list):
        if "All" in status_list:
            return True
        return self.status in status_list

    def date_in_range(self, start_date, end_date):
        try:
            service_date = datetime.strptime(self.request_date.split()[0], "%Y-%m-%d").date()
            return start_date <= service_date <= end_date
        except Exception:
            return False

class ServiceManager:
    def __init__(self):
        self.services = [Service(data) for data in load_services()]

    def save(self):
        save_services([srv.to_dict() for srv in self.services])

    def get_by_id(self, service_id):
        return next((srv for srv in self.services if srv.service_id == service_id), None)

    def filter(self, start_date, end_date, status_filter, vehicle_number):
        results = [srv for srv in self.services if srv.date_in_range(start_date, end_date)]
        if status_filter and "All" not in status_filter:
            results = [srv for srv in results if srv.matches_status(status_filter)]
        if vehicle_number:
            results = [srv for srv in results if srv.matches_vehicle_number(vehicle_number)]
        return results

class UserManager:
    def __init__(self):
        self.users = load_users()

    def get_user_by_email(self, email):
        return next((u for u in self.users if u['email'] == email), None)

# ----------- HELPER FUNCTIONS -----------

def display_service_type(service_dict):
    service_type = service_dict.get('service_type')
    service_types = service_dict.get('service_types')
    if service_type:
        return service_type
    elif service_types:
        return ', '.join(service_types)
    return "N/A"

# ----------- DASHBOARD CLASS -----------

class AdminDashboard:
    def __init__(self):
        self.service_manager = ServiceManager()
        self.user_manager = UserManager()

    def run(self):
        inject_global_css()
        st.title("⚙️ Admin Dashboard")

        admin_email = st.session_state.get("email", "Admin")
        admin_user = self.user_manager.get_user_by_email(admin_email)
        admin_name = admin_user["full_name"] if admin_user and "full_name" in admin_user else admin_email

        st.subheader(f"👋 Welcome back, {admin_name}")
        st.caption("Ready to manage your services today?")

        if 'current_service' not in st.session_state:
            st.session_state['current_service'] = None

        # Show service details, if any selected
        if st.session_state['current_service']:
            self.show_service_detail_page(st.session_state['current_service'])
            return

        # Main Filter UI
        self.show_filters_ui()
        
        # Show service stats and logout
        self.show_statistics_and_logout()

    def show_filters_ui(self):
        st.header("🔍 Filter Services")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.caption("📅 Start Date")
            start_date = st.date_input("Start Date", value=date.today().replace(day=1), label_visibility="collapsed")
        with col2:
            st.caption("📅 End Date")
            end_date = st.date_input("End Date", value=date.today(), label_visibility="collapsed")
        with col3:
            st.caption("📊 Filter by Status")
            status_filter = st.multiselect(
                "Filter by Status",
                ["All", "Pending", "In Progress", "Completed", "Cancelled"],
                default=["All"],
                label_visibility="collapsed"
            )
        with col4:
            st.caption("🔍 Search by Vehicle Number")
            vehicle_number_filter = st.text_input(
                "Search by Vehicle Number",
                placeholder="Enter vehicle number...",
                help="Search for services by vehicle number (partial match)",
                label_visibility="collapsed"
            )

        # Filtering
        filtered_services = self.service_manager.filter(
            start_date, end_date, status_filter, vehicle_number_filter
        )

        # Listing Services
        self.show_services_list(filtered_services)

    def show_services_list(self, filtered_services):
        if filtered_services:
            st.write(f"Found **{len(filtered_services)}** services")
            for srv in filtered_services:
                d = srv.data
                customer_name = d.get('customer_name', 'Unknown')
                customer_email = d.get('customer_email', 'N/A')
                customer_phone = d.get('customer_phone', 'N/A')
                with st.expander(
                    f"Service #{d['service_id']} - {customer_name} - {d['vehicle_no']} - {d['status']}",
                    expanded=False):

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Customer:** {customer_name}")
                        st.write(f"**Email:** {customer_email}")
                        st.write(f"**Phone:** {customer_phone}")
                        st.write(f"**Vehicle:** {d['vehicle_type']} {d['vehicle_brand']} {d['vehicle_model']}")
                        st.write(f"**Vehicle No:** {d['vehicle_no']}")
                        st.write(f"**Service Type:** {display_service_type(d)}")
                    with col2:
                        st.write(f"**Service Date:** {d['service_date']}")
                        st.write(f"**Request Date:** {d['request_date']}")
                        st.write(f"**Status:** {d['status']}")
                    with col3:
                        st.write(f"**Payment Status:** {d.get('payment_status', 'Pending')}")
                        st.write(f"**Pickup Required:** {d['pickup_required']}")
                        st.write(f"**Total Cost:** ₹{d.get('base_cost', 0) + d.get('extra_charges',0)}")
                        if st.button("View Details", key=f"view_{d['service_id']}"):
                            st.session_state['current_service'] = d['service_id']
                            st.rerun()
        else:
            st.info("No services found for the selected filters.")

    def show_service_detail_page(self, service_id):
        service = self.service_manager.get_by_id(service_id)
        if not service:
            st.error("Service not found!")
            return

        d = service.data

        st.title("🔧 Service Details")
        st.caption(f"Service ID: {service_id}")
        if st.button("← Back to Dashboard", key="back_button"):
            st.session_state['current_service'] = None
            st.rerun()

        customer_name = d.get('customer_name', 'Unknown')
        customer_email = d.get('customer_email', 'N/A')
        customer_phone = d.get('customer_phone', 'N/A')

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👤 Customer Information")
            st.write(f"**🧑 Customer:** {customer_name}")
            st.write(f"**📧 Email:** {customer_email}")
            st.write(f"**📱 Phone:** {customer_phone}")

            st.subheader("🚗 Vehicle Information")
            st.write(f"**🚙 Vehicle Type:** {d['vehicle_type']}")
            st.write(f"**🏭 Brand:** {d['vehicle_brand']}")
            st.write(f"**🚗 Model:** {d['vehicle_model']}")
            st.write(f"**🔢 Vehicle No:** {d['vehicle_no']}")
            st.write(f"**🔧 Service Type:** {display_service_type(d)}")
            st.write(f"**📝 Description:** {d['description']}")

        with col2:
            st.subheader("📊 Service Status")
            st.write(f"**📈 Status:** {d['status']}")
            st.write(f"**💳 Payment:** {d.get('payment_status', 'Pending')}")
            st.write(f"**🔧 Assigned Mechanic:** {d.get('assigned_mechanic', 'Not Assigned')}")

            st.subheader("💰 Cost Information")
            base_cost = d.get('base_cost', 0)
            extra_charges = d.get('extra_charges', 0)
            total_cost = base_cost + extra_charges
            st.write(f"**💵 Base Cost:** ₹{base_cost}")
            st.write(f"**➕ Extra Charges:** ₹{extra_charges}")
            st.write(f"**💰 Total Cost:** ₹{total_cost}")

        st.markdown("---")
        # --- Update Status, Mechanic, Charges
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**📈 Update Status**")
            new_status = st.selectbox(
                "Service Status",
                ["Pending", "In Progress", "Completed", "Cancelled"],
                index=["Pending", "In Progress", "Completed", "Cancelled"].index(d['status'])
                if d['status'] in ["Pending", "In Progress", "Completed", "Cancelled"] else 0
            )
            if st.button("🔄 Update Status"):
                service.update_status(new_status)
                self.service_manager.save()
                st.success("✅ Status and progress updated!")
                st.rerun()
        with col2:
            st.markdown("**🔧 Assign Mechanic**")
            mechanic_name = st.text_input(
                "Mechanic Name",
                value=d.get('assigned_mechanic', '')
            )
            if st.button("👨‍🔧 Assign Mechanic"):
                service.assign_mechanic(mechanic_name)
                self.service_manager.save()
                st.success("✅ Mechanic assigned!")
                st.rerun()
        with col3:
            st.markdown("**💸 Add Extra Charges**")
            new_extra_charge = st.number_input(
                "Extra Charges (₹)",
                min_value=0,
                value=extra_charges
            )
            charge_description = st.text_input(
                "Charge Description",
                value=d.get('charge_description', '')
            )
            if st.button("💰 Update Extra Charges"):
                service.add_extra_charges(new_extra_charge, charge_description)
                if 'base_cost' not in d:
                    d['base_cost'] = 0
                self.service_manager.save()
                st.success("✅ Extra charges updated!")
                st.rerun()

        st.markdown("---")
        st.subheader("📝 Work Description")
        current_work_done = d.get('work_done', '')
        work_description = st.text_area(
            "Work Done Description",
            value=current_work_done,
            height=100,
            help="Describe what work was performed"
        )
        if st.button("💾 Save Work Description"):
            service.save_work_description(work_description)
            self.service_manager.save()
            st.success("✅ Work description saved!")
            st.rerun()

        # Payment
        st.markdown("---")
        st.subheader("💳 Payment Management")
        c1, c2 = st.columns(2)
        with c1:
            payment_status = st.selectbox(
                "Payment Status",
                ["Pending", "Done"],
                index=["Pending", "Done"].index(d.get('payment_status', 'Pending'))
            )
            if st.button("💳 Update Payment Status"):
                service.payment_status = payment_status
                self.service_manager.save()
                st.success("✅ Payment status updated!")
                st.rerun()
        with c2:
            if d.get('payment_status', 'Pending') == 'Pending':
                st.error(f"⏳ Payment Pending: ₹{base_cost + extra_charges}")
            else:
                st.success(f"✅ Payment Completed: ₹{base_cost + extra_charges}")

    def show_statistics_and_logout(self):
        st.markdown("---")
        st.subheader("Quick Statistics")

        all_services = self.service_manager.services

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Services", len(all_services))

        with col2:
            completed = len([s for s in all_services if s.status == 'Completed'])
            st.metric("Completed Services", completed)

        with col3:
            pending = len([s for s in all_services if s.status == 'Pending'])
            st.metric("Pending Services", pending)

        with col4:
            total_revenue = sum(
                s.data.get('base_cost', 0) + s.data.get('extra_charges', 0)
                for s in all_services if s.data.get('payment_status') == 'Done'
            )
            st.metric("Total Revenue", f"₹{total_revenue}")

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

# ----------- MAIN APP -----------

def main():
    dashboard = AdminDashboard()
    dashboard.run()

if __name__ == '__main__':
    main()
