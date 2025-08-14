import streamlit as st
from utils import (
    global_css,
    check_password,
    display_password_requirements,
    display_alert
)
from database.users import UserService

class ForgotPasswordFlow:
    def __init__(self):
        self.init_session_state()

    def init_session_state(self):
        if "fp_step" not in st.session_state:
            st.session_state.fp_step = 1
        if "fp_user_data" not in st.session_state:
            st.session_state.fp_user_data = {}

    @staticmethod
    def display_security_notice():
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(231, 76, 60, 0.1) 0%, rgba(192, 57, 43, 0.1) 100%);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            border: 1px solid rgba(231, 76, 60, 0.3);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        ">
            <h4 style="color: #e74c3c; margin: 0 0 10px 0; font-size: 1.2em;">🔐 Security Notice</h4>
            <p style="color: #34495e; margin: 0; font-size: 0.95em; line-height: 1.4;">
                For your security, we require both email and phone verification. 
                Never share your login credentials with anyone.
            </p>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def validate_reset_input(new_password, confirm_password):
        if not new_password or not confirm_password:
            return False, "⚠️ Please fill in both password fields"
        if new_password != confirm_password:
            return False, "❌ Passwords do not match"
        if not check_password(new_password):
            return False, "❌ Password must contain at least one uppercase letter, one digit, minimum 8 characters, and one special character"
        return True, "Password validation successful"

    def step_1_verify(self, col2):
        with col2:
            st.title("🔍 Account Verification")
            st.caption("Please enter your registered email and phone number")

            with st.form("verification_form"):
                st.markdown("### 📧 Email Address")
                email = st.text_input(
                    "📧 Email Address", 
                    placeholder="Enter your registered email", 
                    key="email_verify", 
                    label_visibility="collapsed"
                )
                st.markdown("### 📱 Phone Number")
                phone = st.text_input(
                    "📱 Phone Number", 
                    placeholder="Enter your registered phone number", 
                    key="phone_verify", 
                    label_visibility="collapsed"
                )
                verify_submitted = st.form_submit_button("🔍 Verify Account", use_container_width=True)

            if verify_submitted:
                email_lc = email.strip().lower()
                phone_str = phone.strip()
                if not email_lc or not phone_str:
                    display_alert("⚠️ Please enter both email and phone number", "error")
                else:
                    users = UserService.fetch_all_users()
                    user = next(
                        (u for u in users if u.get("email", "").lower() == email_lc and u.get("phone", "") == phone_str),
                        None
                    )
                    if user:
                        st.session_state.fp_user_data = {
                            "email": email_lc,
                            "phone": phone_str,
                            "full_name": user.get("full_name", "User")
                        }
                        st.session_state.fp_step = 2
                        display_alert("✅ Account verified successfully!", "success")
                        st.rerun()
                    else:
                        display_alert("❌ No account found with the provided email and phone number", "error")

    def step_2_reset_password(self, col2):
        with col2:
            st.title("🔒 Set New Password")
            st.markdown(f"**👤 Account:** {st.session_state.fp_user_data.get('full_name', 'N/A')}")
            st.markdown(f"**📧 Email:** {st.session_state.fp_user_data.get('email', 'N/A')}")

            with st.form("password_reset_form"):
                st.markdown("### 🔒 New Password")
                new_password = st.text_input(
                    "🔒 New Password", 
                    type="password", 
                    placeholder="Enter new password", 
                    key="new_password", 
                    label_visibility="collapsed"
                )
                st.markdown("### 🔐 Confirm Password")
                confirm_password = st.text_input(
                    "🔐 Confirm Password", 
                    type="password", 
                    placeholder="Confirm new password", 
                    key="confirm_new_password", 
                    label_visibility="collapsed"
                )
                reset_submitted = st.form_submit_button("🔄 Reset Password", use_container_width=True)

            if new_password:
                display_password_requirements(new_password)

            if reset_submitted:
                valid, message = self.validate_reset_input(new_password, confirm_password)
                if not valid:
                    display_alert(message, "error")
                else:
                    users = UserService.fetch_all_users()
                    updated = False
                    for i, user in enumerate(users):
                        if (
                            user.get("email", "").lower() == st.session_state.fp_user_data["email"]
                            and user.get("phone") == st.session_state.fp_user_data["phone"]
                        ):
                            users[i]["password"] = new_password
                            updated = True
                            break
                    if updated:
                        UserService.add_user(users)
                        st.session_state.fp_step = 3
                        display_alert("🎉 Password reset successful!", "success")
                        st.balloons()
                        st.experimental_rerun()
                    else:
                        display_alert("❌ Error updating password. Please try again.", "error")

    def step_3_success(self, col2):
        with col2:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
                color: white;
                padding: 30px;
                border-radius: 20px;
                text-align: center;
                margin: 20px 0;
                box-shadow: 0 8px 25px rgba(46, 204, 113, 0.3);
            ">
                <h2 style="margin: 0 0 15px 0; font-size: 2.2em; font-weight: 700;">🎉 Success!</h2>
                <p style="margin: 0; font-size: 1.2em; opacity: 0.9;">
                    Your password has been successfully reset!<br>
                    You can now login with your new password.
                </p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 Go to Login", use_container_width=True):
                st.session_state.page = "login"
                st.session_state.fp_step = 1
                st.session_state.fp_user_data = {}
                st.rerun()

    def navigation(self, col2):
        st.markdown("<br><br>", unsafe_allow_html=True)
        with col2:
            if st.session_state.fp_step == 1:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🔐 Back to Login", use_container_width=True):
                        st.session_state.page = "login"
                        st.session_state.fp_step = 1
                        st.session_state.fp_user_data = {}
                        st.rerun()
                with c2:
                    if st.button("🏠 Back to Home", use_container_width=True):
                        st.session_state.page = "home"
                        st.session_state.fp_step = 1
                        st.session_state.fp_user_data = {}
                        st.rerun()
            elif st.session_state.fp_step == 2:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("⬅️ Back to Verification", use_container_width=True):
                        st.session_state.fp_step = 1
                        st.rerun()
                with c2:
                    if st.button("🏠 Back to Home", use_container_width=True):
                        st.session_state.page = "home"
                        st.session_state.fp_step = 1
                        st.session_state.fp_user_data = {}
                        st.rerun()
            elif st.session_state.fp_step == 3:
                if st.button("🏠 Back to Home", use_container_width=True):
                    st.session_state.page = "home"
                    st.session_state.fp_step = 1
                    st.session_state.fp_user_data = {}
                    st.rerun()
            self.display_security_notice()

    def run(self):
        global_css()
        col1, col2, col3 = st.columns([1, 2, 1])

        if st.session_state.fp_step == 1:
            self.step_1_verify(col2)
        elif st.session_state.fp_step == 2:
            self.step_2_reset_password(col2)
        elif st.session_state.fp_step == 3:
            self.step_3_success(col2)

        self.navigation(col2)

def main():
    ForgotPasswordFlow().run()

if __name__ == "__main__":
    main()
