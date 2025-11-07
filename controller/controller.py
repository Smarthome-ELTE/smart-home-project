import paho.mqtt.client as paho
from paho import mqtt
import json

from db import Database

def is_rule_valid(rule, msg):
    if rule["topic"] != msg.topic:
        return False
    is_triggers_valid = True
    msg_payload = json.loads(msg.payload)
    for trigger in rule["conditions"]:
       is_triggers_valid = is_triggers_valid and (trigger['key'] in msg_payload and msg_payload[trigger['key']] == trigger['value'])
    return is_triggers_valid


class Controller:
    def __init__(self, client_id, protocol, db_path=None):
        self.db = Database(db_path=db_path)
        self.client = paho.Client(client_id=client_id, protocol=protocol, userdata=None)
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

        self.triggers = []

        def on_connect(client, userdata, flags, rc, properties=None):
            print("CONNACK received with code " + str(rc))

        def on_publish(client, userdata, mid, properties=None):
            print("Published mid: " + str(mid))

        def on_subscribe(client, userdata, mid, granted_qos, properties=None):
            print("Subscribed: " + str(mid) + " " + str(granted_qos))

        def on_message(client, userdata, msg):
            print("Received message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
            for trigger in self.triggers:
                if is_rule_valid(trigger["trigger"], msg):
                    print("Running rule: " + trigger["name"])
                    for action in trigger["actions"]:
                        self.publish(action["topic"], json.dumps(action["payload"]), action["qos"])
                else:
                    print("Rule " + trigger["name"] + " not valid")


        self.client.on_connect = on_connect
        self.client.on_subscribe = on_subscribe
        self.client.on_publish = on_publish
        self.client.on_message = on_message

    def connect(self, host, port, username, password):
        self.client.username_pw_set(username, password)
        self.client.connect(host, port)

    def start(self):
        self.client.loop_start()
        self.load_rules()

    def stop(self):
        self.client.loop_stop()

    def subscribe(self, topic, qos):
        self.client.subscribe(topic, qos)

    def publish(self, topic, payload, qos):
        self.client.publish(topic, payload, qos)

    def load_rules(self):
        db_triggers = self.db.get_all_triggers()
        for db_trigger in db_triggers:
            trigger = {
                "id": int(db_trigger[0]),
                "name": db_trigger[1],
                "condition": {
                    "sensor_id": int(db_trigger[2]),
                    "topic": self.db.get_sensor_category(int(db_trigger[2])) + "/get",
                    "conditions": json.loads(db_trigger[3]),
                },
                "actions": [
                    {
                        "topic": self.db.get_device_category(int(db_trigger[4])) + "/send",
                        "payload": {"device_id": int(db_trigger[4])} | json.loads(db_trigger[5]),
                        "qos": 1
                    }
                ],
                "enabled": int(db_trigger[6])
            }
            self.triggers.append(trigger)

    def add_rule(self, name, sensor_id, conditions, device_id, action_payload):
        trigger_id = self.db.add_trigger(name, sensor_id, conditions, device_id, action_payload)
        trigger = {
            "id": trigger_id,
            "name": name,
            "condition": {
                "sensor_id": sensor_id,
                "topic": self.db.get_sensor_category(sensor_id) + "/get",
                "conditions": conditions,
            },
            "actions": [
                {
                    "topic": self.db.get_device_category(device_id) + "/send",
                    "payload": {"device_id": device_id} | action_payload,
                    "qos": 1
                }
            ],
            "enabled": 1
        }
        self.triggers.append(trigger)

    def delete_rule(self, trigger_id):
        self.db.delete_trigger(trigger_id)
        rule_to_delete = None
        for rule in self.triggers:
            if rule["id"] == trigger_id:
                rule_to_delete = rule
        if rule_to_delete is not None: self.triggers.remove(rule_to_delete)

    def switch_trigger(self, trigger_id):
        for trigger in self.triggers:
            if trigger["id"] == trigger_id:
                target_state = (trigger["enabled"] + 1) % 2
                trigger["enabled"] = target_state
                self.db.switch_trigger(trigger_id, target_state)
