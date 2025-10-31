import json


class RuleBuilder:
    def __init__(self, name):
        self.__rule_name = name
        self.__rule_trigger = dict()
        self.__rule_actions = list()

    def add_trigger(self, trigger_topic):
        self.__rule_trigger = {
            'topic': trigger_topic,
            'conditions': []
        }
        return self

    def add_trigger_condition(self, key, value):
        self.__rule_trigger['conditions'].append({"key": key, "value": value})
        return self

    def add_action(self, topic, qos, payload):
        self.__rule_actions.append({
            'topic': topic,
            'qos': qos,
            'payload': json.loads(payload)
        })
        return self

    def build(self):
        return {
            'name': self.__rule_name,
            'trigger': self.__rule_trigger,
            'actions': self.__rule_actions
        }
