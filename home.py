# home.py
import streamlit as st
from utils import set_home_background

class VehicleServiceHubHome:
    def __init__(self):
        """Initialize home page."""
        self.set_background = set_home_background

    def show_welcome_section(self):
        self.set_background()
        st.markdown(
            """
            <div style="height: 70vh;"></div>
            """,
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Get Started", key="get_started_btn", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()

    def show_services_marquee(self):
        st.markdown(
            """
            <div class="moving-line">
                <div class="moving-text">
                    <div class="service-item">⚡ Quick Service - Fast & Reliable</div>
                    <div class="service-item">🔧 Expert Mechanics</div>
                    <div class="service-item">💰 Fair Pricing - Transparent Costs</div>
                    <div class="service-item">🛠️ Complete Vehicle Maintenance</div>
                    <div class="service-item">🚗 All Vehicle Types Supported</div>
                    <div class="service-item">⏰ 24/7 Emergency Service</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    def show_footer(self):
        st.markdown(
            """
            <style>
            .footer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0,0,0,0.8);
                color: white;
                text-align: center;
                padding: 12px 10px;
                font-size: 14px;
                z-index: 9999;
                backdrop-filter: blur(4px);
            }
            main > div.block-container {
                padding-bottom: 60px !important;
            }
            </style>
            <div class="footer">
                © 2025 Vehicle Service Hub | Powered by MotorMates | Your trusted service partner<br>
                📞 Contact: +91-7722969402 | ✉️ Email: gvaibhav046@gmail.com
            </div>
            """,
            unsafe_allow_html=True
        )

    def run(self):
        self.show_welcome_section()
        self.show_services_marquee()
        self.show_footer()

def main():
    """Entry point for home page (for router/import use)"""
    app = VehicleServiceHubHome()
    app.run()
