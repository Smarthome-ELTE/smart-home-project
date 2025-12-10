import json
import paho.mqtt.client as paho
from paho import mqtt
from db import Database


class Monitor:
    def __init__(self, client_id, protocol, db_path=None):
        self.__db_path = db_path
        self.__client = paho.Client(client_id=client_id, protocol=protocol, userdata=None)
        self.__client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

        def on_connect(client, userdata, flags, rc, properties=None):
            print(f"MONITOR: CONNACK received with code {rc}")
            client.subscribe("+/get", qos=1)
            print("MONITOR: Subscribed to topic '+/get'")

            client.subscribe("+/send", qos=1)
            print("MONITOR: Subscribed to topic '+/send'")

        def on_subscribe(client, userdata, mid, granted_qos, properties=None):
            print(f"MONITOR: Subscribed: {mid} {granted_qos}")

        def on_message(client, userdata, msg):
            print(f"MONITOR: Received message: {msg.topic} {msg.payload}")
            
            db = Database(db_path=self.__db_path)

            try:
                payload_data = json.loads(msg.payload)

                topic_parts = msg.topic.split('/')
                if len(topic_parts) == 2:
                    action_type = topic_parts[1]
                else:
                    action_type = "unknown"

                payload_data['action'] = action_type

                source_type = None
                source_id = None

                if "sensor_id" in payload_data:
                    source_id = payload_data["sensor_id"]
                    source_type = "sensor" 
                elif "device_id" in payload_data:
                    source_id = payload_data["device_id"]
                    source_type = "device"

                if source_type and source_id is not None:   
                    db.log_event(source_type, source_id, payload_data)
                    print(f"MONITOR: Logged event from {source_type} {source_id}.")
                else:
                    print("MONITOR: 'sensor_id' or 'device_id' not in payload. Not logging.")

            except json.JSONDecodeError:
                print(f"MONITOR: Error: Could not decode JSON payload from topic {msg.topic}")
            except Exception as e:
                print(f"MONITOR: An error occurred while logging event: {e}")

        self.__client.on_connect = on_connect
        self.__client.on_subscribe = on_subscribe
        self.__client.on_message = on_message

    def connect(self, host, port, username, password):
        self.__client.username_pw_set(username, password)
        self.__client.connect(host, port)

    def start(self):
        print("MONITOR: Starting loop...")
        self.__client.loop_start()

    def stop(self):
        print("MONITOR: Stopping loop...")
        self.__client.loop_stop()