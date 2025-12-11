#!/usr/bin/env python3
"""
Test Controller Rule Evaluation
This simulates what should happen when temperature drops below 18°C
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import Database
import json

print("=" * 70)
print("TESTING CONTROLLER RULE EVALUATION")
print("=" * 70)

db = Database()
cursor = db.conn.cursor()

# Get the rule
cursor.execute("""
    SELECT id, name, sensor_id, device_id, condition, action_payload, enabled
    FROM triggers
    WHERE sensor_id = 100 AND device_id = 200 AND enabled = 1
""")

rule = cursor.fetchone()

if not rule:
    print("\n❌ ERROR: No enabled rule found for sensor=100 → device=200")
    print("Run: python Heating/init_heating_db.py")
    sys.exit(1)

rule_id, name, sensor_id, device_id, condition_str, action_str, enabled = rule

print(f"\n✅ Found enabled rule: {name}")
print(f"   Rule ID: {rule_id}")
print(f"   Sensor: {sensor_id} → Device: {device_id}")

# Parse condition
condition = json.loads(condition_str)
action = json.loads(action_str)

print(f"\n📋 Rule Details:")
print(f"   Condition: {condition}")
print(f"   Action: {action}")

# Test with temperature = 17°C
test_temp = 17

print(f"\n🧪 TEST: Simulating temperature = {test_temp}°C")
print(f"   Rule condition: temperature {condition['temperature']}")

# Parse the condition
temp_condition = condition['temperature']
operator = temp_condition[0]  # '<', '>', '='
value = float(temp_condition[1:])

print(f"   Parsed: temperature {operator} {value}")

# Evaluate
if operator == '<':
    result = test_temp < value
elif operator == '>':
    result = test_temp > value
elif operator == '=':
    result = test_temp == value
else:
    result = False

print(f"\n🎯 Evaluation: {test_temp} {operator} {value} = {result}")

if result:
    print(f"   ✅ RULE SHOULD TRIGGER!")
    print(f"   Expected action: Send command to device {device_id}")
    print(f"   Command: {action}")
    print(f"\n🔥 Controller should publish to 'temperature/send':")
    command = {
        "device_id": device_id,
        "state": action['state'],
        "temperature": action['temperature']
    }
    print(f"   {json.dumps(command, indent=2)}")
else:
    print(f"   ❌ Rule would NOT trigger")

print("\n" + "=" * 70)
print("WHY ISN'T IT WORKING IN THE APP?")
print("=" * 70)

print("\nPossible reasons:")
print("1. ❌ Controller not subscribed to 'temperature/get'")
print("2. ❌ Controller not calling evaluate_rules() on message")
print("3. ❌ Controller not publishing to 'temperature/send'")

print("\n📝 Check your Controller code:")
print("   - Does it subscribe to 'temperature/get'?")
print("   - Does on_message call evaluate_rules()?")
print("   - Does evaluate_rules() actually evaluate conditions?")
print("   - Does it publish commands on match?")

print("\n" + "=" * 70)

db.close()