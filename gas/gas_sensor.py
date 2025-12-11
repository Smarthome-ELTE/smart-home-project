"""
Gas Sensor Module
Handles gas leak detection and gas concentration monitoring
Publishes sensor data to MQTT topic: gas/get
"""

import json
import paho.mqtt.client as paho
from paho import mqtt


class GasSensor:
    """
    Gas Sensor Publisher
    Simulates gas sensors and publishes data to MQTT broker
    Detects gas leaks and gas concentration levels
    """
    
    def __init__(self, sensor_id, sensor_name, client_id, protocol, host, port, username, password):
        """
        Initialize Gas Sensor
        
        Args:
            sensor_id: Unique identifier for the sensor in database
            sensor_name: User-friendly name (e.g., 'Kitchen Gas Sensor')
            client_id: MQTT client identifier
            protocol: MQTT protocol version (e.g., paho.MQTTv5)
            host: MQTT broker host
            port: MQTT broker port
            username: MQTT username
            password: MQTT password
        """
        self.sensor_id = sensor_id
        self.sensor_name = sensor_name
        self.client_id = client_id
        self.protocol = protocol
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
        # Sensor state
        self.current_gas_level = 0  # ppm (parts per million)
        self.gas_detected = False
        self.alert_threshold = 100  # ppm - threshold for gas alert
        
        # MQTT Client
        self.client = paho.Client(client_id=self.client_id, protocol=self.protocol, userdata=None)
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        
        # Set up callbacks
        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print(f"🔋 GAS SENSOR '{self.sensor_name}': Connected successfully")
            else:
                print(f"❌ GAS SENSOR '{self.sensor_name}': Connection failed with code {rc}")
        
        def on_publish(client, userdata, mid, properties=None):
            print(f"📤 GAS SENSOR '{self.sensor_name}': Published message mid {mid}")
        
        self.client.on_connect = on_connect
        self.client.on_publish = on_publish
    
    def connect(self):
        """Connect to MQTT broker"""
        self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.host, self.port)
        print(f"🔗 GAS SENSOR '{self.sensor_name}': Connecting to {self.host}:{self.port}")
    
    def start(self):
        """Start the MQTT loop"""
        self.client.loop_start()
    
    def stop(self):
        """Stop the MQTT loop"""
        self.client.loop_stop()
    
    def publish_reading(self, gas_level):
        """
        Publish gas sensor reading
        
        Args:
            gas_level: Gas concentration level in ppm
        """
        self.current_gas_level = gas_level
        self.gas_detected = gas_level > self.alert_threshold
        
        payload = {
            "sensor_id": self.sensor_id,
            "sensor_name": self.sensor_name,
            "gas_level": gas_level,
            "unit": "ppm",
            "gas_detected": self.gas_detected,
            "alert_threshold": self.alert_threshold,
            "status": "alert" if self.gas_detected else "normal"
        }
        
        topic = "gas/get"
        self.client.publish(topic, json.dumps(payload), qos=1)
        print(f"[GAS] SENSOR '{self.sensor_name}': Published gas_level={gas_level}ppm, status={'ALERT' if self.gas_detected else 'OK'}")
    
    def simulate_reading(self, gas_level):
        """
        Simulate a gas sensor reading (for testing/Node-RED)
        
        Args:
            gas_level: Simulated gas level in ppm
        """
        self.publish_reading(gas_level)
