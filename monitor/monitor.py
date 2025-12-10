"""
Monitor Service - Logs all MQTT messages to database
Subscribes to all topics and records sensor/device activity
"""

import paho.mqtt.client as paho
from paho import mqtt
import json
from db.database import Database


class Monitor:
    """MQTT Monitor that logs all messages to database"""
    
    def __init__(self, client_id, protocol, db_path=None):
        self.db = Database(db_path=db_path)
        self.client = paho.Client(client_id=client_id, protocol=protocol, userdata=None)
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        
        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
    
    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback for when client connects to broker"""
        print("MONITOR: CONNACK received with code " + str(rc))
        
        # Subscribe to all topics
        client.subscribe("+/get", qos=1)
        print("MONITOR: Subscribed to topic '+/get'")
        
        client.subscribe("+/send", qos=1)
        print("MONITOR: Subscribed to topic '+/send'")
    
    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        """Callback for successful subscription"""
        print(f"MONITOR: Subscribed: {mid} {granted_qos}")
    
    def on_message(self, client, userdata, msg):
        """Callback for when a message is received"""
        try:
            payload_str = msg.payload.decode()
            print(f"MONITOR: Received message: {msg.topic} {msg.payload}")
            
            # Parse JSON payload
            payload = json.loads(payload_str)
            
            # Determine source type and ID
            if 'sensor_id' in payload:
                source_type = 'sensor'
                source_id = payload['sensor_id']
                
                # Update sensor's last_payload in database
                self.db.update_sensor_status(source_id, payload_str)
                
            elif 'device_id' in payload:
                source_type = 'device'
                source_id = payload['device_id']
                
                # Update device's current_status in database
                self.db.update_device_status(source_id, payload_str)
                
            else:
                # Unknown message type
                source_type = 'unknown'
                source_id = 0
                print(f"⚠️ MONITOR: Message with no sensor_id or device_id")
            
            # Log event to database
            self.db.log_event(source_type, source_id, payload_str)
            print(f"MONITOR: Logged event from {source_type} {source_id}.")
            
        except json.JSONDecodeError as e:
            print(f"⚠️ MONITOR: Invalid JSON: {msg.payload} - {e}")
        except Exception as e:
            print(f"⚠️ MONITOR: Error processing message: {e}")
    
    def connect(self, host, port, username, password):
        """Connect to MQTT broker"""
        self.client.username_pw_set(username, password)
        self.client.connect(host, port)
    
    def start(self):
        """Start the MQTT client loop"""
        self.client.loop_start()
        print("MONITOR: Starting loop...")
    
    def stop(self):
        """Stop the MQTT client loop"""
        self.client.loop_stop()
        print("MONITOR: Stopping loop...")