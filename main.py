from controller import Controller
from monitor import Monitor
from wireframe import start_gui
import paho.mqtt.client as paho
import uuid
import os
import time

def main():
    HOST = "910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud"
    PORT = 8883
    USERNAME = "main_connection"
    PASSWORD = "dycrax-3ruzdU"
    unique_id = str(uuid.uuid4())[:8]

    controller = Controller(client_id=f'Controller-{unique_id}', protocol=paho.MQTTv5)
    controller.connect(HOST, PORT, USERNAME, PASSWORD)
    controller.start()
    print("CONTROLLER: Service Started.")

    monitor = Monitor(client_id=f'Monitor_Service-{unique_id}', protocol=paho.MQTTv5)
    monitor.connect(HOST, PORT, USERNAME, PASSWORD)
    monitor.start()
    print("MONITOR: Service Started.")

    no_gui = os.getenv('NO_GUI', 'false').lower() == 'true'

    if no_gui:
        # Docker mode - keep services running without GUI
        print("\n🐳 Running in Docker mode (backend only)")
        print("   - Controller and Monitor are active")
        print("   - To use GUI, run: python main.py (on host)")
        print("   - Node-RED: http://localhost:1880")
        print("   - Press Ctrl+C to stop")
        print("\n" + "=" * 60)

        # Keep container alive
        while True:
            time.sleep(1)
    else:
        # Normal mode - start GUI
        # Import wireframe ONLY when GUI is needed
        from wireframe import start_gui

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


if __name__ == "__main__":
    main()
    start_gui()
