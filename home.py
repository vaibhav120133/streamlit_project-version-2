import streamlit as st
from utils import set_home_background

def main():
    # Set the special home background
    set_home_background()
    
    # Create a large spacer to push content to bottom
    st.markdown(
        """
        <div style="height: 70vh;"></div>
        """,
        unsafe_allow_html=True
    )
    
    # Create centered button at the bottom
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Get Started", key="get_started_btn"):
            st.session_state.page = "login"
            st.rerun()
    
    # Add moving line with service information
    st.markdown(
        """
        <div class="moving-line">
            <div class="moving-text">
                <div class="service-item">
                    <span>⚡</span>
                    <span>Quick Service - Fast & Reliable</span>
                </div>
                <div class="service-item">
                    <span>🔧</span>
                    <span>Expert Mechanics - Skilled Professionals</span>
                </div>
                <div class="service-item">
                    <span>💰</span>
                    <span>Fair Pricing - Transparent Costs</span>
                </div>
                <div class="service-item">
                    <span>🛠️</span>
                    <span>Complete Vehicle Maintenance</span>
                </div>
                <div class="service-item">
                    <span>🚗</span>
                    <span>All Vehicle Types Supported</span>
                </div>
                <div class="service-item">
                    <span>⏰</span>
                    <span>24/7 Emergency Service</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Add footer with contact information
    st.markdown(
        """
        <div style="
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0,0,0,0.8);
            color: white;
            text-align: center;
            padding: 10px;
            font-size: 14px;
        ">
            © 2025 Vehicle Service Hub | Powered by MotorMates | Your trusted service partner<br>
            📞 Contact: +91-7722969402 | ✉️ Email: gvaibhav046@gmail.com
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()