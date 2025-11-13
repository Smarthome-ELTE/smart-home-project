import datetime

from database import Database
import time


# Initialize database
db = Database()

print("Clearing previous data...")

# Clear all existing data (in reverse order due to foreign keys)
cursor = db.conn.cursor()
cursor.execute("DELETE FROM events")
cursor.execute("DELETE FROM triggers")
cursor.execute("DELETE FROM devices")
cursor.execute("DELETE FROM sensors")
db.conn.commit()

print("Adding fresh dummy data...")

# Add dummy sensors
cursor.execute("""
    INSERT INTO sensors (name, category, type, last_payload, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Living Room Temp', 'temperature', 'Thermometer', '{"value": 22.5}'))
sensor_id_1 = cursor.lastrowid

cursor.execute("""
    INSERT INTO sensors (name, category, type, last_payload, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Kitchen Light', 'light', 'Photometer', '{"brightness": 80}'))
sensor_id_2 = cursor.lastrowid

cursor.execute("""
    INSERT INTO sensors (name, category, type, last_payload, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Garden Moisture', 'water', 'MoistureSensor', '{"level": 45}'))
sensor_id_3 = cursor.lastrowid

db.conn.commit()

print("Added 3 sensors")

# Add dummy devices
cursor.execute("""
    INSERT INTO devices (name, category, type, current_status, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Main Heater', 'temperature', 'Heater', '{"state": "off"}'))
device_id_1 = cursor.lastrowid

cursor.execute("""
    INSERT INTO devices (name, category, type, current_status, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Smart Bulb', 'light', 'Lightbulb', '{"state": "on", "brightness": 100}'))
device_id_2 = cursor.lastrowid

db.conn.commit()

print("Added 2 devices")

# Add dummy events for sensors
print("Adding sensor events...")
for i in range(15):
    db.log_event('sensor', sensor_id_1, {'value': 20 + i * 0.5, 'unit': 'C', 'action': 'send'})
    time.sleep(0.05)

for i in range(10):
    db.log_event('sensor', sensor_id_2, {'brightness': 50 + i * 5, 'action': 'add'})
    time.sleep(0.05)

for i in range(8):
    db.log_event('sensor', sensor_id_3, {'level': 30 + i * 2, 'action': 'delete'})
    time.sleep(0.05)

# Add dummy events for devices
print("Adding device events...")
for i in range(5):
    state = "on" if i % 2 == 0 else "off"
    db.log_event('device', device_id_1, 'Text')
    time.sleep(0.05)

for i in range(5):
    db.log_event('device', device_id_2, {'state': 'on', 'brightness': 80 + i * 5, 'action': 'get'})
    time.sleep(0.05)

db.conn.commit()

print("Adding triggers...")
condition = {"temperature": ">=14", "humidity": ">=25"}
action_payload = {"temperature": 22}

trigger_id_1 = db.add_trigger("Increase temperature", sensor_id_1, condition, device_id_1, action_payload)
db.log_trigger(str(trigger_id_1), datetime.datetime.now())
db.conn.commit()

print(f"\n✅ Done! Added {len(db.get_recent_events())} total events")
print("Run 'python wireframe.py' to view the data")