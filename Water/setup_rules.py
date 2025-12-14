import datetime

from db import Database

db = Database(db_path="../db/smart_home_monitor.db")

print("Clearing previous data about sensors...")

# Clear all existing data (in reverse order due to foreign keys)
cursor = db.conn.cursor()
cursor.execute("DELETE FROM triggers")
db.conn.commit()

print("Adding fresh dummy triggers...")

# trigger 1
condition_1 = {"water_pressure": "<=1"}
action_payload_1 = {"set_state": 85}

trigger_id_1 = db.add_trigger("Increase water pressure in bathroom", 52, condition_1, 36, action_payload_1)
db.log_trigger(str(trigger_id_1), datetime.datetime.now())

# trigger 2
condition_2 = {"water_pressure": ">=3"}
action_payload_2 = {"set_state": 10}

trigger_id_2 = db.add_trigger("Stop increasing water pressure in bathroom", 52, condition_2, 36, action_payload_2)
db.log_trigger(str(trigger_id_2), datetime.datetime.now())

# trigger 3
condition_3 = {"water_detected": "==1"}
action_payload_3 = {"set_state": 0}

trigger_id_3 = db.add_trigger("Close water valve in kitchen", 53, condition_3, 35, action_payload_3)
db.log_trigger(str(trigger_id_3), datetime.datetime.now())

# trigger 4
condition_4 = {"water_detected": "==0"}
action_payload_4 = {"set_state": 100}

trigger_id_4 = db.add_trigger("Open water valve in kitchen", 53, condition_4, 35, action_payload_4)
db.log_trigger(str(trigger_id_4), datetime.datetime.now())

# trigger 5
condition_5 = {"moisture_level": "<= 25"}
action_payload_5 = {"set_state": 100}

trigger_id_5 = db.add_trigger("Turn on sprinklers", 54, condition_5, 37, action_payload_5)
db.log_trigger(str(trigger_id_5), datetime.datetime.now())

db.conn.commit()

print("Added 5 triggers")
