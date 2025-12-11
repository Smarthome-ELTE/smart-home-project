"""
COMPLETE Database Init - Clean Slate for Demo
Two simple rules: Heat when cold, Turn off when hot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import Database
import json


def initialize_heating_system():
    """Initialize database with two complementary rules"""
    
    db = Database()
    
    print("=" * 70)
    print("🔥 HEATING SYSTEM - COMPLETE INITIALIZATION")
    print("=" * 70)
    
    # ========================================
    # STEP 1: CLEAN EVERYTHING
    # ========================================
    print("\n🗑️  Clearing all existing data...")
    cursor = db.conn.cursor()
    
    # Clear in correct order (foreign key constraints)
    cursor.execute("DELETE FROM events")
    cursor.execute("DELETE FROM triggers")
    cursor.execute("DELETE FROM devices")
    cursor.execute("DELETE FROM sensors")
    
    # Reset autoincrement
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='sensors'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='devices'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='triggers'")
    
    db.conn.commit()
    print("✅ Database cleared and reset")
    
    # ========================================
    # STEP 2: ADD SENSOR
    # ========================================
    print("\n📡 Adding Temperature Sensor...")
    cursor.execute("""
        INSERT INTO sensors (id, name, category, type, last_payload, last_update)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (
        100,
        'Bedroom Temperature',
        'temperature',
        'DHT22_Heating',
        json.dumps({"temperature": 20.0, "humidity": 50, "unit": "C"})
    ))
    print(f"  ✅ Sensor ID 100: Bedroom Temperature (DHT22_Heating)")
    
    # ========================================
    # STEP 3: ADD DEVICE
    # ========================================
    print("\n🔥 Adding Heater Device...")
    cursor.execute("""
        INSERT INTO devices (id, name, category, type, current_status, last_update)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (
        200,
        'Bedroom Heater',
        'temperature',
        'SmartHeater_v2',
        json.dumps({"state": "off", "target_temp": 20, "current_temp": 20, "power": 0})
    ))
    print(f"  ✅ Device ID 200: Bedroom Heater (SmartHeater_v2)")
    
    db.conn.commit()
    
    # ========================================
    # STEP 4: ADD TWO COMPLEMENTARY RULES
    # ========================================
    print("\n⚙️  Adding Automation Rules...")
    
    # Rule 1: Turn ON when cold
    print("\n  📋 Rule 1: Heat When Cold")
    condition_cold = {"temperature": "<18"}
    action_heat = {"state": "on", "temperature": 22}
    
    trigger_id_1 = db.add_trigger(
        name="Heat When Cold",
        sensor_id=100,
        condition=condition_cold,
        device_id=200,
        action_payload=action_heat
    )
    
    cursor.execute("UPDATE triggers SET enabled = 1 WHERE id = ?", (trigger_id_1,))
    print(f"     ✅ Rule ID {trigger_id_1}: Heat When Cold")
    print(f"        IF temperature < 18°C")
    print(f"        THEN turn ON heater, set to 22°C")
    print(f"        Status: ✓ ENABLED")
    
    # Rule 2: Turn OFF when hot
    print("\n  📋 Rule 2: Turn Off When Hot")
    condition_hot = {"temperature": ">23"}
    action_cool = {"state": "off", "temperature": 20}
    
    trigger_id_2 = db.add_trigger(
        name="Turn Off When Hot",
        sensor_id=100,
        condition=condition_hot,
        device_id=200,
        action_payload=action_cool
    )
    
    cursor.execute("UPDATE triggers SET enabled = 1 WHERE id = ?", (trigger_id_2,))
    print(f"     ✅ Rule ID {trigger_id_2}: Turn Off When Hot")
    print(f"        IF temperature > 23°C")
    print(f"        THEN turn OFF heater")
    print(f"        Status: ✓ ENABLED")
    
    db.conn.commit()
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 70)
    print("✅ INITIALIZATION COMPLETE")
    print("=" * 70)
    
    print(f"\n📊 System Configuration:")
    print(f"  📡 Sensor:  ID 100 (Bedroom Temperature)")
    print(f"  🔥 Device:  ID 200 (Bedroom Heater)")
    print(f"  ⚙️  Rules:   2 enabled rules")
    
    print(f"\n🎯 Automation Logic:")
    print(f"  ❄️  Temp < 18°C  → Turn ON heater (target 22°C)")
    print(f"  🌡️  18-23°C      → No action (maintain current state)")
    print(f"  🔥 Temp > 23°C  → Turn OFF heater")
    
    print(f"\n🧪 Testing Instructions:")
    print(f"  1. Start system: python main.py")
    print(f"  2. Open GUI: python wireframe.py")
    print(f"  3. In Node-RED:")
    print(f"     - Click 'Cold (17°C)' → Heater should turn ON")
    print(f"     - Click 'Hot (25°C)' → Heater should turn OFF")
    print(f"     - Click 'Normal (21°C)' → No change")
    
    print("\n" + "=" * 70)
    
    return True


if __name__ == "__main__":
    try:
        success = initialize_heating_system()
        if success:
            print("\n✅ Ready for demo!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()