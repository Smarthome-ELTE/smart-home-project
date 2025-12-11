"""
Monitor Service - Logs all MQTT messages to database
Subscribes to all topics and records sensor/device activity

"""

import paho.mqtt.client as paho
from paho import mqtt
import json
from datetime import datetime, timedelta
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
        
        # Add deduplication tracking
        self.last_logged = {}
        self.min_log_interval = timedelta(seconds=3)  # Only log same device every 3 seconds
    
    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback for when client connects to broker"""
        print("✅ MONITOR: Connected to MQTT broker")
        
        # Subscribe to all topics
        client.subscribe("+/get", qos=1)
        client.subscribe("+/send", qos=1)
        print("✅ MONITOR: Subscribed to all topics")
    
    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        """Callback for successful subscription"""
        # Removed spam - only log once on startup
        pass
    
    def _should_log_to_console(self, source_type, source_id, payload):
        """Determine if we should log this message to console"""
        now = datetime.now()
        key = f"{source_type}_{source_id}"
        
        # First time seeing this source
        if key not in self.last_logged:
            self.last_logged[key] = {'time': now, 'payload': payload}
            return True, "first_message"
        
        last_entry = self.last_logged[key]
        time_diff = now - last_entry['time']
        
        # Check if payload changed significantly
        if self._payload_changed(last_entry['payload'], payload):
            self.last_logged[key] = {'time': now, 'payload': payload}
            return True, "state_changed"
        
        # Periodic update
        if time_diff > self.min_log_interval:
            self.last_logged[key] = {'time': now, 'payload': payload}
            return True, "periodic"
        
        return False, "no_change"
    
    def _payload_changed(self, old_payload, new_payload):
        """Check if payload changed significantly"""
        try:
            old = json.loads(old_payload) if isinstance(old_payload, str) else old_payload
            new = json.loads(new_payload) if isinstance(new_payload, str) else new_payload
            
            # Check for state changes
            if old.get('state') != new.get('state'):
                return True
            
            if old.get('action') != new.get('action'):
                return True
            
            # Check temperature change (0.5°C threshold)
            old_temp = old.get('temperature', old.get('current_temp', 0))
            new_temp = new.get('temperature', new.get('current_temp', 0))
            if abs(old_temp - new_temp) >= 0.5:
                return True
            
            return False
        except:
            return False
    
    def on_message(self, client, userdata, msg):
        """Callback for when a message is received"""
        try:
            payload_str = msg.payload.decode()
            
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
            
            # Log event to database (always, silently)
            self.db.log_event(source_type, source_id, payload_str)
            
            # Only log to console if significant
            should_log, reason = self._should_log_to_console(source_type, source_id, payload_str)
            
            if should_log:
                # Clean, readable log output
                if source_type == 'sensor':
                    temp = payload.get('temperature', '?')
                    humidity = payload.get('humidity', '?')
                    print(f"📊 MONITOR: Sensor {source_id} → {temp}°C, {humidity}% [{reason}]")
                elif source_type == 'device':
                    state = payload.get('state', '?')
                    target = payload.get('target_temp', payload.get('temperature', '?'))
                    action = payload.get('action', 'status')
                    print(f"🔧 MONITOR: Device {source_id} → {state.upper()}, Target: {target}°C [{action}]")
            
        except json.JSONDecodeError as e:
            print(f"⚠️ MONITOR: Invalid JSON: {msg.payload}")
        except Exception as e:
            print(f"⚠️ MONITOR: Error: {e}")
    
    def connect(self, host, port, username, password):
        """Connect to MQTT broker"""
        self.client.username_pw_set(username, password)
        self.client.connect(host, port)
    
    def start(self):
        """Start the MQTT client loop"""
        self.client.loop_start()
        print("🚀 MONITOR: Service started")
    
    def stop(self):
        """Stop the MQTT client loop"""
        self.client.loop_stop()
        print("🛑 MONITOR: Service stopped")