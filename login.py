import streamlit as st
from utils import (
    inject_global_css,
    load_users,
    display_alert
)

def main():
    # Inject central CSS styles
    inject_global_css()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Title
        st.markdown("""
            <h1 style="
                text-align: center;
                color: #2c3e50;
                font-weight: 700;
                margin-top: 0px;
                margin-bottom: 20px;
                font-size: 2.8em;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            ">
                🔐 Welcome Back
            </h1>
            <p style="
                text-align: center;
                color: #34495e;
                margin-bottom: 40px;
                font-size: 1.2em;
                font-weight: 500;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            ">
                Sign in to access your dashboard
            </p>
        """, unsafe_allow_html=True)

        # Login Form
        with st.form("login_form"):
            st.markdown("""
                <h3 style="color:#2c3e50; margin-bottom:15px; font-size:1.3em; font-weight:600;">
                    📧 Email Address
                </h3>
            """, unsafe_allow_html=True)
            email = st.text_input(
                "Email Address", placeholder="Enter your email address",
                key="email_input", label_visibility="collapsed"
            )

            st.markdown("""
                <h3 style="color:#2c3e50; margin-bottom:15px; margin-top:20px; font-size:1.3em; font-weight:600;">
                🔒 Password
                </h3>
            """, unsafe_allow_html=True)
            password = st.text_input(
                "Password", type="password", placeholder="Enter your password",
                key="password_input", label_visibility="collapsed"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            login_submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)

    # Handle Login
    if login_submitted:
        if not email or not password:
            display_alert("⚠️ Please fill in all fields", "warning")
        else:
            users = load_users()
            if not users:
                display_alert("❌ No users found. Please signup first.", "error")
            else:
                user = next((u for u in users if u["email"].lower() == email.lower()), None)
                if user and user["password"] == password:
                    display_alert(f"✅ Welcome back, {user.get('full_name', user['email'])}!", "success")
                    st.session_state.logged_in = True
                    st.session_state.email = user["email"]
                    st.session_state.user_type = user.get("user_type", "Customer")
                    st.session_state.page = "admin_dashboard" if user.get("user_type") == "Admin" else "customer_service"
                    st.rerun()
                else:
                    display_alert("❌ Invalid credentials. Please try again.", "error")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Action Buttons (inside center column)
    with col2:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Forgot Password", use_container_width=True):
                st.session_state.page = "forgot_password"
                st.rerun()
        with col_b:
            if st.button("📝 Sign Up", use_container_width=True):
                st.session_state.page = "signup"
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

if __name__ == "__main__":
    main()
