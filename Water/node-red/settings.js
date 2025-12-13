process.env.MQTT_HOST = '910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud';
process.env.MQTT_PORT = 8883;
process.env.MQTT_USERNAME = 'main_connection';
process.env.MQTT_PASSWORD = 'dycrax-3ruzdU';

module.exports = {

  // Flow file configuration
  flowFile: 'flows.json',
  flowFilePretty: true,

  // Logging
  logging: {
    console: {
      level: 'info',
      metrics: false,
      audit: false,
    },
  },

  // Editor settings
  editorTheme: {
    projects: {
      enabled: false,
    },
    page: {
      title: 'Node-RED - Water System',
    },
    header: {
      title: '💧 Water System Simulation',
    },
  },

  // Function node settings
  functionGlobalContext: {
    // MQTT Configuration
    MQTT_HOST:
      process.env.MQTT_HOST ||
      '910e146c7f1f4c0fa6799235de0cd0fe.s1.eu.hivemq.cloud',
    MQTT_PORT: process.env.MQTT_PORT || 8883,
    MQTT_USERNAME: process.env.MQTT_USERNAME || 'main_connection',
    MQTT_PASSWORD: process.env.MQTT_PASSWORD || 'dycrax-3ruzdU',
  },

  // Context storage
  contextStorage: {
    default: {
      module: 'memory',
    },
  },

  // Export function for external access
  exportGlobalContextKeys: true,
}