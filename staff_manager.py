import streamlit as st
import pandas as pd
from models import DatabaseManager
from db_manager import DatabaseStaffManager
from typing import List, Dict

class StaffManager:
    def __init__(self):
        try:
            self.db_manager = DatabaseManager()
            self.db_manager.create_tables()
            self.staff_manager = DatabaseStaffManager(self.db_manager)
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            self.staff_manager = None
    
    def show_staff_interface(self):
        """Display the staff management interface"""
        st.header("👩‍💼 Staff Management")
        
        if not self.staff_manager:
            st.error("Database connection unavailable")
            return
        
        # Tabs for different operations
        tab1, tab2, tab3, tab4 = st.tabs(["View Staff", "Add Staff", "Edit Staff", "Export Data"])
        
        with tab1:
            self.show_staff_list()
        
        with tab2:
            self.add_staff_form()
        
        with tab3:
            self.edit_staff_form()
        
        with tab4:
            self.export_staff_data()
    
    def show_staff_list(self):
        """Display list of staff members"""
        st.subheader("Staff Members")
        
        staff_members = self.staff_manager.get_all_staff()
        
        if not staff_members:
            st.info("No staff members found. Add your first staff member using the 'Add Staff' tab.")
            return
        
        df = pd.DataFrame(staff_members)
        
        # Search functionality
        search_term = st.text_input("🔍 Search staff by name, position, or email:")
        if search_term:
            mask = (
                df['first_name'].str.contains(search_term, case=False, na=False) |
                df['last_name'].str.contains(search_term, case=False, na=False) |
                df['position'].str.contains(search_term, case=False, na=False) |
                df['email'].str.contains(search_term, case=False, na=False)
            )
            df = df[mask]
        
        # Filter by active status
        show_active_only = st.checkbox("Show only active staff", value=True)
        if show_active_only:
            df = df[df['is_active'] == True]
        
        # Display staff
        if df.empty:
            st.warning("No staff members match your search criteria.")
        else:
            for _, staff in df.iterrows():
                status_icon = "✅" if staff['is_active'] else "❌"
                with st.expander(f"{status_icon} {staff['full_name']} - {staff.get('position', 'No position')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Name:** {staff['full_name']}")
                        st.write(f"**Position:** {staff.get('position', 'Not specified')}")
                        st.write(f"**Email:** {staff.get('email', 'Not provided')}")
                        st.write(f"**Phone:** {staff.get('phone', 'Not provided')}")
                    
                    with col2:
                        st.write(f"**Status:** {'Active' if staff['is_active'] else 'Inactive'}")
                        if staff.get('hourly_rate'):
                            st.write(f"**Hourly Rate:** ${staff['hourly_rate']:.2f}")
                        
                        if staff.get('specialties'):
                            st.write("**Specialties:**")
                            for specialty in staff['specialties']:
                                st.write(f"- {specialty}")
                    
                    with col3:
                        if staff.get('availability'):
                            st.write("**Availability:**")
                            for day, hours in staff['availability'].items():
                                st.write(f"- {day}: {hours}")
                    
                    # Action buttons
                    button_col1, button_col2 = st.columns(2)
                    
                    with button_col1:
                        # Toggle active status
                        action_text = "Deactivate" if staff['is_active'] else "Activate"
                        if st.button(f"{action_text} Staff", key=f"toggle_staff_{staff['id']}"):
                            updated_staff = dict(staff)
                            updated_staff['is_active'] = not staff['is_active']
                            if self.staff_manager.update_staff(int(staff['id']), updated_staff):
                                st.success(f"Staff member {action_text.lower()}d successfully!")
                                st.rerun()
                            else:
                                st.error(f"Failed to {action_text.lower()} staff member.")
                    
                    with button_col2:
                        # Delete button
                        if st.button(f"🗑️ Delete", key=f"delete_staff_{staff['id']}"):
                            if self.staff_manager.delete_staff(int(staff['id'])):
                                st.success(f"Staff member '{staff['full_name']}' deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete staff member.")
    
    def add_staff_form(self):
        """Form to add a new staff member"""
        st.subheader("Add New Staff Member")
        
        with st.form("add_staff_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name *", placeholder="e.g., Jane")
                last_name = st.text_input("Last Name *", placeholder="e.g., Smith")
                email = st.text_input("Email", placeholder="jane.smith@salon.com")
                phone = st.text_input("Phone", placeholder="+1 (555) 123-4567")
                position = st.text_input("Position", placeholder="e.g., Hair Stylist")
                hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, step=0.50, value=0.0)
            
            with col2:
                is_active = st.checkbox("Active Staff Member", value=True)
                
                st.subheader("Specialties")
                specialties_input = st.text_area("Specialties (one per line)", 
                                                placeholder="Hair Cutting\nHair Coloring\nManicure\nPedicure")
                
                st.subheader("Availability")
                availability = {}
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                for day in days:
                    hours = st.text_input(f"{day} Hours", 
                                        placeholder="e.g., 9:00 AM - 5:00 PM or 'Closed'",
                                        key=f"hours_{day}")
                    if hours:
                        availability[day] = hours
            
            submitted = st.form_submit_button("Add Staff Member")
            
            if submitted:
                if first_name and last_name:
                    # Process specialties
                    specialties = []
                    if specialties_input:
                        specialties = [s.strip() for s in specialties_input.split('\n') if s.strip()]
                    
                    staff_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email or None,
                        "phone": phone or None,
                        "position": position or None,
                        "hourly_rate": hourly_rate if hourly_rate > 0 else None,
                        "is_active": is_active,
                        "specialties": specialties,
                        "availability": availability
                    }
                    
                    if self.staff_manager.add_staff(staff_data):
                        st.success(f"Staff member '{first_name} {last_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add staff member.")
                else:
                    st.error("Please fill in the first name and last name (marked with *).")
    
    def edit_staff_form(self):
        """Form to edit an existing staff member"""
        st.subheader("Edit Staff Member")
        
        staff_members = self.staff_manager.get_all_staff()
        
        if not staff_members:
            st.info("No staff members available to edit.")
            return
        
        staff_options = {f"{s['full_name']} - {s.get('position', 'No position')}": s['id'] for s in staff_members}
        selected_staff_key = st.selectbox("Select staff member to edit:", list(staff_options.keys()))
        
        if selected_staff_key:
            staff_id = staff_options[selected_staff_key]
            staff = self.staff_manager.get_staff_by_id(staff_id)
            
            if staff:
                with st.form("edit_staff_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        first_name = st.text_input("First Name *", value=staff.get('first_name', ''))
                        last_name = st.text_input("Last Name *", value=staff.get('last_name', ''))
                        email = st.text_input("Email", value=staff.get('email', '') or '')
                        phone = st.text_input("Phone", value=staff.get('phone', '') or '')
                        position = st.text_input("Position", value=staff.get('position', '') or '')
                        hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, step=0.50, 
                                                    value=staff.get('hourly_rate', 0.0) or 0.0)
                    
                    with col2:
                        is_active = st.checkbox("Active Staff Member", value=staff.get('is_active', True))
                        
                        st.subheader("Specialties")
                        current_specialties = '\n'.join(staff.get('specialties', []))
                        specialties_input = st.text_area("Specialties (one per line)", 
                                                        value=current_specialties,
                                                        placeholder="Hair Cutting\nHair Coloring\nManicure\nPedicure")
                        
                        st.subheader("Availability")
                        availability = {}
                        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        current_availability = staff.get('availability', {})
                        
                        for day in days:
                            hours = st.text_input(f"{day} Hours", 
                                                value=current_availability.get(day, ''),
                                                placeholder="e.g., 9:00 AM - 5:00 PM or 'Closed'",
                                                key=f"edit_hours_{day}")
                            if hours:
                                availability[day] = hours
                    
                    submitted = st.form_submit_button("Update Staff Member")
                    
                    if submitted:
                        if first_name and last_name:
                            # Process specialties
                            specialties = []
                            if specialties_input:
                                specialties = [s.strip() for s in specialties_input.split('\n') if s.strip()]
                            
                            updated_staff = {
                                "first_name": first_name,
                                "last_name": last_name,
                                "email": email or None,
                                "phone": phone or None,
                                "position": position or None,
                                "hourly_rate": hourly_rate if hourly_rate > 0 else None,
                                "is_active": is_active,
                                "specialties": specialties,
                                "availability": availability
                            }
                            
                            if self.staff_manager.update_staff(staff_id, updated_staff):
                                st.success(f"Staff member '{first_name} {last_name}' updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update staff member.")
                        else:
                            st.error("Please fill in the first name and last name (marked with *).")
    
    def export_staff_data(self):
        """Export staff data"""
        st.subheader("Export Staff Data")
        
        staff_members = self.staff_manager.get_all_staff()
        
        if not staff_members:
            st.info("No staff data to export.")
            return
        
        df = pd.DataFrame(staff_members)
        
        # Flatten complex fields for export
        export_df = df.copy()
        
        # Convert specialties to string
        if 'specialties' in export_df.columns:
            export_df['specialties'] = export_df['specialties'].apply(
                lambda x: '; '.join(x) if x else ''
            )
        
        # Convert availability to string
        if 'availability' in export_df.columns:
            export_df['availability'] = export_df['availability'].apply(
                lambda x: '; '.join([f"{day}: {hours}" for day, hours in x.items()]) if x else ''
            )
        
        st.write("Preview of export data:")
        st.dataframe(export_df)
        
        # Download button
        csv_data = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Staff CSV",
            data=csv_data,
            file_name="salon_staff.csv",
            mime="text/csv"
        )