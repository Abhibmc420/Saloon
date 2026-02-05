import sqlite3, os

db='seed_salon.db'
print('DB file exists:', os.path.exists(db))
try:
    conn=sqlite3.connect(db)
    cur=conn.cursor()
    cur.execute("SELECT id, customer_id, service_id, appointment_datetime, notes FROM bookings WHERE notes LIKE '%Smoke test booking%'")
    rows=cur.fetchall()
    print('Matches:', len(rows))
    for r in rows:
        print(r)
    conn.close()
except Exception as e:
    print('Error querying DB:', e)
