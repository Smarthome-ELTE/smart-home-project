"""
Controller with MINIMAL console output
Only logs important events, not every detail
"""

import datetime
import paho.mqtt.client as paho
from paho import mqtt
import json
from db import Database


def is_trigger_valid(trigger_condition, msg):
    """Check if trigger condition matches the message"""
    
    # Check topic
    if trigger_condition["topic"] != msg.topic:
        return False
    
    msg_payload = json.loads(msg.payload)
    
    # Check sensor_id
    if "sensor_id" not in msg_payload or trigger_condition["sensor_id"] != msg_payload["sensor_id"]:
        return False
    
    # Check conditions
    conditions = trigger_condition["conditions"]
    
    for key, comparator in conditions.items():
        if key not in msg_payload:
            return False
        
        value = msg_payload[key]
        expression = str(value) + comparator
        result = eval(expression)
        
        if not result:
            return False
    
    return True


class Controller:
    def __init__(self, client_id, protocol, db_path=None):
        self.__db = Database(db_path=db_path)
        self.__triggers = []
        self.__last_trigger_time = {}
        
        # Create MQTT client
        self.__client = paho.Client(client_id=client_id, protocol=protocol, userdata=None)
        self.__client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        
        # Set up callbacks
        self.__client.on_connect = self._on_connect
        self.__client.on_subscribe = self._on_subscribe
        self.__client.on_publish = self._on_publish
        self.__client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """Called when connected to MQTT broker"""
        print(f"✅ CONTROLLER: Connected")
        
        # Subscribe to ALL temperature topics
        self.__client.subscribe("temperature/get", qos=1)
        
        # Also subscribe to other categories
        categories = set(map(lambda cat_tuple: cat_tuple[0], self.__db.get_all_sensor_categories()))
        for category in categories:
            if category != "temperature":
                topic = category + "/get"
                self.__client.subscribe(topic, qos=1)

    def _on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        """Called when subscription is confirmed - SILENT"""
        pass

    def _on_publish(self, client, userdata, mid, properties=None):
        """Called when message is published - SILENT"""
        pass

    def _on_message(self, client, userdata, msg):
        """Called when message is received - MINIMAL LOGGING"""
        try:
            payload = json.loads(msg.payload)
            sensor_id = payload.get('sensor_id', 'unknown')
            temp = payload.get('temperature', '?')
        except Exception as e:
            return
        
        # Get enabled triggers
        enabled_triggers = [tr for tr in self.__triggers if tr["enabled"] > 0]
        
        for trigger in enabled_triggers:
            if is_trigger_valid(trigger["condition"], msg):
                # Check cooldown (prevent rapid repeated triggers)
                trigger_id = trigger["id"]
                current_time = datetime.datetime.now()
                
                if trigger_id in self.__last_trigger_time:
                    time_since_last = (current_time - self.__last_trigger_time[trigger_id]).total_seconds()
                    if time_since_last < 5:  # 5 second cooldown
                        continue
                
                # LOG ONLY THE ACTION
                print(f"⚡ RULE TRIGGERED: {trigger['name']}")
                
                # Update last trigger time
                self.__last_trigger_time[trigger_id] = current_time
                
                # Log trigger execution
                self.__db.log_trigger(trigger["id"], current_time)
                
                # Execute actions
                for action in trigger["actions"]:
                    self.__client.publish(
                        action["topic"], 
                        json.dumps(action["payload"]), 
                        qos=action["qos"]
                    )
                
                # Only execute first matching trigger
                break

    def connect(self, host, port, username, password):
        """Connect to MQTT broker"""
        self.__client.username_pw_set(username, password)
        self.__client.connect(host, port)

    def start(self):
        """Start the MQTT client loop"""
        self.__client.loop_start()
        
        # Load triggers from database
        self.load_triggers()
        
        print(f"🚀 CONTROLLER: Active with {len([t for t in self.__triggers if t['enabled']])} enabled rules")

    def stop(self):
        """Stop the MQTT client loop"""
        self.__client.loop_stop()

    def subscribe(self, topic, qos):
        """Subscribe to additional topic"""
        self.__client.subscribe(topic, qos)

    def publish(self, topic, payload, qos):
        """Publish message"""
        self.__client.publish(topic, payload, qos)

    def load_triggers(self):
        """Load all triggers from database - SILENT"""
        db_triggers = self.__db.get_all_triggers()
        
        for db_trigger in db_triggers:
            trigger_id = int(db_trigger[0])
            name = db_trigger[1]
            sensor_id = int(db_trigger[2])
            conditions = json.loads(db_trigger[3])
            device_id = int(db_trigger[4])
            action_payload = json.loads(db_trigger[5])
            enabled = int(db_trigger[6])
            
            # Get sensor category for topic
            sensor_category = self.__db.get_sensor_category(sensor_id)
            
            # Get device category for action topic
            device_category = self.__db.get_device_category(device_id)
            
            trigger = {
                "id": trigger_id,
                "name": name,
                "condition": {
                    "sensor_id": sensor_id,
                    "topic": sensor_category + "/get",
                    "conditions": conditions,
                },
                "actions": [
                    {
                        "topic": device_category + "/send",
                        "payload": {"device_id": device_id, **action_payload},
                        "qos": 1
                    }
                ],
                "enabled": enabled
            }
            
            self.__triggers.append(trigger)

    def add_trigger(self, name, sensor_id, conditions, device_id, action_payload):
        """Add new trigger"""
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
        
        print(f"✅ Rule added: {name}")

    def delete_trigger(self, trigger_id):
        """Delete trigger"""
        self.__db.delete_trigger(trigger_id)
        self.__triggers = [tr for tr in self.__triggers if tr["id"] != trigger_id]

    def switch_trigger(self, trigger_id):
        """Toggle trigger enabled/disabled"""
        for trigger in self.__triggers:
            if trigger["id"] == trigger_id:
                target_state = (trigger["enabled"] + 1) % 2
                trigger["enabled"] = target_state
                self.__db.switch_trigger(trigger_id, target_state)
                
                status = "ENABLED" if target_state else "DISABLED"
                print(f"✅ Rule '{trigger['name']}': {status}")
                break