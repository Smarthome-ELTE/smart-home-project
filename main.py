from controller import Controller
from monitor import Monitor
from wireframe import start_gui
import paho.mqtt.client as paho


def main():
    HOST = "910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud"
    PORT = 8883
    USERNAME = "main_connection"
    PASSWORD = "dycrax-3ruzdU"

    controller = Controller(client_id='Controller', protocol=paho.MQTTv5)
    controller.connect(HOST, PORT, USERNAME, PASSWORD)
    controller.start()
    print("CONTROLLER: Service Started.")

    monitor = Monitor(client_id='Monitor_Service', protocol=paho.MQTTv5)
    monitor.connect(HOST, PORT, USERNAME, PASSWORD)
    monitor.start()
    print("MONITOR: Service Started.")


if __name__ == "__main__":
    main()
    start_gui()
