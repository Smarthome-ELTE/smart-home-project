#!/usr/bin/env python3
"""
Diagnostic script to check database sensor and device IDs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import Database

def check_database():
    """Check what sensors and devices exist in database"""
    
    db = Database()
    
    print("=" * 60)
    print("DATABASE DIAGNOSTIC CHECK")
    print("=" * 60)
    
    # Check heating sensors
    print("\n📡 HEATING SENSORS (type = 'DHT22_Heating'):")
    cursor = db.conn.cursor()
    cursor.execute("""
        SELECT id, name, type, category 
        FROM sensors 
        WHERE type = 'DHT22_Heating'
        ORDER BY id
    """)
    sensors = cursor.fetchall()
    
    if sensors:
        for sensor_id, name, type_, category in sensors:
            print(f"  ID: {sensor_id} | Name: {name} | Type: {type_} | Category: {category}")
    else:
        print("  ⚠️  NO HEATING SENSORS FOUND!")
        print("  Run: python Heating/init_heating_db.py")
    
    # Check heating devices
    print("\n🔧 HEATING DEVICES (type = 'SmartHeater_v2'):")
    cursor.execute("""
        SELECT id, name, type, category 
        FROM devices 
        WHERE type = 'SmartHeater_v2'
        ORDER BY id
    """)
    devices = cursor.fetchall()
    
    if devices:
        for device_id, name, type_, category in devices:
            print(f"  ID: {device_id} | Name: {name} | Type: {type_} | Category: {category}")
    else:
        print("  ⚠️  NO HEATING DEVICES FOUND!")
        print("  Run: python Heating/init_heating_db.py")
    
    # Check all sensors (to see if wrong type)
    print("\n📊 ALL SENSORS IN DATABASE:")
    cursor.execute("SELECT id, name, type, category FROM sensors ORDER BY id")
    all_sensors = cursor.fetchall()
    
    if all_sensors:
        for sensor_id, name, type_, category in all_sensors:
            marker = "✅" if type_ == 'DHT22_Heating' else "❌"
            print(f"  {marker} ID: {sensor_id} | Name: {name} | Type: {type_} | Category: {category}")
    else:
        print("  ⚠️  DATABASE IS EMPTY!")
    
    # Check all devices
    print("\n🔧 ALL DEVICES IN DATABASE:")
    cursor.execute("SELECT id, name, type, category FROM devices ORDER BY id")
    all_devices = cursor.fetchall()
    
    if all_devices:
        for device_id, name, type_, category in all_devices:
            marker = "✅" if type_ == 'SmartHeater_v2' else "❌"
            print(f"  {marker} ID: {device_id} | Name: {name} | Type: {type_} | Category: {category}")
    else:
        print("  ⚠️  NO DEVICES IN DATABASE!")
    
    # Check heating rules
    print("\n⚙️  HEATING AUTOMATION RULES:")
    cursor.execute("""
        SELECT id, name, sensor_id, device_id, enabled 
        FROM triggers 
        WHERE name LIKE '%Heat%' OR name LIKE '%Room:%'
        ORDER BY id
    """)
    rules = cursor.fetchall()
    
    if rules:
        for rule_id, name, sensor_id, device_id, enabled in rules:
            status = "✓ Enabled" if enabled else "✗ Disabled"
            print(f"  {status} | Rule ID: {rule_id} | {name}")
            print(f"       Sensor: {sensor_id} → Device: {device_id}")
    else:
        print("  ⚠️  NO HEATING RULES FOUND!")
    
    print("\n" + "=" * 60)
    print("✅ DIAGNOSTIC COMPLETE")
    print("=" * 60)
    
    # Recommendations
    print("\n💡 NEXT STEPS:")
    
    if not sensors:
        print("  1. Run: python Heating/init_heating_db.py")
        print("     This will create sensors with correct types")
    
    if sensors:
        sensor_id = sensors[0][0]
        print(f"  1. Update Node-RED to use sensor_id: {sensor_id}")
        print(f"     In 'Generate Temperature' function node")
    
    if devices:
        device_id = devices[0][0]
        print(f"  2. Heater device ID is: {device_id}")
    
    db.close()

if __name__ == "__main__":
    check_database()