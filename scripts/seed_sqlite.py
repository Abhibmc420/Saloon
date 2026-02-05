import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports like `manage_db` work when run from scripts dir
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from manage_db import DatabaseManager, cmd_seed

# Force SQLite fallback for this run
os.environ.pop('DATABASE_URL', None)
os.environ['SQLITE_PATH'] = 'seed_salon.db'

if __name__ == '__main__':
    db = DatabaseManager()
    cmd_seed(db)
