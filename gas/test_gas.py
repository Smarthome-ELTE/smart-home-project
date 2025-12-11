"""
Gas System Testing Module
Tests gas sensors and gas pipe valves functionality
"""

import sys
import time
import json
import paho.mqtt.client as paho
from gas import GasSensor, GasPipeValve


def test_gas_sensor():
    """Test gas sensor publishing"""
    print("\n" + "="*60)
    print("🧪 TESTING GAS SENSOR")
    print("="*60)
    
    # MQTT Configuration
    HOST = "910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud"
    PORT = 8883
    USERNAME = "main_connection"
    PASSWORD = "dycrax-3ruzdU"
    
    try:
        # Create gas sensor instance
        gas_sensor = GasSensor(
            sensor_id=1,
            sensor_name="Test Gas Sensor",
            client_id="GasSensor_Test",
            protocol=paho.MQTTv5,
            host=HOST,
            port=PORT,
            username=USERNAME,
            password=PASSWORD
        )
        
        # Connect and start
        gas_sensor.connect()
        gas_sensor.start()
        
        print("\n📤 Publishing test readings...")
        
        # Test normal readings
        test_readings = [
            (30, "Normal reading"),
            (50, "Moderate reading"),
            (120, "High reading (above 100ppm threshold)"),
            (250, "Critical reading (above 200ppm)"),
            (0, "Reset to normal")
        ]
        
        for gas_level, description in test_readings:
            print(f"\n   Publishing: {gas_level}ppm - {description}")
            gas_sensor.publish_reading(gas_level)
            time.sleep(2)
        
        gas_sensor.stop()
        print("\n✅ Gas sensor test completed successfully!")
    
    except Exception as e:
        print(f"❌ Gas sensor test failed: {e}")
        import traceback
        traceback.print_exc()


def test_gas_valve():
    """Test gas pipe valve control"""
    print("\n" + "="*60)
    print("🧪 TESTING GAS PIPE VALVE")
    print("="*60)
    
    # MQTT Configuration
    HOST = "910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud"
    PORT = 8883
    USERNAME = "main_connection"
    PASSWORD = "dycrax-3ruzdU"
    
    try:
        # Create gas valve instance
        gas_valve = GasPipeValve(
            device_id=2,
            device_name="Test Gas Valve",
            client_id="GasValve_Test",
            protocol=paho.MQTTv5,
            host=HOST,
            port=PORT,
            username=USERNAME,
            password=PASSWORD
        )
        
        # Connect and start
        gas_valve.connect()
        gas_valve.start()
        
        print("\n🎮 Testing valve controls...")
        
        # Test valve operations
        operations = [
            ("open", "Opening valve"),
            ("close", "Closing valve"),
            ("open", "Opening valve again"),
            ("close", "Final close")
        ]
        
        for command, description in operations:
            print(f"\n   {description}...")
            gas_valve.set_valve(command)
            status = gas_valve.get_status()
            print(f"   Current state: {status['state']}")
            time.sleep(2)
        
        gas_valve.stop()
        print("\n✅ Gas valve test completed successfully!")
    
    except Exception as e:
        print(f"❌ Gas valve test failed: {e}")
        import traceback
        traceback.print_exc()


def test_gas_integration():
    """Test integration between sensor and valve"""
    print("\n" + "="*60)
    print("🧪 TESTING GAS SYSTEM INTEGRATION")
    print("="*60)
    
    # MQTT Configuration
    HOST = "910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud"
    PORT = 8883
    USERNAME = "main_connection"
    PASSWORD = "dycrax-3ruzdU"
    
    try:
        print("\n🔗 Starting integrated test...")
        print("   Simulating: High gas detected -> Automatic valve closure")
        
        # Create sensor
        gas_sensor = GasSensor(
            sensor_id=1,
            sensor_name="Kitchen Gas",
            client_id="GasSensor_Integration",
            protocol=paho.MQTTv5,
            host=HOST,
            port=PORT,
            username=USERNAME,
            password=PASSWORD
        )
        
        # Create valve
        gas_valve = GasPipeValve(
            device_id=2,
            device_name="Main Valve",
            client_id="GasValve_Integration",
            protocol=paho.MQTTv5,
            host=HOST,
            port=PORT,
            username=USERNAME,
            password=PASSWORD
        )
        
        # Connect both
        gas_sensor.connect()
        gas_valve.connect()
        gas_sensor.start()
        gas_valve.start()
        
        print("\n📊 Scenario: Gas leak detected")
        print("   1. Sensor detects high gas level (300ppm)")
        gas_sensor.publish_reading(300)
        time.sleep(2)
        
        print("   2. Automation rule triggers valve closure")
        gas_valve.set_valve("close")
        time.sleep(2)
        
        print("   3. System status:")
        print(f"      - Sensor reading: {gas_sensor.current_gas_level}ppm")
        print(f"      - Valve status: {gas_valve.get_status()['state']}")
        print(f"      - Alert active: {gas_sensor.gas_detected}")
        
        gas_sensor.stop()
        gas_valve.stop()
        print("\n✅ Integration test completed successfully!")
    
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🔧 GAS SYSTEM TEST SUITE")
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == "sensor":
            test_gas_sensor()
        elif test_type == "valve":
            test_gas_valve()
        elif test_type == "integration":
            test_gas_integration()
        else:
            print("❌ Unknown test type. Use 'sensor', 'valve', or 'integration'")
    else:
        print("\nRunning all tests...\n")
        test_gas_sensor()
        test_gas_valve()
        test_gas_integration()
        print("\n" + "="*60)
        print("✨ ALL TESTS COMPLETED!")
        print("="*60)
