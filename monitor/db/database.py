from datetime import datetime
import json
import os
import sqlite3


class MonitorDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join("monitor", "db", "smart_home_monitor.db")
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
        
        /* Sensors */
        
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   
            name TEXT NOT NULL,                             -- User friendly name for GUI, e.g.: 'Living Room Temperature'             
            type TEXT NOT NULL,                             -- Sensor category, e.q.: 'Temperature', 'Light', 'Gas', 'Water'         
            data_topic TEXT UNIQUE NOT NULL,                -- The unique 'address' this sensor sends data to, e.g.: 'smarthome/living_room/temperature'                                                   
            last_payload TEXT,                              -- A *cache* of the last JSON data from this sensor, e.g.: '{"value": 21.5}'                                                       
            last_update TIMESTAMP                            -- The date and time 'last_payload' was updated.         
        );

        /* Devices */
        
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   
            name TEXT NOT NULL,                             -- User friendly name for GUI, e.g.: 'Main Heater'
            type TEXT NOT NULL,                             -- Device category, e.g., 'Smart bulb', 'Heater'
            status_topic TEXT UNIQUE NOT NULL,              -- The unique 'address' this device sends its *current_status* to, e.g.: 'smarthome/main_heater/status'
            command_topic TEXT UNIQUE NOT NULL,             -- The unique 'address' the Controller sends *commands* to, e.g.: 'smarthome/main_heater/set'
            current_status TEXT,                            -- A *cache* of the last JSON status received from 'status_topic', e.g.: '{"state": "on", "mode": "auto"}' */
            last_update TIMESTAMP                           -- The date and time 'current_status' was updated.
        );

        /* Events */
        
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,                      -- Specifies which table the 'source_id' refers to, e.g.: 'sensor' or 'device' 
            source_id INTEGER NOT NULL,                     -- The 'id' from either the 'sensors' or 'devices' table that this event came from
            topic TEXT NOT NULL,                            -- The MQTT topic (address) the message was published on, e.g.: 'smarthome/living_room/temperature'
            payload TEXT NOT NULL,                          -- The full JSON data exactly as it was received, e.g.: '{"value": 21.5, "unit": "C"}' 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP    -- The date and time this event was saved to the database. (Automatically set by SQLite) 
        );      

        /* Triggers */
        
        CREATE TABLE IF NOT EXISTS triggers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,                             -- User-friendly name for the GUI. e.g.: 'Turn on heater when cold'
            sensor_id INTEGER NOT NULL,                     -- The 'id' from the 'sensors' table that this rule "listens" to.
            condition TEXT NOT NULL,                        -- The condition logic, e.g.: 'payload.temperature > 25'
            device_id INTEGER NOT NULL,                     -- The 'id' from the 'devices' table that this rule controls.
            action_payload TEXT NOT NULL,                   -- The JSON command to send to device, e.g.: '{"state": "off"}'
            enabled INTEGER NOT NULL DEFAULT 1,             -- A simple toggle (0=disabled, 1=enabled) so users can turn rules on or off from the GUI 
            last_triggered TIMESTAMP,                       -- Logs the last time this rule was successfully fired
            
            -- Links this rule to a specific sensor
            FOREIGN KEY (sensor_id) REFERENCES sensors (id),
            
            -- Links this rule to a specific device
            FOREIGN KEY (device_id) REFERENCES devices (id)
        );
        """)
        self.conn.commit()

    def log_event(self, source_type, source_id, topic, payload_json):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO events (source_type, source_id, topic, payload)
            VALUES (?, ?, ?, ?)
        """, (source_type, source_id, topic, json.dumps(payload_json)))
        self.conn.commit()

    def get_recent_events(self, limit=50):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))
        return cursor.fetchall()
