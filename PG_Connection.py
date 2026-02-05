import os
import psycopg2

# Example Postgres connection that reads from environment variables.
# This is only intended as a quick local connectivity test; prefer using SQLAlchemy in the app.

def connect_and_print_version():
    conn_info = dict(
        host=os.getenv('PG_HOST', 'localhost'),
        port=os.getenv('PG_PORT', '5432'),
        database=os.getenv('PG_DATABASE', 'Saloon'),
        user=os.getenv('PG_USER', 'postgres'),
        password=os.getenv('PG_PASSWORD', ''),
    )

    if not conn_info['password']:
        print("PG_Connection: No password set in environment variables; aborting connection.")
        return

    conn = psycopg2.connect(**conn_info)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    db_version = cur.fetchone()
    print("PostgreSQL version:", db_version)
    cur.close()
    conn.close()


if __name__ == '__main__':
    connect_and_print_version()
