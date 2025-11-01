from database import MonitorDatabase
import time


# Initialize database
db = MonitorDatabase()

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
    INSERT INTO sensors (name, type, data_topic, last_payload, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Living Room Temp', 'Temperature', 'smarthome/living/temp', '{"value": 22.5}'))
sensor_id_1 = cursor.lastrowid

cursor.execute("""
    INSERT INTO sensors (name, type, data_topic, last_payload, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Kitchen Light', 'Light', 'smarthome/kitchen/light', '{"brightness": 80}'))
sensor_id_2 = cursor.lastrowid

cursor.execute("""
    INSERT INTO sensors (name, type, data_topic, last_payload, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Garden Moisture', 'Water', 'smarthome/garden/moisture', '{"level": 45}'))
sensor_id_3 = cursor.lastrowid

db.conn.commit()

print("Added 3 sensors")

# Add dummy devices
cursor.execute("""
    INSERT INTO devices (name, type, status_topic, command_topic, current_status, last_update)
    VALUES (?, ?, ?, ?, ?, datetime('now'))
""", ('Main Heater', 'Heater', 'smarthome/heater/status', 'smarthome/heater/set', '{"state": "off"}'))
device_id_1 = cursor.lastrowid

cursor.execute("""
    INSERT INTO devices (name, type, status_topic, command_topic, current_status, last_update)
    VALUES (?, ?, ?, ?, ?, datetime('now'))
""", ('Smart Bulb', 'Light', 'smarthome/bulb/status', 'smarthome/bulb/set', '{"state": "on", "brightness": 100}'))
device_id_2 = cursor.lastrowid

db.conn.commit()

print("Added 2 devices")

# Add dummy events for sensors
print("Adding sensor events...")
for i in range(15):
    db.log_event('sensor', sensor_id_1, 'smarthome/living/temp', {'value': 20 + i * 0.5, 'unit': 'C'})
    time.sleep(0.05)

for i in range(10):
    db.log_event('sensor', sensor_id_2, 'smarthome/kitchen/light', {'brightness': 50 + i * 5})
    time.sleep(0.05)

for i in range(8):
    db.log_event('sensor', sensor_id_3, 'smarthome/garden/moisture', {'level': 30 + i * 2})
    time.sleep(0.05)

# Add dummy events for devices
print("Adding device events...")
for i in range(5):
    state = "on" if i % 2 == 0 else "off"
    db.log_event('device', device_id_1, 'smarthome/heater/status', {'state': state, 'temperature': 22 + i})
    time.sleep(0.05)

for i in range(5):
    db.log_event('device', device_id_2, 'smarthome/bulb/status', {'state': 'on', 'brightness': 80 + i * 5})
    time.sleep(0.05)

db.conn.commit()

print(f"\n✅ Done! Added {len(db.get_recent_events())} total events")
print("Run 'python wireframe.py' to view the data")