const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');
const cors = require('cors');
const multer = require('multer');
const fs = require('fs');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// File upload configuration
const upload = multer({ dest: 'uploads/' });

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'client/build')));

// Simple reverse proxy to Flask LLM backend (default localhost:7001)
const FLASK_HOST = process.env.FLASK_HOST || 'localhost';
const FLASK_PORT = Number(process.env.FLASK_PORT || process.env.LLM_PORT || 7001);

function forwardToFlask(req, res, targetPath) {
  try {
    const payload = req.method === 'GET' ? null : JSON.stringify(req.body || {});
    const options = {
      hostname: FLASK_HOST,
      port: FLASK_PORT,
      path: targetPath,
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...(payload ? { 'Content-Length': Buffer.byteLength(payload) } : {}),
      },
    };

    const proxyReq = http.request(options, (proxyRes) => {
      const chunks = [];
      proxyRes.on('data', (chunk) => chunks.push(chunk));
      proxyRes.on('end', () => {
        const body = Buffer.concat(chunks);
        res.status(proxyRes.statusCode || 502);
        // Try to preserve JSON; fall back to raw
        const contentType = proxyRes.headers['content-type'] || 'application/json';
        res.setHeader('Content-Type', contentType);
        res.send(body);
      });
    });

    proxyReq.on('error', (err) => {
      console.error(`[Proxy Error] Failed to connect to Flask LLM backend at ${FLASK_HOST}:${FLASK_PORT}`);
      console.error(`[Proxy Error] Details: ${err.message}`);
      res.status(503).json({ 
        error: 'LLM backend unavailable', 
        details: err.message,
        backend_url: `http://${FLASK_HOST}:${FLASK_PORT}${targetPath}`
      });
    });

    if (payload) {
      proxyReq.write(payload);
    }
    proxyReq.end();
  } catch (e) {
    res.status(500).json({ error: 'Proxy failure', details: e.message });
  }
}

// Expose Flask endpoints via same-origin for the client
app.post('/mm_infer', (req, res) => forwardToFlask(req, res, '/mm_infer'));
app.get('/health', (req, res) => forwardToFlask(req, res, '/health'));

// Serve video files from root directory
app.use('/out.mp4', express.static(path.join(__dirname, 'out.mp4')));
app.use('/out_annotated.mp4', express.static(path.join(__dirname, 'out_annotated.mp4')));

// Also serve from Sonar directory if needed
app.use('/sonar', express.static(path.join(__dirname, 'Sonar')));

// Mock sensor data generator
class SensorSimulator {
  constructor() {
    this.baseline = {
      engineTemp: 82,
      engineRPM: 1200,
      oilPressure: 45,
      fuelLevel: 75,
      batteryVoltage: 13.8,
      waterDepth: 45,
      boatSpeed: 0,
      gpsLat: 37.7749,
      gpsLon: -122.4194,
      engineRunHours: 1247.5
    };
    this.anomalyChance = 0.02;
  }

  generateReading() {
    const addNoise = (base, variance) => base + (Math.random() - 0.5) * variance;
    const createAnomaly = Math.random() < this.anomalyChance;

    return {
      timestamp: Date.now(),
      engine: {
        temperature: addNoise(this.baseline.engineTemp, 4) + (createAnomaly ? 20 : 0),
        rpm: Math.max(0, addNoise(this.baseline.engineRPM, 100)),
        oilPressure: addNoise(this.baseline.oilPressure, 3) - (createAnomaly ? 10 : 0),
        runHours: this.baseline.engineRunHours + (Math.random() * 0.01),
        status: createAnomaly ? 'warning' : 'normal'
      },
      fuel: {
        level: Math.max(0, Math.min(100, this.baseline.fuelLevel - Math.random() * 0.01)),
        consumptionRate: addNoise(2.5, 0.5)
      },
      electrical: {
        batteryVoltage: addNoise(this.baseline.batteryVoltage, 0.2),
        amperage: addNoise(15, 3)
      },
      navigation: {
        depth: addNoise(this.baseline.waterDepth, 5),
        speed: Math.max(0, addNoise(this.baseline.boatSpeed, 2)),
        heading: Math.random() * 360,
        gps: {
          latitude: this.baseline.gpsLat + (Math.random() - 0.5) * 0.001,
          longitude: this.baseline.gpsLon + (Math.random() - 0.5) * 0.001
        }
      },
      sonar: {
        fishDetected: Math.random() < 0.15,
        fishDepth: Math.random() < 0.15 ? addNoise(30, 10) : null,
        fishSize: Math.random() < 0.15 ? ['small', 'medium', 'large'][Math.floor(Math.random() * 3)] : null,
        bottomHardness: addNoise(50, 20)
      },
      resonance: {
        propeller: addNoise(120, 5),
        hull: addNoise(60, 3),
        engine: addNoise(200, 10)
      }
    };
  }
}

const simulator = new SensorSimulator();

// AI Anomaly Detection
class AnomalyDetector {
  constructor() {
    this.history = [];
    this.maxHistory = 100;
  }

  addReading(data) {
    this.history.push(data);
    if (this.history.length > this.maxHistory) {
      this.history.shift();
    }
  }

  detectAnomalies(currentReading) {
    if (this.history.length < 10) return [];

    const anomalies = [];

    // Check engine temperature
    const avgTemp = this.history.reduce((sum, r) => sum + r.engine.temperature, 0) / this.history.length;
    if (currentReading.engine.temperature > avgTemp + 15) {
      anomalies.push({
        type: 'engine_overheat',
        severity: 'high',
        message: 'Engine temperature significantly above baseline',
        value: currentReading.engine.temperature,
        baseline: avgTemp.toFixed(1)
      });
    }

    // Check oil pressure
    const avgOil = this.history.reduce((sum, r) => sum + r.engine.oilPressure, 0) / this.history.length;
    if (currentReading.engine.oilPressure < avgOil - 8) {
      anomalies.push({
        type: 'low_oil_pressure',
        severity: 'critical',
        message: 'Oil pressure below safe operating range',
        value: currentReading.engine.oilPressure,
        baseline: avgOil.toFixed(1)
      });
    }

    // Check battery voltage
    if (currentReading.electrical.batteryVoltage < 12.5) {
      anomalies.push({
        type: 'low_battery',
        severity: 'medium',
        message: 'Battery voltage low - charging system may need attention',
        value: currentReading.electrical.batteryVoltage
      });
    }

    return anomalies;
  }
}

const anomalyDetector = new AnomalyDetector();

// WebSocket connection handling
wss.on('connection', (ws) => {
  console.log('Client connected');

  const interval = setInterval(() => {
    const sensorData = simulator.generateReading();
    anomalyDetector.addReading(sensorData);
    const anomalies = anomalyDetector.detectAnomalies(sensorData);

    ws.send(JSON.stringify({
      sensorData,
      anomalies,
      aiStatus: {
        monitoring: true,
        samplesCollected: anomalyDetector.history.length,
        baselineCalibrated: anomalyDetector.history.length >= 10
      }
    }));
  }, 1000);

  ws.on('close', () => {
    console.log('Client disconnected');
    clearInterval(interval);
  });
});

// File upload endpoint for sensor data
app.post('/api/upload-sensor-data', upload.single('sensorFile'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  try {
    const fileContent = fs.readFileSync(req.file.path, 'utf8');
    const parsedData = parseSensorFile(fileContent, req.file.mimetype);

    // Update simulator baseline with uploaded data
    if (parsedData && parsedData.engine) {
      simulator.baseline = {
        ...simulator.baseline,
        engineTemp: parsedData.engine.temperature || simulator.baseline.engineTemp,
        engineRPM: parsedData.engine.rpm || simulator.baseline.engineRPM,
        oilPressure: parsedData.engine.oilPressure || simulator.baseline.oilPressure
      };
    }

    // Clean up uploaded file
    fs.unlinkSync(req.file.path);

    res.json({
      success: true,
      message: 'Sensor data uploaded and applied',
      data: parsedData
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to process sensor file', details: error.message });
  }
});

// Parse sensor data from uploaded file
function parseSensorFile(content, mimeType) {
  try {
    // JSON format
    if (mimeType === 'application/json' || content.trim().startsWith('{')) {
      return JSON.parse(content);
    }

    // CSV format
    if (mimeType === 'text/csv' || content.includes(',')) {
      const lines = content.trim().split('\n');
      const headers = lines[0].split(',').map(h => h.trim());
      const values = lines[1].split(',').map(v => parseFloat(v.trim()));

      const data = {};
      headers.forEach((header, idx) => {
        const parts = header.split('.');
        if (parts.length === 2) {
          if (!data[parts[0]]) data[parts[0]] = {};
          data[parts[0]][parts[1]] = values[idx];
        }
      });
      return data;
    }

    // Plain text key-value pairs
    const lines = content.trim().split('\n');
    const data = {};
    lines.forEach(line => {
      const [key, value] = line.split(':').map(s => s.trim());
      if (key && value) {
        const parts = key.split('.');
        if (parts.length === 2) {
          if (!data[parts[0]]) data[parts[0]] = {};
          data[parts[0]][parts[1]] = parseFloat(value);
        }
      }
    });
    return data;
  } catch (error) {
    throw new Error('Unable to parse sensor data file');
  }
}

// Chat endpoint (placeholder for LLM integration)
app.post('/api/chat', (req, res) => {
  const { message, context } = req.body;

  // Placeholder response - replace with actual LLM integration
  const placeholderResponse = {
    response: `I received your message: "${message}". The backend LLM model will be connected here. Current context shows ${context?.anomalies?.length || 0} anomalies detected.`,
    timestamp: Date.now()
  };

  res.json(placeholderResponse);
});

// API endpoints
app.get('/api/status', (req, res) => {
  res.json({
    status: 'online',
    version: '1.0.0',
    aiEnabled: true
  });
});

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'client/build', 'index.html'));
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log('='.repeat(60));
  console.log('🚤 AI-POWERED BOAT MONITORING SYSTEM');
  console.log('='.repeat(60));
  console.log(`Server running on port ${PORT}`);
  console.log(`WebSocket ready for real-time sensor data`);
  console.log(`Proxying LLM requests to http://${FLASK_HOST}:${FLASK_PORT}`);
  console.log(`Open http://localhost:${PORT} to view dashboard`);
  console.log('='.repeat(60));
});
