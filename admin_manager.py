import streamlit as st
from db_manager import DatabaseUserManager
from models import DatabaseManager

# Local safe_rerun helper (keeps admin manager independent of app module)
def safe_rerun():
    try:
        if hasattr(st, 'experimental_rerun'):
            return st.experimental_rerun()
        if hasattr(st, 'rerun'):
            return st.rerun()
    except Exception:
        pass
    st.session_state['_force_rerender'] = not st.session_state.get('_force_rerender', False)
    st.stop()

class AdminManager:
    def __init__(self):
        try:
            self.db_manager = DatabaseManager()
            self.user_manager = DatabaseUserManager(self.db_manager)
        except Exception as e:
            st.error(f"Failed to initialize Admin manager: {e}")
            self.user_manager = None

    def show_admin_panel(self):
        st.header('🔒 Admin Panel')

        if not self.user_manager:
            st.error('User manager not available')
            return

        st.subheader('User Management')
        users = self.user_manager.get_all_users()
        if not users:
            st.info('No users found')
            return

        for u in users:
            cols = st.columns([3,1,1])
            with cols[0]:
                st.write(f"**{u['full_name'] or u['email']}** — {u['email']}")
            with cols[1]:
                new_admin = st.checkbox('Admin', value=u['is_admin'], key=f"admin_{u['id']}")
            with cols[2]:
                if st.button('Update', key=f"u_update_{u['id']}"):
                    self.user_manager.set_admin(u['id'], bool(new_admin))
                    st.success('Updated')
                    safe_rerun()
