import streamlit as st
import base64
import os

def set_home_background():
    image_path = "static/home_bg_image.png"
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
                    width: 50%;
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

def inject_global_css():
    image_path="static/bg_image.jpg"
    def _encode_image(path):
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return None

    b64 = _encode_image(image_path)
    bg_css = ""
    if b64:
        bg_css = f"""
            .stApp {{
                background-image: url("data:image/png;base64,{b64}") !important;
                background-size: cover !important;
                background-position: center center !important;
                background-repeat: no-repeat !important;
                background-attachment: fixed !important;
            }}
            .main {{
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 20px;
                margin: 20px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
            }}
        """
    common_css = """
        .stButton > button, .stFormSubmitButton > button {
            background: rgba(52, 73, 94, 0.9) !important;
            color: #ecf0f1 !important;
            border: 2px solid rgba(52, 73, 94, 0.9) !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 1.1em !important;
            padding: 15px 30px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
            cursor: pointer;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            background: rgba(44, 62, 80, 1) !important;
            border-color: rgba(44, 62, 80, 1) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3) !important;
        }
        .stButton > button:active, .stFormSubmitButton > button:active {
            transform: translateY(0px) !important;
        }
        .stSelectbox > div > div {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
            border: 2px solid #667eea;
        }
        .stTextInput > div > div > input,
        input[type="text"],
        input[type="email"],
        input[type="password"],
        .stTextArea > div > div > textarea {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
            border: 2px solid #667eea;
            padding: 12px !important;
            color: #2c3e50 !important;
            font-size: 1.05em !important;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #764ba2 !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
            background: rgba(255, 255, 255, 1) !important;
            outline: none;
        }
        .stExpander {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin: 10px 0;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin: 10px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        .success-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .warning-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .info-card {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        h1 {
            color: #333;
            text-align: center;
            font-weight: 700;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        h2 {
            color: #555;
            font-weight: 600;
            margin-bottom: 20px;
        }
        h3 {
            color: #667eea;
            font-weight: 600;
            margin-bottom: 15px;
        }
    """

    st.markdown(f"<style>{bg_css}{common_css}</style>", unsafe_allow_html=True)


def display_password_requirements(password: str):
    special_chars = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~"
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in special_chars for c in password)
    has_length = len(password) >= 8

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
            <p style="margin: 5px 0; color: #34495e; font-size: 0.9em;">{'✅' if has_upper else '❌'} At least one uppercase letter</p>
            <p style="margin: 5px 0; color: #34495e; font-size: 0.9em;">{'✅' if has_digit else '❌'} At least one digit</p>
            <p style="margin: 5px 0; color: #34495e; font-size: 0.9em;">{'✅' if has_special else '❌'} At least one special character</p>
            <p style="margin: 5px 0; color: #34495e; font-size: 0.9em;">{'✅' if has_length else '❌'} At least 8 characters long</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def check_password(password: str) -> bool:
    special_chars = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~"
    return (
        len(password) >= 8
        and any(c.isupper() for c in password)
        and any(c.isdigit() for c in password)
        and any(c in special_chars for c in password)
    )

def display_alert(message: str, alert_type="info"):
    color_map = {
        "success": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
        "warning": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "error": "linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)",
        "info": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
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
        unsafe_allow_html=True,
    )
