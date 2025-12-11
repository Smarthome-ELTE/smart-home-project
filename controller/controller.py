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
        self.__last_trigger_time = {}  # Track last trigger execution time
        
        # Create MQTT client
        self.__client = paho.Client(client_id=client_id, protocol=protocol, userdata=None)
        self.__client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        
        # Set up callbacks BEFORE connecting
        self.__client.on_connect = self._on_connect
        self.__client.on_subscribe = self._on_subscribe
        self.__client.on_publish = self._on_publish
        self.__client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """Called when connected to MQTT broker"""
        print(f"🎮 CONTROLLER: Connected! Result code: {rc}")
        
        # Subscribe to ALL temperature topics
        self.__client.subscribe("temperature/get", qos=1)
        print(f"🎮 CONTROLLER: Subscribed to 'temperature/get'")
        
        # Also subscribe to other categories if they exist
        categories = set(map(lambda cat_tuple: cat_tuple[0], self.__db.get_all_sensor_categories()))
        for category in categories:
            if category != "temperature":  # Already subscribed above
                topic = category + "/get"
                self.__client.subscribe(topic, qos=1)
                print(f"🎮 CONTROLLER: Subscribed to '{topic}'")

    def _on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        """Called when subscription is confirmed"""
        print(f"🎮 CONTROLLER: Subscription confirmed: {mid} {granted_qos}")

    def _on_publish(self, client, userdata, mid, properties=None):
        """Called when message is published"""
        print(f"🎮 CONTROLLER: Published mid: {mid}")

    def _on_message(self, client, userdata, msg):
        """Called when message is received - THIS IS THE CRITICAL FUNCTION"""
        print(f"\n{'='*70}")
        print(f"🎮 CONTROLLER: RECEIVED MESSAGE!")
        print(f"   Topic: {msg.topic}")
        print(f"   Payload: {msg.payload.decode()}")
        print(f"{'='*70}")
        
        try:
            payload = json.loads(msg.payload)
            sensor_id = payload.get('sensor_id', 'unknown')
            temp = payload.get('temperature', '?')
            print(f"🎮 CONTROLLER: Parsed - Sensor {sensor_id}, Temp: {temp}°C")
        except Exception as e:
            print(f"🎮 CONTROLLER: Error parsing payload: {e}")
            return
        
        # Get enabled triggers
        enabled_triggers = [tr for tr in self.__triggers if tr["enabled"] > 0]
        print(f"🎮 CONTROLLER: Checking {len(enabled_triggers)} enabled rules...")
        
        for trigger in enabled_triggers:
            print(f"\n   🔍 Evaluating: '{trigger['name']}'")
            print(f"      Sensor ID: {trigger['condition']['sensor_id']}")
            print(f"      Conditions: {trigger['condition']['conditions']}")
            
            if is_trigger_valid(trigger["condition"], msg):
                print(f"   ✅ RULE MATCHED: {trigger['name']}")
                
                # Check cooldown (prevent rapid repeated triggers)
                trigger_id = trigger["id"]
                current_time = datetime.datetime.now()
                
                if trigger_id in self.__last_trigger_time:
                    time_since_last = (current_time - self.__last_trigger_time[trigger_id]).total_seconds()
                    if time_since_last < 5:  # 5 second cooldown
                        print(f"   ⏸️  Cooldown active ({time_since_last:.1f}s), skipping")
                        continue
                
                print(f"   🔥 EXECUTING ACTIONS...")
                
                # Update last trigger time
                self.__last_trigger_time[trigger_id] = current_time
                
                # Log trigger execution
                self.__db.log_trigger(trigger["id"], current_time)
                
                # Execute actions
                for action in trigger["actions"]:
                    print(f"      📤 Publishing to: {action['topic']}")
                    print(f"         Payload: {json.dumps(action['payload'])}")
                    
                    self.__client.publish(
                        action["topic"], 
                        json.dumps(action["payload"]), 
                        qos=action["qos"]
                    )
                    print(f"      ✅ Command published!")
                    
                # Only execute first matching trigger
                break
            else:
                print(f"   ❌ Rule '{trigger['name']}' did not match")

    def connect(self, host, port, username, password):
        """Connect to MQTT broker"""
        print(f"🎮 CONTROLLER: Connecting to {host}:{port}...")
        self.__client.username_pw_set(username, password)
        self.__client.connect(host, port)

    def start(self):
        """Start the MQTT client loop"""
        print(f"🎮 CONTROLLER: Starting MQTT loop...")
        self.__client.loop_start()
        
        # Load triggers from database
        self.load_triggers()
        
        print(f"✅ CONTROLLER: Service Started")
        print(f"   Loaded {len(self.__triggers)} triggers")
        for trigger in self.__triggers:
            status = "✅ ENABLED" if trigger["enabled"] else "❌ DISABLED"
            print(f"   {status} - {trigger['name']}")

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
        """Load all triggers from database"""
        print(f"\n🎮 CONTROLLER: Loading triggers from database...")
        
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
            
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            print(f"   {status} | {name}")
            print(f"      Sensor {sensor_id} ({sensor_category}/get)")
            print(f"      → Device {device_id} ({device_category}/send)")
            print(f"      Conditions: {conditions}")
            print(f"      Action: {action_payload}")

    def add_trigger(self, name, sensor_id, conditions, device_id, action_payload):
        """Add new trigger"""
        print(f"🎮 CONTROLLER: Adding trigger '{name}'...")
        
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
        
        print(f"✅ CONTROLLER: Trigger '{name}' added successfully!")

    def delete_trigger(self, trigger_id):
        """Delete trigger"""
        self.__db.delete_trigger(trigger_id)
        
        self.__triggers = [tr for tr in self.__triggers if tr["id"] != trigger_id]
        
        print(f"✅ CONTROLLER: Deleted trigger ID {trigger_id}")

    def switch_trigger(self, trigger_id):
        """Toggle trigger enabled/disabled"""
        for trigger in self.__triggers:
            if trigger["id"] == trigger_id:
                target_state = (trigger["enabled"] + 1) % 2
                trigger["enabled"] = target_state
                self.__db.switch_trigger(trigger_id, target_state)
                
                status = "ENABLED" if target_state else "DISABLED"
                print(f"✅ CONTROLLER: Trigger '{trigger['name']}' {status}")
                break