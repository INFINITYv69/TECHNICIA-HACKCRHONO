/*
 * 🌍 Carbon-Vision AI + IoT System (Offline Simulation Mode)
 * Works without Azure IoT Hub — shows telemetry locally in the console.
 */

let messageId = 0;
let systemState = 'IDLE';

function randomRange(min, max) {
  return parseFloat((Math.random() * (max - min) + min).toFixed(2));
}

function readMQ2() {
  const base = randomRange(60, 150);
  return Math.random() < 0.85 ? base : base + randomRange(400, 800);
}

function readDistance() {
  return randomRange(10, 200);
}

function runAIScan() {
  const detected = Math.random() > 0.9;
  const intensity = detected ? randomRange(20, 75) : randomRange(0, 10);
  return { emissionDetected: detected, intensity: parseFloat(intensity.toFixed(2)) };
}

function activateBuzzer(state) {
  console.log(`[Buzzer] ${state ? '🚨 ALERT ON' : '✅ Normal'}`);
}

function controlRelay(state) {
  console.log(`[Relay] ${state ? '⚡ Activated' : '🟢 Idle'}`);
  systemState = state ? 'SHUTDOWN' : 'IDLE';
}

function simulateTelemetry() {
  messageId++;

  const gas_ppm = readMQ2();
  const distance_cm = readDistance();
  const { emissionDetected, intensity } = runAIScan();

  const ALERT_GAS_THRESHOLD = 300;
  const ALERT_DISTANCE_THRESHOLD = 20;

  const localAlert = gas_ppm > ALERT_GAS_THRESHOLD || distance_cm < ALERT_DISTANCE_THRESHOLD || emissionDetected;

  activateBuzzer(localAlert);
  controlRelay(localAlert);

  const payload = {
    messageId,
    systemState,
    sensorData: { gas_ppm, distance_cm },
    visionData: { emissionDetected, emission_intensity: intensity },
    alertStatus: localAlert,
    timestamp: new Date().toISOString()
  };

  console.log('\n📡 Telemetry Update:', JSON.stringify(payload, null, 2));
}

console.log('🌍 Carbon-Vision AI + IoT System (Offline Simulation Mode)');
setInterval(simulateTelemetry, 3000);
