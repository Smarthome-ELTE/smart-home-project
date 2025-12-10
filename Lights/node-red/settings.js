// settings.js

// 1. Define MQTT credentials and Host/Port
// IMPORTANT: Replace the placeholder values with the ACTUAL credentials 
// used by your project's MQTT broker if they are different from the example below.
process.env.MQTT_HOST = '910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud';
process.env.MQTT_PORT = 8883;
process.env.MQTT_USERNAME = 'main_connection';
process.env.MQTT_PASSWORD = 'dycrax-3ruzdU';

module.exports = {
  // 2. Flow File Configuration
  // This tells Node-RED where to find your flows
  flowFile: 'flows.json', 
  flowFilePretty: true,

  // 3. Define Global Context for Function Nodes
  // This makes the environment variables accessible within your Function nodes (if needed)
  functionGlobalContext: {
    // MQTT Configuration
    MQTT_HOST:
      process.env.MQTT_HOST ||
      '910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud',
    MQTT_PORT: process.env.MQTT_PORT || 8883,
    MQTT_USERNAME: process.env.MQTT_USERNAME || 'main_connection',
    MQTT_PASSWORD: process.env.MQTT_PASSWORD || 'dycrax-3ruzdU',
  },

  // 4. Custom Editor Title (Optional, but good for branding)
  editorTheme: {
    page: {
      title: 'Node-RED - Light System',
    },
    header: {
      title: '💡 Light System Simulation',
    },
  },
  
  // 5. Context storage (Standard default)
  contextStorage: {
    default: {
      module: 'memory',
    },
  },

  // Export function for external access
  exportGlobalContextKeys: true,
};