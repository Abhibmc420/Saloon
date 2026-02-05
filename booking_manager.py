import streamlit as st
import pandas as pd
from models import DatabaseManager, Booking, Invoice
from db_manager import DatabaseCustomerManager, DatabaseServiceManager, DatabaseStaffManager
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional
import calendar

class BookingManager:
    def __init__(self):
        try:
            self.db_manager = DatabaseManager()
            self.db_manager.create_tables()
            
            # Initialize sub-managers
            self.customer_manager = DatabaseCustomerManager(self.db_manager)
            self.service_manager = DatabaseServiceManager(self.db_manager)
            self.staff_manager = DatabaseStaffManager(self.db_manager)
            
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            self.db_manager = None
    
    def show_booking_interface(self):
        """Display the booking management interface"""
        st.header("📅 Appointment Booking System")
        
        if not self.db_manager:
            st.error("Database connection unavailable")
            return
        
        # Tabs for different operations
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Calendar View", "New Booking", "Request Booking", "Manage Bookings", "Today's Schedule", "Export Data"]) 
        
        with tab1:
            self.show_calendar_view()
        
        with tab2:
            self.create_booking_form()
        
        with tab3:
            self.request_booking_form()
        
        with tab4:
            self.manage_bookings()
        
        with tab5:
            self.show_todays_schedule()
        
        with tab6:
            self.export_bookings_data()
    
    def show_calendar_view(self):
        """Display calendar view of bookings"""
        st.subheader("📅 Calendar View")
        
        # Date selector
        selected_date = st.date_input("Select Date", datetime.now().date())
        
        # Get bookings for selected date
        bookings = self.get_bookings_by_date(selected_date)

        # If user is not admin, filter to their bookings only
        user = st.session_state.get('user')
        if user and not user.get('is_admin'):
            cust = self.customer_manager.get_customer_by_email(user.get('email'))
            if cust:
                bookings = [b for b in bookings if b['customer_id'] == cust['id']]
            else:
                bookings = []

        if not bookings:
            st.info(f"No appointments scheduled for {selected_date.strftime('%B %d, %Y')}")
            return
        
        # Display time slots
        st.write(f"**Appointments for {selected_date.strftime('%B %d, %Y')}:**")
        
        # Sort bookings by time
        sorted_bookings = sorted(bookings, key=lambda x: x['appointment_datetime'])
        
        for booking in sorted_bookings:
            appointment_time = booking['appointment_datetime']
            end_time = booking['end_datetime']
            
            # Status indicator
            status_color = {
                'scheduled': '🟡',
                'completed': '✅',
                'cancelled': '❌',
                'no_show': '🔴'
            }
            
            status_icon = status_color.get(booking['status'], '⚪')
            
            with st.expander(f"{status_icon} {appointment_time.strftime('%I:%M %p')} - {booking['customer_name']} ({booking['service_name']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Customer:** {booking['customer_name']}")
                    st.write(f"**Service:** {booking['service_name']}")
                    st.write(f"**Duration:** {booking['duration']} min")
                    st.write(f"**Price:** ${booking['total_price']:.2f}")
                
                with col2:
                    st.write(f"**Staff:** {booking.get('staff_name', 'Unassigned')}")
                    st.write(f"**Status:** {booking['status'].replace('_', ' ').title()}")
                    st.write(f"**Payment:** {booking['payment_status'].replace('_', ' ').title()}")
                
                with col3:
                    if booking.get('notes'):
                        st.write(f"**Notes:** {booking['notes']}")
                    
                    # Quick status updates
                    if booking['status'] == 'scheduled':
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            if st.button("Mark Complete", key=f"complete_{booking['id']}"):
                                self.update_booking_status(booking['id'], 'completed')
                                st.rerun()
                        with col_b:
                            if st.button("Mark No-Show", key=f"noshow_{booking['id']}"):
                                self.update_booking_status(booking['id'], 'no_show')
                                st.rerun()
                        with col_c:
                            # Invoice / payment actions (admin or owner)
                            from db_manager import DatabaseInvoiceManager
                            dm = self.db_manager
                            inv_mgr = DatabaseInvoiceManager(dm)
                            # find existing invoice for booking
                            session = dm.get_session()
                            try:
                                inv = session.query(Invoice).filter(Invoice.booking_id == booking['id']).first()
                            finally:
                                session.close()

                            if inv:
                                if st.button(f"View Invoice ({inv.invoice_number})", key=f"view_inv_{inv.id}"):
                                    # show invoice details
                                    st.write(f"**Invoice:** {inv.invoice_number}")
                                    st.write(f"**Amount:** {inv.amount} {inv.currency}")
                                    st.write(f"**Status:** {inv.status}")
                                    if inv.upi_qr:
                                        st.image(inv.upi_qr)
                                    if inv.status != 'paid':
                                        if st.button('Mark Paid (manual)', key=f"markpaid_{inv.id}"):
                                            inv_mgr.mark_paid(inv.id)
                                            st.success('Marked invoice as paid')
                                            safe_rerun()
                            else:
                                if st.button('Generate Invoice', key=f'gen_inv_{booking["id"]}'):
                                    # generate a UPI invoice
                                    # default merchant UPI id (for testing)
                                    merchant_upi = os.getenv('MERCHANT_UPI', 'merchant@upi')
                                    merchant_name = os.getenv('MERCHANT_NAME', 'NeerJazz')
                                    # generate upi uri
                                    upi_uri = build_upi_uri(merchant_upi, merchant_name, booking['total_price'], tn=f"Booking {booking['id']}")
                                    # save QR image
                                    qr_path = f"invoices/qr_{booking['id']}.png"
                                    import os as _os
                                    _os.makedirs('invoices', exist_ok=True)
                                    from payments import save_qr_to_file
                                    save_qr_to_file(upi_uri, qr_path)
                                    inv = inv_mgr.create_invoice(booking['id'], booking['total_price'], upi_uri=upi_uri, upi_qr=qr_path)
                                    if inv:
                                        st.success('Invoice generated')
                                        safe_rerun()
    
    def create_booking_form(self):
        """Form to create a new booking (internal use by staff/admin)"""
        st.subheader("📝 New Appointment Booking")
        
        # Get available customers, services, and staff
        customers = self.customer_manager.get_all_customers()
        services = self.service_manager.get_all_services()
        staff_members = [s for s in self.staff_manager.get_all_staff() if s['is_active']]
        
        if not customers:
            st.warning("No customers available. Please add customers first.")
            return
        
        if not services:
            st.warning("No services available. Please add services first.")
            return
        
        with st.form("new_booking_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Customer selection
                customer_options = {f"{c['full_name']} ({c.get('email', 'No email')})": c['id'] for c in customers}
                selected_customer = st.selectbox("Select Customer *", list(customer_options.keys()))
                customer_id = customer_options[selected_customer] if selected_customer else None
                
                # Service selection
                service_options = {f"{s['name']} - ${s['base_price']:.2f} ({s['duration']} min)": s['id'] for s in services}
                selected_service = st.selectbox("Select Service *", list(service_options.keys()))
                service_id = service_options[selected_service] if selected_service else None
                
                # Get selected service details
                selected_service_data = next((s for s in services if s['id'] == service_id), None) if service_id else None
                
                # Date and time
                appointment_date = st.date_input("Appointment Date *", min_value=datetime.now().date())
                appointment_time = st.time_input("Appointment Time *", value=time(9, 0))
            
            with col2:
                # Staff selection (optional)
                if staff_members:
                    staff_options = {f"{s['full_name']} ({s.get('position', 'Staff')})": s['id'] for s in staff_members}
                    staff_options_list = ["Unassigned"] + list(staff_options.keys())
                    selected_staff = st.selectbox("Assign Staff Member", staff_options_list)
                    staff_id = None
                    if selected_staff != "Unassigned":
                        staff_id = staff_options.get(selected_staff)
                else:
                    st.info("No active staff members available")
                    staff_id = None
                
                # Pricing
                if selected_service_data:
                    base_price = selected_service_data['base_price']
                    duration = selected_service_data['duration']
                    
                    # Add-ons selection
                    selected_addons = []
                    if selected_service_data.get('add_ons'):
                        st.write("**Available Add-ons:**")
                        for addon in selected_service_data['add_ons']:
                            if st.checkbox(f"{addon['name']} (+${addon['price']:.2f})", key=f"addon_{addon['name']}"):
                                selected_addons.append(addon)
                    
                    # Calculate total price
                    addon_total = sum(addon['price'] for addon in selected_addons)
                    total_price = base_price + addon_total
                    
                    st.write(f"**Base Price:** ${base_price:.2f}")
                    if addon_total > 0:
                        st.write(f"**Add-ons:** ${addon_total:.2f}")
                    st.write(f"**Total Price:** ${total_price:.2f}")
                    st.write(f"**Duration:** {duration} minutes")
                else:
                    total_price = 0
                    duration = 30
                    selected_addons = []
                
                # Notes
                notes = st.text_area("Notes", placeholder="Any special instructions or notes...")
            
            submitted = st.form_submit_button("Create Booking")
            
            if submitted:
                if customer_id and service_id and appointment_date and appointment_time:
                    # Combine date and time
                    appointment_datetime = datetime.combine(appointment_date, appointment_time)
                    end_datetime = appointment_datetime + timedelta(minutes=duration)
                    
                    # Check for conflicts
                    if self.check_booking_conflict(appointment_datetime, end_datetime, staff_id):
                        st.error("Time slot conflict! Please choose a different time.")
                        return
                    
                    booking_data = {
                        'customer_id': customer_id,
                        'service_id': service_id,
                        'staff_id': staff_id,
                        'appointment_datetime': appointment_datetime,
                        'end_datetime': end_datetime,
                        'total_price': total_price,
                        'notes': notes,
                        'add_ons': selected_addons,
                        'status': 'scheduled',
                        'payment_status': 'pending'
                    }
                    
                    if self.create_booking(booking_data):
                        st.success("Booking created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create booking.")
                else:
                    st.error("Please fill in all required fields (marked with *).")
    
    def manage_bookings(self):
        """Manage existing bookings"""
        st.subheader("📋 Manage Bookings")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Filter by Status", 
                                       ["All", "Scheduled", "Completed", "Cancelled", "No Show"])
        
        with col2:
            date_from = st.date_input("From Date", datetime.now().date() - timedelta(days=7))
        
        with col3:
            date_to = st.date_input("To Date", datetime.now().date() + timedelta(days=7))
        
        # Get filtered bookings
        bookings = self.get_filtered_bookings(status_filter, date_from, date_to)

        # If non-admin user, limit to their bookings
        user = st.session_state.get('user')
        if user and not user.get('is_admin'):
            cust = self.customer_manager.get_customer_by_email(user.get('email'))
            if cust:
                bookings = [b for b in bookings if b['customer_id'] == cust['id']]
            else:
                bookings = []

        if not bookings:
            st.info("No bookings found matching the criteria.")
            return
        
        # Display bookings
        for booking in bookings:
            appointment_time = booking['appointment_datetime']
            
            with st.expander(f"{appointment_time.strftime('%m/%d %I:%M %p')} - {booking['customer_name']} ({booking['service_name']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Booking details
                    st.write(f"**Customer:** {booking['customer_name']}")
                    st.write(f"**Service:** {booking['service_name']}")
                    st.write(f"**Staff:** {booking.get('staff_name', 'Unassigned')}")
                    st.write(f"**Date:** {appointment_time.strftime('%B %d, %Y')}")
                    st.write(f"**Time:** {appointment_time.strftime('%I:%M %p')} - {booking['end_datetime'].strftime('%I:%M %p')}")
                    st.write(f"**Price:** ${booking['total_price']:.2f}")
                
                with col2:
                    # Status and actions
                    new_status = st.selectbox("Status", 
                                            ["scheduled", "completed", "cancelled", "no_show"],
                                            index=["scheduled", "completed", "cancelled", "no_show"].index(booking['status']),
                                            key=f"status_{booking['id']}")
                    
                    new_payment_status = st.selectbox("Payment", 
                                                    ["pending", "paid", "refunded"],
                                                    index=["pending", "paid", "refunded"].index(booking['payment_status']),
                                                    key=f"payment_{booking['id']}")
                    
                    if booking.get('notes'):
                        st.write(f"**Notes:** {booking['notes']}")
                    
                    # Update buttons
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("Update", key=f"update_{booking['id']}"):
                            self.update_booking(booking['id'], {
                                'status': new_status,
                                'payment_status': new_payment_status
                            })
                            st.success("Booking updated!")
                            st.rerun()
                    
                    with col_b:
                        if st.button("Delete", key=f"delete_{booking['id']}"):
                            if self.delete_booking(booking['id']):
                                st.success("Booking deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete booking.")
    
    def show_todays_schedule(self):
        """Show today's appointment schedule"""
        st.subheader("📋 Today's Schedule")
        
        today = datetime.now().date()
        bookings = self.get_bookings_by_date(today)
        
        if not bookings:
            st.info("No appointments scheduled for today.")
            return
        
        # Group by staff
        staff_bookings = {}
        unassigned_bookings = []
        
        for booking in bookings:
            staff_name = booking.get('staff_name', 'Unassigned')
            if staff_name == 'Unassigned':
                unassigned_bookings.append(booking)
            else:
                if staff_name not in staff_bookings:
                    staff_bookings[staff_name] = []
                staff_bookings[staff_name].append(booking)
        
        # Display by staff member
        for staff_name, bookings_list in staff_bookings.items():
            st.write(f"**{staff_name}:**")
            sorted_bookings = sorted(bookings_list, key=lambda x: x['appointment_datetime'])
            
            for booking in sorted_bookings:
                time_str = booking['appointment_datetime'].strftime('%I:%M %p')
                end_time_str = booking['end_datetime'].strftime('%I:%M %p')
                status_icon = {'scheduled': '🟡', 'completed': '✅', 'cancelled': '❌', 'no_show': '🔴'}.get(booking['status'], '⚪')
                
                st.write(f"  {status_icon} {time_str}-{end_time_str}: {booking['customer_name']} - {booking['service_name']}")
        
        # Unassigned bookings
        if unassigned_bookings:
            st.write("**Unassigned:**")
            sorted_unassigned = sorted(unassigned_bookings, key=lambda x: x['appointment_datetime'])
            
            for booking in sorted_unassigned:
                time_str = booking['appointment_datetime'].strftime('%I:%M %p')
                end_time_str = booking['end_datetime'].strftime('%I:%M %p')
                status_icon = {'scheduled': '🟡', 'completed': '✅', 'cancelled': '❌', 'no_show': '🔴'}.get(booking['status'], '⚪')
                
                st.write(f"  {status_icon} {time_str}-{end_time_str}: {booking['customer_name']} - {booking['service_name']}")
    
    def request_booking_form(self):
        """Form for end-users to request a booking (creates a 'requested' booking)"""
        st.subheader("📨 Request an Appointment")

        # Brief intro
        st.markdown("""
        <div style='margin-bottom:8px;'>
            <small>Fill out the form below and we'll confirm your appointment shortly. Prefer a specific staff member? Choose below (optional).</small>
        </div>
        """, unsafe_allow_html=True)

        # If user is signed in, pre-fill name and email
        user = st.session_state.get('user')

        service_list = self.service_manager.get_all_services()
        if not service_list:
            st.info('No services available at the moment.')
            return

        staff_members = [s for s in self.staff_manager.get_all_staff() if s.get('is_active')]

        # Styled container
        st.markdown("""
            <style>
            .form-card { padding:16px; border-radius:8px; background: #ffffff; box-shadow: 0 6px 18px rgba(0,0,0,0.06); }
            .summary-card { padding:12px; border-radius:8px; background: linear-gradient(180deg, #fff8f0, #fff0f6); border:1px solid rgba(0,0,0,0.03); }
            .muted { color: #6b6b6b; font-size:12px }
            </style>
        """, unsafe_allow_html=True)

        with st.form('request_booking_form'):
            col_left, col_right = st.columns([2, 1])

            with col_left:
                with st.container():
                    st.markdown("<div class='form-card'>", unsafe_allow_html=True)
                    name = st.text_input('Full name *', value=(user.get('full_name') if user else ''), placeholder='Jane Doe')
                    email = st.text_input('Email *', value=(user.get('email') if user else ''), placeholder='you@example.com')
                    phone = st.text_input('Phone (optional)', placeholder='+1 555 123 4567')

                    # Service selection with compact display
                    service_options = {s['id']: s for s in service_list}
                    service_labels = [f"{s['name']} — ${s['base_price']:.2f} ({s.get('duration', 30)} mins)" for s in service_list]
                    selected_service_label = st.selectbox('Select Service *', service_labels)
                    selected_service = next((s for s in service_list if f"{s['name']} — ${s['base_price']:.2f} ({s.get('duration', 30)} mins)" == selected_service_label), service_list[0])

                    # Preferred staff
                    staff_options = ['No preference'] + [f"{s.get('first_name','')} {s.get('last_name','')}" for s in staff_members]
                    preferred_staff = st.selectbox('Preferred Staff (optional)', staff_options)

                    # Date and time in a compact row
                    dcol1, dcol2 = st.columns(2)
                    with dcol1:
                        appointment_date = st.date_input('Preferred Date *', min_value=datetime.now().date())
                    with dcol2:
                        appointment_time = st.time_input('Preferred Time *', value=time(9, 0))

                    notes = st.text_area('Notes / Preferences', placeholder='Any additional details (allergies, preferred stylist vibe, etc.)')

                    st.markdown("<div class='muted'>By requesting, you agree to our <a href='#'>booking & cancellation policy</a>.</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            with col_right:
                # Booking summary card
                st.markdown("<div class='summary-card'>", unsafe_allow_html=True)
                st.write("### Your Request")
                st.write(f"**Service:** {selected_service.get('name')} — ${selected_service.get('base_price'):.2f}")
                st.write(f"**Duration:** {selected_service.get('duration', 30)} minutes")

                # Show description if available
                if selected_service.get('description'):
                    st.write(f"**About:** {selected_service.get('description')}")

                st.write('---')
                st.write(f"**Preferred Date:** {appointment_date.strftime('%Y-%m-%d') if isinstance(appointment_date, datetime) else appointment_date}")
                st.write(f"**Preferred Time:** {appointment_time.strftime('%I:%M %p') if isinstance(appointment_time, time) else appointment_time}")

                # Calculate end time preview
                try:
                    start_dt = datetime.combine(appointment_date, appointment_time)
                    end_dt = start_dt + timedelta(minutes=selected_service.get('duration', 30))
                    st.write(f"**Estimated End:** {end_dt.strftime('%I:%M %p')}")
                except Exception:
                    pass

                if preferred_staff and preferred_staff != 'No preference':
                    st.write(f"**Preferred Staff:** {preferred_staff}")

                st.write('---')
                st.write(f"**Estimated Total:** **${selected_service.get('base_price'):.2f}**")
                st.markdown("</div>", unsafe_allow_html=True)

            submitted = st.form_submit_button('Request Booking')

            if submitted:
                # Basic validation
                if not name or not email:
                    st.error('Please provide your name and email.')
                    return
                if '@' not in email or '.' not in email:
                    st.error('Please provide a valid email address.')
                    return

                # Create or find customer
                parts = name.split()
                first_name = parts[0]
                last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
                customer = self.customer_manager.get_or_create_customer_by_email(email, first_name, last_name)

                appointment_datetime = datetime.combine(appointment_date, appointment_time)
                end_datetime = appointment_datetime + timedelta(minutes=selected_service.get('duration', 30))

                # Map preferred staff name back to staff_id
                staff_id = None
                if preferred_staff and preferred_staff != 'No preference':
                    # Attempt to find staff member id
                    match = next((s for s in staff_members if f"{s.get('first_name','')} {s.get('last_name','')}" == preferred_staff), None)
                    if match:
                        staff_id = match.get('id')

                booking_data = {
                    'customer_id': customer['id'],
                    'service_id': selected_service.get('id'),
                    'staff_id': staff_id,
                    'appointment_datetime': appointment_datetime,
                    'end_datetime': end_datetime,
                    'total_price': selected_service.get('base_price', 0.0),
                    'notes': notes,
                    'add_ons': [],
                    'status': 'requested',
                    'payment_status': 'pending'
                }

                if self.create_booking(booking_data):
                    st.success('✅ Your booking request has been submitted. An admin will review and confirm it.')
                    st.info('We have sent a confirmation email (if provided) and will reach out if there are questions.')

                    # Show a compact summary with reference
                    ref = f"REQ-{int(datetime.now().timestamp())}"
                    st.markdown("<div style='margin-top:12px;padding:12px;border-radius:6px;background:#f6fffa;border:1px solid #e6ffef;'>", unsafe_allow_html=True)
                    st.write(f"**Reference:** {ref}")
                    st.write(f"**Name:** {name}")
                    st.write(f"**Email:** {email}")
                    st.write(f"**Service:** {selected_service.get('name')}")
                    st.write(f"**Date / Time:** {appointment_date} {appointment_time.strftime('%I:%M %p')}")
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error('Failed to submit booking request. Please try again later.')

    def export_bookings_data(self):
        """Export bookings data"""
        st.subheader("Export Bookings Data")
        
        # Date range for export
        col1, col2 = st.columns(2)
        with col1:
            export_from = st.date_input("Export From", datetime.now().date() - timedelta(days=30))
        with col2:
            export_to = st.date_input("Export To", datetime.now().date() + timedelta(days=30))
        
        bookings = self.get_filtered_bookings("All", export_from, export_to)
        
        if not bookings:
            st.info("No bookings data to export.")
            return
        
        df = pd.DataFrame(bookings)
        
        st.write("Preview of export data:")
        st.dataframe(df)
        
        # Download button
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Bookings CSV",
            data=csv_data,
            file_name=f"salon_bookings_{export_from}_{export_to}.csv",
            mime="text/csv"
        )
    
    # Database methods
    def get_bookings_by_date(self, date) -> List[Dict]:
        """Get all bookings for a specific date"""
        session = self.db_manager.get_session()
        try:
            start_datetime = datetime.combine(date, datetime.min.time())
            end_datetime = datetime.combine(date, datetime.max.time())
            
            bookings = session.query(Booking).filter(
                Booking.appointment_datetime >= start_datetime,
                Booking.appointment_datetime <= end_datetime
            ).all()
            
            return [self._booking_to_dict(booking, session) for booking in bookings]
        finally:
            session.close()
    
    def get_filtered_bookings(self, status_filter: str, date_from, date_to) -> List[Dict]:
        """Get filtered bookings"""
        session = self.db_manager.get_session()
        try:
            query = session.query(Booking).filter(
                Booking.appointment_datetime >= datetime.combine(date_from, datetime.min.time()),
                Booking.appointment_datetime <= datetime.combine(date_to, datetime.max.time())
            )
            
            if status_filter != "All":
                query = query.filter(Booking.status == status_filter.lower().replace(' ', '_'))
            
            bookings = query.all()
            return [self._booking_to_dict(booking, session) for booking in bookings]
        finally:
            session.close()
    
    def create_booking(self, booking_data: Dict) -> bool:
        """Create a new booking"""
        session = self.db_manager.get_session()
        try:
            booking = Booking(**booking_data)
            session.add(booking)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error creating booking: {e}")
            return False
        finally:
            session.close()
    
    def update_booking_status(self, booking_id: int, status: str) -> bool:
        """Update booking status"""
        return self.update_booking(booking_id, {'status': status})
    
    def update_booking(self, booking_id: int, updates: Dict) -> bool:
        """Update booking"""
        session = self.db_manager.get_session()
        try:
            booking = session.query(Booking).filter(Booking.id == booking_id).first()
            if not booking:
                return False
            
            for key, value in updates.items():
                setattr(booking, key, value)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error updating booking: {e}")
            return False
        finally:
            session.close()
    
    def delete_booking(self, booking_id: int) -> bool:
        """Delete booking"""
        session = self.db_manager.get_session()
        try:
            booking = session.query(Booking).filter(Booking.id == booking_id).first()
            if not booking:
                return False
            
            session.delete(booking)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error deleting booking: {e}")
            return False
        finally:
            session.close()
    
    def check_booking_conflict(self, start_time: datetime, end_time: datetime, staff_id: Optional[int]) -> bool:
        """Check if booking time conflicts with existing bookings"""
        session = self.db_manager.get_session()
        try:
            query = session.query(Booking).filter(
                Booking.status.in_(['scheduled']),  # Only check against scheduled bookings
                Booking.appointment_datetime < end_time,
                Booking.end_datetime > start_time
            )
            
            if staff_id:
                query = query.filter(Booking.staff_id == staff_id)
            
            conflicts = query.count()
            return conflicts > 0
        finally:
            session.close()
    
    def _booking_to_dict(self, booking: Booking, session) -> Dict:
        """Convert booking model to dictionary with related data"""
        # Get related objects
        customer = booking.customer
        service = booking.service
        staff = booking.staff_member
        
        return {
            'id': booking.id,
            'customer_id': booking.customer_id,
            'customer_name': f"{customer.first_name} {customer.last_name}" if customer else "Unknown",
            'service_id': booking.service_id,
            'service_name': service.name if service else "Unknown",
            'staff_id': booking.staff_id,
            'staff_name': f"{staff.first_name} {staff.last_name}" if staff else None,
            'appointment_datetime': booking.appointment_datetime,
            'end_datetime': booking.end_datetime,
            'duration': int((booking.end_datetime - booking.appointment_datetime).total_seconds() / 60),
            'status': booking.status,
            'total_price': booking.total_price,
            'payment_status': booking.payment_status,
            'payment_method': booking.payment_method,
            'notes': booking.notes,
            'add_ons': booking.add_ons or []
        }