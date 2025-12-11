"""
Gas System Database Initialization
Populates database with gas sensors and gas pipe valve devices
"""

from db import Database
import json


def init_gas_db(db_path=None):
    """
    Initialize gas sensors and devices in the database
    
    Args:
        db_path: Path to the database file (optional)
    """
    db = Database(db_path=db_path)
    
    print("\n" + "="*60)
    print("🔧 GAS SYSTEM INITIALIZATION")
    print("="*60)
    
    # Define Gas Sensors
    gas_sensors = [
        {
            "name": "Kitchen Gas Sensor",
            "category": "gas",
            "type": "MQ-6 Gas Sensor"
        },
        {
            "name": "Living Room Gas Sensor",
            "category": "gas",
            "type": "MQ-6 Gas Sensor"
        },
        {
            "name": "Utility Room Gas Sensor",
            "category": "gas",
            "type": "MQ-6 Gas Sensor"
        }
    ]
    
    # Define Gas Devices (Valves)
    gas_devices = [
        {
            "name": "Main Gas Pipe Valve",
            "category": "gas",
            "type": "Solenoid Valve",
            "default_status": {"state": "closed", "mode": "auto"}
        },
        {
            "name": "Kitchen Gas Valve",
            "category": "gas",
            "type": "Manual Ball Valve",
            "default_status": {"state": "closed", "mode": "manual"}
        },
        {
            "name": "Boiler Gas Valve",
            "category": "gas",
            "type": "Solenoid Valve",
            "default_status": {"state": "closed", "mode": "auto"}
        }
    ]
    
    # Add gas sensors to database
    print("\n📊 Adding Gas Sensors:")
    cursor = db.conn.cursor()
    for sensor in gas_sensors:
        try:
            cursor.execute("""
                INSERT INTO sensors (name, category, type, last_payload, last_update)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (sensor["name"], sensor["category"], sensor["type"], 
                  json.dumps({"gas_level": 0, "unit": "ppm", "status": "normal"})))
            
            sensor_id = cursor.lastrowid
            db.conn.commit()
            print(f"   ✅ Added: {sensor['name']} (ID: {sensor_id})")
        except Exception as e:
            print(f"   ❌ Error adding {sensor['name']}: {e}")
    
    # Add gas devices to database
    print("\n🚰 Adding Gas Pipe Valves:")
    for device in gas_devices:
        try:
            cursor.execute("""
                INSERT INTO devices (name, category, type, current_status, last_update)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (device["name"], device["category"], device["type"], 
                  json.dumps(device["default_status"])))
            
            device_id = cursor.lastrowid
            db.conn.commit()
            print(f"   ✅ Added: {device['name']} (ID: {device_id})")
        except Exception as e:
            print(f"   ❌ Error adding {device['name']}: {e}")
    
    print("\n" + "="*60)
    print("✨ Gas System Initialization Complete!")
    print("="*60)
    print("\nSensors and devices are now ready for automation rules.")
    print("Use Controller to create triggers based on gas sensor readings.")


if __name__ == "__main__":
    init_gas_db()
