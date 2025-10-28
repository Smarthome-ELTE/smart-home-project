import paho.mqtt.client as paho
from paho import mqtt
import json


def is_rule_valid(rule, msg):
    if rule["topic"] != msg.topic:
        return False
    is_triggers_valid = True
    msg_payload = json.loads(msg.payload)
    for trigger in rule["conditions"]:
        if trigger['key'] in msg_payload and msg_payload[trigger['key']] == trigger['value']:
            is_triggers_valid = is_triggers_valid and True
        else:
            is_triggers_valid = is_triggers_valid and False
    return is_triggers_valid


class Controller:
    def __init__(self, client_id, protocol):
        self.client = paho.Client(client_id=client_id, protocol=protocol, userdata=None)
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

        self.rules = []

        def on_connect(client, userdata, flags, rc, properties=None):
            print("CONNACK received with code " + str(rc))

        def on_publish(client, userdata, mid, properties=None):
            print("Piblished mid: " + str(mid))

        def on_subscribe(client, userdata, mid, granted_qos, properties=None):
            print("Subscribed: " + str(mid) + " " + str(granted_qos))

        def on_message(client, userdata, msg):
            print("Received message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
            for rule in self.rules:
                if is_rule_valid(rule["trigger"], msg):
                    print("Running rule: " + rule["name"])
                    for action in rule["actions"]:
                        self.publish(action["topic"], json.dumps(action["payload"]), action["qos"])
                else:
                    print("Rule " + rule["name"] + " not valid")


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
        self.save_rules()

    def subscribe(self, topic, qos):
        self.client.subscribe(topic, qos)

    def publish(self, topic, payload, qos):
        self.client.publish(topic, payload, qos)

    def load_rules(self):
        with open('controller_rules.json') as json_file:
            self.rules = json.load(json_file)

    def save_rules(self):
        with open('controller_rules.json', 'w') as json_file:
            json_file.write(json.dumps(self.rules))

    def add_rule(self, rule):
        self.rules.append(rule)

    def delete_rule(self, rule_name):
        rule_to_delete = None
        for rule in self.rules:
            if rule["name"] == rule_name:
                rule_to_delete = rule
        if rule_to_delete is not None: self.rules.remove(rule_to_delete)
