import streamlit as st
import base64
import os
import json
from datetime import datetime

# File paths
USERS_FILE = "users.json"
SERVICES_FILE = "services.json"

def set_background_image(image_path="bg_image.jpg"):
    """Set background image for the app"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode()
            
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("data:image/png;base64,{base64_image}");
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                }}
                
                /* Enhanced styling for better aesthetics */
                .main {{
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 15px;
                    padding: 20px;
                    margin: 20px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                    backdrop-filter: blur(10px);
                }}
                
                .stButton > button {{
                    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 25px;
                    font-weight: 600;
                    font-size: 16px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                }}
                
                .stButton > button:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
                }}
                
                .stSelectbox > div > div {{
                    background: rgba(255, 255, 255, 0.8);
                    border-radius: 10px;
                    border: 2px solid #667eea;
                }}
                
                .stTextInput > div > div > input {{
                    background: rgba(255, 255, 255, 0.8);
                    border-radius: 10px;
                    border: 2px solid #667eea;
                    padding: 12px;
                }}
                
                .stTextArea > div > div > textarea {{
                    background: rgba(255, 255, 255, 0.8);
                    border-radius: 10px;
                    border: 2px solid #667eea;
                    padding: 12px;
                }}
                
                .stExpander {{
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 10px;
                    border: 1px solid #e0e0e0;
                    margin: 10px 0;
                }}
                
                .metric-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 10px;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                }}
                
                .success-card {{
                    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                }}
                
                .warning-card {{
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                }}
                
                .info-card {{
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                }}
                
                h1 {{
                    color: #333;
                    text-align: center;
                    font-weight: 700;
                    margin-bottom: 30px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                }}
                
                h2 {{
                    color: #555;
                    font-weight: 600;
                    margin-bottom: 20px;
                }}
                
                h3 {{
                    color: #667eea;
                    font-weight: 600;
                    margin-bottom: 15px;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning(f"Background image '{image_path}' not found!")
    except Exception as e:
        st.error(f"Error loading background image: {str(e)}")

def set_home_background():
    """Special background for home page"""
    image_path = "background1.png"
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                b64_string = base64.b64encode(img_file.read()).decode()
            
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("data:image/webp;base64,{b64_string}");
                    background-size: 100% 100%;
                    background-position: center top;
                    background-repeat: no-repeat;
                    margin-top: 0px !important;
                    padding-top: 0px !important;
                    height: 100vh;
                    position: relative;
                }}
                
                header[data-testid="stHeader"] {{
                    display: none !important;
                }}
                
                footer {{
                    display: none !important;
                }}
                
                .block-container {{
                    padding-top: 0rem !important;
                    padding-bottom: 50px !important;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-end;
                    align-items: center;
                    max-width: 100% !important;
                }}
                
                .element-container:has(.stButton) {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    width: 100%;
                }}
                
                .stButton {{
                    display: flex;
                    justify-content: center;
                    width: 100%;
                    margin: 0 auto;
                }}
                
                .stButton > button {{
                    background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
                    color: white !important;
                    border: none !important;
                    padding: 20px 40px !important;
                    font-size: 24px !important;
                    font-weight: 700 !important;
                    border-radius: 50px !important;
                    cursor: pointer !important;
                    transition: all 0.3s ease !important;
                    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4) !important;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}
                
                .stButton > button:hover {{
                    background: linear-gradient(45deg, #FF5252, #FF7979);
                    transform: translateY(-3px) !important;
                    box-shadow: 0 12px 30px rgba(255, 107, 107, 0.6) !important;
                }}
                
                .moving-line {{
                    width: 100%;
                    overflow: hidden;
                    background: rgba(255,255,255,0.1);
                    backdrop-filter: blur(0px);
                    border-radius: 20px;
                    padding: 10px 0;
                    margin-top: 10px;
                    position: relative;
                }}
                
                .moving-text {{
                    display: flex;
                    animation: scroll 25s linear infinite;
                    white-space: nowrap;
                    gap: 80px;
                    align-items: center;
                }}
                
                .service-item {{
                    display: inline-flex;
                    align-items: center;
                    gap: 10px;
                    background: rgba(255,255,255,0.2);
                    padding: 10px 20px;
                    border-radius: 20px;
                    backdrop-filter: blur(5px);
                    color: white;
                    font-weight: 600;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
                    border: 1px solid rgba(255,255,255,0.3);
                    min-width: 250px;
                    justify-content: center;
                }}
                
                @keyframes scroll {{
                    0% {{ transform: translateX(100%); }}
                    100% {{ transform: translateX(-100%); }}
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning(f"Background image '{image_path}' not found!")
    except Exception as e:
        st.error(f"Error loading background image: {str(e)}")

def display_password_requirements(password):
    """Display password requirements with visual indicators"""
    special_chars = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~"
    has_upper = any(char.isupper() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in special_chars for char in password)
    has_length = len(password) >= 8
    
    # Visual indicators
    upper_icon = "✅" if has_upper else "❌"
    digit_icon = "✅" if has_digit else "❌"
    special_icon = "✅" if has_special else "❌"
    length_icon = "✅" if has_length else "❌"
    
    st.markdown(
        f"""
        <div style="
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        ">
            <h4 style="color: #2c3e50; margin: 0 0 10px 0; font-size: 1.1em;">🛡️ Password Requirements:</h4>
            <p style="margin: 5px 0; color: #34495e; font-size: 0.9em;">{upper_icon} At least one uppercase letter</p>
            <p style="margin: 5px 0; color: #34495e; font-size: 0.9em;">{digit_icon} At least one digit</p>
            <p style="margin: 5px 0; color: #34495e; font-size: 0.9em;">{special_icon} At least one special character</p>
            <p style="margin: 5px 0; color: #34495e; font-size: 0.9em;">{length_icon} At least 8 characters long</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return []

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_services():
    """Load services from JSON file"""
    if os.path.exists(SERVICES_FILE):
        try:
            with open(SERVICES_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return []

def save_services(services):
    """Save services to JSON file"""
    with open(SERVICES_FILE, "w") as f:
        json.dump(services, f, indent=4)

def check_password(password):
    """Validate password strength"""
    special_chars = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~"
    has_upper = any(char.isupper() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in special_chars for char in password)
    has_len = len(password) >= 8
    
    return has_upper and has_digit and has_special and has_len

def get_user_by_email(email):
    """Get user by email"""
    users = load_users()
    return next((u for u in users if u["email"] == email), None)

def display_metric_card(title, value, color="primary"):
    """Display a metric card with custom styling"""
    color_map = {
        "primary": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "success": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
        "warning": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "info": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
    }
    
    st.markdown(
        f"""
        <div style="
            background: {color_map.get(color, color_map['primary'])};
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin: 10px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        ">
            <h3 style="margin: 0; color: white;">{title}</h3>
            <h2 style="margin: 10px 0 0 0; color: white; font-size: 2em;">{value}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_alert(message, alert_type="info"):
    """Display styled alert messages"""
    color_map = {
        "success": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
        "warning": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "error": "linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)",
        "info": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
    }
    
    st.markdown(
        f"""
        <div style="
            background: {color_map.get(alert_type, color_map['info'])};
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        ">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )

def create_navigation_buttons():
    """Create styled navigation buttons"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏠 Home", key="nav_home"):
            st.session_state.page = "home"
            st.rerun()
    
    with col2:
        if st.button("👤 Profile", key="nav_profile"):
            if st.session_state.get("logged_in", False):
                user_type = st.session_state.get("user_type", "Customer")
                if user_type == "Admin":
                    st.session_state.page = "admin_dashboard"
                else:
                    st.session_state.page = "customer_service"
            else:
                st.session_state.page = "login"
            st.rerun()
    
    with col3:
        if st.button("🚪 Logout", key="nav_logout"):
            st.session_state.page = "home"
            st.session_state.logged_in = False
            st.session_state.pop("email", None)
            st.session_state.pop("user_type", None)
            st.rerun()

