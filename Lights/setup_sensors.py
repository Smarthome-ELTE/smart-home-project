from db import Database
import os

# Adjust path if necessary
db = Database(db_path="db/smart_home_monitor.db")

print("Clearing previous data about light sensors...")
cursor = db.conn.cursor()
cursor.execute("DELETE FROM sensors WHERE category='light'")
db.conn.commit()

print("Adding fresh dummy data about light sensors...")

# 1. Ambient Brightness Sensor (Input for dimming/automation)
cursor.execute("""
    INSERT INTO sensors (name, category, type, last_payload, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Living Room Ambient Light', 'light', 'Photoresistor', '{"brightness": 50}'))
sensor_id_1 = cursor.lastrowid

# 2. Motion Sensor (Input for simple ON/OFF automation)
cursor.execute("""
    INSERT INTO sensors (name, category, type, last_payload, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Living Room Motion', 'light', 'PIR', '{"motion_detected": 0}'))
sensor_id_2 = cursor.lastrowid

db.conn.commit()
print(f"Added 2 light sensors. IDs: {sensor_id_1}, {sensor_id_2}")
