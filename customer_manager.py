import streamlit as st
import pandas as pd
from models import DatabaseManager
from db_manager import DatabaseCustomerManager
from typing import List, Dict

class CustomerManager:
    def __init__(self):
        try:
            self.db_manager = DatabaseManager()
            self.db_manager.create_tables()
            self.customer_manager = DatabaseCustomerManager(self.db_manager)
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            self.customer_manager = None
    
    def show_customer_interface(self):
        """Display the customer management interface"""
        st.header("👥 Customer Management")
        
        if not self.customer_manager:
            st.error("Database connection unavailable")
            return
        
        # Tabs for different operations
        tab1, tab2, tab3, tab4 = st.tabs(["View Customers", "Add Customer", "Edit Customer", "Export Data"])
        
        with tab1:
            self.show_customers_list()
        
        with tab2:
            self.add_customer_form()
        
        with tab3:
            self.edit_customer_form()
        
        with tab4:
            self.export_customers_data()
    
    def show_customers_list(self):
        """Display list of customers"""
        st.subheader("Customers List")
        
        user = st.session_state.get('user')

        # If not admin, show only their own data
        if user and not user.get('is_admin'):
            customers = []
            cust = self.customer_manager.get_customer_by_email(user.get('email'))
            if cust:
                customers = [cust]
        else:
            customers = self.customer_manager.get_all_customers()

        if not customers:
            st.info("No customers found. Add your first customer using the 'Add Customer' tab.")
            return
        
        df = pd.DataFrame(customers)
        
        # Search functionality
        search_term = st.text_input("🔍 Search customers by name, email, or phone:")
        if search_term:
            mask = (
                df['first_name'].str.contains(search_term, case=False, na=False) |
                df['last_name'].str.contains(search_term, case=False, na=False) |
                df['email'].str.contains(search_term, case=False, na=False) |
                df['phone'].str.contains(search_term, case=False, na=False)
            )
            df = df[mask]
        
        # Display customers
        if df.empty:
            st.warning("No customers match your search criteria.")
        else:
            for _, customer in df.iterrows():
                with st.expander(f"{customer['full_name']} - {customer.get('email', 'No email')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Name:** {customer['full_name']}")
                        st.write(f"**Email:** {customer.get('email', 'Not provided')}")
                        st.write(f"**Phone:** {customer.get('phone', 'Not provided')}")
                    
                    with col2:
                        st.write(f"**Address:** {customer.get('address', 'Not provided')}")
                        if customer.get('notes'):
                            st.write(f"**Notes:** {customer['notes']}")
                    
                    # Delete button
                    if st.button(f"🗑️ Delete {customer['full_name']}", key=f"delete_customer_{customer['id']}"):
                        if self.customer_manager.delete_customer(int(customer['id'])):
                            st.success(f"Customer '{customer['full_name']}' deleted successfully!")
                            try:
                                if hasattr(st, 'experimental_rerun'):
                                    st.experimental_rerun()
                                elif hasattr(st, 'rerun'):
                                    st.rerun()
                                else:
                                    st.session_state['_force_rerender'] = not st.session_state.get('_force_rerender', False)
                                    st.stop()
                            except Exception:
                                st.session_state['_force_rerender'] = not st.session_state.get('_force_rerender', False)
                                st.stop()
                        else:
                            st.error("Failed to delete customer.")
    
    def add_customer_form(self):
        """Form to add a new customer"""
        st.subheader("Add New Customer")
        
        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name *", placeholder="e.g., John")
                last_name = st.text_input("Last Name *", placeholder="e.g., Doe")
                email = st.text_input("Email", placeholder="john.doe@email.com")
                phone = st.text_input("Phone", placeholder="+1 (555) 123-4567")
            
            with col2:
                address = st.text_area("Address", placeholder="Full address...")
                notes = st.text_area("Notes", placeholder="Any special notes about the customer...")
            
            submitted = st.form_submit_button("Add Customer")
            
            if submitted:
                if first_name and last_name:
                    customer_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email or None,
                        "phone": phone or None,
                        "address": address or None,
                        "notes": notes
                    }
                    
                    if self.customer_manager.add_customer(customer_data):
                        st.success(f"Customer '{first_name} {last_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add customer.")
                else:
                    st.error("Please fill in the first name and last name (marked with *).")
    
    def edit_customer_form(self):
        """Form to edit an existing customer"""
        st.subheader("Edit Customer")
        
        customers = self.customer_manager.get_all_customers()
        
        if not customers:
            st.info("No customers available to edit.")
            return
        
        customer_options = {f"{c['full_name']} ({c.get('email', 'No email')})": c['id'] for c in customers}
        selected_customer_key = st.selectbox("Select customer to edit:", list(customer_options.keys()))
        
        if selected_customer_key:
            customer_id = customer_options[selected_customer_key]
            customer = self.customer_manager.get_customer_by_id(customer_id)
            
            if customer:
                with st.form("edit_customer_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        first_name = st.text_input("First Name *", value=customer.get('first_name', ''))
                        last_name = st.text_input("Last Name *", value=customer.get('last_name', ''))
                        email = st.text_input("Email", value=customer.get('email', '') or '')
                        phone = st.text_input("Phone", value=customer.get('phone', '') or '')
                    
                    with col2:
                        address = st.text_area("Address", value=customer.get('address', '') or '')
                        notes = st.text_area("Notes", value=customer.get('notes', '') or '')
                    
                    submitted = st.form_submit_button("Update Customer")
                    
                    if submitted:
                        if first_name and last_name:
                            updated_customer = {
                                "first_name": first_name,
                                "last_name": last_name,
                                "email": email or None,
                                "phone": phone or None,
                                "address": address or None,
                                "notes": notes
                            }
                            
                            if self.customer_manager.update_customer(customer_id, updated_customer):
                                st.success(f"Customer '{first_name} {last_name}' updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update customer.")
                        else:
                            st.error("Please fill in the first name and last name (marked with *).")
    
    def export_customers_data(self):
        """Export customers data"""
        st.subheader("Export Customers Data")
        
        customers = self.customer_manager.get_all_customers()
        
        if not customers:
            st.info("No customers data to export.")
            return
        
        df = pd.DataFrame(customers)
        
        st.write("Preview of export data:")
        st.dataframe(df)
        
        # Download button
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Customers CSV",
            data=csv_data,
            file_name="salon_customers.csv",
            mime="text/csv"
        )