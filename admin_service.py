import streamlit as st
from datetime import datetime, date
from utils import inject_global_css
from database import (
    fetch_all_services,
    fetch_all_mechanics,
    update_service,
    fetch_all_users,
)

def display_service_type(service_dict):
    """Format service types for display."""
    if not service_dict:
        return "N/A"
    service_types = service_dict.get('service_types')
    if service_types:
        if isinstance(service_types, list):
            return ', '.join(str(x) for x in service_types if x)
        else:
            return str(service_types)
    return "N/A"

class Service:
    def __init__(self, data):
        self.data = data or {}

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
    def payment_status(self):
        return self.data.get('payment_status', 'Pending')

    @property
    def assigned_mechanic(self):
        return self.data.get('assigned_mechanic')

    @assigned_mechanic.setter
    def assigned_mechanic(self, val):
        self.data['assigned_mechanic'] = val

    @property
    def extra_charges(self):
        return self.data.get('extra_charges', 0) or 0

    @extra_charges.setter
    def extra_charges(self, val):
        self.data['extra_charges'] = val

    @property
    def charge_description(self):
        return self.data.get('charge_description', '')

    @charge_description.setter
    def charge_description(self, val):
        self.data['charge_description'] = val

    def update_status(self, new_status):
        self.status = new_status

    def assign_mechanic(self, mechanic_id):
        self.assigned_mechanic = mechanic_id

    def add_extra_charges(self, extra_charges, charge_desc):
        self.extra_charges = extra_charges
        self.charge_description = charge_desc
        base_cost = self.data.get('base_cost', 0) or 0
        total_cost = base_cost + extra_charges
        paid_amt = self.data.get('Paid',0) or 0
        if self.payment_status == "Done" and total_cost > paid_amt:
            self.data['payment_status'] = 'Pending'

    def save_work_description(self, description):
        self.data['work_done'] = description

    def to_update_dict(self):
        """Return only updatable fields."""
        keys = [
            'status', 'assigned_mechanic', 'extra_charges', 
            'charge_description', 'work_done', 'description', 'payment_status'
        ]
        return {k: self.data[k] for k in keys if k in self.data}

class ServiceManager:
    def __init__(self):
        self.reload_services()

    def reload_services(self):
        try:
            raw_services = fetch_all_services()
            self.services = [Service(s) for s in raw_services if s]
        except Exception as e:
            st.error(f"Failed to reload services: {e}")
            self.services = []

    def save(self):
        try:
            for srv in self.services:
                if srv.service_id:
                    updates = srv.to_update_dict()
                    if updates:
                        update_service(srv.service_id, updates)
        except Exception as e:
            st.error(f"Failed to save services: {e}")

    def get_by_id(self, service_id):
        return next((srv for srv in self.services if str(srv.service_id) == str(service_id)), None)

class UserManager:
    def __init__(self):
        try:
            self.users = fetch_all_users()
        except Exception as e:
            st.error(f"Failed to load users: {e}")
            self.users = []

    def get_user_by_email(self, email):
        return next((u for u in self.users if u.get('email') == email), None)

class AdminDashboard:
    def __init__(self):
        self.service_manager = ServiceManager()
        self.user_manager = UserManager()
        self.mechanics = fetch_all_mechanics()
        self.mechanic_options = {m['mechanic_id']: m['mechanic_name'] for m in self.mechanics}

    def run(self):
        inject_global_css()
        st.title("⚙️ Admin Dashboard")
        self.welcome_message()
        if 'current_service' not in st.session_state:
            st.session_state['current_service'] = None
        if st.session_state['current_service']:
            self.show_service_detail_page(st.session_state['current_service'])
            return
        if st.button("🔄 Reload Services"):
            self.service_manager.reload_services()
            st.rerun()
        self.show_filters_ui()
        self.show_statistics_and_logout()

    def welcome_message(self):
        admin_email = st.session_state.get("email", "Admin")
        admin_user = self.user_manager.get_user_by_email(admin_email)
        admin_name = admin_user.get("full_name", admin_email) if admin_user else admin_email
        st.subheader(f"👋 Welcome back, {admin_name}")

    def show_filters_ui(self):
        st.header("🔍 Filter Services")
        total_services = len(self.service_manager.services)
        st.info(f"📊 Total services in system: {total_services}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            default_start = date.today().replace(day=1)
            start_date = st.date_input("Start Date", value=default_start)
        with col2:
            end_date = st.date_input("End Date", value=date.today())
        with col3:
            status_filter = st.multiselect(
                "Status Filter",
                ["All", "Pending", "In Progress", "Completed", "Cancelled"],
                default=["All"]
            )
        with col4:
            vehicle_number_filter = st.text_input(
                "Vehicle Number Filter", placeholder="Type vehicle no..."
            )
        filtered = self.filter_services(start_date, end_date, status_filter, vehicle_number_filter)
        self.show_services_list(filtered)

    def filter_services(self, start_date, end_date, status_filter, vehicle_number_filter):
        def date_in_range(service):
            try:
                s_date = service.data.get('request_date')
                if not s_date:
                    return True
                s_date = datetime.strptime(str(s_date), "%Y-%m-%d %H:%M:%S").date()
                return start_date <= s_date <= end_date
            except:
                return True

        def status_match(service):
            if "All" in status_filter or not status_filter:
                return True
            return service.status in status_filter

        def vehicle_no_match(service):
            if not vehicle_number_filter:
                return True
            vehicle_no = service.data.get('vehicle_no', '').lower()
            return vehicle_number_filter.lower() in vehicle_no

        return [srv for srv in self.service_manager.services if date_in_range(srv) and status_match(srv) and vehicle_no_match(srv)]

    def show_services_list(self, services):
        if not services:
            st.warning("❌ No services found for selected filters.")
            return
        st.success(f"✅ Found {len(services)} services")
        for i, srv in enumerate(services):
            d = srv.data
            service_id = d.get('service_id', f'temp_{i}')
            title = (
                f"**🔧 Service #{service_id} - {d.get('customer_name', 'Unknown')} - {d.get('vehicle_type', 'N/A')} - "
                f"{d.get('vehicle_no', 'N/A')} - {srv.status}**"
            )
            with st.expander(title, expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Customer:** {d.get('customer_name', 'N/A')}")
                    st.write(f"**Email:** {d.get('customer_email', 'N/A')}")
                    st.write(f"**Phone:** {d.get('customer_phone', 'N/A')}")
                    st.write(f"**Vehicle:** {d.get('vehicle_type', 'N/A')} - {d.get('vehicle_brand', 'N/A')} - {d.get('vehicle_model', 'N/A')}")
                    st.write(f"**Vehicle Number:** {d.get('vehicle_no', 'N/A')}")
                    st.write(f"**Service Types:** {display_service_type(d)}")
                with col2:
                    st.write(f"**Service Date:** {d.get('service_date', 'N/A')}")
                    st.write(f"**Request Date:** {d.get('request_date', 'N/A')}")
                    st.write(f"**Status:** {srv.status}")
                    mech_id = d.get('assigned_mechanic')
                    mech_name = self.mechanic_options.get(mech_id, "Not Assigned")
                    st.write(f"**Assigned Mechanic:** {mech_name}")
                with col3:
                    base = d.get('base_cost', 0) or 0
                    extra = d.get('extra_charges', 0) or 0
                    paid_amt = d.get('Paid', 0) or 0
                    total = base + extra
                    st.write(f"**Base Cost:** ₹{base}")
                    st.write(f"**Extra Charges:** ₹{extra}")
                    st.write(f"**Total Cost:** ₹{total}")
                    st.write(f"**Paid Amount:** ₹{paid_amt}")
                    st.write(f"**Payment Status:** {d.get('payment_status', 'Pending')}")
                if st.button("👀 View Details", key=f"view_{service_id}_{i}"):
                    st.session_state['current_service'] = service_id
                    st.rerun()

    def show_service_detail_page(self, service_id):
        service = self.service_manager.get_by_id(service_id)
        if not service:
            st.error("❌ Service not found!")
            if st.button("← Back to Dashboard"):
                st.session_state['current_service'] = None
                st.rerun()
            return
        d = service.data

        st.title("🔧 Service Details")
        st.write(f"**Service ID: {service_id}**")
        if st.button("← Back", key="back_button"):
            st.session_state['current_service'] = None
            st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👤 Customer Information")
            st.write(f"**Customer:** {d.get('customer_name', 'N/A')}")
            st.write(f"**Email:** {d.get('customer_email', 'N/A')}")
            st.write(f"**Phone:** {d.get('customer_phone', 'N/A')}")
            st.write(f"**Pickup Required:** {d.get('pickup_required')}")
            if d.get("pickup_address"):
                st.write(f"**Pickup Address:** {d.get('pickup_address')}")

        with col2:
            st.subheader("🚗 Vehicle Information")
            st.write(f"**Type:** {d.get('vehicle_type', 'N/A')}")
            st.write(f"**Brand:** {d.get('vehicle_brand', 'N/A')}")
            st.write(f"**Model:** {d.get('vehicle_model', 'N/A')}")
            st.write(f"**Vehicle No:** {d.get('vehicle_no', 'N/A')}")
            st.write(f"**Service Types:** {display_service_type(d)}")
            st.write(f"**Description:** {d.get('description', '')}")
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Status")
            status_options = ["Pending", "In Progress", "Completed", "Cancelled"]
            curr_status = service.status
            new_status = st.selectbox(
                "Service Status",
                status_options,
                index=status_options.index(curr_status) if curr_status in status_options else 0
            )
            if st.button("Update Status"):
                service.update_status(new_status)
                self.service_manager.save()
                st.success("Status updated successfully.")
                st.rerun()

        with col2:
            st.subheader("🔧 Assign Mechanic")
            mech_keys = [None] + list(self.mechanic_options.keys())

            def mech_name_or_none(mid):
                return "None" if mid is None else self.mechanic_options.get(mid, "Unknown")

            curr_mech_id = service.assigned_mechanic
            mech_default = 0
            if curr_mech_id in self.mechanic_options:
                mech_default = mech_keys.index(curr_mech_id)
            selected_mech = st.selectbox(
                "Mechanic", mech_keys, format_func=mech_name_or_none, index=mech_default
            )
            if st.button("Assign Mechanic"):
                service.assign_mechanic(selected_mech)
                self.service_manager.save()
                st.success("Mechanic assigned successfully")
                st.rerun()
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💸 Extra Charges")
            new_extra = st.number_input(
                "Extra Charges (₹)", min_value=0, value=service.extra_charges, step=10
            )
            charge_desc = st.text_input("Description for Extra Charges", value=service.charge_description)
            if st.button("Update Extra Charges"):
                service.add_extra_charges(new_extra, charge_desc)
                self.service_manager.save()
                st.success("Extra charges updated")
                st.rerun()
        
        with col2:
            st.subheader("📝 Work Description")
            work_done = st.text_area("Work Done Description", value=d.get("work_done", ""), height=100)
            if st.button("Save Work Description"):
                service.save_work_description(work_done)
                self.service_manager.save()
                st.success("Work description saved")
                st.rerun()

        st.markdown("---")
        st.subheader("💳 Payment Information")
        payment_status = d.get("payment_status", "Pending")
        base = d.get('base_cost', 0) or 0
        extra = d.get('extra_charges', 0) or 0
        paid_amt = d.get("Paid",0) or 0
        total = base + extra
        st.write(f"**Base Cost:** ₹{base}")
        st.write(f"**Extra Charges:** ₹{extra}")
        st.write(f"**Total Cost:** ₹{total}")
        st.write(f"**Paid Amount:** ₹{paid_amt}")
        st.write(f"**Payment Status:** {payment_status}")

    def show_statistics_and_logout(self):
        st.markdown("---")
        st.subheader("📊 Quick Statistics")
        total = len(self.service_manager.services)
        completed = len([s for s in self.service_manager.services if s.status == "Completed"])
        pending = len([s for s in self.service_manager.services if s.status == "Pending"])
        progress = len([s for s in self.service_manager.services if s.status == "In Progress"])
        revenue = sum(
            (s.data.get('base_cost', 0) or 0) + (s.data.get('extra_charges', 0) or 0)
            for s in self.service_manager.services if s.data.get('payment_status') == "Done"
        )
        cols = st.columns(5)
        cols[0].metric("📋 Total Services", total)
        cols[1].metric("✅ Completed", completed)
        cols[2].metric("⏳ Pending", pending)
        cols[3].metric("⏳ In Progress", progress)
        cols[4].metric("💰 Revenue", f"₹{revenue}")
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("🚪 Logout"):
                st.session_state.clear()
                st.session_state.page = "login"
                st.session_state.logged_in = False
                st.rerun()
                
def main():
    dashboard = AdminDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
