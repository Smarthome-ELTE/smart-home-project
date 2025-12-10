"""
Database initialization script for Smart Home Heating System
Adds sensors, devices, and automation triggers for temperature control
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import Database
import time
import json


def initialize_heating_system():
    """Initialize database with heating system components"""
    
    # Initialize database
    db = Database()
    
    print("=" * 60)
    print("SMART HOME HEATING SYSTEM - DATABASE INITIALIZATION")
    print("=" * 60)
    
    print("\n🗑️  Clearing previous data...")
    
    # Clear all existing data (in reverse order due to foreign keys)
    cursor = db.conn.cursor()
    cursor.execute("DELETE FROM events")
    cursor.execute("DELETE FROM triggers")
    cursor.execute("DELETE FROM devices")
    cursor.execute("DELETE FROM sensors")
    db.conn.commit()
    
    print("✅ Database cleared successfully")
    
    # ========================================
    # SENSORS
    # ========================================
    print("\n📡 Adding sensors...")
    
    # Temperature Sensor 1 (Living Room)
    cursor.execute("""
        INSERT INTO sensors (name, category, type, last_payload, last_update)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (
        'Living Room Temperature',
        'temperature',
        'DHT22_Heating',
        json.dumps({"temperature": 20.5, "humidity": 45, "unit": "C"})
    ))
    sensor_temp_living = cursor.lastrowid
    print(f"  ✓ Sensor ID {sensor_temp_living}: Living Room Temperature (DHT22_Heating)")
    
    # Temperature Sensor 2 (Bedroom)
    cursor.execute("""
        INSERT INTO sensors (name, category, type, last_payload, last_update)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (
        'Bedroom Temperature',
        'temperature',
        'DHT22_Heating',
        json.dumps({"temperature": 19.0, "humidity": 50, "unit": "C"})
    ))
    sensor_temp_bedroom = cursor.lastrowid
    print(f"  ✓ Sensor ID {sensor_temp_bedroom}: Bedroom Temperature (DHT22_Heating)")
    
    # Light Sensor (for completeness)
    cursor.execute("""
        INSERT INTO sensors (name, category, type, last_payload, last_update)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (
        'Living Room Light',
        'light',
        'LDR',
        json.dumps({"brightness": 75, "unit": "lux"})
    ))
    sensor_light = cursor.lastrowid
    print(f"  ✓ Sensor ID {sensor_light}: Living Room Light (LDR)")
    
    # Water Sensor (for completeness)
    cursor.execute("""
        INSERT INTO sensors (name, category, type, last_payload, last_update)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (
        'Garden Moisture',
        'water',
        'Soil Moisture',
        json.dumps({"moisture": 45, "unit": "%"})
    ))
    sensor_water = cursor.lastrowid
    print(f"  ✓ Sensor ID {sensor_water}: Garden Moisture (Soil Moisture)")
    
    db.conn.commit()
    
    # ========================================
    # DEVICES
    # ========================================
    print("\n🔧 Adding devices...")
    
    # Heater 1 (Living Room)
    cursor.execute("""
        INSERT INTO devices (name, category, type, current_status, last_update)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (
        'Living Room Heater',
        'temperature',
        'SmartHeater_v2',
        json.dumps({"state": "off", "target_temp": 20, "power": 0})
    ))
    device_heater_living = cursor.lastrowid
    print(f"  ✓ Device ID {device_heater_living}: Living Room Heater (SmartHeater_v2)")
    
    # Heater 2 (Bedroom)
    cursor.execute("""
        INSERT INTO devices (name, category, type, current_status, last_update)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (
        'Bedroom Heater',
        'temperature',
        'SmartHeater_v2',
        json.dumps({"state": "off", "target_temp": 18, "power": 0})
    ))
    device_heater_bedroom = cursor.lastrowid
    print(f"  ✓ Device ID {device_heater_bedroom}: Bedroom Heater (SmartHeater_v2)")
    
    # Smart Bulb (for completeness)
    cursor.execute("""
        INSERT INTO devices (name, category, type, current_status, last_update)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (
        'Living Room Bulb',
        'light',
        'SmartBulb',
        json.dumps({"state": "off", "brightness": 100})
    ))
    device_bulb = cursor.lastrowid
    print(f"  ✓ Device ID {device_bulb}: Living Room Bulb (SmartBulb)")
    
    db.conn.commit()
    
    # ========================================
    # AUTOMATION TRIGGERS
    # ========================================
    print("\n⚙️  Adding automation triggers...")
    
    # Trigger 1: Turn on living room heater when cold
    condition_cold = {"temperature": "<18"}
    action_heat = {"state": "on", "temperature": 22}
    
    trigger_id_1 = db.add_trigger(
        name="Living Room: Heat When Cold",
        sensor_id=sensor_temp_living,
        condition=condition_cold,
        device_id=device_heater_living,
        action_payload=action_heat
    )
    print(f"  ✓ Trigger ID {trigger_id_1}: Living Room - Heat When Cold (<18°C → Heat to 22°C)")
    
    # Trigger 2: Turn off living room heater when hot
    condition_hot = {"temperature": ">24"}
    action_off = {"state": "off"}
    
    trigger_id_2 = db.add_trigger(
        name="Living Room: Stop Heat When Hot",
        sensor_id=sensor_temp_living,
        condition=condition_hot,
        device_id=device_heater_living,
        action_payload=action_off
    )
    print(f"  ✓ Trigger ID {trigger_id_2}: Living Room - Stop Heat When Hot (>24°C → Turn Off)")
    
    # Trigger 3: Bedroom heating at night
    condition_bedroom_cold = {"temperature": "<17"}
    action_bedroom_heat = {"state": "on", "temperature": 20}
    
    trigger_id_3 = db.add_trigger(
        name="Bedroom: Night Heating",
        sensor_id=sensor_temp_bedroom,
        condition=condition_bedroom_cold,
        device_id=device_heater_bedroom,
        action_payload=action_bedroom_heat
    )
    print(f"  ✓ Trigger ID {trigger_id_3}: Bedroom - Night Heating (<17°C → Heat to 20°C)")
    
    # Trigger 4: Auto lights based on brightness
    condition_dark = {"brightness": "<30"}
    action_lights_on = {"state": "on", "brightness": 80}
    
    trigger_id_4 = db.add_trigger(
        name="Auto Lights When Dark",
        sensor_id=sensor_light,
        condition=condition_dark,
        device_id=device_bulb,
        action_payload=action_lights_on
    )
    print(f"  ✓ Trigger ID {trigger_id_4}: Auto Lights (<30 lux → 80% brightness)")
    
    db.conn.commit()
    
    # ========================================
    # SAMPLE EVENTS (Optional - for testing GUI)
    # ========================================
    print("\n📊 Adding sample events (last 2 hours of activity)...")
    
    # Simulate temperature readings
    temps = [20.5, 19.8, 18.5, 17.2, 16.8, 18.0, 19.5, 21.0, 22.5, 23.0]
    for i, temp in enumerate(temps):
        payload = {
            "sensor_id": sensor_temp_living,
            "temperature": temp,
            "humidity": 45 + i,
            "unit": "C",
            "action": "send"
        }
        db.log_event('sensor', sensor_temp_living, payload)
        time.sleep(0.02)  # Small delay for timestamp variation
    
    print(f"  ✓ Added {len(temps)} temperature sensor events")
    
    # Simulate heater activations (when temp dropped below 18°C)
    heater_events = [
        {"state": "on", "temperature": 22, "power": 2000},
        {"state": "on", "temperature": 22, "power": 2000},
        {"state": "off", "temperature": 22, "power": 0}
    ]
    for event in heater_events:
        payload = {
            "device_id": device_heater_living,
            **event,
            "action": "status"
        }
        db.log_event('device', device_heater_living, payload)
        time.sleep(0.02)
    
    print(f"  ✓ Added {len(heater_events)} heater events")
    
    db.conn.commit()
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 60)
    print("✅ DATABASE INITIALIZATION COMPLETE!")
    print("=" * 60)
    
    print(f"\n📊 Summary:")
    print(f"  • Sensors: 4 (2 temperature, 1 light, 1 water)")
    print(f"  • Devices: 3 (2 heaters, 1 bulb)")
    print(f"  • Automation Rules: 4")
    print(f"  • Sample Events: {len(temps) + len(heater_events)}")
    
    print(f"\n🎯 Heating System Configuration:")
    print(f"  • Living Room: Heat to 22°C when below 18°C")
    print(f"  • Living Room: Stop heating when above 24°C")
    print(f"  • Bedroom: Heat to 20°C when below 17°C")
    
    print(f"\n🚀 Next Steps:")
    print(f"  1. Start Node-RED: node-red")
    print(f"  2. Import flow from: node-red-flows/heating_system_flow.json")
    print(f"  3. Configure MQTT broker in Node-RED")
    print(f"  4. Run application: python main.py")
    print(f"  5. Test by clicking 'Cold (17°C)' button in Node-RED")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        initialize_heating_system()
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()