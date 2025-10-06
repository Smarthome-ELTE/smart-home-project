# Smart Home Automation System

A Python-based smart home automation system that monitors sensors and controls devices using MQTT protocol.

## Project Scope

This system provides real-time monitoring and automation for smart home devices:
- **Monitoring**: Collect and display data from sensors (light, temperature, water/humidity, gas)
- **Control**: Automate devices (smart bulbs, heaters, water/gas valves) based on sensor data
- **Visualization**: GUI for monitoring system state and managing automation rules

## System Architecture

- **Sensors (Publishers)** send data via MQTT
- **Controller (Subscriber + Publisher)** applies automation rules
- **Monitor (Subscriber)** visualizes data in Tkinter GUI
- **Database (SQLite)** stores events

## Tech Stack

- **Language**: Python
- **Communication**: MQTT Protocol
- **Database**: SQLite
- **GUI**: Tkinter
- **Event Format**: JSON
- **Simulation**: Node-RED
