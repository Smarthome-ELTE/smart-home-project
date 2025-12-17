import datetime
from db import Database

# Adjust path if necessary
db = Database(db_path="db/smart_home_monitor.db")

print("Clearing previous data about light triggers...")

cursor = db.conn.cursor()
cursor.execute("DELETE FROM triggers")
db.conn.commit()

print("Fetching necessary IDs...")

# Assuming the Light Sensor ID is '55' and Device ID is '38' from setup scripts,
# you should fetch them dynamically to be safe:

cursor.execute("SELECT id FROM sensors WHERE name='Living Room Ambient Light'")
ambient_sensor_id = cursor.fetchone()[0]

cursor.execute("SELECT id FROM sensors WHERE name='Living Room Motion'")
motion_sensor_id = cursor.fetchone()[0]

cursor.execute("SELECT id FROM devices WHERE name='Main Smart Bulb'")
bulb_device_id = cursor.fetchone()[0]


print("Adding fresh dummy light triggers...")

# Trigger 1:
condition_1 = {"brightness": ">=60 & <80"}

action_payload_1 = {"state": "on", "brightness": 40, "hue": 0, "saturation": 0}

trigger_id_1 = db.add_trigger(
    "1. Ambient Dimmer (B: 60-80)",
    ambient_sensor_id,
    condition_1,
    bulb_device_id,
    action_payload_1
)
db.log_trigger(str(trigger_id_1), datetime.datetime.now())

# Trigger 2:

condition_2 = {"brightness": "<60"}
action_payload_2 = {"state": "on", "brightness": 100, "hue": 0, "saturation": 0}

trigger_id_2 = db.add_trigger(
    "2. Auto-On (B: <60)",
    ambient_sensor_id,
    condition_2,
    bulb_device_id,
    action_payload_2
)
db.log_trigger(str(trigger_id_2), datetime.datetime.now())


# Trigger 3:
# Condition: Ambient brightness is >=80
condition_3 = {"brightness": ">=80"}
action_payload_3 = {"state": "off"}

trigger_id_3 = db.add_trigger(
    "3. Auto-Off (B: >=80)",
    ambient_sensor_id,
    condition_3,
    bulb_device_id,
    action_payload_3
)
db.log_trigger(str(trigger_id_3), datetime.datetime.now())


# Trigger 4


condition_4 = {"motion_detected": "==0"}

action_payload_4 = {"state": "off"}

trigger_id_4 = db.add_trigger(
    "4. Auto-Off (No Motion)",
    motion_sensor_id,
    condition_4,
    bulb_device_id,
    action_payload_4
)
db.log_trigger(str(trigger_id_4), datetime.datetime.now())

# Trigger 5

condition_5 = {"motion_detected": "==1"}
action_payload_5 = {"state": "on", "brightness": 100, "hue": 0, "saturation": 0}

trigger_id_5 = db.add_trigger(
    "5. Motion-On (Motion == 1)",
    motion_sensor_id,
    condition_5,
    bulb_device_id,
    action_payload_5
)
db.log_trigger(str(trigger_id_5), datetime.datetime.now())

db.conn.commit()
print(f"Added 2 light triggers. Trigger IDs: {trigger_id_1}, {trigger_id_2}")