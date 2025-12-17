from db import Database

# Adjust path if necessary
db = Database(db_path="db/smart_home_monitor.db")

print("Clearing previous data about light devices...")
cursor = db.conn.cursor()
cursor.execute("DELETE FROM devices WHERE category='light'")
db.conn.commit()

print("Adding fresh dummy data about light devices...")

# 1. Smart LED Bulb (Output for state, brightness, hue, saturation)
initial_status = {
    "state": "off",
    "brightness": 0,
    "hue": 0,
    "saturation": 0
}

cursor.execute("""
    INSERT INTO devices (name, category, type, current_status, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Main Smart Bulb', 'light', 'SmartLED', ''))
device_id_1 = cursor.lastrowid

db.conn.commit()
print(f"Added 1 light device. ID: {device_id_1}")
