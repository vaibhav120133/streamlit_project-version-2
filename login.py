import streamlit as st
from utils import set_background_image, load_users, display_alert

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
        # Title with icon - optimized for light background
        st.markdown(
            """
            <h1 style="
                text-align: center;
                color: #2c3e50;
                margin-top: 0px;
                margin-bottom: 20px;
                font-size: 2.8em;
                font-weight: 700;
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
            """,
            unsafe_allow_html=True
        )
        
        # Login form with dark styling for light background
        with st.form("login_form"):
            st.markdown("""
            <h3 style="
                color: #2c3e50;
                margin-bottom: 15px;
                font-size: 1.1em;
                font-weight: 600;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            ">📧 Email Address</h3>
            """, unsafe_allow_html=True)
            
            email = st.text_input("", placeholder="Enter your email address", key="email_input")
            
            st.markdown("""
            <h3 style="
                color: #2c3e50;
                margin-bottom: 15px;
                margin-top: 20px;
                font-size: 1.1em;
                font-weight: 600;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            ">🔒 Password</h3>
            """, unsafe_allow_html=True)
            
            password = st.text_input("", type="password", placeholder="Enter your password", key="password_input")
            
            # Submit button
            st.markdown("<br>", unsafe_allow_html=True)
            login_submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)
    
    # Handle login
    if login_submitted:
        if not email or not password:
            display_alert("⚠️ Please fill in all fields", "warning")
        else:
            users = load_users()
            
            if not users:
                display_alert("❌ No users found. Please signup first.", "error")
            else:
                # Find user by email
                user = next((u for u in users if u["email"] == email), None)
                
                if user and user["password"] == password:
                    display_alert(f"✅ Welcome back, {user.get('full_name', user['email'])}!", "success")
                    
                    # Set session state
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.session_state.user_type = user.get("user_type", "Customer")
                    
                    # Redirect based on user type
                    if user.get("user_type") == "Admin":
                        st.session_state.page = "admin_dashboard"
                    else:
                        st.session_state.page = "customer_service"
                    
                    st.rerun()
                else:
                    display_alert("❌ Invalid credentials. Please try again.", "error")

    # Action buttons with dark styling for light background
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Custom CSS for buttons
    st.markdown("""
    <style>
    .stButton > button {
        background: rgba(52, 73, 94, 0.9) !important;
        color: #ecf0f1 !important;
        border: 2px solid rgba(52, 73, 94, 0.9) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
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
    </style>
    """, unsafe_allow_html=True)
    
    # All content now inside the middle column
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
        
        # Back to home
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

if __name__ == "__main__":
    main()