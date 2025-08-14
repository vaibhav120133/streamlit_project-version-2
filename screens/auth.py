import streamlit as st
from utils import (
    global_css,
    display_alert
)
from database.users import UserService

class LoginPage:
    def __init__(self):
        if "login_alert_msg" not in st.session_state:
            st.session_state.login_alert_msg = None
        if "login_alert_type" not in st.session_state:
            st.session_state.login_alert_type = None

    def page_header(self, col):
        with col:
            st.title("🔐 Welcome Back")
            st.caption("Sign in to access your dashboard")

    def login_form(self, col):
        with col:
            with st.form("login_form"):
                if st.session_state.login_alert_msg:
                    display_alert(st.session_state.login_alert_msg, st.session_state.login_alert_type)
                
                st.markdown("### 📧 Email Address")
                email = st.text_input(
                    "Email Address", placeholder="Enter your email address",
                    key="email_input", label_visibility="collapsed"
                )
                st.markdown("### 🔒 Password")
                password = st.text_input(
                    "Password", type="password", placeholder="Enter your password",
                    key="password_input", label_visibility="collapsed"
                )
                login_submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)
            
            if login_submitted:
                self.handle_login(email, password)

    def handle_login(self, email, password):
        st.session_state.login_alert_msg = None
        st.session_state.login_alert_type = None
        
        if not email or not password:
            st.session_state.login_alert_msg = "⚠️ Please fill in all fields"
            st.session_state.login_alert_type = "warning"
            st.rerun()
        else:
            users = UserService().fetch_all_users()
            if not users:
                st.session_state.login_alert_msg = "❌ No users found. Please signup first."
                st.session_state.login_alert_type = "error"
                st.rerun()
            else:
                user = next((u for u in users if u["email"].lower() == email.lower()), None)
                if user and user["password"] == password:
                    st.session_state.login_alert_msg = None 
                    st.session_state.login_alert_type = None
                    
                    st.session_state.logged_in = True
                    st.session_state.email = user["email"]
                    st.session_state.user_type = user.get("user_type", "Customer")
                    print(f"[LOGIN] {st.session_state.user_type} logged in: {st.session_state.email}")
                    st.session_state.page = "customer_service" if user.get("user_type") == "Customer" else "admin_dashboard"
                    st.rerun()
                else:
                    st.session_state.login_alert_msg = "❌ Invalid credentials. Please try again."
                    st.session_state.login_alert_type = "error"
                    st.rerun()

    def action_buttons(self, col):
        with col:
            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔄 Forgot Password", use_container_width=True):
                    st.session_state.login_alert_msg = None
                    st.session_state.login_alert_type = None
                    st.session_state.page = "forgot_password"
                    st.rerun()
            with col_b:
                if st.button("📝 Sign Up", use_container_width=True):
                    st.session_state.login_alert_msg = None
                    st.session_state.login_alert_type = None
                    st.session_state.page = "signup"
                    st.rerun()
            st.divider()
            if st.button("🏠 Back to Home", use_container_width=True):
                st.session_state.login_alert_msg = None
                st.session_state.login_alert_type = None
                st.session_state.page = "home"
                st.rerun()

    def render(self):
        global_css()
        col1, col2, col3 = st.columns([1, 2, 1])
        self.page_header(col2)
        self.login_form(col2)
        self.action_buttons(col2)

def main():
    LoginPage().render()

if __name__ == "__main__":
    main()