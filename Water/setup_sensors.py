from db import Database

db = Database(db_path="../db/smart_home_monitor.db")

print("Clearing previous data about sensors...")

# Clear all existing data (in reverse order due to foreign keys)
cursor = db.conn.cursor()
cursor.execute("DELETE FROM sensors")
db.conn.commit()

print("Adding fresh dummy data about sensors...")

# Add dummy sensors
cursor.execute("""
    INSERT INTO sensors (name, category, type, last_payload, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Bathroom Water Pressure', 'water', 'Pressure', ''))
sensor_id_1 = cursor.lastrowid

cursor.execute("""
    INSERT INTO sensors (name, category, type, last_payload, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Kitchen Water Leak', 'water', 'Water leak', ''))
sensor_id_2 = cursor.lastrowid

cursor.execute("""
    INSERT INTO sensors (name, category, type, last_payload, last_update)
    VALUES (?, ?, ?, ?, datetime('now'))
""", ('Garden Moisture', 'water', 'MoistureSensor', ''))
sensor_id_3 = cursor.lastrowid

db.conn.commit()

print("Added 3 sensors")
