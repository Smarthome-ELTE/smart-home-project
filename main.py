from controller import Controller
import paho.mqtt.client as paho


def main():
    controller = Controller(client_id='Controller', protocol=paho.MQTTv5)
    controller.connect(host="910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud", port=8883,
                       username="main_connection", password="dycrax-3ruzdU")

    controller.subscribe(topic="encyclopedia/#", qos=1)

    controller.start()

    controller.publish(topic="encyclopedia/temperature", payload="hot", qos=1)
    controller.publish(topic="encyclopedia/temperature", payload="cold", qos=1)
    controller.publish(topic="encyclopedia/temperature", payload="mild", qos=1)

    controller.stop()


if __name__ == "__main__":
    main()
