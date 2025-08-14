import streamlit as st

class VehicleServiceApp:
    def __init__(self):
        self.init_session_state()
        self.page_modules = {
            "home": "screens.home",
            "login": "screens.auth",
            "signup": "screens.signup",
            "forgot_password": "screens.forgot_password",
            "customer_service": "screens.customer_service",
            "admin_dashboard": "screens.admin_service",
        }

    def init_session_state(self):
        st.session_state.setdefault("page", "home")
        st.session_state.setdefault("logged_in", False)
        st.session_state.setdefault("user_type", "Customer")
        st.session_state.setdefault("email", "")

    def run(self):
        page = st.session_state.page
        try:
            mod_name = self.page_modules.get(page, "screens.home")
            module = __import__(mod_name, fromlist=["main"])
            module.main()
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please try refreshing the page or contact support if the problem persists.")
            if st.button("🏠 Go to Home"):
                st.session_state.page = "home"
                st.rerun()

if __name__ == "__main__":
    st.set_page_config(
        page_title="MotorMates Services",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    app = VehicleServiceApp()
    app.run()
