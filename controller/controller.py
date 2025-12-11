import datetime
import paho.mqtt.client as paho
from paho import mqtt
import json
from db import Database


def is_trigger_valid(trigger_condition, msg):
    """Check if trigger condition matches the message"""
    
    # Debug: Show what we're checking
    print(f"  🔍 Checking trigger condition:")
    print(f"     Expected topic: {trigger_condition['topic']}")
    print(f"     Actual topic: {msg.topic}")
    
    if trigger_condition["topic"] != msg.topic:
        print(f"     ❌ Topic mismatch!")
        return False
    
    msg_payload = json.loads(msg.payload)
    print(f"     Payload: {msg_payload}")
    
    if "sensor_id" not in msg_payload:
        print(f"     ❌ No sensor_id in payload!")
        return False
        
    if trigger_condition["sensor_id"] != msg_payload["sensor_id"]:
        print(f"     ❌ Sensor ID mismatch: expected {trigger_condition['sensor_id']}, got {msg_payload['sensor_id']}")
        return False
    
    print(f"     ✅ Sensor ID matches: {msg_payload['sensor_id']}")
    
    conditions = trigger_condition["conditions"]
    is_triggers_valid = True
    
    print(f"     Evaluating conditions: {conditions}")

    for key, comparator in conditions.items():
        if key not in msg_payload:
            print(f"     ❌ Key '{key}' not in payload!")
            is_triggers_valid = False
            break
            
        value = msg_payload[key]
        expression = str(value) + comparator
        result = eval(expression)
        
        print(f"     Condition: {key} {comparator}")
        print(f"     Expression: {expression} = {result}")
        
        is_triggers_valid = is_triggers_valid and result
        if not is_triggers_valid:
            print(f"     ❌ Condition failed!")
            break
    
    if is_triggers_valid:
        print(f"     ✅ ALL CONDITIONS PASSED!")
    
    return is_triggers_valid


class Controller:
    def __init__(self, client_id, protocol, db_path=None):
        self.__db = Database(db_path=db_path)
        self.__client = paho.Client(client_id=client_id, protocol=protocol, userdata=None)
        self.__client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

        self.__triggers = []

        def on_connect(client, userdata, flags, rc, properties=None):
            print("CONNACK received with code " + str(rc))

        def on_publish(client, userdata, mid, properties=None):
            print("Published mid: " + str(mid))

        def on_subscribe(client, userdata, mid, granted_qos, properties=None):
            print("Subscribed: " + str(mid) + " " + str(granted_qos))

        def on_message(client, userdata, msg):
            print(f"\n🎮 CONTROLLER: Received message: {msg.topic}")
            print(f"   Payload: {msg.payload.decode()}")
            
            enabled_triggers = list(filter(lambda tr: tr["enabled"] > 0, self.__triggers))
            print(f"   📋 Checking {len(enabled_triggers)} enabled triggers...")
            
            for trigger in enabled_triggers:
                print(f"\n   🎯 Evaluating trigger: '{trigger['name']}'")
                
                if is_trigger_valid(trigger["condition"], msg):
                    print(f"   ✅ TRIGGER MATCHED: {trigger['name']}")
                    print(f"   🔥 Executing actions...")
                    
                    self.__db.log_trigger(trigger["id"], datetime.datetime.now())
                    
                    for action in trigger["actions"]:
                        print(f"      📤 Publishing to {action['topic']}")
                        print(f"         Payload: {json.dumps(action['payload'])}")
                        self.publish(action["topic"], json.dumps(action["payload"]), action["qos"])
                else:
                    print(f"   ❌ Trigger '{trigger['name']}' did not match")

        self.__client.on_connect = on_connect
        self.__client.on_subscribe = on_subscribe
        self.__client.on_publish = on_publish
        self.__client.on_message = on_message

        # Subscribe to all sensor categories
        categories = set(map(lambda cat_tuple: cat_tuple[0], self.__db.get_all_sensor_categories()))
        print(f"📡 Controller subscribing to categories: {categories}")
        for category in categories:
            topic = category + "/get"
            print(f"   Subscribing to: {topic}")
            self.__client.subscribe(topic, 1)

    def connect(self, host, port, username, password):
        self.__client.username_pw_set(username, password)
        self.__client.connect(host, port)
        print(f"🔌 CONTROLLER: Connecting to {host}:{port}...")

    def start(self):
        print(f"🚀 CONTROLLER: Starting loop...")
        self.__client.loop_start()
        self.load_triggers()
        print(f"✅ CONTROLLER: Service Started")
        print(f"   Loaded {len(self.__triggers)} triggers")

    def stop(self):
        self.__client.loop_stop()

    def subscribe(self, topic, qos):
        self.__client.subscribe(topic, qos)

    def publish(self, topic, payload, qos):
        self.__client.publish(topic, payload, qos)

    def load_triggers(self):
        """Load all triggers from database"""
        db_triggers = self.__db.get_all_triggers()
        print(f"\n📋 Loading triggers from database...")
        
        for db_trigger in db_triggers:
            trigger_id = int(db_trigger[0])
            name = db_trigger[1]
            sensor_id = int(db_trigger[2])
            conditions = json.loads(db_trigger[3])
            device_id = int(db_trigger[4])
            action_payload = json.loads(db_trigger[5])
            enabled = int(db_trigger[6])
            
            trigger = {
                "id": trigger_id,
                "name": name,
                "condition": {
                    "sensor_id": sensor_id,
                    "topic": self.__db.get_sensor_category(sensor_id) + "/get",
                    "conditions": conditions,
                },
                "actions": [
                    {
                        "topic": self.__db.get_device_category(device_id) + "/send",
                        "payload": {"device_id": device_id, **action_payload},
                        "qos": 1
                    }
                ],
                "enabled": enabled
            }
            
            self.__triggers.append(trigger)
            
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            print(f"   {status} | {name}")
            print(f"      Sensor {sensor_id} ({trigger['condition']['topic']})")
            print(f"      Conditions: {conditions}")
            print(f"      → Device {device_id} ({trigger['actions'][0]['topic']})")
            print(f"      Action: {action_payload}")

    def add_trigger(self, name, sensor_id, conditions, device_id, action_payload):
        trigger_id = self.__db.add_trigger(name, sensor_id, conditions, device_id, action_payload)
        trigger = {
            "id": trigger_id,
            "name": name,
            "condition": {
                "sensor_id": sensor_id,
                "topic": self.__db.get_sensor_category(sensor_id) + "/get",
                "conditions": conditions,
            },
            "actions": [
                {
                    "topic": self.__db.get_device_category(device_id) + "/send",
                    "payload": {"device_id": device_id, **action_payload},
                    "qos": 1
                }
            ],
            "enabled": 1
        }
        self.__triggers.append(trigger)
        print(f"✅ CONTROLLER: Added trigger '{name}'")

    def delete_trigger(self, trigger_id):
        self.__db.delete_trigger(trigger_id)
        trigger_to_delete = None
        for trigger in self.__triggers:
            if trigger["id"] == trigger_id:
                trigger_to_delete = trigger
        if trigger_to_delete is not None: 
            self.__triggers.remove(trigger_to_delete)
            print(f"✅ CONTROLLER: Deleted trigger ID {trigger_id}")

    def switch_trigger(self, trigger_id):
        for trigger in self.__triggers:
            if trigger["id"] == trigger_id:
                target_state = (trigger["enabled"] + 1) % 2
                trigger["enabled"] = target_state
                self.__db.switch_trigger(trigger_id, target_state)
                status = "ENABLED" if target_state else "DISABLED"
                print(f"✅ CONTROLLER: Trigger '{trigger['name']}' {status}")