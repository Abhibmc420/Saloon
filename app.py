import streamlit as st
import os
from dotenv import load_dotenv
from db_services_manager import DbServicesManager
from db_products_manager import DbProductsManager
from customer_manager import CustomerManager
from staff_manager import StaffManager
from booking_manager import BookingManager
from dashboard import Dashboard
from admin_manager import AdminManager


# Helper to safely trigger a rerun across Streamlit versions
def safe_rerun():
    """Call Streamlit's rerun if available, otherwise toggle a session flag and stop to force re-render.

    Tries in order: st.experimental_rerun(), st.rerun(), then fallback to toggling a session flag + st.stop().
    """
    try:
        # Preferred modern API
        if hasattr(st, 'experimental_rerun'):
            return st.experimental_rerun()
        # Some versions have st.rerun()
        if hasattr(st, 'rerun'):
            return st.rerun()
    except Exception:
        # If the call raises, fall back to session toggle
        pass

    # Final safe fallback
    st.session_state['_force_rerender'] = not st.session_state.get('_force_rerender', False)
    st.stop()

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

    # Set a default current page so navigation persists
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Dashboard"

def main():
    st.set_page_config(
        page_title="NeerJazz Salon Management System",
        page_icon="💄",
        layout="wide"
    )
   
    # Initialize session state
    initialize_session_state()
    
    st.title("💄NeerJazz Salon Management System")
    
    # If no user is signed in, show landing/about + login area only
    if not st.session_state.get('user'):
        # Branding area: logo and title
        logo_path = os.getenv('LOGO_PATH', r'H:\Company Setup\Project\Neerjazz_MakeOverSaloon\Celebrity Pics\logo.png')
        hero_dir = os.getenv('HERO_IMAGES_PATH', r'H:\Company Setup\Project\Neerjazz_MakeOverSaloon\Celebrity Pics')

        col_logo, col_title = st.columns([1, 4])
        with col_logo:
            try:
                if logo_path and os.path.exists(logo_path):
                    st.image(logo_path, width=140)
                else:
                    st.markdown("**NeerJazz Makeovers**")
            except Exception:
                st.markdown("**NeerJazz Makeovers**")

        with col_title:
            st.title("NeerJazz Salon Management System")
            st.subheader('Welcome to NeerJazz — Beauty and Relaxation')
            st.write('NeerJazz offers premium salon services including hair, nails, makeup, and spa treatments. Request an appointment below or sign in to manage bookings.')

        # Hero area: show a vibrant banner and static hero images grid (no marquee)
        st.markdown('---')
        try:
            # Gather up to 8 hero images for the collage
            image_files = []
            if hero_dir and os.path.isdir(hero_dir):
                for fname in sorted(os.listdir(hero_dir)):
                    if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        full = os.path.join(hero_dir, fname)
                        image_files.append(full)
                        if len(image_files) >= 8:
                            break

            # Enhanced hero banner with big CTA
            st.markdown(
                "<div style='background: linear-gradient(90deg, #ff6f61, #ffb347); padding:24px; border-radius:12px; color:#ffffff; display:flex; align-items:center; justify-content:space-between;'>"
                "<div style=\"padding-right:16px;\">"
                "<h1 style=\"margin:0; font-size:28px;\">Experience Luxury Makeovers<span style=\"font-size:22px; margin-left:10px;\">✨</span></h1>"
                "<p style=\"margin:4px 0 0; opacity:0.95;\">Premium hair, makeup & spa services — curated for you. Book a personalized appointment today.</p>"
                "</div>"
                "<div>"
                "<a href=\"#\" style=\"background:#ffffff;color:#ff6f61;padding:10px 18px;border-radius:10px;font-weight:700;text-decoration:none;box-shadow:0 8px 20px rgba(0,0,0,0.12);\">Book Now</a>"
                "</div>"
                "</div>",
                unsafe_allow_html=True
            )

            # Collage layout for hero images (nice, irregular grid with small rotations)
            def _to_data_uri(path):
                import base64, mimetypes
                try:
                    with open(path, 'rb') as fh:
                        data = fh.read()
                    mime = mimetypes.guess_type(path)[0] or 'image/png'
                    return f"data:{mime};base64,{base64.b64encode(data).decode()}"
                except Exception:
                    return None

            def _render_collage(img_paths):
                css = """
                <style>
                .collage-wrapper{margin-top:18px;margin-bottom:12px;display:flex;justify-content:center}
                .collage{display:grid;grid-template-columns:repeat(12,1fr);grid-auto-rows:200px;gap:14px;align-items:stretch;max-width:1260px;margin:0 auto}
                .collage .tile{overflow:hidden;border-radius:12px;background:#fff;position:relative}
                .collage img{width:100%;height:100%;object-fit:cover;border-radius:12px;box-shadow:0 12px 30px rgba(0,0,0,0.18);transition:transform .35s, filter .35s;display:block}
                .collage .tile:hover img{transform:scale(1.04);filter:brightness(1.04)}
                .tile-large{grid-column:span 6;grid-row:span 2}
                .tile-medium{grid-column:span 4;grid-row:span 2}
                .tile-small{grid-column:span 3;grid-row:span 1}
                .tile-caption{position:absolute;left:12px;bottom:12px;background:rgba(0,0,0,0.6);color:#fff;padding:6px 10px;border-radius:6px;font-size:13px;opacity:0;transform:translateY(8px);transition:opacity .28s, transform .28s}
                .tile:hover .tile-caption{opacity:1;transform:translateY(0)}
                .featured-badge{position:absolute;top:12px;right:12px;background:linear-gradient(90deg,#ffd166,#ff6b6b);color:#fff;padding:6px 10px;border-radius:999px;font-size:12px;font-weight:700;box-shadow:0 6px 18px rgba(0,0,0,0.12)}
                @media(max-width:1100px){.collage{grid-template-columns:repeat(6,1fr);grid-auto-rows:180px}}
                @media(max-width:768px){.collage{grid-template-columns:repeat(2,1fr);grid-auto-rows:160px}}
                </style>
                """
                tiles = []
                # Assign a varied layout to make a collage feeling (larger/clearer tiles)
                layout = ['tile-large','tile-medium','tile-medium','tile-large','tile-medium','tile-small','tile-small','tile-small']

                # Configuration: badge text and which images are 'featured' (comma-separated basenames)
                badge_text = os.getenv('FEATURED_BADGE_TEXT', 'Featured')
                featured_list_env = os.getenv('HERO_FEATURED_IMAGES', '')
                featured_set = set([f.strip() for f in featured_list_env.split(',') if f.strip()]) if featured_list_env else set()

                for i, p in enumerate(img_paths):
                    data = _to_data_uri(p)
                    if not data:
                        continue
                    cls = layout[i] if i < len(layout) else 'tile-small'
                    caption = os.path.basename(p)

                    # Determine featured status: explicit list wins; otherwise fallback to first image
                    is_featured = (caption in featured_set) if featured_set else (i == 0)
                    badge_html = f'<div class="featured-badge">{badge_text}</div>' if is_featured else ''
                    dot_html = '<div class="featured-dot"></div>' if is_featured else ''

                    tiles.append(f'<div class="tile {cls}">{badge_html}{dot_html}<img src="{data}" alt="{caption}" loading="lazy"/><div class="tile-caption">{caption}</div></div>')

                html = f"<div class='collage-wrapper'>{css}<div class='collage'>{''.join(tiles)}</div></div>"
                st.markdown(html, unsafe_allow_html=True)

            if image_files:
                _render_collage(image_files)

                # CTA buttons under collage
                c1, c2, c3 = st.columns([1.5, 1, 1])
                with c1:
                    st.markdown("**Want an appointment now?**")
                    if st.button('Request Appointment', key='cta_request'):
                        st.session_state['current_page'] = 'Appointment Booking'
                        safe_rerun()
                with c2:
                    if st.button('View Services', key='cta_services'):
                        st.session_state['current_page'] = 'Services Management'
                        safe_rerun()
                with c3:
                    if st.button('Contact Us', key='cta_contact'):
                        st.info('You can reach us at support@neerjazz.example or use the Contact section in the Admin Panel.')

                # Quick Book Now action (keeps the link but also provides a button to open inline compact form)
                if st.button('Book Now (Quick)', key='banner_book_now'):
                    st.session_state['show_inline_booking'] = True
                    safe_rerun()

                # Render inline compact booking form when requested
                if st.session_state.get('show_inline_booking'):
                    # anchor for direct links
                    st.markdown("<a id='booking'></a>", unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown("#### Quick Booking — Compact Form")

                    # Load services and products
                    try:
                        services = st.session_state.get('services_manager').load_data() if st.session_state.get('services_manager') else []
                    except Exception:
                        services = []

                    try:
                        products = st.session_state.get('products_manager').load_data() if st.session_state.get('products_manager') else []
                    except Exception:
                        products = []

                    # Compact form layout
                    with st.form('collage_booking_form'):
                        col_l, col_r = st.columns([2, 1])
                        with col_l:
                            name = st.text_input('Full name *', placeholder='Jane Doe')
                            email = st.text_input('Email *', placeholder='you@example.com')
                            phone = st.text_input('Phone (optional)', placeholder='+1 555 123 4567')

                            if services:
                                service_labels = [f"{s['name']} — ${s['base_price']:.2f} ({s.get('duration',30)}m)" for s in services]
                                selected_service_label = st.selectbox('Service *', service_labels)
                                selected_service = next((s for s in services if f"{s['name']} — ${s['base_price']:.2f} ({s.get('duration',30)}m)" == selected_service_label), services[0])
                            else:
                                st.warning('No services available at the moment.')
                                selected_service = None

                            # Products dropdown (professional display)
                            if products:
                                product_options = [f"{p['name']} — {p.get('brand','')} (${p.get('selling_price',0):.2f}) [Stock: {p.get('quantity',0)}]" for p in products]
                                selected_products = st.multiselect('Add Product(s) (optional)', product_options)
                                # Resolve selected product dicts
                                selected_products_objs = [p for p in products if f"{p['name']} — {p.get('brand','')} (${p.get('selling_price',0):.2f}) [Stock: {p.get('quantity',0)}]" in selected_products]
                            else:
                                selected_products = []
                                selected_products_objs = []

                            dcol1, dcol2 = st.columns(2)
                            with dcol1:
                                appointment_date = st.date_input('Preferred Date *')
                            with dcol2:
                                appointment_time = st.time_input('Preferred Time *')

                            notes = st.text_area('Notes (optional)', placeholder='Any preferences or details...')

                        with col_r:
                            st.markdown('<div style="padding:12px;border-radius:8px;background:#fff7f8;border:1px solid rgba(0,0,0,0.04)">', unsafe_allow_html=True)
                            st.write('### Summary')
                            if selected_service:
                                st.write(f"**Service:** {selected_service.get('name')} — ${selected_service.get('base_price'):.2f}")
                                est_duration = selected_service.get('duration', 30)
                            else:
                                st.write('**Service:** Not selected')
                                est_duration = 30

                            if selected_products_objs:
                                st.write('**Products:**')
                                for sp in selected_products_objs:
                                    st.write(f"- {sp['name']} ({sp.get('brand','')}) — ${sp.get('selling_price',0):.2f}")
                            else:
                                st.write('**Products:** None')

                            # calculate estimated total
                            try:
                                service_price = selected_service.get('base_price', 0) if selected_service else 0
                                products_total = sum(p.get('selling_price', 0) for p in selected_products_objs)
                                estimated_total = service_price + products_total
                                st.write('---')
                                st.write(f"**Estimated Total:** ${estimated_total:.2f}")
                            except Exception:
                                pass

                            st.markdown('</div>', unsafe_allow_html=True)

                        submitted = st.form_submit_button('Request Booking')

                        if submitted:
                            # basic validation
                            if not name or not email or not selected_service:
                                st.error('Please fill in your name, email, and select a service.')
                            else:
                                # create/get customer
                                from models import DatabaseManager
                                dm = DatabaseManager()
                                cust_mgr = dm.get_or_create_user if False else None

                                # Use booking manager
                                bm = st.session_state.get('booking_manager') if st.session_state.get('booking_manager') else None
                                # fallback
                                if not bm:
                                    from booking_manager import BookingManager
                                    bm = BookingManager()

                                # get or create customer record via booking manager's customer manager
                                first_name = name.split()[0]
                                last_name = ' '.join(name.split()[1:]) if len(name.split())>1 else ''
                                try:
                                    customer = bm.customer_manager.get_or_create_customer_by_email(email, first_name, last_name)
                                except Exception:
                                    customer = {'id': None}

                                appointment_datetime = datetime.combine(appointment_date, appointment_time)
                                end_dt = appointment_datetime + timedelta(minutes=(selected_service.get('duration',30) if selected_service else 30))

                                booking_data = {
                                    'customer_id': customer.get('id'),
                                    'service_id': selected_service.get('id') if selected_service else None,
                                    'staff_id': None,
                                    'appointment_datetime': appointment_datetime,
                                    'end_datetime': end_dt,
                                    'total_price': estimated_total,
                                    'notes': notes,
                                    'add_ons': {'products': [ {'id': p.get('id'), 'name': p.get('name'), 'selling_price': p.get('selling_price')} for p in selected_products_objs ]},
                                    'status': 'requested',
                                    'payment_status': 'pending'
                                }

                                if bm.create_booking(booking_data):
                                    st.success('✅ Your booking request has been submitted. We will confirm shortly.')
                                    # hide inline form
                                    st.session_state['show_inline_booking'] = False
                                    safe_rerun()
                                else:
                                    st.error('Failed to create booking. Please try again later.')
            else:
                st.info('No hero images found at configured HERO_IMAGES_PATH. Set HERO_IMAGES_PATH in your .env to show hero images.')
        except Exception as e:
            st.error(f'Failed to load hero images: {e}')

        st.markdown('---')
        st.subheader('Login')
        login_type = st.radio('Sign in as', ['End User', 'Administrator'], index=0, horizontal=True)

        if login_type == 'Administrator':
            with st.form('admin_login'):
                admin_user = st.text_input('Username', value=os.getenv('ADMIN_USER', 'Admin'))
                admin_pass = st.text_input('Password', type='password', value=os.getenv('ADMIN_PASS', 'admin123'))
                submitted = st.form_submit_button('Sign in')
                if submitted:
                    if admin_user == os.getenv('ADMIN_USER', 'Admin') and admin_pass == os.getenv('ADMIN_PASS', 'admin123'):
                        st.session_state['user'] = {'id': 0, 'email': None, 'full_name': 'Administrator', 'is_admin': True}
                        st.success('Signed in as admin')
                        safe_rerun()
                    else:
                        st.error('Invalid admin credentials')
        else:
            if st.button('Sign in with Google'):
                try:
                    from auth import google_sign_in
                    info = google_sign_in()
                    if info and info.get('email'):
                        from models import DatabaseManager
                        dm = DatabaseManager()
                        user_obj = dm.get_or_create_user(info['email'], info.get('full_name'), info.get('google_id'))
                        st.session_state['user'] = {
                            'id': user_obj['id'],
                            'email': user_obj['email'],
                            'full_name': user_obj.get('full_name'),
                            'is_admin': user_obj.get('is_admin', False)
                        }
                        safe_rerun()
                    else:
                        st.error('Google sign-in failed')
                except Exception as e:
                    st.error(f'Sign-in failed: {e}')

        # Public booking request form (below login)
        st.markdown('---')
        st.subheader('Request an appointment (no sign-in required)')
        from booking_manager import BookingManager
        bm = BookingManager()
        bm.request_booking_form()
        return

    # At this point we have a signed-in user
    # Sidebar navigation (left-pane links)
    st.sidebar.title('Navigation')

    pages = [
        'Dashboard',
        'Services Management',
        'Products Management',
        'Customer Management',
        'Staff Management',
        'Appointment Booking',
    ]

    # Add Admin Panel if user is admin
    user = st.session_state.get('user')
    if user and user.get('is_admin'):
        pages.insert(len(pages)-1, 'Admin Panel')

    # Ensure a default page is set (persist across reruns)
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard'

    # Show vertical navigation buttons in the left pane
    for p in pages:
        if st.sidebar.button(p, width='stretch', key=f'nav_{p}'):
            st.session_state.current_page = p

    # Authentication area
    st.sidebar.markdown('---')
    u = st.session_state.get('user')
    st.sidebar.write(f"Signed in as **{u.get('full_name') or u.get('email')}**")
    if st.sidebar.button('Sign out'):
        st.session_state.pop('user', None)
        safe_rerun()

    # Use the currently selected page
    page = st.session_state.current_page
    
    # Check if managers are initialized
    if not all(key in st.session_state for key in ['services_manager', 'products_manager', 'customer_manager', 'staff_manager', 'booking_manager', 'dashboard']):
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
        elif page == "Admin Panel":
            # Only allow admins
            user = st.session_state.get('user')
            if not user or not user.get('is_admin'):
                st.error('Admin access required')
            else:
                am = AdminManager()
                am.show_admin_panel()
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
