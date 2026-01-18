import psycopg2

# Database connection parameters
conn = psycopg2.connect(
    host="localhost",       # or IP address / domain
    port="5432",            # default PostgreSQL port
    database="Saloon",  # your DB name
    user="postgresP",          # your DB user
    password="Admin123"   # your DB password
)

# Create a cursor
cur = conn.cursor()

# Run a query
cur.execute("SELECT version();")
db_version = cur.fetchone()
print("PostgreSQL version:", db_version)

# Close connections
cur.close()
conn.close()
