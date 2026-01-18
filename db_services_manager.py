import streamlit as st
import pandas as pd
from models import DatabaseManager
from db_manager import DatabaseServiceManager
from typing import Dict


class DbServicesManager:
    def __init__(self):
        """Initialize database-backed services manager (no JSON dependency)."""
        try:
            self.db_manager = DatabaseManager()
            self.db_manager.create_tables()
            self.service_manager = DatabaseServiceManager(self.db_manager)
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            raise

    def load_data(self):
        """Load services data from the database."""
        return self.service_manager.get_all_services()
    
    def show_services_interface(self):
        """Display the services management interface"""
        st.header("🎯 Services Management")
        
        # Show database status
        st.success("✅ Connected to PostgreSQL database")
        
        # Tabs for different operations
        tab1, tab2, tab3, tab4 = st.tabs(["View Services", "Add Service", "Edit Service", "Export Data"])
        
        with tab1:
            self.show_services_list()
        
        with tab2:
            self.add_service_form()
        
        with tab3:
            self.edit_service_form()
        
        with tab4:
            self.export_services_data()
    
    def show_services_list(self):
        """Display list of services with search and filter functionality"""
        st.subheader("Services List")
        
        services = self.load_data()
        
        if not services:
            st.info("No services found. Add your first service using the 'Add Service' tab.")
            return
        
        df = pd.DataFrame(services)
        
        # Search functionality
        search_term = st.text_input("🔍 Search services by name or category:")
        if search_term:
            mask = (
                df['name'].str.contains(search_term, case=False, na=False) |
                df['category'].str.contains(search_term, case=False, na=False)
            )
            df = df[mask]
        
        # Category filter
        categories = ['All'] + sorted(df['category'].unique().tolist())
        selected_category = st.selectbox("Filter by category:", categories)
        
        if selected_category != 'All':
            df = df[df['category'] == selected_category]
        
        # Display services
        if df.empty:
            st.warning("No services match your search criteria.")
        else:
            for _, service in df.iterrows():
                with st.expander(f"{service['name']} - ${service['base_price']:.2f}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Category:** {service['category']}")
                        st.write(f"**Duration:** {service['duration']} minutes")
                        st.write(f"**Base Price:** ${service['base_price']:.2f}")
                    
                    with col2:
                        if service.get('pricing_tiers'):
                            st.write("**Pricing Tiers:**")
                            for tier in service['pricing_tiers']:
                                st.write(f"- {tier['name']}: ${tier['price']:.2f}")
                    
                    with col3:
                        if service.get('add_ons'):
                            st.write("**Add-ons:**")
                            for addon in service['add_ons']:
                                st.write(f"- {addon['name']}: +${addon['price']:.2f}")
                    
                    st.write(f"**Description:** {service.get('description', 'No description provided')}")
                    
                    # Delete button
                    if st.button(f"🗑️ Delete {service['name']}", key=f"delete_service_{service['id']}"):
                        if self._delete_service(int(service['id'])):
                            st.success(f"Service '{service['name']}' deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete service.")
    
    def add_service_form(self):
        """Form to add a new service"""
        st.subheader("Add New Service")
        
        with st.form("add_service_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Service Name *", placeholder="e.g., Hair Cut")
                category = st.text_input("Category *", placeholder="e.g., Hair Services")
                base_price = st.number_input("Base Price ($) *", min_value=0.0, step=0.01)
                duration = st.number_input("Duration (minutes) *", min_value=1, step=5, value=30)
            
            with col2:
                description = st.text_area("Description", placeholder="Describe the service...")
            
            st.subheader("Pricing Tiers (Optional)")
            num_tiers = st.number_input("Number of pricing tiers", min_value=0, max_value=5, value=0)
            
            pricing_tiers = []
            if num_tiers > 0:
                for i in range(num_tiers):
                    st.write(f"**Tier {i+1}:**")
                    tier_col1, tier_col2 = st.columns(2)
                    with tier_col1:
                        tier_name = st.text_input(f"Tier name", key=f"tier_name_{i}")
                    with tier_col2:
                        tier_price = st.number_input(f"Price ($)", min_value=0.0, step=0.01, key=f"tier_price_{i}")
                    
                    if tier_name and tier_price > 0:
                        pricing_tiers.append({"name": tier_name, "price": tier_price})
            
            st.subheader("Add-ons (Optional)")
            num_addons = st.number_input("Number of add-ons", min_value=0, max_value=10, value=0)
            
            add_ons = []
            if num_addons > 0:
                for i in range(num_addons):
                    st.write(f"**Add-on {i+1}:**")
                    addon_col1, addon_col2 = st.columns(2)
                    with addon_col1:
                        addon_name = st.text_input(f"Add-on name", key=f"addon_name_{i}")
                    with addon_col2:
                        addon_price = st.number_input(f"Price ($)", min_value=0.0, step=0.01, key=f"addon_price_{i}")
                    
                    if addon_name and addon_price > 0:
                        add_ons.append({"name": addon_name, "price": addon_price})
            
            submitted = st.form_submit_button("Add Service")
            
            if submitted:
                if name and category and base_price > 0:
                    service_data = {
                        "name": name,
                        "category": category,
                        "base_price": base_price,
                        "duration": duration,
                        "description": description,
                        "pricing_tiers": pricing_tiers,
                        "add_ons": add_ons,
                    }

                    if self._add_service(service_data):
                        st.success(f"Service '{name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add service.")
                else:
                    st.error("Please fill in all required fields (marked with *).")
    
    def edit_service_form(self):
        """Form to edit an existing service"""
        st.subheader("Edit Service")
        
        services = self.load_data()
        
        if not services:
            st.info("No services available to edit.")
            return
        
        service_options = {f"{s['name']} - {s['category']}": s['id'] for s in services}
        selected_service_key = st.selectbox("Select service to edit:", list(service_options.keys()))
        
        if selected_service_key:
            service_id = service_options[selected_service_key]
            service = self._get_service_by_id(service_id)
            
            if service:
                with st.form("edit_service_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        name = st.text_input("Service Name *", value=service.get('name', ''))
                        category = st.text_input("Category *", value=service.get('category', ''))
                        base_price = st.number_input("Base Price ($) *", min_value=0.0, step=0.01, value=service.get('base_price', 0.0))
                        duration = st.number_input("Duration (minutes) *", min_value=1, step=5, value=service.get('duration', 30))
                    
                    with col2:
                        description = st.text_area("Description", value=service.get('description', ''))
                    
                    # Edit pricing tiers
                    st.subheader("Pricing Tiers")
                    existing_tiers = service.get('pricing_tiers', [])
                    num_tiers = st.number_input("Number of pricing tiers", min_value=0, max_value=5, value=len(existing_tiers))
                    
                    pricing_tiers = []
                    for i in range(num_tiers):
                        st.write(f"**Tier {i+1}:**")
                        tier_col1, tier_col2 = st.columns(2)
                        
                        existing_tier = existing_tiers[i] if i < len(existing_tiers) else {}
                        
                        with tier_col1:
                            tier_name = st.text_input(f"Tier name", value=existing_tier.get('name', ''), key=f"edit_tier_name_{i}")
                        with tier_col2:
                            tier_price = st.number_input(f"Price ($)", min_value=0.0, step=0.01, value=existing_tier.get('price', 0.0), key=f"edit_tier_price_{i}")
                        
                        if tier_name and tier_price > 0:
                            pricing_tiers.append({"name": tier_name, "price": tier_price})
                    
                    # Edit add-ons
                    st.subheader("Add-ons")
                    existing_addons = service.get('add_ons', [])
                    num_addons = st.number_input("Number of add-ons", min_value=0, max_value=10, value=len(existing_addons))
                    
                    add_ons = []
                    for i in range(num_addons):
                        st.write(f"**Add-on {i+1}:**")
                        addon_col1, addon_col2 = st.columns(2)
                        
                        existing_addon = existing_addons[i] if i < len(existing_addons) else {}
                        
                        with addon_col1:
                            addon_name = st.text_input(f"Add-on name", value=existing_addon.get('name', ''), key=f"edit_addon_name_{i}")
                        with addon_col2:
                            addon_price = st.number_input(f"Price ($)", min_value=0.0, step=0.01, value=existing_addon.get('price', 0.0), key=f"edit_addon_price_{i}")
                        
                        if addon_name and addon_price > 0:
                            add_ons.append({"name": addon_name, "price": addon_price})
                    
                    submitted = st.form_submit_button("Update Service")
                    
                    if submitted:
                        if name and category and base_price > 0:
                            updated_service = {
                                "name": name,
                                "category": category,
                                "base_price": base_price,
                                "duration": duration,
                                "description": description,
                                "pricing_tiers": pricing_tiers,
                                "add_ons": add_ons
                            }
                            
                            if self._update_service(service_id, updated_service):
                                st.success(f"Service '{name}' updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update service.")
                        else:
                            st.error("Please fill in all required fields (marked with *).")
    
    def export_services_data(self):
        """Export services data"""
        st.subheader("Export Services Data")
        
        services = self.load_data()
        
        if not services:
            st.info("No services data to export.")
            return
        
        df = pd.DataFrame(services)
        
        # Flatten complex fields for export
        export_df = df.copy()
        
        # Convert pricing tiers to string
        if 'pricing_tiers' in export_df.columns:
            export_df['pricing_tiers'] = export_df['pricing_tiers'].apply(
                lambda x: '; '.join([f"{tier['name']}: ${tier['price']:.2f}" for tier in x]) if x else ''
            )
        
        # Convert add-ons to string
        if 'add_ons' in export_df.columns:
            export_df['add_ons'] = export_df['add_ons'].apply(
                lambda x: '; '.join([f"{addon['name']}: +${addon['price']:.2f}" for addon in x]) if x else ''
            )
        
        st.write("Preview of export data:")
        st.dataframe(export_df)
        
        # Download button
        csv_data = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Services CSV",
            data=csv_data,
            file_name="salon_services.csv",
            mime="text/csv"
        )
    
    def _add_service(self, service_data: Dict) -> bool:
        """Add service using the database manager."""
        return self.service_manager.add_service(service_data)

    def _update_service(self, service_id: int, service_data: Dict) -> bool:
        """Update service using the database manager."""
        return self.service_manager.update_service(service_id, service_data)

    def _delete_service(self, service_id: int) -> bool:
        """Delete service using the database manager."""
        return self.service_manager.delete_service(service_id)

    def _get_service_by_id(self, service_id: int) -> Dict:
        """Get service by ID using the database manager."""
        return self.service_manager.get_service_by_id(service_id) or {}