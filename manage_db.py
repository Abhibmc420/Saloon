"""Database management CLI

Usage:
    python manage_db.py init    # create tables
    python manage_db.py drop    # drop tables
    python manage_db.py seed    # seed from data/services.json and data/products.json
    python manage_db.py status  # print table counts
"""
import argparse
import json
import os
import sys
from models import DatabaseManager

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
SERVICES_FILE = os.path.join(DATA_DIR, 'services.json')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')


def cmd_init(db: DatabaseManager):
    db.create_tables()
    print("✅ Tables created")


def cmd_drop(db: DatabaseManager):
    # Use metadata.drop_all to drop tables
    db.engine.dispose()
    from models import Base
    Base.metadata.drop_all(bind=db.engine)
    print("✅ Tables dropped")


def cmd_seed(db: DatabaseManager):
    # Load data files
    services = []
    products = []

    # Ensure tables exist before seeding
    db.create_tables()

    if os.path.exists(SERVICES_FILE):
        with open(SERVICES_FILE, 'r', encoding='utf-8') as fh:
            services = json.load(fh)
    else:
        print(f"⚠️ Services file not found: {SERVICES_FILE}")

    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as fh:
            products = json.load(fh)
    else:
        print(f"⚠️ Products file not found: {PRODUCTS_FILE}")

    ok = db.migrate_json_data(services, products)
    if ok:
        print("✅ Seeded database from JSON files")
    else:
        print("❌ Seeding failed")


def cmd_status(db: DatabaseManager):
    session = db.get_session()
    try:
        from models import Service, Product, Customer, Staff, Booking
        counts = {
            'services': session.query(Service).count(),
            'products': session.query(Product).count(),
            'customers': session.query(Customer).count(),
            'staff': session.query(Staff).count(),
            'bookings': session.query(Booking).count(),
        }
        for k, v in counts.items():
            print(f"{k}: {v}")
    finally:
        session.close()


def main():
    p = argparse.ArgumentParser(description="Manage salon database")
    p.add_argument('action', choices=['init', 'drop', 'seed', 'status'])
    args = p.parse_args()

    try:
        db = DatabaseManager()
    except Exception as e:
        print(f"Failed to initialize database manager: {e}")
        sys.exit(2)

    if args.action == 'init':
        cmd_init(db)
    elif args.action == 'drop':
        cmd_drop(db)
    elif args.action == 'seed':
        cmd_seed(db)
    elif args.action == 'status':
        cmd_status(db)


if __name__ == '__main__':
    main()
