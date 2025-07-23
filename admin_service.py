import streamlit as st
from datetime import datetime, date
from utils import inject_global_css
from database import fetch_all_services, fetch_all_users, update_service

# ----------- HELPER FUNCTIONS -----------

def safe_get(data_dict, key, default="N/A"):
    """Safely get value from dictionary with fallback"""
    if not data_dict:
        return default
    value = data_dict.get(key, default)
    return str(value) if value is not None else default

def display_service_type(service_dict):
    """Safely display service type with fallbacks"""
    if not service_dict:
        return "N/A"
    service_type = service_dict.get('service_type')
    service_types = service_dict.get('service_types')
    if service_type:
        return str(service_type)
    elif service_types:
        if isinstance(service_types, list):
            return ', '.join(str(x) for x in service_types if x)
        else:
            return str(service_types)
    return "N/A"

# ----------- DATA MODEL CLASSES -----------

class Service:
    def __init__(self, data):
        self.data = data if data else {}

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
        if not vehicle_number:
            return True
        vehicle_no = self.data.get('vehicle_no', '')
        if not vehicle_no:
            return False
        return vehicle_number.lower() in str(vehicle_no).lower()

    def matches_status(self, status_list):
        if not status_list or "All" in status_list:
            return True
        return self.status in status_list

    def date_in_range(self, start_date, end_date):
        try:
            request_date = self.request_date
            if not request_date:
                return True  # Include services without dates
            if isinstance(request_date, str):
                try:
                    service_date = datetime.strptime(request_date.split()[0], "%Y-%m-%d").date()
                except ValueError:
                    try:
                        service_date = datetime.strptime(request_date[:10], "%Y-%m-%d").date()
                    except ValueError:
                        return True
            elif hasattr(request_date, 'date'):
                service_date = request_date.date()
            else:
                service_date = request_date
            return start_date <= service_date <= end_date
        except Exception as e:
            st.write(f"DEBUG: Date parsing error for service {self.service_id}: {e}")
            return True  # Include service if date parsing fails

class ServiceManager:
    def __init__(self):
        self.services = []
        self.reload_services()

    def reload_services(self):
        try:
            raw_services = fetch_all_services()
            self.services = [Service(data) for data in raw_services if data]
        except Exception as e:
            st.error(f"❌ ERROR: Failed to reload services: {e}")
            self.services = []

    def save(self):
        # Save each service individually to the DB
        try:
            for srv in self.services:
                if srv.service_id:
                    update_service(srv.service_id, srv.to_dict())
        except Exception as e:
            st.error(f"❌ ERROR: Failed to save services: {e}")

    def get_by_id(self, service_id):
        # Ensure comparison as str for consistency
        return next((srv for srv in self.services if str(srv.service_id) == str(service_id)), None)

    def filter(self, start_date, end_date, status_filter, vehicle_number):
        try:
            results = self.services.copy()
            date_filtered = []
            for srv in results:
                if srv.date_in_range(start_date, end_date):
                    date_filtered.append(srv)
            status_filtered = []
            for srv in date_filtered:
                if srv.matches_status(status_filter):
                    status_filtered.append(srv)
            if vehicle_number:
                vehicle_filtered = []
                for srv in status_filtered:
                    if srv.matches_vehicle_number(vehicle_number):
                        vehicle_filtered.append(srv)
                results = vehicle_filtered
            else:
                results = status_filtered
            return results
        except Exception as e:
            st.error(f"❌ ERROR: Failed to filter services: {e}")
            return []

class UserManager:
    def __init__(self):
        try:
            self.users = fetch_all_users()
        except Exception as e:
            st.error(f"❌ ERROR: Failed to load users: {e}")
            self.users = []

    def get_user_by_email(self, email):
        return next((u for u in self.users if u.get('email') == email), None)

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
        admin_name = admin_user.get("full_name", admin_email) if admin_user else admin_email
        st.subheader(f"👋 Welcome back, {admin_name}")
        st.caption("Ready to manage your services today?")

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

    def show_filters_ui(self):
        st.header("🔍 Filter Services")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.caption("📅 Start Date")
            default_start = date.today().replace(day=1)
            if default_start.month > 6:
                default_start = default_start.replace(month=default_start.month - 6)
            else:
                default_start = default_start.replace(year=default_start.year - 1, month=default_start.month + 6)
            start_date = st.date_input("Start Date", value=default_start, label_visibility="collapsed")

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

        if vehicle_number_filter:
            st.write(f"🔍 Vehicle number filter: '{vehicle_number_filter}'")

        filtered_services = self.service_manager.filter(
            start_date, end_date, status_filter, vehicle_number_filter
        )
        self.show_services_list(filtered_services)

    def show_services_list(self, filtered_services):
        if not filtered_services:
            st.warning("❌ No services found for the selected filters.")
            st.info("💡 Try adjusting your date range or status filters.")
            return

        st.success(f"✅ Found **{len(filtered_services)}** services")
        for i, srv in enumerate(filtered_services):
            try:
                d = srv.data
                if not d:
                    continue
                customer_name = safe_get(d, 'customer_name', 'Unknown')
                customer_email = safe_get(d, 'customer_email')
                customer_phone = safe_get(d, 'customer_phone')
                service_id = safe_get(d, 'service_id', f'temp_{i}')
                vehicle_no = safe_get(d, 'vehicle_no')
                status = safe_get(d, 'status', 'Pending')

                with st.expander(
                    f"🔧 Service #{service_id} - {customer_name} - {vehicle_no} - {status}",
                    expanded=False
                ):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**👤 Customer:** {customer_name}")
                        st.write(f"**📧 Email:** {customer_email}")
                        st.write(f"**📱 Phone:** {customer_phone}")
                        st.write(f"**🚗 Vehicle:** {safe_get(d, 'vehicle_type')} {safe_get(d, 'vehicle_brand')} {safe_get(d, 'vehicle_model')}")
                        st.write(f"**🔢 Vehicle No:** {vehicle_no}")
                        st.write(f"**🔧 Service Type:** {display_service_type(d)}")
                    with col2:
                        st.write(f"**📅 Service Date:** {safe_get(d, 'service_date')}")
                        st.write(f"**📅 Request Date:** {safe_get(d, 'request_date')}")
                        st.write(f"**📊 Status:** {status}")
                        st.write(f"**👨🔧 Mechanic:** {safe_get(d, 'assigned_mechanic', 'Not Assigned')}")
                    with col3:
                        st.write(f"**💳 Payment:** {safe_get(d, 'payment_status', 'Pending')}")
                        st.write(f"**🚚 Pickup:** {safe_get(d, 'pickup_required')}")
                        base_cost = d.get('base_cost', 0) or 0
                        extra_charges = d.get('extra_charges', 0) or 0
                        total_cost = base_cost + extra_charges
                        st.write(f"**💰 Total Cost:** ₹{total_cost}")

                    if st.button("👀 View Details", key=f"view_{service_id}_{i}"):
                        st.session_state['current_service'] = service_id
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Error displaying service {i}: {e}")
                continue

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
        st.caption(f"Service ID: {service_id}")
        if st.button("← Back to Dashboard", key="back_button"):
            st.session_state['current_service'] = None
            st.rerun()

        customer_name = safe_get(d, 'customer_name', 'Unknown')
        customer_email = safe_get(d, 'customer_email')
        customer_phone = safe_get(d, 'customer_phone')
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👤 Customer Information")
            st.write(f"**🧑 Customer:** {customer_name}")
            st.write(f"**📧 Email:** {customer_email}")
            st.write(f"**📱 Phone:** {customer_phone}")
            st.subheader("🚗 Vehicle Information")
            st.write(f"**🚙 Vehicle Type:** {safe_get(d, 'vehicle_type')}")
            st.write(f"**🏭 Brand:** {safe_get(d, 'vehicle_brand')}")
            st.write(f"**🚗 Model:** {safe_get(d, 'vehicle_model')}")
            st.write(f"**🔢 Vehicle No:** {safe_get(d, 'vehicle_no')}")
            st.write(f"**🔧 Service Type:** {display_service_type(d)}")
            st.write(f"**📝 Description:** {safe_get(d, 'description', '')}")
        with col2:
            st.subheader("📊 Service Status")
            st.write(f"**📈 Status:** {safe_get(d, 'status', 'Pending')}")
            st.write(f"**💳 Payment:** {safe_get(d, 'payment_status', 'Pending')}")
            st.write(f"**🔧 Assigned Mechanic:** {safe_get(d, 'assigned_mechanic', 'Not Assigned')}")
            st.subheader("💰 Cost Information")
            base_cost = d.get('base_cost', 0) or 0
            extra_charges = d.get('extra_charges', 0) or 0
            total_cost = base_cost + extra_charges
            st.write(f"**💵 Base Cost:** ₹{base_cost}")
            st.write(f"**➕ Extra Charges:** ₹{extra_charges}")
            st.write(f"**💰 Total Cost:** ₹{total_cost}")

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**📈 Update Status**")
            status_options = ["Pending", "In Progress", "Completed", "Cancelled"]
            current_status = d.get('status', 'Pending')
            try:
                current_index = status_options.index(current_status)
            except ValueError:
                current_index = 0
            new_status = st.selectbox("Service Status", status_options, index=current_index)
            if st.button("🔄 Update Status"):
                try:
                    service.update_status(new_status)
                    self.service_manager.save()
                    st.success("✅ Status updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to update status: {e}")
        with col2:
            st.markdown("**🔧 Assign Mechanic**")
            mechanic_name = st.text_input("Mechanic Name", value=safe_get(d, 'assigned_mechanic', ''))
            if st.button("👨🔧 Assign Mechanic"):
                try:
                    service.assign_mechanic(mechanic_name)
                    self.service_manager.save()
                    st.success("✅ Mechanic assigned!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to assign mechanic: {e}")
        with col3:
            st.markdown("**💸 Add Extra Charges**")
            new_extra_charge = st.number_input("Extra Charges (₹)", min_value=0, value=extra_charges)
            charge_description = st.text_input("Charge Description", value=safe_get(d, 'charge_description', ''))
            if st.button("💰 Update Extra Charges"):
                try:
                    service.add_extra_charges(new_extra_charge, charge_description)
                    if 'base_cost' not in d:
                        d['base_cost'] = 0
                    self.service_manager.save()
                    st.success("✅ Extra charges updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to update charges: {e}")

        st.markdown("---")
        st.subheader("📝 Work Description")
        current_work_done = safe_get(d, 'work_done', '')
        work_description = st.text_area("Work Done Description", value=current_work_done, height=100,
                                        help="Describe what work was performed")
        if st.button("💾 Save Work Description"):
            try:
                service.save_work_description(work_description)
                self.service_manager.save()
                st.success("✅ Work description saved!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to save work description: {e}")

        st.markdown("---")
        st.subheader("💳 Payment Management")
        c1, c2 = st.columns(2)
        with c1:
            payment_status_options = ["Pending", "Done"]
            current_payment = d.get('payment_status', 'Pending')
            try:
                current_payment_index = payment_status_options.index(current_payment)
            except ValueError:
                current_payment_index = 0
            payment_status = st.selectbox("Payment Status", payment_status_options, index=current_payment_index)
            if st.button("💳 Update Payment Status"):
                try:
                    service.payment_status = payment_status
                    self.service_manager.save()
                    st.success("✅ Payment status updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to update payment: {e}")
        with c2:
            if d.get('payment_status', 'Pending') == 'Pending':
                st.error(f"⏳ Payment Pending: ₹{total_cost}")
            else:
                st.success(f"✅ Payment Completed: ₹{total_cost}")

    def show_statistics_and_logout(self):
        st.markdown("---")
        st.subheader("📊 Quick Statistics")
        try:
            all_services = self.service_manager.services
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📋 Total Services", len(all_services))
            with col2:
                completed = len([s for s in all_services if s.status == 'Completed'])
                st.metric("✅ Completed Services", completed)
            with col3:
                pending = len([s for s in all_services if s.status == 'Pending'])
                st.metric("⏳ Pending Services", pending)
            with col4:
                total_revenue = sum(
                    (s.data.get('base_cost', 0) or 0) + (s.data.get('extra_charges', 0) or 0)
                    for s in all_services if s.data.get('payment_status') == 'Done'
                )
                st.metric("💰 Total Revenue", f"₹{total_revenue}")
        except Exception as e:
            st.error(f"❌ Failed to calculate statistics: {e}")

        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚪 Logout"):
                st.session_state.page = "login"
                st.session_state.logged_in = False
                st.session_state.pop("email", None)
                st.session_state.pop("user_type", None)
                st.session_state.pop("current_service", None)
                st.rerun()

def main():
    try:
        dashboard = AdminDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"❌ Critical Error: {e}")
        st.write("Please check your database connection and configuration.")
        st.subheader("🔧 Debug Information")
        st.write(f"Session state: {dict(st.session_state)}")

if __name__ == "__main__":
    main()
