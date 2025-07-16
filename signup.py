import streamlit as st
from utils import (
    set_background_image, 
    load_users, 
    save_users, 
    display_alert, 
    check_password,
    display_password_requirements
)

def display_privacy_notice():
    """Display privacy and security notice"""
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

def validate_user_input(full_name, email, phone, password, confirm_password):
    """Validate all user input and return validation status with specific error messages"""
    
    # Check if all fields are filled
    if not full_name or not email or not phone or not password or not confirm_password:
        return False, "⚠️ Please fill in all fields"
    
    # Validate full name (no numbers, minimum length)
    if len(full_name.strip()) < 2:
        return False, "❌ Full name must be at least 2 characters long"
    
    if any(char.isdigit() for char in full_name):
        return False, "❌ Full name cannot contain numbers"
    
    # Validate email format
    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "❌ Please enter a valid email address"
    
    # Validate phone number
    if not phone.isdigit() or len(phone) != 10:
        return False, "❌ Phone number must be exactly 10 digits"
    
    # Validate password strength
    if not check_password(password):
        return False, "❌ Password must contain at least one uppercase letter, one digit, have mininmun len 8 and one special character"
    
    # Check password confirmation
    if password != confirm_password:
        return False, "❌ Passwords do not match"
    
    return True, "Validation successful"

def check_existing_users(full_name, email, phone):
    """Check if user already exists and return specific error message"""
    users = load_users()
    
    # Check if full name already exists
    if any(u["full_name"].lower() == full_name.lower() for u in users):
        return False, "❌ Full name already exists. Please choose a different name."
    
    # Check if email already exists
    if any(u["email"].lower() == email.lower() for u in users):
        return False, "❌ Email already registered. Please use a different email or login."
    
    # Check if phone already exists
    if any(u["phone"] == phone for u in users):
        return False, "❌ Phone number already registered. Please use a different number."
    
    return True, "User validation successful"

def main():
    # Set background image
    set_background_image()
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
        # Title with enhanced styling
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
                🚀 Join Our Community
            </h1>
            <p style="
                text-align: center;
                color: #34495e;
                margin-bottom: 30px;
                font-size: 1.2em;
                font-weight: 500;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            ">
                Create your account to access premium vehicle services
            </p>
            """,
            unsafe_allow_html=True
        )
        
        # Registration form with enhanced styling
        with st.form("signup_form"):
            # Full Name
            st.markdown("""
            <h3 style="
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 1.1em;
                font-weight: 600;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            ">👤 Full Name</h3>
            """, unsafe_allow_html=True)
            
            full_name = st.text_input("", placeholder="Enter your full name", key="fullname_input")
            
            # Email
            st.markdown("""
            <h3 style="
                color: #2c3e50;
                margin-bottom: 10px;
                margin-top: 15px;
                font-size: 1.1em;
                font-weight: 600;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            ">📧 Email Address</h3>
            """, unsafe_allow_html=True)
            
            email = st.text_input("", placeholder="Enter your email address", key="email_input")
            
            # Phone Number
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
            
            phone = st.text_input("", placeholder="Enter your 10-digit phone number", key="phone_input")
            
            # Password
            st.markdown("""
            <h3 style="
                color: #2c3e50;
                margin-bottom: 10px;
                margin-top: 15px;
                font-size: 1.1em;
                font-weight: 600;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            ">🔒 Password</h3>
            """, unsafe_allow_html=True)
            
            password = st.text_input("", type="password", placeholder="Create a strong password", key="password_input")
            
            # Confirm Password
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
            
            confirm_password = st.text_input("", type="password", placeholder="Confirm your password", key="confirm_password_input")
            
            # Submit button
            st.markdown("<br>", unsafe_allow_html=True)
            signup_submitted = st.form_submit_button("🎉 Create Account", use_container_width=True)
    
    # Display password requirements if password is being typed
    if password:
        with col2:
            display_password_requirements(password)
    
    # Handle registration
    if signup_submitted:
        with col2:
            # Validate user input
            input_valid, input_message = validate_user_input(full_name, email, phone, password, confirm_password)
            
            if not input_valid:
                display_alert(input_message, "error")
            else:
                # Check for existing users
                user_valid, user_message = check_existing_users(full_name, email, phone)
                
                if not user_valid:
                    display_alert(user_message, "error")
                else:
                    # Create new user
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
                    
                    # Auto-login after successful registration
                    st.session_state.logged_in = True
                    st.session_state.email = email.lower().strip()
                    st.session_state.user_type = "Customer"
                    
                    # Celebratory animation
                    st.balloons()
                    
                    # Redirect to customer service page
                    st.session_state.page = "customer_service"
                    st.rerun()

    # Enhanced CSS for buttons and inputs
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
    
    # Action buttons
    st.markdown("<br><br>", unsafe_allow_html=True)
    
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
        
        # Privacy notice
        display_privacy_notice()

if __name__ == "__main__":
    main()