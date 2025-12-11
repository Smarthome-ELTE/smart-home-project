# 🏗️ Gas System Architecture & Data Flow

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMART HOME SYSTEM v2.0                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              MQTT BROKER (HiveMQ Cloud)                  │   │
│  │     910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud │   │
│  └──────────────────────────────────────────────────────────┘   │
│           ▲                                       ▲               │
│           │                                       │               │
│  Topics:  │ gas/get (publish)                    │ gas/send      │
│           │ (sensor readings)                    │ (valve cmds)   │
│           │                                       │               │
│  ┌────────┴──────────────────────┬───────────────┴────────────┐  │
│  │                                │                             │  │
│  │        NODE-RED SIMULATOR      │      PYTHON CONTROLLER     │  │
│  │  ┌──────────────────────────┐  │  ┌─────────────────────┐   │  │
│  │  │  Gas Sensor Functions    │  │  │  Controller.py      │   │  │
│  │  │  - Kitchen (MQ-6)        │  │  │  - Load triggers    │   │  │
│  │  │  - Living Room (MQ-6)    │  │  │  - Process events   │   │  │
│  │  │  - Utility Room (MQ-6)   │  │  │  - Execute rules    │   │  │
│  │  │                          │  │  └─────────────────────┘   │  │
│  │  │  Valve Control Handler   │  │                             │  │
│  │  │  - Monitor valve cmds    │  │  ┌─────────────────────┐   │  │
│  │  │  - Simulate responses    │  │  │  Monitor.py         │   │  │
│  │  │                          │  │  │  - Log events       │   │  │
│  │  │  Manual Test Buttons     │  │  │  - Store in DB      │   │  │
│  │  │  - Simulate high level   │  │  └─────────────────────┘   │  │
│  │  │  - Reset to normal       │  │                             │  │
│  │  └──────────────────────────┘  │                             │  │
│  └────────────────────────────────┴─────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          SQLite DATABASE (smart_home_monitor.db)         │   │
│  │                                                           │   │
│  │  SENSORS TABLE (Gas category)                            │   │
│  │  ├─ ID:1 Kitchen Gas Sensor (MQ-6)                      │   │
│  │  ├─ ID:2 Living Room Gas Sensor (MQ-6)                  │   │
│  │  └─ ID:3 Utility Room Gas Sensor (MQ-6)                 │   │
│  │                                                           │   │
│  │  DEVICES TABLE (Gas category)                            │   │
│  │  ├─ ID:2 Main Gas Pipe Valve (Solenoid)                 │   │
│  │  ├─ ID:3 Kitchen Gas Valve (Manual Ball)                │   │
│  │  └─ ID:4 Boiler Gas Valve (Solenoid)                    │   │
│  │                                                           │   │
│  │  TRIGGERS TABLE (Gas automation rules)                   │   │
│  │  └─ Automation rules linking sensors to devices          │   │
│  │                                                           │   │
│  │  EVENTS TABLE (All gas events)                           │   │
│  │  └─ Historical log of all gas system activity            │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          TKINTER GUI (wireframe.py)                      │   │
│  │                                                           │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  TABS: [🔥 Heating] [💨 Gas]                       │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │                                                           │   │
│  │  LEFT PANEL (Gas Controls)   │  RIGHT PANEL (Events)    │   │
│  │  ┌─────────────────────────┐ │ ┌──────────────────────┐  │   │
│  │  │ Current Gas Levels      │ │ │ Recent Events        │  │   │
│  │  │ • Kitchen: XX ppm       │ │ │ • Event 1            │  │   │
│  │  │ • Living Room: XX ppm   │ │ │ • Event 2            │  │   │
│  │  │ • Utility: XX ppm       │ │ │ • Event 3            │  │   │
│  │  │                         │ │ │                      │  │   │
│  │  │ Valve Controls          │ │ │ [Refresh] [Clear]    │  │   │
│  │  │ • Main: [O] [C]         │ │ └──────────────────────┘  │   │
│  │  │ • Kitchen: [O] [C]      │ │                             │   │
│  │  │ • Boiler: [O] [C]       │ │                             │   │
│  │  │                         │ │                             │   │
│  │  │ Automation Rules        │ │                             │   │
│  │  │ • Rule List             │ │                             │   │
│  │  │ [+ Add Rule]            │ │                             │   │
│  │  └─────────────────────────┘ │                             │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

### Sensor Publishing Flow
```
Node-RED Sensor         MQTT Broker              Python Controller
    │                        │                           │
    │─ Timer (5s) ────────►  │                           │
    │                        │                           │
    ├─ Generate Level        │                           │
    ├─ Create JSON           │                           │
    │                        │                           │
    └─ Publish gas/get ─────►│ gas/get topic             │
                             │                           │
                             ├─ Store payload ──────────►│
                             │                           │
                             │                    Check Triggers
                             │                           │
                             │                    Execute Actions
                             │◄─────────────────────────┤
                             │                           │
                        Monitor.py                       │
                             │                           │
                             ├─ Log Event               │
                             ├─ Store in DB             │
                             └─ Update GUI              │
```

### Valve Control Flow
```
GUI / Automation Rule      MQTT Broker            Node-RED / Hardware
         │                      │                        │
         │                      │                        │
    Create Command              │                        │
    (device_id, state)          │                        │
         │                      │                        │
         └─ Publish gas/send ──►│ gas/send topic         │
                                │                        │
                                ├─ Route to subscriber ─►│
                                │                        │
                                │                    Process Command
                                │                        │
                                │◄─── Status Update ─────┤
                                │                        │
                        Monitor.py                       │
                                │                        │
                                ├─ Log Event             │
                                ├─ Store in DB           │
                                └─ Update GUI            │
```

## Gas Level State Machine

```
                    ┌─────────────┐
                    │   NORMAL    │
                    │  < 100 ppm  │
                    │     🟢      │
                    └──────┬──────┘
                           │ gas_level > 100
                           ▼
                    ┌─────────────┐
                    │    ALERT    │
                    │ 100-200 ppm │
                    │     🟡      │
                    └──────┬──────┘
                           │ gas_level > 200
                           ▼
                    ┌─────────────┐
                    │  CRITICAL   │
                    │  > 200 ppm  │
                    │     🔴      │
                    │   CLOSE     │
                    │   VALVE     │
                    └──────┬──────┘
                           │ sensor reset
                           ▼
                    ┌─────────────┐
                    │   NORMAL    │
                    │  < 100 ppm  │
                    │     🟢      │
                    └─────────────┘
```

## Valve State Machine

```
                   Initial State: CLOSED
                           │
                           ▼
                    ┌─────────────┐
                    │   CLOSED    │
                    │     🟢      │
                    │   (SAFE)    │
                    └──────┬──────┘
                           │ Command: open
                           ▼
                    ┌─────────────┐
                    │    OPEN     │
                    │     🔴      │
                    │   (UNSAFE)  │
                    └──────┬──────┘
                           │ Command: close
                           ▼
                    ┌─────────────┐
                    │   CLOSED    │
                    │     🟢      │
                    │   (SAFE)    │
                    └─────────────┘
```

## Message Format Examples

### Incoming: Sensor Reading
```
Topic: gas/get
QoS: 1

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

### Outgoing: Valve Command
```
Topic: gas/send
QoS: 1

{
  "device_id": 2,
  "state": "close",
  "mode": "auto"
}
```

### Response: Valve Status
```
Topic: gas/send
QoS: 1

{
  "device_id": 2,
  "device_name": "Main Gas Valve",
  "state": "closed",
  "mode": "auto",
  "status": "closed"
}
```

## Module Dependencies

```
main.py
  ├─ controller/controller.py
  │  ├─ db/database.py
  │  └─ paho.mqtt
  │
  ├─ monitor/monitor.py
  │  ├─ db/database.py
  │  └─ paho.mqtt
  │
  └─ wireframe.py (GUI)
     ├─ heating/heating_gui.py
     ├─ gas/gas_gui.py          [NEW]
     ├─ monitor/monitor_gui.py
     └─ db/database.py
```

## File Organization

```
smart-home-project/
│
├── Core Modules
│  ├── controller/
│  │  ├── __init__.py
│  │  ├── controller.py
│  │  └── rules.py
│  │
│  ├── monitor/
│  │  ├── __init__.py
│  │  ├── monitor.py
│  │  └── monitor_gui.py
│  │
│  └── db/
│     ├── __init__.py
│     ├── database.py
│     └── add_dummy_data.py
│
├── System Modules
│  ├── Heating/
│  │  ├── heating_gui.py
│  │  ├── init_heating_db.py
│  │  ├── test_heating.py
│  │  └── node-red/
│  │     ├── settings.js
│  │     └── flows.json (existing)
│  │
│  └── gas/                      [NEW]
│     ├── __init__.py
│     ├── gas_sensor.py
│     ├── gas_device.py
│     ├── gas_gui.py
│     ├── init_gas_db.py
│     ├── test_gas.py
│     └── README.md
│
├── GUI
│  └── wireframe.py              [UPDATED]
│
├── Entry Point
│  └── main.py
│
├── Node-RED
│  └── Heating/node-red/
│     ├── flows-gas.json         [NEW]
│     └── settings.js
│
├── Documentation
│  ├── README.md
│  ├── GAS_INTEGRATION_SUMMARY.md    [NEW]
│  ├── GAS_QUICK_REFERENCE.md        [NEW]
│  ├── GAS_IMPLEMENTATION_CHECKLIST.md [NEW]
│  └── GAS_SYSTEM_ARCHITECTURE.md    [NEW - this file]
│
├── Config
│  ├── docker-compose.yml
│  ├── Dockerfile
│  └── requirements.txt
│
└── Files
   └── wireframe.py
```

## Execution Timeline

```
Application Startup
│
├─ 0s: Load configuration
│
├─ 1s: Connect to MQTT Broker
│
├─ 2s: Initialize Database
│       ├─ Load sensors (3 gas sensors)
│       ├─ Load devices (3 valves)
│       └─ Load triggers (automation rules)
│
├─ 3s: Initialize Controller
│       ├─ Subscribe to gas/get
│       ├─ Subscribe to gas/send
│       └─ Start MQTT loop
│
├─ 4s: Initialize Monitor
│       ├─ Subscribe to +/get
│       ├─ Subscribe to +/send
│       └─ Start logging
│
├─ 5s: Launch GUI
│       ├─ Create tabs
│       ├─ Load heating panel
│       ├─ Load gas panel (new)
│       ├─ Initialize event displays
│       └─ Start auto-refresh
│
└─ 6s: System Ready!
    ├─ Waiting for sensor events
    ├─ Node-RED publishing every 5s
    └─ Ready for automation rules
```

## Event Sequence Diagram

### Normal Operation
```
Time  Node-RED       MQTT Broker    Controller     Monitor        Database
│
├─ 0s: Generate reading
│      (45 ppm)
│      │
│      └──► Publish ──► gas/get ──► Subscribe ──► Log ──► Store in events
│                                   │                        │
│                                   ├─ Check triggers        │
│                                   │  (no match)            │
│                                   │                        │
│      (5 second intervals)
│
├─ 5s: Generate reading
│      (48 ppm)
│      │
│      └──► Publish ──► gas/get ──► Subscribe ──► Log ──► Store in events
│
├─ 10s: Generate reading
│      (42 ppm)
│      │
│      └──► Publish ──► gas/get ──► Subscribe ──► Log ──► Store in events
│
└─ ... (continues)
```

### Emergency Scenario
```
Time  Node-RED       MQTT Broker    Controller     Monitor        Database
│
├─ 0s: Manual trigger
│      (Simulate high)
│      │
│      └──► Publish ──► gas/get ──► Subscribe
│           (250 ppm)             │
│                                 ├─ Check triggers
│                                 │  ✓ Rule matches!
│                                 │  (gas > 100)
│                                 │
│                                 ├─ Execute action
│                                 │  (close valve)
│                                 │
│                                 └──► Publish ──► gas/send
│                                      (close cmd)
│
│      Handler receives
│      valve command
│      │
│      └──► Process ──────────────────► Log ──► Store in events
│           (state change)               │
│           │                            │
│           └─ Simulate valve close      │
│
└─ System in safe state (valve closed)
```

---

**This architecture supports:**
- ✅ Real-time sensor monitoring
- ✅ Instant valve control
- ✅ Automation rule execution
- ✅ Event persistence
- ✅ GUI visualization
- ✅ Emergency response
- ✅ System scalability
