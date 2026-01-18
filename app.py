import streamlit as st
import os
from dotenv import load_dotenv
from db_services_manager import DbServicesManager
from db_products_manager import DbProductsManager
from customer_manager import CustomerManager
from staff_manager import StaffManager
from booking_manager import BookingManager
from dashboard import Dashboard

# Initialize session state with error handling
@st.cache_resource
def init_managers():
    """Initialize all managers with error handling"""
    try:
        managers = {}
        managers['services_manager'] = DbServicesManager()
        managers['products_manager'] = DbProductsManager()
        managers['customer_manager'] = CustomerManager()
        managers['staff_manager'] = StaffManager()
        managers['booking_manager'] = BookingManager()
        managers['dashboard'] = Dashboard()
        return managers
    except Exception as e:
        st.error(f"Failed to initialize application: {e}")
        return None

def initialize_session_state():
    """Initialize session state"""
    managers = init_managers()
    if managers:
        for key, manager in managers.items():
            if key not in st.session_state:
                st.session_state[key] = manager

def main():
    st.set_page_config(
        page_title="NeerJazz Salon Management System",
        page_icon="💄",
        layout="wide"
    )
   
    # Initialize session state
    initialize_session_state()
    
    st.title("💄NeerJazz Salon Management System")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")    
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["Dashboard", "Services Management", "Products Management", "Customer Management", "Staff Management", "Appointment Booking"]
    )
    
    # Check if managers are initialize                                                                                                                                                                                   if not all(key in st.session_state for key in ['services_manager', 'products_manager', 'customer_manager', 'staff_manager', 'booking_manager', 'dashboard']):
    st.error("Application not properly initialized. Please refresh the page.")
    return None
    try:
        if page == "Dashboard":
            st.session_state.dashboard.show_dashboard(
                st.session_state.services_manager,
                st.session_state.products_manager
            )
        elif page == "Services Management":
            st.session_state.services_manager.show_services_interface()
        elif page == "Products Management":
            st.session_state.products_manager.show_products_interface()
        elif page == "Customer Management":
            st.session_state.customer_manager.show_customer_interface()
        elif page == "Staff Management":
            st.session_state.staff_manager.show_staff_interface()
        elif page == "Appointment Booking":
            st.session_state.booking_manager.show_booking_interface()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please try refreshing the page or contact support if the issue persists.")

# st.sidebar.title("Navigation")

# # Define all pages
# pages = [
#     "Dashboard",
#     "Services Management",
#     "Products Management",
#     "Customer Management",
#     "Staff Management",
#     "Appointment Booking"
# ]

# # Initialize current page in session state
# if "current_page" not in st.session_state:
#     st.session_state.current_page = "Dashboard"

# # Create buttons for each page
# for p in pages:
#     if st.sidebar.button(p, use_container_width=True):
#         st.session_state.current_page = p

# # Check if managers are initialized
# if not all(key in st.session_state for key in [
#     'services_manager',
#     'products_manager',
#     'customer_manager',
#     'staff_manager',
#     'booking_manager',
#     'dashboard'
# ]):
#     st.error("Application not properly initialized. Please refresh the page.")
# else:
#     try:
#         if st.session_state.current_page == "Dashboard":
#             st.session_state.dashboard.show_dashboard(
#                 st.session_state.services_manager,
#                 st.session_state.products_manager
#             )
#         elif st.session_state.current_page == "Services Management":
#             st.session_state.services_manager.show_services_interface()
#         elif st.session_state.current_page == "Products Management":
#             st.session_state.products_manager.show_products_interface()
#         elif st.session_state.current_page == "Customer Management":
#             st.session_state.customer_manager.show_customer_interface()
#         elif st.session_state.current_page == "Staff Management":
#             st.session_state.staff_manager.show_staff_interface()
#         elif st.session_state.current_page == "Appointment Booking":
#             st.session_state.booking_manager.show_booking_interface()
#     except Exception as e:
#         st.error(f"An error occurred: {e}")
#         st.info("Please try refreshing the page or contact support if the issue persists.")

if __name__ == "__main__":
    main()
