import datetime

import paho.mqtt.client as paho
from paho import mqtt
import json

from db import Database


def is_rule_valid(trigger_condition, msg):
    if trigger_condition["topic"] != msg.topic:
        return False
    msg_payload = json.loads(msg.payload)
    if "sensor_id" not in msg_payload or trigger_condition["sensor_id"] != msg_payload["sensor_id"]:
        return False
    conditions = trigger_condition["conditions"]
    is_triggers_valid = True

    for key, comparator in conditions.items():
        is_triggers_valid = is_triggers_valid and (
                key in msg_payload and eval(str(msg_payload[key]) + comparator))
        if not is_triggers_valid:
            break
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
            print("Received message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
            enabled_triggers = filter(lambda tr: tr["enabled"] > 0, self.__triggers)
            for trigger in enabled_triggers:
                if is_rule_valid(trigger["condition"], msg):
                    print("Running trigger_condition: " + trigger["name"])
                    self.__db.log_trigger(trigger["id"], datetime.datetime.now())
                    for action in trigger["actions"]:
                        self.publish(action["topic"], json.dumps(action["payload"]), action["qos"])
                else:
                    print("Rule " + trigger["name"] + " not valid")

        self.__client.on_connect = on_connect
        self.__client.on_subscribe = on_subscribe
        self.__client.on_publish = on_publish
        self.__client.on_message = on_message

        categories = set(map(lambda cat_tuple: cat_tuple[0], self.__db.get_all_sensor_categories()))
        for category in categories:
            self.__client.subscribe(category + "/get", 1)

    def connect(self, host, port, username, password):
        self.__client.username_pw_set(username, password)
        self.__client.connect(host, port)

    def start(self):
        self.__client.loop_start()
        self.load_rules()

    def stop(self):
        self.__client.loop_stop()

    def subscribe(self, topic, qos):
        self.__client.subscribe(topic, qos)

    def publish(self, topic, payload, qos):
        self.__client.publish(topic, payload, qos)

    def load_rules(self):
        db_triggers = self.__db.get_all_triggers()
        for db_trigger in db_triggers:
            trigger = {
                "id": int(db_trigger[0]),
                "name": db_trigger[1],
                "condition": {
                    "sensor_id": int(db_trigger[2]),
                    "topic": self.__db.get_sensor_category(int(db_trigger[2])) + "/get",
                    "conditions": json.loads(db_trigger[3]),
                },
                "actions": [
                    {
                        "topic": self.__db.get_device_category(int(db_trigger[4])) + "/send",
                        "payload": {"device_id": int(db_trigger[4])} | json.loads(db_trigger[5]),
                        "qos": 1
                    }
                ],
                "enabled": int(db_trigger[6])
            }
            self.__triggers.append(trigger)

    def add_rule(self, name, sensor_id, conditions, device_id, action_payload):
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
                    "payload": {"device_id": device_id} | action_payload,
                    "qos": 1
                }
            ],
            "enabled": 1
        }
        self.__triggers.append(trigger)

    def delete_rule(self, trigger_id):
        self.__db.delete_trigger(trigger_id)
        rule_to_delete = None
        for rule in self.__triggers:
            if rule["id"] == trigger_id:
                rule_to_delete = rule
        if rule_to_delete is not None: self.__triggers.remove(rule_to_delete)

    def switch_trigger(self, trigger_id):
        for trigger in self.__triggers:
            if trigger["id"] == trigger_id:
                target_state = (trigger["enabled"] + 1) % 2
                trigger["enabled"] = target_state
                self.__db.switch_trigger(trigger_id, target_state)
