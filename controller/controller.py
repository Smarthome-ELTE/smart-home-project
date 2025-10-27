import paho.mqtt.client as paho
from paho import mqtt


class Controller:
    def __init__(self, client_id, protocol):
        self.client = paho.Client(client_id=client_id, protocol=protocol, userdata=None)
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.on_connect = on_connect
        self.client.on_subscribe = on_subscribe
        self.client.on_publish = on_publish
        self.client.on_message = on_message

    def connect(self, host, port, username, password):
        self.client.username_pw_set(username, password)
        self.client.connect(host, port)

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()

    def subscribe(self, topic, qos):
        self.client.subscribe(topic, qos)

    def publish(self, topic, payload, qos):
        self.client.publish(topic, payload, qos)


def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code " + str(rc))


def on_publish(client, userdata, mid, properties=None):
    print("Piblished mid: " + str(mid))


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
