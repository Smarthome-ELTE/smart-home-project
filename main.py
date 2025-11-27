"""
Smart Home Automation System - Main Entry Point
Initializes Controller, Monitor, and GUI with heating system support
"""

from controller import Controller
from monitor import Monitor
from wireframe import start_gui
import paho.mqtt.client as paho
import sys


def main():
    """Initialize and start all system components"""
    
    print("=" * 60)
    print("SMART HOME HEATING SYSTEM - STARTING")
    print("=" * 60)
    
    # MQTT Broker Configuration
    HOST = "910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud"
    PORT = 8883
    USERNAME = "main_connection"
    PASSWORD = "dycrax-3ruzdU"
    
    try:
        # Initialize Controller
        print("\n🎮 Initializing Controller...")
        controller = Controller(client_id='Controller', protocol=paho.MQTTv5)
        controller.connect(HOST, PORT, USERNAME, PASSWORD)
        controller.start()
        print("✅ CONTROLLER: Service Started")
        print("   - Subscribed to: temperature/get, light/get, water/get, gas/get")
        print("   - Loaded automation rules from database")
        
        # Initialize Monitor
        print("\n📊 Initializing Monitor...")
        monitor = Monitor(client_id='Monitor_Service', protocol=paho.MQTTv5)
        monitor.connect(HOST, PORT, USERNAME, PASSWORD)
        monitor.start()
        print("✅ MONITOR: Service Started")
        print("   - Subscribed to: +/get, +/send")
        print("   - Logging all events to database")
        
        # Start GUI
        print("\n🖥️  Starting GUI...")
        print("=" * 60)
        print("\n💡 TIPS:")
        print("   1. Use Node-RED to simulate temperature sensors")
        print("   2. Click 'Cold (17°C)' in Node-RED to trigger heating")
        print("   3. Watch automation rules execute in real-time")
        print("   4. Monitor all events in the GUI")
        print("\n" + "=" * 60)
        
        # Launch GUI (blocking call)
        start_gui(controller=controller)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Shutdown requested by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\n🛑 Stopping services...")
        try:
            controller.stop()
            print("   ✓ Controller stopped")
        except:
            pass
        try:
            monitor.stop()
            print("   ✓ Monitor stopped")
        except:
            pass
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()