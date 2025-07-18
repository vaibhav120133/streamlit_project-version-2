import streamlit as st
from utils import (
    inject_global_css,
    load_users,
    save_users,
    display_alert,
    check_password,
    display_password_requirements,
)

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

def check_existing_users(full_name, email, phone):
    """Return False, error_msg if conflict found"""
    users = load_users()
    if any(u["full_name"].lower() == full_name.lower() for u in users):
        return False, "❌ Full name already exists. Please choose another."
    if any(u["email"].lower() == email.lower() for u in users):
        return False, "❌ Email already registered. Please login or use another."
    if any(u["phone"] == phone for u in users):
        return False, "❌ Phone already registered. Please use another."
    return True, "OK"

def main():
    # Inject your global CSS for consistent look
    inject_global_css()

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
            <h1 style="
                text-align: center;
                color: #2c3e50;
                font-weight: 700;
                margin-top: 0px;
                margin-bottom: 20px;
                font-size: 2.8em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            ">🚀 Join Our Community</h1>
            <p style="
                text-align:center;
                color:#34495e;
                margin-bottom:30px;
                font-size:1.2em;
                font-weight:500;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            ">
                Create your account to access premium vehicle services
            </p>
        """, unsafe_allow_html=True)

        with st.form("signup_form"):
            # INPUTS (with non-empty 'label' but hidden via label_visibility)
            st.markdown("""<h3 style="color:#2c3e50; margin-bottom:8px; font-size:1.3em; font-weight:600;">👤 Full Name</h3>""", unsafe_allow_html=True)
            full_name = st.text_input(
                "Full Name", placeholder="Enter your full name",
                key="fullname_input", label_visibility="collapsed"
            )
            st.markdown("""<h3 style="color:#2c3e50; margin-bottom:8px; font-size:1.3em; font-weight:600;">📧 Email Address</h3>""", unsafe_allow_html=True)
            email = st.text_input(
                "Email Address", placeholder="Enter your email address",
                key="email_input", label_visibility="collapsed"
            )
            st.markdown("""<h3 style="color:#2c3e50; margin-bottom:8px; font-size:1.3em; font-weight:600;">📱 Phone Number</h3>""", unsafe_allow_html=True)
            phone = st.text_input(
                "Phone Number", placeholder="Enter your 10-digit phone number",
                key="phone_input", label_visibility="collapsed"
            )
            st.markdown("""<h3 style="color:#2c3e50; margin-bottom:8px; font-size:1.3em; font-weight:600;">🔒 Password</h3>""", unsafe_allow_html=True)
            password = st.text_input(
                "Password", type="password",
                placeholder="Create a strong password",
                key="password_input", label_visibility="collapsed"
            )
            st.markdown("""<h3 style="color:#2c3e50; margin-bottom:8px; font-size:1.3em; font-weight:600;">🔐 Confirm Password</h3>""", unsafe_allow_html=True)
            confirm_password = st.text_input(
                "Confirm Password", type="password",
                placeholder="Confirm your password",
                key="confirm_password_input", label_visibility="collapsed"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            signup_submitted = st.form_submit_button("🎉 Create Account", use_container_width=True)

        if password:
            display_password_requirements(password)

        # Submission logic
        if signup_submitted:
            # Validate user input
            input_valid, msg = validate_user_input(full_name, email, phone, password, confirm_password)
            if not input_valid:
                display_alert(msg, "error")
            else:
                user_valid, msg = check_existing_users(full_name, email, phone)
                if not user_valid:
                    display_alert(msg, "error")
                else:
                    user = {
                        "full_name": full_name.strip(),
                        "email": email.lower().strip(),
                        "phone": phone,
                        "password": password,
                        "user_type": "Customer"
                    }
                    users = load_users()
                    users.append(user)
                    save_users(users)
                    display_alert(f"🎉 Registration successful! Welcome, {full_name}!", "success")
                    st.session_state.logged_in = True
                    st.session_state.email = email.lower().strip()
                    st.session_state.user_type = "Customer"
                    st.balloons()
                    st.session_state.page = "customer_service"
                    st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    # Action buttons
    with col2:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔐 Already have an account?", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
        with col_b:
            if st.button("🏠 Back to Home", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()

        # Privacy Notice (Optional: add your text or import a helper here)
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                text-align: center;
                border: 1px solid rgba(102, 126, 234, 0.3);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            ">
                <h4 style="color: #2c3e50; margin: 0 0 10px 0; font-size: 1.2em;">🛡️ Your Privacy & Security</h4>
                <p style="color: #34495e; margin: 0; font-size: 0.95em; line-height: 1.4;">
                    We prioritize your data security and never share your personal information with third parties. 
                    Your account is protected with industry-standard encryption.
                </p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
