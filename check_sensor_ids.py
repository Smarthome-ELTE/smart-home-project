#!/usr/bin/env python3
"""
Quick diagnostic: Check last 10 events to see what sensor IDs are being used
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import Database
import json

db = Database()

print("=" * 60)
print("LAST 10 EVENTS - SENSOR ID CHECK")
print("=" * 60)

cursor = db.conn.cursor()
cursor.execute("""
    SELECT source_type, source_id, payload, timestamp 
    FROM events 
    ORDER BY timestamp DESC 
    LIMIT 10
""")

events = cursor.fetchall()

for source_type, source_id, payload_str, timestamp in events:
    try:
        payload = json.loads(payload_str)
        
        if source_type == 'sensor':
            # Check if this sensor exists
            cursor.execute("SELECT name, type, category FROM sensors WHERE id = ?", (source_id,))
            sensor = cursor.fetchone()
            
            if sensor:
                name, type_, category = sensor
                print(f"✅ sensor_id: {source_id} EXISTS → {name} ({type_}) → {category}/get")
            else:
                print(f"❌ sensor_id: {source_id} NOT FOUND → shows as unknown/get")
                
        elif source_type == 'device':
            cursor.execute("SELECT name, type, category FROM devices WHERE id = ?", (source_id,))
            device = cursor.fetchone()
            
            if device:
                name, type_, category = device
                action = payload.get('action', 'unknown')
                print(f"✅ device_id: {source_id} EXISTS → {name} ({type_}) → {category}/{action}")
            else:
                print(f"❌ device_id: {source_id} NOT FOUND")
                
    except Exception as e:
        print(f"⚠️  Error parsing event: {e}")

print("\n" + "=" * 60)
print("EXPECTED SENSOR IDS:")
print("=" * 60)

cursor.execute("SELECT id, name, type FROM sensors WHERE type='DHT22_Heating'")
for sensor_id, name, type_ in cursor.fetchall():
    print(f"  ✅ Use sensor_id: {sensor_id} for {name}")

db.close()