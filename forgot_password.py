import streamlit as st
from utils import (
    check_password, 
    set_background_image,
    display_password_requirements,
    display_alert,
    load_users,
    save_users
)

USERS_FILE = "users.json"

def display_security_notice():
    """Display security notice"""
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

def validate_reset_input(new_password, confirm_password):
    """Validate password reset input"""
    if not new_password or not confirm_password:
        return False, "⚠️ Please fill in both password fields"
    
    if new_password != confirm_password:
        return False, "❌ Passwords do not match"
    
    if not check_password(new_password):
        return False, "❌ Password must contain at least one uppercase letter, one digit, have minimum 8 len and one special character"
    
    return True, "Password validation successful"

def main():
    # Set background image
    set_background_image()
    
    # Enhanced CSS styling (matching signup.py)
    st.markdown("""
    <style>
        input[type="text"], input[type="email"], input[type="password"] {
            color: #2c3e50 !important; /* Dark text color */
            background-color: #f4f6f7 !important; /* Light gray background for contrast */
            border: 1px solid #ccc !important;
            padding: 10px;
            border-radius: 5px;
        }

        input::placeholder {
            color: #95a5a6 !important; /* Slightly muted placeholder color */
        }

        textarea {
            color: #2c3e50 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Force narrow layout with Streamlit columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Title with enhanced styling (matching signup.py)
        st.markdown(
            """
            <h1 style="
                text-align: center;
                color: #2c3e50;
                margin-top: 0px;
                margin-bottom: 15px;
                font-size: 2.8em;
                font-weight: 700;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            ">
                🔐 Reset Password
            </h1>
            <p style="
                text-align: center;
                color: #34495e;
                margin-bottom: 30px;
                font-size: 1.2em;
                font-weight: 500;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            ">
                Secure password recovery for your account
            </p>
            """,
            unsafe_allow_html=True
        )
    
    # Initialize session state for multi-step process
    if "fp_step" not in st.session_state:
        st.session_state.fp_step = 1
    if "fp_user_data" not in st.session_state:
        st.session_state.fp_user_data = {}

    # Step 1: Email and Phone Verification
    if st.session_state.fp_step == 1:
        with col2:
            st.markdown("""
            <h2 style="
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 1.4em;
                font-weight: 600;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            ">🔍 Account Verification</h2>
            """, unsafe_allow_html=True)
            
            st.markdown(":red[Please enter your registered email and phone number]")
            
            with st.form("verification_form"):
                # Email field
                st.markdown("""
                <h3 style="
                    color: #2c3e50;
                    margin-bottom: 10px;
                    font-size: 1.1em;
                    font-weight: 600;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
                ">📧 Email Address</h3>
                """, unsafe_allow_html=True)
                
                email = st.text_input("", placeholder="Enter your registered email address", key="email_verify")
                
                # Phone field
                st.markdown("""
                <h3 style="
                    color: #2c3e50;
                    margin-bottom: 10px;
                    margin-top: 15px;
                    font-size: 1.1em;
                    font-weight: 600;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
                ">📱 Phone Number</h3>
                """, unsafe_allow_html=True)
                
                phone = st.text_input("", placeholder="Enter your registered phone number", key="phone_verify")
                
                st.markdown("<br>", unsafe_allow_html=True)
                verify_submitted = st.form_submit_button("🔍 Verify Account", use_container_width=True)
        
        if verify_submitted:
            with col2:
                if not email or not phone:
                    display_alert("⚠️ Please enter both email and phone number", "error")
                else:
                    users = load_users()
                    if not users:
                        display_alert("❌ No users found. Please signup first.", "error")
                    else:
                        # Find user by email and phone
                        user = next((u for u in users if u["email"].lower() == email.lower() and u["phone"] == phone), None)
                        
                        if user:
                            st.session_state.fp_user_data = {
                                "email": email.lower(),
                                "phone": phone,
                                "full_name": user.get("full_name", "")
                            }
                            st.session_state.fp_step = 2
                            display_alert("✅ Account verified successfully!", "success")
                            st.rerun()
                        else:
                            display_alert("❌ No account found with the provided email and phone number", "error")

    # Step 2: Password Reset
    elif st.session_state.fp_step == 2:
        with col2:
            st.markdown("""
            <h2 style="
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 1.4em;
                font-weight: 600;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            ">🔒 Set New Password</h2>
            """, unsafe_allow_html=True)
            
            # User info display
            st.markdown(f":blue[**👤 Account Details:**]")
            st.markdown(f":blue[**Name:** {st.session_state.fp_user_data.get('full_name', 'N/A')}]")
            st.markdown(f":blue[**Email:** {st.session_state.fp_user_data.get('email', 'N/A')}]")
            
            with st.form("password_reset_form"):
                # New password field
                st.markdown("""
                <h3 style="
                    color: #2c3e50;
                    margin-bottom: 10px;
                    font-size: 1.1em;
                    font-weight: 600;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
                ">🔒 New Password</h3>
                """, unsafe_allow_html=True)
                
                new_password = st.text_input("", type="password", placeholder="Enter your new password", key="new_password")
                
                # Confirm password field
                st.markdown("""
                <h3 style="
                    color: #2c3e50;
                    margin-bottom: 10px;
                    margin-top: 15px;
                    font-size: 1.1em;
                    font-weight: 600;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
                ">🔐 Confirm Password</h3>
                """, unsafe_allow_html=True)
                
                confirm_password = st.text_input("", type="password", placeholder="Confirm your new password", key="confirm_new_password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                reset_submitted = st.form_submit_button("🔄 Reset Password", use_container_width=True)
        
        # Display password requirements if password is being typed
        if new_password:
            with col2:
                display_password_requirements(new_password)
        
        if reset_submitted:
            with col2:
                input_valid, input_message = validate_reset_input(new_password, confirm_password)
                
                if not input_valid:
                    display_alert(input_message, "error")
                else:
                    users = load_users()
                    user_updated = False
                    
                    for i, user in enumerate(users):
                        if (user["email"].lower() == st.session_state.fp_user_data["email"] and 
                            user["phone"] == st.session_state.fp_user_data["phone"]):
                            users[i]["password"] = new_password
                            user_updated = True
                            break
                    
                    if user_updated:
                        save_users(users)
                        st.session_state.fp_step = 3
                        display_alert("🎉 Password reset successful!", "success")
                        st.balloons()
                        st.rerun()
                    else:
                        display_alert("❌ Error updating password. Please try again.", "error")

    # Step 3: Success Message
    elif st.session_state.fp_step == 3:
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
                <h2 style="
                    margin: 0 0 15px 0;
                    font-size: 2.2em;
                    font-weight: 700;
                    color: white;
                ">
                    🎉 Success!
                </h2>
                <p style="
                    margin: 0;
                    font-size: 1.2em;
                    color: white;
                    opacity: 0.9;
                ">
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

    st.markdown("""
    <style>
    /* Form submit button styling */
    .stFormSubmitButton > button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        font-size: 1.1em !important;
        font-weight: 700 !important;
        padding: 15px 30px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stFormSubmitButton > button:hover {
        background: linear-gradient(45deg, #5a67d8 0%, #6b46c1 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Regular button styling */
    .stButton > button {
        background: rgba(52, 73, 94, 0.9) !important;
        color: #ecf0f1 !important;
        border: 2px solid rgba(52, 73, 94, 0.9) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1em !important;
        padding: 12px 20px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton > button:hover {
        background: rgba(44, 62, 80, 1) !important;
        border-color: rgba(44, 62, 80, 1) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Enhanced input styling */
    .stTextInput > div > div > input {
        font-size: 1.05em !important;
        padding: 12px 15px !important;
        border-radius: 10px !important;
        border: 2px solid #667eea !important;
        background: rgba(255, 255, 255, 0.9) !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #764ba2 !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        background: rgba(255, 255, 255, 1) !important;
    }
    
    /* Form container styling */
    .stForm {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Navigation buttons
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    with col2:
        if st.session_state.fp_step == 1:
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("🔐 Back to Login", use_container_width=True):
                    st.session_state.page = "login"
                    st.session_state.fp_step = 1
                    st.session_state.fp_user_data = {}
                    st.rerun()
            
            with col_b:
                if st.button("🏠 Back to Home", use_container_width=True):
                    st.session_state.page = "home"
                    st.session_state.fp_step = 1
                    st.session_state.fp_user_data = {}
                    st.rerun()
        
        elif st.session_state.fp_step == 2:
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("⬅️ Back to Verification", use_container_width=True):
                    st.session_state.fp_step = 1
                    st.rerun()
            
            with col_b:
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
        
        # Security notice
        display_security_notice()

if __name__ == "__main__":
    main()
