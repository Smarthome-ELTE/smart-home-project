"""
SIMPLIFIED Database Init - BEDROOM ONLY
One functional rule: Heat when cold
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import Database
import json


def initialize_heating_system():
    """Initialize database - BEDROOM ONLY, ONE RULE"""
    
    db = Database()
    
    print("=" * 60)
    print("BEDROOM HEATING SYSTEM - SIMPLIFIED INIT")
    print("=" * 60)
    
    print("\n🗑️  Clearing all data...")
    cursor = db.conn.cursor()
    cursor.execute("DELETE FROM events")
    cursor.execute("DELETE FROM triggers")
    cursor.execute("DELETE FROM devices")
    cursor.execute("DELETE FROM sensors")
    db.conn.commit()
    print("✅ Database cleared")
    
    # ========================================
    # BEDROOM SENSOR (ID: 100)
    # ========================================
    print("\n📡 Adding Bedroom Temperature Sensor...")
    cursor.execute("""
        INSERT INTO sensors (id, name, category, type, last_payload, last_update)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (
        100,
        'Bedroom Temperature',
        'temperature',
        'DHT22_Heating',
        json.dumps({"temperature": 19.0, "humidity": 50, "unit": "C"})
    ))
    print(f"  ✅ Sensor ID 100: Bedroom Temperature (DHT22_Heating)")
    
    # ========================================
    # BEDROOM HEATER (ID: 200)
    # ========================================
    print("\n🔥 Adding Bedroom Heater...")
    cursor.execute("""
        INSERT INTO devices (id, name, category, type, current_status, last_update)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (
        200,
        'Bedroom Heater',
        'temperature',
        'SmartHeater_v2',
        json.dumps({"state": "off", "target_temp": 18, "power": 0})
    ))
    print(f"  ✅ Device ID 200: Bedroom Heater (SmartHeater_v2)")
    
    db.conn.commit()
    
    # ========================================
    # ONE AUTOMATION RULE
    # ========================================
    print("\n⚙️  Adding ONE automation rule...")
    
    condition = {"temperature": "<18"}
    action = {"state": "on", "temperature": 22}
    
    trigger_id = db.add_trigger(
        name="Bedroom: Heat When Cold",
        sensor_id=100,
        condition=condition,
        device_id=200,
        action_payload=action
    )
    
    # ENABLE IT BY DEFAULT
    cursor.execute("UPDATE triggers SET enabled = 1 WHERE id = ?", (trigger_id,))
    db.conn.commit()
    
    print(f"  ✅ Rule ID {trigger_id}: Bedroom Heat When Cold")
    print(f"     Condition: temperature < 18°C")
    print(f"     Action: Turn ON heater, set to 22°C")
    print(f"     Status: ✓ ENABLED")
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 60)
    print("✅ INITIALIZATION COMPLETE")
    print("=" * 60)
    
    print(f"\n📊 Configuration:")
    print(f"  📡 Sensor:  ID 100 (Bedroom Temperature)")
    print(f"  🔥 Heater:  ID 200 (Bedroom Heater)")
    print(f"  ⚙️  Rule:    Heat to 22°C when temp < 18°C (ENABLED)")
    
    print(f"\n🚀 Usage:")
    print(f"  1. Node-RED: Use sensor_id=100, device_id=200")
    print(f"  2. Run: python main.py")
    print(f"  3. Test: Click 'Cold (17°C)' in Node-RED")
    print(f"  4. Watch: Heater turns ON automatically!")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        initialize_heating_system()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()