# 💨 Gas System Module

Gas sensor and gas pipe valve management system for the Smart Home Automation Platform.

## Overview

The Gas System module provides:
- **Gas Sensors**: Monitor gas concentration levels (ppm)
- **Gas Pipe Valves**: Automatic/manual control of gas supply
- **Automation Rules**: Trigger valve actions based on sensor readings
- **Safety Features**: Alert thresholds and emergency shutdown capabilities

## Components

### 1. Gas Sensor (`gas_sensor.py`)
- **Class**: `GasSensor`
- **Functionality**:
  - Publishes gas level readings to MQTT topic `gas/get`
  - Detects gas leaks when level exceeds threshold (default: 100 ppm)
  - JSON payload with sensor metadata

**Sensor Payload Format**:
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
```

### 2. Gas Pipe Valve (`gas_device.py`)
- **Class**: `GasPipeValve`
- **Functionality**:
  - Subscribes to MQTT topic `gas/send`
  - Controls gas pipe valve (open/close)
  - Supports manual and automatic modes
  - Publishes status updates

**Valve Control Payload**:
```json
{
  "device_id": 2,
  "state": "open",
  "mode": "auto"
}
```

**Valve Status Response**:
```json
{
  "device_id": 2,
  "device_name": "Main Gas Valve",
  "state": "closed",
  "mode": "auto",
  "status": "closed"
}
```

### 3. Gas GUI Panel (`gas_gui.py`)
- **Class**: `GasControlPanel`
- **Features**:
  - Real-time gas level display for all sensors
  - Manual valve control buttons
  - Gas automation rules management
  - Safety status indicators

### 4. Database Initialization (`init_gas_db.py`)
- Populates database with:
  - 3 Gas Sensors (Kitchen, Living Room, Utility Room)
  - 3 Gas Pipe Valves (Main, Kitchen, Boiler)
- Default sensor type: MQ-6 Gas Sensor
- Default valve type: Solenoid/Manual Ball Valve

### 5. Test Suite (`test_gas.py`)
- Unit tests for sensors and valves
- Integration tests
- Simulation capabilities

## Directory Structure

```
gas/
├── __init__.py              # Module initialization
├── gas_sensor.py            # Gas sensor implementation
├── gas_device.py            # Gas valve implementation
├── gas_gui.py               # GUI panel
├── init_gas_db.py           # Database initialization
└── test_gas.py              # Test suite
```

## MQTT Topics

| Topic | Direction | Purpose |
|-------|-----------|---------|
| `gas/get` | Publish | Gas sensor readings |
| `gas/send` | Subscribe | Gas valve commands |

## Sensor Specifications

### MQ-6 Gas Sensor
- **Detection Range**: 200-5000 ppm (typical)
- **Alert Threshold**: 100 ppm (configurable)
- **Update Interval**: 5 seconds (Node-RED simulation)
- **Categories**: Kitchen, Living Room, Utility Room

## Valve Specifications

### Main Gas Valve
- **Type**: Solenoid Valve
- **States**: Open (unsafe) / Closed (safe)
- **Mode**: Automatic (Controller-managed)
- **Default**: Closed

### Kitchen Gas Valve
- **Type**: Manual Ball Valve
- **States**: Open / Closed
- **Mode**: Manual (User-controlled)
- **Default**: Closed

### Boiler Gas Valve
- **Type**: Solenoid Valve
- **States**: Open / Closed
- **Mode**: Automatic (Heating system integration)
- **Default**: Closed

## Database Schema

### Sensors Table
```sql
CREATE TABLE sensors (
  id INTEGER PRIMARY KEY,
  name TEXT,              -- "Kitchen Gas Sensor"
  category TEXT,          -- "gas"
  type TEXT,              -- "MQ-6 Gas Sensor"
  last_payload TEXT,      -- JSON
  last_update TIMESTAMP
);
```

### Devices Table
```sql
CREATE TABLE devices (
  id INTEGER PRIMARY KEY,
  name TEXT,              -- "Main Gas Valve"
  category TEXT,          -- "gas"
  type TEXT,              -- "Solenoid Valve"
  current_status TEXT,    -- JSON
  last_update TIMESTAMP
);
```

### Triggers Table
```sql
CREATE TABLE triggers (
  id INTEGER PRIMARY KEY,
  name TEXT,              -- "Close valve on gas leak"
  sensor_id INTEGER,      -- Reference to gas sensor
  condition TEXT,         -- JSON condition logic
  device_id INTEGER,      -- Reference to gas valve
  action_payload TEXT,    -- JSON action
  enabled INTEGER,        -- 0 or 1
  last_triggered TIMESTAMP
);
```

## Usage

### 1. Initialize Database
```bash
python -m gas.init_gas_db
```

### 2. Run Test Suite
```bash
# All tests
python -m gas.test_gas

# Specific test
python -m gas.test_gas sensor
python -m gas.test_gas valve
python -m gas.test_gas integration
```

### 3. Use in GUI
The `GasControlPanel` is integrated into `wireframe.py`:
```python
from gas.gas_gui import GasControlPanel

gas_panel = GasControlPanel(parent_frame, controller)
```

### 4. Manual Valve Control
```python
from gas import GasPipeValve
import paho.mqtt.client as paho

valve = GasPipeValve(
    device_id=2,
    device_name="Main Gas Valve",
    client_id="app_valve",
    protocol=paho.MQTTv5,
    host="broker.example.com",
    port=8883,
    username="user",
    password="pass"
)

valve.connect()
valve.start()

valve.open_valve()   # Open the valve
valve.close_valve()  # Close the valve

valve.stop()
```

## Automation Rules Example

### Rule: Close Main Valve on Gas Leak
```json
{
  "name": "Auto-close on gas leak",
  "sensor_id": 1,
  "condition": {
    "key": "gas_level",
    "comparator": "> 100"
  },
  "device_id": 2,
  "action_payload": {
    "state": "close",
    "mode": "auto"
  }
}
```

## Node-RED Simulation

**File**: `Heating/node-red/flows-gas.json`

Simulates:
- 3 gas sensors with realistic fluctuations
- Valve control responses
- Emergency scenario buttons

**Features**:
- ✅ Automatic sensor readings (5-second interval)
- ✅ High gas level simulation button
- ✅ Reset to normal button
- ✅ Real-time debug output
- ✅ MQTT integration with HiveMQ Cloud

## Safety Features

1. **Alert Thresholds**:
   - Normal: < 100 ppm
   - Alert: 100-200 ppm
   - Critical: > 200 ppm

2. **Emergency Actions**:
   - Automatic valve closure on high readings
   - Manual override capability
   - Status logging for analysis

3. **Monitoring**:
   - Real-time sensor displays
   - Alert notifications
   - Event history tracking

## Integration with Main System

The Gas System integrates with:
- **Controller**: Automation rule execution
- **Monitor**: Event logging and visualization
- **Database**: State persistence
- **GUI (wireframe.py)**: User interface (Tab 2)
- **Node-RED**: Sensor simulation

## Future Enhancements

- [ ] Gas consumption tracking
- [ ] Leak detection algorithms
- [ ] Mobile app alerts
- [ ] Historical trend analysis
- [ ] Multi-sensor averaging
- [ ] Integration with emergency services
- [ ] Voice alerts

## Troubleshooting

### Sensors not publishing
1. Check MQTT broker connectivity
2. Verify credentials in Node-RED settings
3. Ensure `gas/get` topic is accessible
4. Check controller subscriptions

### Valves not responding
1. Verify MQTT message format
2. Check device_id matches database
3. Ensure `gas/send` topic permissions
4. Review controller logs

### GUI not displaying data
1. Verify database has gas sensors/devices
2. Run `init_gas_db.py` to initialize
3. Check database path configuration
4. Restart the application

## License

Part of the Smart Home Automation System project.
