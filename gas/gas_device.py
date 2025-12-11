"""
Gas Pipe Valve Module
Handles control of gas pipe valves
Subscribes to MQTT topic: gas/send
"""

import json
import paho.mqtt.client as paho
from paho import mqtt


class GasPipeValve:
    """
    Gas Pipe Valve Actuator
    Controls gas pipe valves based on automation rules
    Listens on MQTT topic: gas/send
    """
    
    def __init__(self, device_id, device_name, client_id, protocol, host, port, username, password):
        """
        Initialize Gas Pipe Valve
        
        Args:
            device_id: Unique identifier for the device in database
            device_name: User-friendly name (e.g., 'Main Gas Valve')
            client_id: MQTT client identifier
            protocol: MQTT protocol version (e.g., paho.MQTTv5)
            host: MQTT broker host
            port: MQTT broker port
            username: MQTT username
            password: MQTT password
        """
        self.device_id = device_id
        self.device_name = device_name
        self.client_id = client_id
        self.protocol = protocol
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
        # Device state
        self.valve_state = "closed"  # "open" or "closed"
        self.mode = "manual"  # "manual" or "auto"
        
        # MQTT Client
        self.client = paho.Client(client_id=self.client_id, protocol=self.protocol, userdata=None)
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        
        # Set up callbacks
        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print(f"🚰 GAS PIPE VALVE '{self.device_name}': Connected successfully")
                client.subscribe("gas/send", qos=1)
            else:
                print(f"❌ GAS PIPE VALVE '{self.device_name}': Connection failed with code {rc}")
        
        def on_message(client, userdata, msg):
            self._on_message_received(msg)
        
        def on_subscribe(client, userdata, mid, granted_qos, properties=None):
            print(f"✅ GAS PIPE VALVE '{self.device_name}': Subscribed to gas/send")
        
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_subscribe = on_subscribe
    
    def connect(self):
        """Connect to MQTT broker"""
        self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.host, self.port)
        print(f"🔗 GAS PIPE VALVE '{self.device_name}': Connecting to {self.host}:{self.port}")
    
    def start(self):
        """Start the MQTT loop"""
        self.client.loop_start()
    
    def stop(self):
        """Stop the MQTT loop"""
        self.client.loop_stop()
    
    def _on_message_received(self, msg):
        """
        Handle incoming MQTT message
        
        Args:
            msg: MQTT message object
        """
        try:
            payload = json.loads(msg.payload)
            
            if payload.get("device_id") != self.device_id:
                return
            
            # Extract command
            command = payload.get("state", "").lower()
            mode = payload.get("mode", "manual")
            
            if command in ["open", "close"]:
                self.set_valve(command)
                self.mode = mode
                self._publish_status()
            else:
                print(f"⚠️  GAS PIPE VALVE '{self.device_name}': Unknown command '{command}'")
        
        except json.JSONDecodeError:
            print(f"❌ GAS PIPE VALVE '{self.device_name}': Invalid JSON payload")
        except Exception as e:
            print(f"❌ GAS PIPE VALVE '{self.device_name}': Error processing message: {e}")
    
    def set_valve(self, state):
        """
        Set valve state
        
        Args:
            state: "open" or "close"
        """
        if state.lower() in ["open", "close"]:
            self.valve_state = state.lower()
            status_marker = "[OPEN]" if state == "open" else "[CLOSED]"
            print(f"{status_marker} GAS PIPE VALVE '{self.device_name}': Valve set to {state.upper()}")
            self._publish_status()
        else:
            print(f"⚠️  GAS PIPE VALVE '{self.device_name}': Invalid state '{state}'")
    
    def _publish_status(self):
        """Publish current valve status"""
        payload = {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "state": self.valve_state,
            "mode": self.mode,
            "status": "open" if self.valve_state == "open" else "closed"
        }
        
        topic = "gas/send"
        self.client.publish(topic, json.dumps(payload), qos=1)
        print(f"[PUBLISH] GAS PIPE VALVE '{self.device_name}': Status published - {self.valve_state.upper()}")
    
    def open_valve(self):
        """Open the gas pipe valve"""
        self.set_valve("open")
    
    def close_valve(self):
        """Close the gas pipe valve (emergency/safety measure)"""
        self.set_valve("close")
    
    def get_status(self):
        """Get current valve status"""
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "state": self.valve_state,
            "mode": self.mode
        }
