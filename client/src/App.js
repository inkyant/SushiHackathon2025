import React, { useState, useEffect } from 'react';
import './App.css';
import VideoPlayer from './components/VideoPlayer';
import ChatWindow from './components/ChatWindow';
import PanelExpander from './components/PanelExpander';

function App() {
  const [sensorData, setSensorData] = useState(() => ({
    timestamp: Date.now(),
    engine: {
      temperature: 82,
      rpm: 1200,
      oilPressure: 45,
      runHours: 1247.5,
      status: 'normal'
    },
    fuel: {
      level: 75,
      consumptionRate: 2.5
    },
    electrical: {
      batteryVoltage: 13.8,
      amperage: 15
    },
    navigation: {
      depth: 45,
      speed: 0,
      heading: 0,
      gps: { latitude: 37.7749, longitude: -122.4194 }
    },
    sonar: {
      fishDetected: false,
      fishDepth: null,
      fishSize: null,
      bottomHardness: 50
    },
    resonance: {
      propeller: 120,
      hull: 60,
      engine: 200
    }
  }));
  const [anomalies, setAnomalies] = useState([]);
  const [aiStatus, setAiStatus] = useState({ monitoring: false, samplesCollected: 0, baselineCalibrated: false });
  const [connected, setConnected] = useState(false);
  const [fishAlert, setFishAlert] = useState(false);
  const [expandedPanel, setExpandedPanel] = useState(null);
  const [currentView, setCurrentView] = useState('engine'); // 'engine' or 'assistant'
  const [sonarVideoOpen, setSonarVideoOpen] = useState(false);
  const [sonarClickCount, setSonarClickCount] = useState(0);
  const [sonarLastClickTime, setSonarLastClickTime] = useState(0);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:3001');

    ws.onopen = () => {
      setConnected(true);
      console.log('Connected to boat sensors');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.sensorData) setSensorData(data.sensorData);
        if (Array.isArray(data.anomalies)) setAnomalies(data.anomalies);
        if (data.aiStatus) setAiStatus(data.aiStatus);

        if (data.sensorData?.sonar?.fishDetected) {
          setFishAlert(true);
          setTimeout(() => setFishAlert(false), 3000);
        }
      } catch (err) {
        console.warn('Failed to parse WS message', err);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      console.log('Disconnected from sensors');
    };

    return () => ws.close();
  }, []);

  const getStatusColor = (value, min, max, reverse = false) => {
    const percentage = ((value - min) / (max - min)) * 100;
    if (reverse) {
      if (percentage > 80) return '#ff4444';
      if (percentage > 60) return '#ffaa00';
      return '#00ff88';
    }
    if (percentage < 20) return '#ff4444';
    if (percentage < 40) return '#ffaa00';
    return '#00ff88';
  };

  const handleExpandPanel = (panelName, content) => {
    setExpandedPanel({ name: panelName, content });
  };

  const handleSonarClick = () => {
    const now = Date.now();

    // Reset click count if more than 1 second has passed since last click
    if (now - sonarLastClickTime > 1000) {
      setSonarClickCount(1);
      setSonarLastClickTime(now);
      return;
    }

    // Increment click count
    const newCount = sonarClickCount + 1;
    setSonarClickCount(newCount);
    setSonarLastClickTime(now);

    // Show video after 3 clicks
    if (newCount >= 3) {
      setSonarVideoOpen(true);
      setSonarClickCount(0); // Reset counter
    }
  };

  // Always render UI with initial mock, live data will stream via WS

  return (
    <div className="App">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <h1>⚓ VESSEL CONTROL SYSTEM</h1>
          <div className="ai-badge">
            <span className="ai-indicator"></span>
            AI MONITORING ACTIVE
          </div>
        </div>
        <div className="header-right">
          <div className="status-indicator">
            <span className={`status-dot ${connected ? 'online' : 'offline'}`}></span>
            {connected ? 'ONLINE' : 'OFFLINE'}
          </div>
          <div className="timestamp">
            {new Date(sensorData.timestamp || Date.now()).toLocaleTimeString()}
          </div>
        </div>
      </header>

      {/* Fish Alert Banner */}
      {fishAlert && (
        <div className="fish-alert">
          <div className="alert-content">
            <span className="alert-icon-text">ALERT</span>
            <div>
              <h3>FISH DETECTED</h3>
              <p>Depth: {sensorData.sonar.fishDepth?.toFixed(1)}m | Size: {sensorData.sonar.fishSize?.toUpperCase()}</p>
            </div>
          </div>
        </div>
      )}

      {/* Anomaly Alerts */}
      {anomalies.length > 0 && (
        <div className="anomaly-alerts">
          {anomalies.map((anomaly, idx) => (
            <div key={idx} className={`anomaly-alert severity-${anomaly.severity}`}>
              <span className="alert-icon-text">!</span>
              <div>
                <h4>{anomaly.type.replace(/_/g, ' ').toUpperCase()}</h4>
                <p>{anomaly.message}</p>
                <small>Current: {anomaly.value} | Baseline: {anomaly.baseline}</small>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Main Content Area - Conditional Views */}
      <div className="main-content">

        {/* Boat Status View */}
        {currentView === 'engine' && (
          <div className="dashboard-grid">

        {/* Engine Panel - Top (Consolidated with 6 gauges) */}
          <div className="panel panel-engine panel-large">
            <div className="panel-header">
              <h2>ENGINE SYSTEMS</h2>
              <div className="panel-header-actions">
                <span className={`status-badge ${sensorData.engine.status}`}>
            {sensorData.engine.status.toUpperCase()}
                </span>
                <button className="expand-btn" onClick={() => handleExpandPanel('ENGINE SYSTEMS', renderEngineContent())}>
            ⛶
                </button>
                {/* Test Data Button */}
                <button
            className="demo-trigger-btn"
            onClick={() => {
              setSensorData({
                ...sensorData,
                engine: {
                  ...sensorData.engine,
                  rpm: 1800,
                  temperature: 85,
                  oilPressure: 45,
                  runHours: 123.4,
                  status: 'testing'
                },
                fuel: {
                  ...sensorData.fuel,
                  consumptionRate: 2.5,
                  level: 75
                },
                electrical: {
                  ...sensorData.electrical,
                  batteryVoltage: 13.8,
                  amperage: 22.5
                },
                navigation: {
                  ...sensorData.navigation,
                  speed: 12.3,
                  heading: 270,
                  depth: 33.2,
                  gps: {
              latitude: 37.7749,
              longitude: -122.4194
                  }
                },
                resonance: {
                  ...sensorData.resonance,
                  propeller: 80,
                  engine: 120,
                  hull: 60
                },
                timestamp: Date.now(),
                sonar: {
                  ...sensorData.sonar,
                  fishDetected: false,
                  fishDepth: null,
                  fishSize: null
                }
              });
            }}
                >
            Inject Test Data
                </button>
              </div>
            </div>
            <div className="gauge-group gauge-group-six">
              {/* Row 1: RPM, Fuel Flow, Coolant Temp */}
            <div className="gauge">
              <svg viewBox="0 0 200 120" className="gauge-svg">
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1a1f3a" strokeWidth="20" />
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#00d4ff" strokeWidth="20" strokeDasharray={`${(sensorData.engine.rpm / 3000) * 251} 251`} className="gauge-progress" />
                <text x="100" y="80" textAnchor="middle" className="gauge-value">{Math.round(sensorData.engine.rpm)}</text>
                <text x="100" y="100" textAnchor="middle" className="gauge-label">RPM</text>
              </svg>
            </div>
            <div className="gauge">
              <svg viewBox="0 0 200 120" className="gauge-svg">
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1a1f3a" strokeWidth="20" />
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#00ff88" strokeWidth="20" strokeDasharray={`${(sensorData.fuel.consumptionRate / 5) * 251} 251`} className="gauge-progress" />
                <text x="100" y="80" textAnchor="middle" className="gauge-value">{sensorData.fuel.consumptionRate.toFixed(1)}</text>
                <text x="100" y="100" textAnchor="middle" className="gauge-label">FUEL L/H</text>
              </svg>
            </div>
            <div className="gauge">
              <svg viewBox="0 0 200 120" className="gauge-svg">
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1a1f3a" strokeWidth="20" />
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke={getStatusColor(sensorData.engine.temperature, 60, 110, true)} strokeWidth="20" strokeDasharray={`${((sensorData.engine.temperature - 60) / 50) * 251} 251`} className="gauge-progress" />
                <text x="100" y="80" textAnchor="middle" className="gauge-value">{sensorData.engine.temperature.toFixed(1)}</text>
                <text x="100" y="100" textAnchor="middle" className="gauge-label">COOLANT</text>
              </svg>
            </div>
            {/* Row 2: Oil Pressure, Battery, Run Hours */}
            <div className="gauge">
              <svg viewBox="0 0 200 120" className="gauge-svg">
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1a1f3a" strokeWidth="20" />
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke={getStatusColor(sensorData.engine.oilPressure, 20, 60)} strokeWidth="20" strokeDasharray={`${(sensorData.engine.oilPressure / 60) * 251} 251`} className="gauge-progress" />
                <text x="100" y="80" textAnchor="middle" className="gauge-value">{sensorData.engine.oilPressure.toFixed(1)}</text>
                <text x="100" y="100" textAnchor="middle" className="gauge-label">OIL PSI</text>
              </svg>
            </div>
            <div className="gauge">
              <svg viewBox="0 0 200 120" className="gauge-svg">
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1a1f3a" strokeWidth="20" />
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke={getStatusColor(sensorData.electrical.batteryVoltage, 12, 15)} strokeWidth="20" strokeDasharray={`${((sensorData.electrical.batteryVoltage - 12) / 3) * 251} 251`} className="gauge-progress" />
                <text x="100" y="80" textAnchor="middle" className="gauge-value">{sensorData.electrical.batteryVoltage.toFixed(1)}</text>
                <text x="100" y="100" textAnchor="middle" className="gauge-label">BATTERY V</text>
              </svg>
            </div>
            <div className="gauge">
              <svg viewBox="0 0 200 120" className="gauge-svg">
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1a1f3a" strokeWidth="20" />
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#00d4ff" strokeWidth="20" strokeDasharray="251 251" className="gauge-progress" />
                <text x="100" y="80" textAnchor="middle" className="gauge-value">{sensorData.engine.runHours.toFixed(1)}</text>
                <text x="100" y="100" textAnchor="middle" className="gauge-label">RUN HOURS</text>
              </svg>
            </div>
          </div>
        </div>

        {/* Smaller Panels - Reordered */}
        <div className="panel panel-small panel-ai">
          <div className="panel-header">
            <h2>AI STATUS</h2>
            <button className="expand-btn" onClick={() => handleExpandPanel('AI DIAGNOSTICS', renderAIContent())}>
              ⛶
            </button>
          </div>
          <div className="ai-status-compact">
            <div className="ai-stat-compact">
              <span className="ai-stat-label">BASELINE</span>
              <span className={`ai-stat-value ${aiStatus?.baselineCalibrated ? 'active' : 'inactive'}`}>
                {aiStatus?.baselineCalibrated ? '✓' : '⋯'}
              </span>
            </div>
            <div className="ai-stat-compact">
              <span className="ai-stat-label">SAMPLES</span>
              <span className="ai-stat-value active">{aiStatus?.samplesCollected || 0}</span>
            </div>
            <div className="ai-stat-compact">
              <span className="ai-stat-label">ANOMALIES</span>
              <span className={`ai-stat-value ${anomalies.length > 0 ? 'warning' : 'active'}`}>
                {anomalies.length}
              </span>
            </div>
          </div>
        </div>

        <div className="panel panel-small">
          <div className="panel-header">
            <h2>NAVIGATION</h2>
            <button className="expand-btn" onClick={() => handleExpandPanel('NAVIGATION', renderNavigationContent())}>
              ⛶
            </button>
          </div>
          <div className="nav-data compact">
            <div className="data-row">
              <span className="data-label">SPEED</span>
              <span className="data-value">{sensorData.navigation.speed.toFixed(1)} kts</span>
            </div>
            <div className="data-row">
              <span className="data-label">HEADING</span>
              <span className="data-value">{Math.round(sensorData.navigation.heading)}°</span>
            </div>
            <div className="data-row">
              <span className="data-label">DEPTH</span>
              <span className="data-value">{sensorData.navigation.depth.toFixed(1)} m</span>
            </div>
          </div>
        </div>

        <div className="panel panel-small">
          <div className="panel-header">
            <h2>RESONANCE</h2>
            <button className="expand-btn" onClick={() => handleExpandPanel('RESONANCE ANALYSIS', renderResonanceContent())}>
              ⛶
            </button>
          </div>
          <div className="resonance-data compact">
            <div className="resonance-item">
              <span className="resonance-label">PROP</span>
              <div className="resonance-bar">
                <div className="resonance-value" style={{ width: `${(sensorData.resonance.propeller / 150) * 100}%` }}></div>
              </div>
              <span className="resonance-hz">{sensorData.resonance.propeller.toFixed(1)}</span>
            </div>
            <div className="resonance-item">
              <span className="resonance-label">ENGINE</span>
              <div className="resonance-bar">
                <div className="resonance-value" style={{ width: `${(sensorData.resonance.engine / 250) * 100}%` }}></div>
              </div>
              <span className="resonance-hz">{sensorData.resonance.engine.toFixed(1)}</span>
            </div>
          </div>
        </div>

          </div>
        )}

        {/* Sonar View */}
        {currentView === 'sonar' && (
          <div className="sonar-view" onClick={handleSonarClick}>
            <VideoPlayer
              embedded={true}
              showBoundingBoxes={false}
            />
          </div>
        )}

        {/* AI Assistant View */}
        {currentView === 'assistant' && (
          <div className="assistant-view">
            <div className="assistant-content">
              <ChatWindow
                isOpen={true}
                onClose={() => {}}
                sensorData={sensorData}
                anomalies={anomalies}
                embedded={true}
              />
            </div>
          </div>
        )}

      </div>

      {/* Bottom Navigation Bar */}
      <nav className="bottom-nav">
        <button
          className={`nav-item ${currentView === 'engine' ? 'active' : ''}`}
          onClick={() => setCurrentView('engine')}
        >
          <span className="nav-label">Boat Status</span>
        </button>
        <button
          className={`nav-item ${currentView === 'sonar' ? 'active' : ''}`}
          onClick={() => setCurrentView('sonar')}
        >
          <span className="nav-label">Sonar</span>
        </button>
        <button
          className={`nav-item ${currentView === 'assistant' ? 'active' : ''}`}
          onClick={() => setCurrentView('assistant')}
        >
          <span className="nav-label">Maintenance Assistant</span>
        </button>
      </nav>

      {/* Sonar Video Modal */}
      <VideoPlayer
        isOpen={sonarVideoOpen}
        onClose={() => setSonarVideoOpen(false)}
        showBoundingBoxes={true}
      />

      {/* Panel Expander */}
      <PanelExpander
        isExpanded={expandedPanel !== null}
        onClose={() => setExpandedPanel(null)}
        title={expandedPanel?.name}
      >
        {expandedPanel?.content}
      </PanelExpander>

      {/* Footer */}
      <footer className="footer">
        <p>AI-Powered Boat Monitoring System • Zero-Cost Fisherman Solution</p>
      </footer>
    </div>
  );

  // Helper functions to render expanded panel content
  function renderEngineContent() {
    return (
      <div className="gauge-group expanded">
        <div className="gauge">
          <svg viewBox="0 0 200 120" className="gauge-svg">
            <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1a1f3a" strokeWidth="20" />
            <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke={getStatusColor(sensorData.engine.temperature, 60, 110, true)} strokeWidth="20" strokeDasharray={`${((sensorData.engine.temperature - 60) / 50) * 251} 251`} className="gauge-progress" />
            <text x="100" y="80" textAnchor="middle" className="gauge-value">{sensorData.engine.temperature.toFixed(1)}°</text>
            <text x="100" y="100" textAnchor="middle" className="gauge-label">TEMPERATURE</text>
          </svg>
        </div>
        <div className="gauge">
          <svg viewBox="0 0 200 120" className="gauge-svg">
            <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1a1f3a" strokeWidth="20" />
            <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#00d4ff" strokeWidth="20" strokeDasharray={`${(sensorData.engine.rpm / 3000) * 251} 251`} className="gauge-progress" />
            <text x="100" y="80" textAnchor="middle" className="gauge-value">{Math.round(sensorData.engine.rpm)}</text>
            <text x="100" y="100" textAnchor="middle" className="gauge-label">RPM</text>
          </svg>
        </div>
        <div className="gauge">
          <svg viewBox="0 0 200 120" className="gauge-svg">
            <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1a1f3a" strokeWidth="20" />
            <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke={getStatusColor(sensorData.engine.oilPressure, 20, 60)} strokeWidth="20" strokeDasharray={`${(sensorData.engine.oilPressure / 60) * 251} 251`} className="gauge-progress" />
            <text x="100" y="80" textAnchor="middle" className="gauge-value">{sensorData.engine.oilPressure.toFixed(1)}</text>
            <text x="100" y="100" textAnchor="middle" className="gauge-label">OIL PSI</text>
          </svg>
        </div>
      </div>
    );
  }

  function renderNavigationContent() {
    return (
      <div className="nav-data">
        <div className="data-row"><span className="data-label">SPEED</span><span className="data-value">{sensorData.navigation.speed.toFixed(1)} kts</span></div>
        <div className="data-row"><span className="data-label">HEADING</span><span className="data-value">{Math.round(sensorData.navigation.heading)}°</span></div>
        <div className="data-row"><span className="data-label">DEPTH</span><span className="data-value">{sensorData.navigation.depth.toFixed(1)} m</span></div>
        <div className="data-row"><span className="data-label">POSITION</span><span className="data-value gps">{sensorData.navigation.gps.latitude.toFixed(4)}°N<br/>{Math.abs(sensorData.navigation.gps.longitude).toFixed(4)}°W</span></div>
      </div>
    );
  }

  function renderFuelContent() {
    return (
      <div>
        <div className="bar-gauge"><div className="bar-gauge-label"><span>FUEL LEVEL</span><span>{sensorData.fuel.level.toFixed(1)}%</span></div><div className="bar-gauge-track"><div className="bar-gauge-fill" style={{ width: `${sensorData.fuel.level}%`, background: getStatusColor(sensorData.fuel.level, 0, 100) }}></div></div></div>
        <div className="data-row"><span className="data-label">CONSUMPTION</span><span className="data-value">{sensorData.fuel.consumptionRate.toFixed(2)} L/h</span></div>
        <div className="data-row"><span className="data-label">BATTERY</span><span className="data-value" style={{ color: getStatusColor(sensorData.electrical.batteryVoltage, 12, 15) }}>{sensorData.electrical.batteryVoltage.toFixed(2)} V</span></div>
        <div className="data-row"><span className="data-label">AMPERAGE</span><span className="data-value">{sensorData.electrical.amperage.toFixed(1)} A</span></div>
      </div>
    );
  }

  function renderResonanceContent() {
    return (
      <div className="resonance-data">
        <div className="resonance-item"><span className="resonance-label">PROPELLER</span><div className="resonance-bar"><div className="resonance-value" style={{ width: `${(sensorData.resonance.propeller / 150) * 100}%` }}></div></div><span className="resonance-hz">{sensorData.resonance.propeller.toFixed(1)} Hz</span></div>
        <div className="resonance-item"><span className="resonance-label">HULL</span><div className="resonance-bar"><div className="resonance-value" style={{ width: `${(sensorData.resonance.hull / 100) * 100}%` }}></div></div><span className="resonance-hz">{sensorData.resonance.hull.toFixed(1)} Hz</span></div>
        <div className="resonance-item"><span className="resonance-label">ENGINE</span><div className="resonance-bar"><div className="resonance-value" style={{ width: `${(sensorData.resonance.engine / 250) * 100}%` }}></div></div><span className="resonance-hz">{sensorData.resonance.engine.toFixed(1)} Hz</span></div>
      </div>
    );
  }

  function renderAIContent() {
    return (
      <div>
        <div className="ai-status-grid">
          <div className="ai-stat"><span className="ai-stat-label">BASELINE</span><span className={`ai-stat-value ${aiStatus?.baselineCalibrated ? 'active' : 'inactive'}`}>{aiStatus?.baselineCalibrated ? 'CALIBRATED' : 'CALIBRATING'}</span></div>
          <div className="ai-stat"><span className="ai-stat-label">SAMPLES</span><span className="ai-stat-value active">{aiStatus?.samplesCollected || 0}</span></div>
          <div className="ai-stat"><span className="ai-stat-label">ANOMALIES</span><span className={`ai-stat-value ${anomalies.length > 0 ? 'warning' : 'active'}`}>{anomalies.length}</span></div>
        </div>
        {aiStatus?.baselineCalibrated && (
          <div className="ai-message">
            <p>✓ All systems operating within normal parameters</p>
            <p className="ai-submessage">Predictive maintenance monitoring active</p>
          </div>
        )}
      </div>
    );
  }
}

export default App;
