"""
Smoke test: create a test service (if needed), customer, requested booking, verify, then cleanup.
"""
import os
import sys
from datetime import datetime, timedelta, time
# Ensure project root is on sys.path so local imports work when running as a script
sys.path.insert(0, os.getcwd())

os.environ['SQLITE_PATH'] = 'seed_salon.db'

from booking_manager import BookingManager

print('Initializing BookingManager...')
bm = BookingManager()

# Ensure there's at least one service
services = bm.service_manager.get_all_services()
if not services:
    print('No services found — creating a test service')
    svc = {
        'name': 'Test Cut',
        'category': 'Hair',
        'base_price': 15.0,
        'duration': 30,
        'description': 'A quick smoke-test haircut',
        'pricing_tiers': [],
        'add_ons': []
    }
    ok = bm.service_manager.add_service(svc)
    print('Service created:', ok)
    services = bm.service_manager.get_all_services()

service = services[0]
print('Using service:', service['name'], 'id=', service['id'])

# Create/get customer
email = 'smoke_test_user@example.test'
first_name = 'Smoke'
last_name = 'Tester'
customer = bm.customer_manager.get_or_create_customer_by_email(email, first_name, last_name)
print('Customer:', customer)

# Schedule for tomorrow at 10:00
appt_date = (datetime.now() + timedelta(days=1)).date()
appt_time = time(10, 0)
appointment_datetime = datetime.combine(appt_date, appt_time)
end_datetime = appointment_datetime + timedelta(minutes=service.get('duration', 30))

booking_data = {
    'customer_id': customer['id'],
    'service_id': service['id'],
    'staff_id': None,
    'appointment_datetime': appointment_datetime,
    'end_datetime': end_datetime,
    'total_price': service.get('base_price', 0.0),
    'notes': 'Smoke test booking',
    'add_ons': [],
    'status': 'requested',
    'payment_status': 'pending'
}

print('Creating booking...')
created = bm.create_booking(booking_data)
print('Created:', created)

# Verify
bookings = bm.get_bookings_by_date(appt_date)
matches = [b for b in bookings if b['customer_id'] == customer['id'] and b['service_id'] == service['id'] and b['notes'] == 'Smoke test booking']
if matches:
    print('Found booking(s):')
    for b in matches:
        print(b)
    # Cleanup: delete created bookings
    for b in matches:
        print('Deleting booking id', b['id'], '...')
        ok = bm.delete_booking(b['id'])
        print('Deleted:', ok)
else:
    print('No matching booking found.')

print('Smoke test completed.')
