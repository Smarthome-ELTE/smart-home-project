from time import sleep

from controller import Controller, RuleBuilder
import paho.mqtt.client as paho


def main():
    controller = Controller(client_id='Controller', protocol=paho.MQTTv5)
    controller.connect(host="910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud", port=8883,
                       username="main_connection", password="dycrax-3ruzdU")

    controller.subscribe(topic="encyclopedia/#", qos=1)

    controller.start()  # needed to set up subscriptions before the messages below are sent

    sleep(1)

    controller.publish(topic="encyclopedia/temperature", payload="{\"temperature\" : 14, \"humidity\" : 25}", qos=1)

    rule = (RuleBuilder("added rule")
            .add_trigger("encyclopedia/temperature").add_trigger_condition("temperature", 25)
            .add_action(topic="encyclopedia/humidity", qos=1, payload="{\"humidity\" : 25}")
            .build())

    controller.add_rule(rule)

    controller.publish(topic="encyclopedia/temperature", payload="{\"temperature\" : 25}", qos=1)

    sleep(1)
    controller.delete_rule("added rule")

    controller.stop()


if __name__ == "__main__":
    main()