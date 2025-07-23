import streamlit as st
from utils import (
    inject_global_css,
    display_alert,
    check_password,
    display_password_requirements,
)
from database import fetch_all_users, add_user

class SignUpPage:
    def __init__(self):
        # Initialize fields (useful for validation and state)
        self.full_name = ""
        self.email = ""
        self.phone = ""
        self.password = ""
        self.confirm_password = ""
        self.signup_submitted = False

    @staticmethod
    def validate_user_input(full_name, email, phone, password, confirm_password):
        """Validate all user input and return (True, msg) or (False, error_msg)"""
        if not full_name or not email or not phone or not password or not confirm_password:
            return False, "⚠️ Please fill in all fields"
        if len(full_name.strip()) < 2:
            return False, "❌ Full name must be at least 2 characters"
        if any(char.isdigit() for char in full_name):
            return False, "❌ Full name cannot contain numbers"
        if "@" not in email or "." not in email.split("@")[-1]:
            return False, "❌ Please enter a valid email address"
        if not phone.isdigit() or len(phone) != 10:
            return False, "❌ Phone number must be exactly 10 digits"
        if not check_password(password):
            return False, "❌ Password must be 8+ chars with uppercase, digit, and special character"
        if password != confirm_password:
            return False, "❌ Passwords do not match"
        return True, "OK"

    @staticmethod
    def check_existing_users(full_name, email, phone):
        """Return False, error_msg if conflict found"""
        users = fetch_all_users()
        if any(u["full_name"].lower() == full_name.lower() for u in users):
            return False, "❌ Full name already exists. Please choose another."
        if any(u["email"].lower() == email.lower() for u in users):
            return False, "❌ Email already registered. Please login or use another."
        if any(u["phone"] == phone for u in users):
            return False, "❌ Phone already registered. Please use another."
        return True, "OK"

    def page_header(self, col):
        with col:
            st.title("🚀 Join Our Community")
            st.markdown(
                "Create your account to access premium vehicle services"
            )
            st.divider()

    def signup_form(self, col):
        with col:
            with st.form("signup_form"):
                st.markdown("### 👤 Full Name")
                self.full_name = st.text_input(
                    "Full Name", placeholder="Enter your full name",
                    key="fullname_input", label_visibility="collapsed"
                )

                st.markdown("### 📧 Email Address")
                self.email = st.text_input(
                    "Email Address", placeholder="Enter your email address",
                    key="email_input", label_visibility="collapsed"
                )

                st.markdown("### 📱 Phone Number")
                self.phone = st.text_input(
                    "Phone Number", placeholder="Enter your 10-digit phone number",
                    key="phone_input", label_visibility="collapsed"
                )

                st.markdown("### 🔒 Password")
                self.password = st.text_input(
                    "Password", type="password",
                    placeholder="Create a strong password",
                    key="password_input", label_visibility="collapsed"
                )

                st.markdown("### 🔐 Confirm Password")
                self.confirm_password = st.text_input(
                    "Confirm Password", type="password",
                    placeholder="Confirm your password",
                    key="confirm_password_input", label_visibility="collapsed"
                )

                self.signup_submitted = st.form_submit_button(
                    "🎉 Create Account", use_container_width=True
                )

    def password_requirements_ui(self, col):
        with col:
            if self.password:
                display_password_requirements(self.password)

    def handle_signup(self):
        if self.signup_submitted:
            input_valid, msg = self.validate_user_input(
                self.full_name, self.email, self.phone, self.password, self.confirm_password
            )
            if not input_valid:
                display_alert(msg, "error")
            else:
                user_valid, msg = self.check_existing_users(self.full_name, self.email, self.phone)
                if not user_valid:
                    display_alert(msg, "error")
                else:
                    user = {
                        "full_name": self.full_name.strip(),
                        "email": self.email.lower().strip(),
                        "phone": self.phone,
                        "password": self.password,
                        "user_type": "Customer"
                    }
                    add_user(user)
                    display_alert(f"🎉 Registration successful! Welcome, {self.full_name}!", "success")
                    st.session_state.logged_in = True
                    st.session_state.email = self.email.lower().strip()
                    st.session_state.user_type = "Customer"
                    st.balloons()
                    st.session_state.page = "customer_service"
                    st.rerun()

    def action_buttons(self, col):
        with col:
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔐 Already have an account?", use_container_width=True):
                    st.session_state.page = "login"
                    st.rerun()
            with col_b:
                if st.button("🏠 Back to Home", use_container_width=True):
                    st.session_state.page = "home"
                    st.rerun()

    def privacy_notice(self, col):
        with col:
            st.info(
                "🛡️ **Your Privacy & Security**\n\n"
                "We prioritize your data security and never share your personal information with third parties. "
                "Your account is protected with industry-standard encryption.",
                icon="🔐"
            )

    def render(self):
        inject_global_css()
        col1, col2, col3 = st.columns([1,2,1])
        self.page_header(col2)
        self.signup_form(col2)
        self.password_requirements_ui(col2)
        self.handle_signup()
        self.action_buttons(col2)
        self.privacy_notice(col2)

def main():
    SignUpPage().render()

if __name__ == "__main__":
    main()
