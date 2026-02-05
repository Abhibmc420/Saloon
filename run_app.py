import os
import sys

# Force SQLite fallback for local runs
os.environ.pop('DATABASE_URL', None)
os.environ['SQLITE_PATH'] = 'seed_salon.db'

# Run Streamlit programmatically
try:
    # Newer Streamlit exposes a main function in web.cli
    import streamlit.web.cli as stcli
    sys.argv = ["streamlit", "run", "app.py"]
    if __name__ == '__main__':
        sys.exit(stcli.main())
except Exception as e:
    print('Failed to start Streamlit:', e)
    raise
