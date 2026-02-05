import os
import tempfile
import shutil
from models import DatabaseManager


def test_sqlite_fallback(tmp_path, monkeypatch):
    # Unset DATABASE_URL to force SQLite fallback
    monkeypatch.delenv('DATABASE_URL', raising=False)
    dbfile = tmp_path / "test_salon.db"
    monkeypatch.setenv('SQLITE_PATH', str(dbfile))

    db = DatabaseManager()
    assert db.database_url.startswith('sqlite:///')
    # Create tables and ensure DB file appears
    db.create_tables()
    assert os.path.exists(str(dbfile))


def test_migrate_json_data(tmp_path, monkeypatch):
    # Setup a temp sqlite database and temporary data files
    dbfile = tmp_path / "test_salon2.db"
    monkeypatch.setenv('DATABASE_URL', f"sqlite:///{dbfile}")

    # Create sample JSON data files
    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    services_file = data_dir / 'services.json'
    products_file = data_dir / 'products.json'

    services_file.write_text('[{"name": "Cut", "category": "Hair", "base_price": 20.0, "duration": 30}]')
    products_file.write_text('[{"name": "Shampoo", "brand": "Acme", "category": "Hair", "cost_price": 2.0, "selling_price": 5.0, "quantity": 10, "low_stock_threshold": 2}]')

    # Temporarily change working directory so manage_db seed would find files if used; but we'll call migrate_json_data directly
    db = DatabaseManager()
    db.create_tables()

    import json
    services = json.loads(services_file.read_text())
    products = json.loads(products_file.read_text())

    ok = db.migrate_json_data(services, products)
    assert ok

    # Check data persisted
    session = db.get_session()
    try:
        from models import Service, Product
        assert session.query(Service).count() == 1
        assert session.query(Product).count() == 1
    finally:
        session.close()
