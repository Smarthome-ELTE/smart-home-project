from controller import Controller
from monitor import Monitor
from wireframe import start_gui
import paho.mqtt.client as paho
import uuid

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


if __name__ == "__main__":
    main()
    start_gui()
