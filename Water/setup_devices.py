from db import Database

db = Database(db_path="../db/smart_home_monitor.db")

print("Clearing previous data about sensors...")

# Clear all existing data (in reverse order due to foreign keys)
cursor = db.conn.cursor()
cursor.execute("DELETE FROM devices")
db.conn.commit()

print("Adding fresh dummy data about devices...")

# Add dummy devices
cursor.execute("""
    INSERT INTO devices (name, category, type, current_status, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Kitchen Water Valve', 'water', 'Valve', ''))
device_id_1 = cursor.lastrowid

cursor.execute("""
    INSERT INTO devices (name, category, type, current_status, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Bathroom Water Valve', 'water', 'Valve', ''))
device_id_2 = cursor.lastrowid

cursor.execute("""
    INSERT INTO devices (name, category, type, current_status, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Garden Sprinkler Valve', 'water', 'Valve', ''))
device_id_3 = cursor.lastrowid

db.conn.commit()

print("Added 3 devices")
