import streamlit as st

# Configure the page
st.set_page_config(
    page_title="Vehicle Service Management System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state initialization
if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_type" not in st.session_state:
    st.session_state.user_type = "Customer"
if "email" not in st.session_state:
    st.session_state.email = ""

# Routing logic with improved error handling
try:
    if st.session_state.page == "home":
        import home
        home.main()
    elif st.session_state.page == "login":
        import login
        login.main()
    elif st.session_state.page == "signup":
        import signup
        signup.main()
    elif st.session_state.page == "forgot_password":
        import forgot_password
        forgot_password.main()
    elif st.session_state.page == "customer_service":
        import customer_service
        customer_service.main()
    elif st.session_state.page == "admin_dashboard":
        import admin_service
        admin_service.main()
    else:
        st.error("🚫 Unknown page. Redirecting to home...")
        st.session_state.page = "home"
        st.rerun()
        
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please try refreshing the page or contact support if the problem persists.")
    
    # Provide a way to go back to home
    if st.button("🏠 Go to Home"):
        st.session_state.page = "home"
        st.rerun()