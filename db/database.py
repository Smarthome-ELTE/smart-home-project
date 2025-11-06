from datetime import datetime
import json
import os
import sqlite3


class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join("db", "smart_home_monitor.db")
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
        
        /* Sensors */
        
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   
            name TEXT NOT NULL,                             -- User friendly name for GUI, e.g.: 'Living Room Temperature'      
            category TEXT NOT NULL,                         -- Sensor category, e.q.: 'temperature', 'light', 'gas', 'water' 
            type TEXT NOT NULL,                             -- Sensor type, e.q.: 'Thermometer', 'Hygrometer'                                                        
            last_payload TEXT,                              -- Cached JSON of the most recent data from this sensor, e.g.: '{"value": 21.5}'                                                       
            last_update TIMESTAMP                           -- The date and time 'last_payload' was updated.         
        );

        /* Devices */
        
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   
            name TEXT NOT NULL,                             -- User friendly name for GUI, e.g.: 'Main Heater'
            category TEXT NOT NULL,                         -- Device category, e.q.: 'temperature', 'light', 'gas', 'water' 
            type TEXT NOT NULL,                             -- Device type, e.q.: 'Heater', 'Plug', 'Lightbulb'                 
            current_status TEXT,                            -- Cached JSON of the most recent device state, e.g.: '{"state": "on", "mode": "auto"}'
            last_update TIMESTAMP                           -- The date and time 'current_status' was updated.
        );

        /* Events */
        
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,                      -- Specifies which table the 'source_id' refers to, e.g.: 'sensor' or 'device' 
            source_id INTEGER NOT NULL,                     -- The 'id' from either the 'sensors' or 'devices' table that this event came from
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

    def log_event(self, source_type, source_id, payload_json):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO events (source_type, source_id, payload)
            VALUES (?, ?, ?)
        """, (source_type, source_id, json.dumps(payload_json)))
        self.conn.commit()

    def get_recent_events(self, limit=50):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))
        return cursor.fetchall()

    def get_sensor_category(self, sensor_id):
        cur = self.conn.cursor()
        cur.execute("SELECT category FROM sensors WHERE id=?", (sensor_id,))
        row = cur.fetchone()
        return row[0] if row else "unknown"

    def get_device_category(self, device_id):
        cur = self.conn.cursor()
        cur.execute("SELECT category FROM devices WHERE id=?", (device_id,))
        row = cur.fetchone()
        return row[0] if row else "unknown"

    def add_trigger(self, name, sensor_id, condition, device_id, action_payload, enabled):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO triggers (name, sensor_id, condition, device_id, action_payload, enabled)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, sensor_id, json.dumps(condition), device_id, json.dumps(action_payload), enabled))
        self.conn.commit()
