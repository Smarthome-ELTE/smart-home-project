# 💨 Gas System - Quick Reference Guide

## File Locations

```
smart-home-project/
├── gas/                          # New Gas System Module
│   ├── __init__.py              # Module initialization
│   ├── gas_sensor.py            # Sensor implementation (99 lines)
│   ├── gas_device.py            # Valve implementation (140 lines)
│   ├── gas_gui.py               # GUI panel (335 lines)
│   ├── init_gas_db.py           # Database init (78 lines)
│   ├── test_gas.py              # Test suite (217 lines)
│   └── README.md                # Full documentation
├── wireframe.py                 # UPDATED: Added gas tab and imports
├── Heating/node-red/
│   └── flows-gas.json           # NEW: Node-RED gas simulation
└── GAS_INTEGRATION_SUMMARY.md   # Integration summary
```

## Total Lines Added
- **Gas Sensor Module**: 99 lines
- **Gas Device Module**: 140 lines
- **Gas GUI Panel**: 335 lines
- **Database Init**: 78 lines
- **Test Suite**: 217 lines
- **Node-RED Flows**: 380+ lines
- **Documentation**: 600+ lines
- **Total**: 1,850+ lines of production code and documentation

## Quick Commands

### Initialize Database
```bash
python -m gas.init_gas_db
```
✅ Creates 3 sensors + 3 valves in database

### Run All Tests
```bash
python -m gas.test_gas
```
✅ Tests sensors, valves, and integration scenarios

### Run Specific Test
```bash
python -m gas.test_gas sensor       # Test sensor publishing
python -m gas.test_gas valve        # Test valve control
python -m gas.test_gas integration  # Test full workflow
```

### Start Application
```bash
python main.py
```
✅ Launches GUI with 2 tabs (Heating + Gas)

## Database Schema

### Sensors Added
| ID | Name | Type | Category |
|----|------|------|----------|
| 1 | Kitchen Gas Sensor | MQ-6 Gas Sensor | gas |
| 2 | Living Room Gas Sensor | MQ-6 Gas Sensor | gas |
| 3 | Utility Room Gas Sensor | MQ-6 Gas Sensor | gas |

### Devices Added
| ID | Name | Type | Category | Default State |
|----|------|------|----------|--------------|
| 2 | Main Gas Pipe Valve | Solenoid Valve | gas | Closed |
| 3 | Kitchen Gas Valve | Manual Ball Valve | gas | Closed |
| 4 | Boiler Gas Valve | Solenoid Valve | gas | Closed |

## MQTT Message Examples

### Gas Sensor Reading (Published)
```json
{
  "sensor_id": 1,
  "sensor_name": "Kitchen Gas Sensor",
  "gas_level": 45.5,
  "unit": "ppm",
  "gas_detected": false,
  "alert_threshold": 100,
  "status": "normal"
}
Topic: gas/get
QoS: 1
```

### Valve Control Command (Received)
```json
{
  "device_id": 2,
  "state": "close",
  "mode": "auto"
}
Topic: gas/send
QoS: 1
```

### Valve Status Response (Published)
```json
{
  "device_id": 2,
  "device_name": "Main Gas Valve",
  "state": "closed",
  "mode": "auto",
  "status": "closed"
}
Topic: gas/send
QoS: 1
```

## GUI Overview

### Tab 1: 🔥 Heating System
- Heating controls (unchanged)
- Real-time temperature display
- Heater status and controls
- Event monitor

### Tab 2: 💨 Gas System (NEW)
**Left Panel**:
- Current Gas Levels
  - Kitchen: X ppm (Status)
  - Living Room: X ppm (Status)
  - Utility Room: X ppm (Status)
- Gas Pipe Valves Control
  - Main Gas Valve: OPEN/CLOSED with buttons
  - Kitchen Gas Valve: OPEN/CLOSED with buttons
  - Boiler Gas Valve: OPEN/CLOSED with buttons
- Gas Automation Rules
  - Rule list with enable/disable
  - Add Rule button

**Right Panel**:
- Recent Events monitor
- All gas-related events logged
- Type, Topic, Payload, Time columns

## Gas Level Classification

| Level | Status | Indicator | Action |
|-------|--------|-----------|--------|
| 0-100 ppm | Normal | 🟢 | No action |
| 100-200 ppm | Alert | 🟡 | Warning notification |
| 200+ ppm | Critical | 🔴 | Auto-close valve + alert |

## Automation Rule Creation

### Example 1: Auto-close on leak
```python
controller.add_trigger(
    name="Emergency Shutdown",
    sensor_id=1,           # Kitchen sensor
    conditions={"gas_level": "> 100"},
    device_id=2,           # Main valve
    action_payload={"state": "close", "mode": "auto"}
)
```

### Example 2: Alert on high level
```python
controller.add_trigger(
    name="High Gas Alert",
    sensor_id=2,           # Living room sensor
    conditions={"gas_level": "> 200"},
    device_id=3,           # Kitchen valve
    action_payload={"state": "close", "mode": "auto"}
)
```

## Node-RED Features

**File**: `Heating/node-red/flows-gas.json`

### Automatic Flows
- 3 gas sensors publish every 5 seconds
- Realistic fluctuations (±0.5-10 ppm per reading)
- Status classification (normal/alert/critical)
- Debug panels show live readings

### Manual Simulation
- 🚨 **Simulate High Gas Level**: Send 250 ppm event
- ✅ **Reset to Normal**: Send 10 ppm event
- Test automation triggers

### Valve Monitoring
- Subscribe to valve commands
- Display valve state changes
- Log all control actions

## File Imports

### In Your Code
```python
# Import gas components
from gas import GasSensor, GasPipeValve
from gas.gas_gui import GasControlPanel
from gas.init_gas_db import init_gas_db

# Use in controller
controller.subscribe("gas/get", 1)
controller.subscribe("gas/send", 1)
```

### In GUI (wireframe.py)
```python
from gas.gas_gui import GasControlPanel

# Create gas control panel
gas_panel = GasControlPanel(parent_frame, controller)
gas_panel.pack(fill="both", expand=True)
```

## Common Tasks

### Task 1: Create Gas Automation Rule
1. Click "💨 Gas System" tab
2. Click "➕ Add Gas Automation Rule"
3. Fill in rule details:
   - Name: "My Gas Rule"
   - Sensor: Select gas sensor
   - Condition: Gas threshold
   - Action: Valve state
4. Click "Save Rule"

### Task 2: Test Sensor
1. Start Node-RED (port 1880)
2. Click "🚨 Simulate High Gas Level" button
3. Check GUI - gas level should increase
4. Check Monitor - event should appear

### Task 3: Control Valve Manually
1. Go to "💨 Gas System" tab
2. Under "Gas Pipe Valves Control"
3. Click "🔓 Open" or "🔒 Close" button
4. Valve state updates immediately

### Task 4: View Event History
1. Open any system tab
2. Right panel shows all events
3. Filter by date if needed
4. Click refresh to update

## Testing Scenarios

### Scenario 1: Normal Operation
- All sensors: 10-50 ppm
- All valves: Closed
- Status: Normal 🟢

### Scenario 2: Gas Alert
- Kitchen sensor: 120 ppm
- Auto-trigger rule: Close main valve
- Status: Alert 🟡

### Scenario 3: Emergency
- Any sensor: 250 ppm
- Auto-trigger rule: Close all valves
- Status: Critical 🔴
- Manual override available

## Troubleshooting

### Sensors Not Publishing
```bash
# Check MQTT connection
# In Node-RED: Check MQTT node configuration
# Broker: 910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud
# Port: 8883
# Username: main_connection
# Password: dycrax-3ruzdU
```

### Valves Not Responding
```bash
# Check controller is running
# Verify device_id matches database
# Check gas/send topic permissions
```

### GUI Showing No Data
```bash
# Run: python -m gas.init_gas_db
# Restart application
# Check database path configuration
```

## Configuration

### Alert Threshold
```python
# In gas_sensor.py - GasSensor class
self.alert_threshold = 100  # Change this value (ppm)
```

### Update Interval
```javascript
// In Node-RED flows-gas.json
"repeat": "5"  // Change to desired seconds
```

### MQTT Broker
```javascript
// In Heating/node-red/flows-gas.json
"broker": "your.broker.address",
"port": "8883"
```

## API Reference

### GasSensor
```python
sensor = GasSensor(sensor_id, name, client_id, protocol, host, port, user, pass)
sensor.connect()
sensor.start()
sensor.publish_reading(45.5)  # ppm
sensor.stop()
```

### GasPipeValve
```python
valve = GasPipeValve(device_id, name, client_id, protocol, host, port, user, pass)
valve.connect()
valve.start()
valve.open_valve()
valve.close_valve()
status = valve.get_status()
valve.stop()
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2025-12-11 | Added full gas system |
| 1.0 | Previous | Heating system only |

---

**Need Help?** See `gas/README.md` for detailed documentation.
