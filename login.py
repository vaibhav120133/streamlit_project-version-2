import streamlit as st
from utils import (
    inject_global_css,
    display_alert
)
from database import fetch_all_users

class LoginPage:
    def __init__(self):
        self.email = ""
        self.password = ""
        self.login_submitted = False

    def page_header(self, col):
        with col:
            st.title("🔐 Welcome Back")
            st.markdown("Sign in to access your dashboard")
            st.divider()

    def login_form(self, col):
        with col:
            with st.form("login_form"):
                st.markdown("### 📧 Email Address")
                self.email = st.text_input(
                    "Email Address", placeholder="Enter your email address",
                    key="email_input", label_visibility="collapsed"
                )
                st.markdown("### 🔒 Password")
                self.password = st.text_input(
                    "Password", type="password", placeholder="Enter your password",
                    key="password_input", label_visibility="collapsed"
                )
                self.login_submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)

    def handle_login(self):
        if self.login_submitted:
            if not self.email or not self.password:
                display_alert("⚠️ Please fill in all fields", "warning")
            else:
                users = fetch_all_users()
                if not users:
                    display_alert("❌ No users found. Please signup first.", "error")
                else:
                    user = next((u for u in users if u["email"].lower() == self.email.lower()), None)
                    if user and user["password"] == self.password:
                        display_alert(f"✅ Welcome back, {user.get('full_name', user['email'])}!", "success")
                        st.session_state.logged_in = True
                        st.session_state.email = user["email"]
                        st.session_state.user_type = user.get("user_type", "Customer")
                        st.session_state.page = "admin_dashboard" if user.get("user_type") == "Admin" else "customer_service"
                        st.rerun()
                    else:
                        display_alert("❌ Invalid credentials. Please try again.", "error")

    def action_buttons(self, col):
        with col:
            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔄 Forgot Password", use_container_width=True):
                    st.session_state.page = "forgot_password"
                    st.rerun()
            with col_b:
                if st.button("📝 Sign Up", use_container_width=True):
                    st.session_state.page = "signup"
                    st.rerun()
            st.divider()
            if st.button("🏠 Back to Home", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()

    def render(self):
        inject_global_css()
        col1, col2, col3 = st.columns([1, 2, 1])
        self.page_header(col2)
        self.login_form(col2)
        self.handle_login()
        self.action_buttons(col2)

def main():
    LoginPage().render()

if __name__ == "__main__":
    main()
