"""
Database module for Smart Home System
Handles SQLite database operations for sensors, devices, triggers, and events
"""

import sqlite3
import json
from datetime import datetime


class Database:
    def __init__(self, db_path=None):
        """Initialize database connection and create tables if needed"""
        if db_path is None:
            db_path = 'db/smart_home_monitor.db'
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Sensors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                type TEXT NOT NULL,
                last_payload TEXT,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                type TEXT NOT NULL,
                current_status TEXT,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Triggers/Automation Rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sensor_id INTEGER NOT NULL,
                condition TEXT NOT NULL,
                device_id INTEGER NOT NULL,
                action_payload TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                FOREIGN KEY (sensor_id) REFERENCES sensors(id),
                FOREIGN KEY (device_id) REFERENCES devices(id)
            )
        ''')
        
        # Events log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,
                source_id INTEGER NOT NULL,
                payload TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trigger execution log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trigger_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger_id INTEGER NOT NULL,
                executed_at TIMESTAMP NOT NULL,
                FOREIGN KEY (trigger_id) REFERENCES triggers(id)
            )
        ''')
        
        self.conn.commit()
    
    # ========================================
    # SENSOR METHODS
    # ========================================
    
    def get_all_sensors(self):
        """Get all sensors"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sensors")
        return cursor.fetchall()
    
    def get_sensor_by_id(self, sensor_id):
        """Get sensor by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sensors WHERE id = ?", (sensor_id,))
        return cursor.fetchone()
    
    def get_sensor_category(self, sensor_id):
        """Get sensor category by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT category FROM sensors WHERE id = ?", (sensor_id,))
        result = cursor.fetchone()
        return result[0] if result else "unknown"
    
    def get_all_sensor_categories(self):
        """Get all unique sensor categories"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM sensors")
        return cursor.fetchall()
    
    def update_sensor_status(self, sensor_id, payload):
        """Update sensor's last payload and timestamp"""
        cursor = self.conn.cursor()
        
        # If payload is dict, convert to JSON string
        if isinstance(payload, dict):
            payload_str = json.dumps(payload)
        else:
            payload_str = payload
        
        cursor.execute("""
            UPDATE sensors 
            SET last_payload = ?, 
                last_update = datetime('now') 
            WHERE id = ?
        """, (payload_str, sensor_id))
        
        self.conn.commit()
    
    # ========================================
    # DEVICE METHODS
    # ========================================
    
    def get_all_devices(self):
        """Get all devices"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM devices")
        return cursor.fetchall()
    
    def get_device_by_id(self, device_id):
        """Get device by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        return cursor.fetchone()
    
    def get_device_category(self, device_id):
        """Get device category by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT category FROM devices WHERE id = ?", (device_id,))
        result = cursor.fetchone()
        return result[0] if result else "unknown"
    
    def update_device_status(self, device_id, payload):
        """Update device's current status and timestamp"""
        cursor = self.conn.cursor()
        
        # If payload is dict, convert to JSON string
        if isinstance(payload, dict):
            payload_str = json.dumps(payload)
        else:
            payload_str = payload
        
        cursor.execute("""
            UPDATE devices 
            SET current_status = ?, 
                last_update = datetime('now') 
            WHERE id = ?
        """, (payload_str, device_id))
        
        self.conn.commit()
    
    # ========================================
    # TRIGGER/AUTOMATION METHODS
    # ========================================
    
    def get_all_triggers(self):
        """Get all automation triggers"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM triggers")
        return cursor.fetchall()
    
    def add_trigger(self, name, sensor_id, condition, device_id, action_payload):
        """Add new automation trigger"""
        cursor = self.conn.cursor()
        
        # Convert dicts to JSON strings
        condition_str = json.dumps(condition) if isinstance(condition, dict) else condition
        action_str = json.dumps(action_payload) if isinstance(action_payload, dict) else action_payload
        
        cursor.execute("""
            INSERT INTO triggers (name, sensor_id, condition, device_id, action_payload, enabled)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (name, sensor_id, condition_str, device_id, action_str))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def delete_trigger(self, trigger_id):
        """Delete automation trigger"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM triggers WHERE id = ?", (trigger_id,))
        self.conn.commit()
    
    def switch_trigger(self, trigger_id, target_state=None):
        """Toggle trigger enabled/disabled state"""
        cursor = self.conn.cursor()
        
        if target_state is None:
            # Toggle
            cursor.execute("""
                UPDATE triggers 
                SET enabled = CASE WHEN enabled = 1 THEN 0 ELSE 1 END 
                WHERE id = ?
            """, (trigger_id,))
        else:
            # Set specific state
            cursor.execute("""
                UPDATE triggers 
                SET enabled = ? 
                WHERE id = ?
            """, (target_state, trigger_id))
        
        self.conn.commit()
    
    def log_trigger(self, trigger_id, executed_at):
        """Log trigger execution"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO trigger_logs (trigger_id, executed_at)
            VALUES (?, ?)
        """, (trigger_id, executed_at))
        self.conn.commit()
    
    # ========================================
    # EVENT LOGGING METHODS
    # ========================================
    
    def log_event(self, source_type, source_id, payload):
        """Log an event (sensor reading or device action)"""
        cursor = self.conn.cursor()
        
        # Convert payload to JSON string if it's a dict
        if isinstance(payload, dict):
            payload_str = json.dumps(payload)
        else:
            payload_str = payload
        
        cursor.execute("""
            INSERT INTO events (source_type, source_id, payload, timestamp)
            VALUES (?, ?, ?, datetime('now'))
        """, (source_type, source_id, payload_str))
        
        self.conn.commit()
    
    def get_recent_events(self, limit=50):
        """Get recent events"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, source_type, source_id, payload, timestamp
            FROM events
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
    
    def get_events_by_source(self, source_type, source_id, limit=20):
        """Get events for specific sensor or device"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, source_type, source_id, payload, timestamp
            FROM events
            WHERE source_type = ? AND source_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (source_type, source_id, limit))
        return cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        self.conn.close()