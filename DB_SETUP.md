# Database Setup & Usage ⚙️

Steps to get the database running and migrate/seed data:

1. Copy `.env.example` to `.env` and fill in your `DATABASE_URL` (Postgres) or leave commented to use SQLite fallback.

2. For Postgres with Docker Compose:
   - Start a local database: `docker-compose up -d`
   - Use `DATABASE_URL=postgresql://postgres:changeme@localhost:5432/Saloon` in `.env`

3. Manage DB with the CLI:
   - Create tables: `python manage_db.py init`
   - Seed from `data/services.json` and `data/products.json`: `python manage_db.py seed`
   - Drop tables: `python manage_db.py drop`
   - Check status (counts): `python manage_db.py status`

4. Alembic migrations:
   - Initialize is already scaffolded in `alembic/` with an initial migration `0001_initial`.
   - To run migrations: `alembic upgrade head` (make sure `alembic.ini` or env sets `sqlalchemy.url` via `DATABASE_URL`)

5. Tests (requires pytest):
   - Install dependencies: `pip install -r requirements.txt` or use your environment.
   - Run tests: `pytest -q`

Notes:
- The app defaults to SQLite (`salon.db`) when `DATABASE_URL` is not provided for easy local development.
- Do NOT commit your real `.env` file to version control.
