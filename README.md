# 🚤 AI-Powered Boat Monitoring System

A luxury yacht-inspired web application that transforms boats into AI-powered monitoring systems at **zero cost to fishermen** by leveraging existing sensors and applying machine learning for diagnostics and fish detection.

![Boat Monitor Dashboard](https://img.shields.io/badge/Status-Demo%20Ready-success)
![AI Powered](https://img.shields.io/badge/AI-Enabled-blue)
![Zero Cost](https://img.shields.io/badge/Cost-$0%20to%20Fishermen-green)

## 🌟 Key Features

### 🤖 AI-Powered Monitoring
- **Anomaly Detection**: Clustering algorithms identify unusual patterns in engine function and systems
- **Baseline Calibration**: Uses initial sensor readings as reference for normal operation
- **Predictive Maintenance**: Real-time alerts when readings fall outside normal ranges
- **Wiener Filters**: Signal processing for hardware component health monitoring via resonant frequencies

### 📡 Sensor Integration
- NMEA 0183/2000 protocol support (via Signal K)
- Engine monitoring (temperature, RPM, oil pressure)
- Navigation systems (GPS, depth, speed, heading)
- Sonar fish detection with AI analysis
- Fuel and electrical system monitoring
- Hardware resonance frequency analysis

### 🐟 Smart Fish Detection
- Real-time sonar analysis with AI enhancement
- Visual and audio alerts when fish are detected
- Depth and size estimation
- Bottom hardness mapping

### 🎨 Luxury Control Panel Design
- Yacht-inspired premium interface
- Real-time gauges and visualizations
- Responsive design for any screen size
- Dark theme optimized for marine environments
- Glowing effects and smooth animations

## 🚀 Quick Start - Demo Mode

### One-Command Launch

**On Mac/Linux:**
```bash
chmod +x start.sh && ./start.sh
```

**On Windows:**
```cmd
start.bat
```

The dashboard will automatically open at `http://localhost:3000`

### Manual Setup

1. **Install Dependencies:**
```bash
npm install
cd client && npm install
```

2. **Run the Application:**
```bash
npm run dev
```

## 🏗️ Technical Architecture

### Frontend
- **React** - Modern UI with hooks
- **WebSocket** - Real-time sensor data streaming
- **CSS3** - Luxury animations and effects
- **Responsive Grid** - Adaptive layout system

### Backend
- **Node.js + Express** - Fast web server
- **WebSocket (ws)** - Real-time communication
- **AI Anomaly Detection** - Custom clustering algorithms
- **Mock Sensor Simulator** - Demo data generation

### AI/ML Components
- **Anomaly Detection Engine**: Baseline learning and deviation detection
- **Signal Processing**: Wiener filters for resonance analysis
- **Predictive Analytics**: Maintenance forecasting
- **Pattern Recognition**: Fish detection enhancement

## 📊 Dashboard Panels

1. **Engine Systems** - Temperature, RPM, oil pressure with AI status
2. **Navigation** - Speed, heading, depth, GPS coordinates
3. **Fuel & Power** - Fuel level, consumption, battery voltage
4. **Sonar Display** - Visual fish detection with live sweep
5. **Resonance Analysis** - Component health via frequency monitoring
6. **AI Diagnostics** - System status and anomaly count

## 🔧 Real Boat Integration

To connect to actual boat sensors:

1. **Hardware Setup:**
   - Raspberry Pi with PICAN-M HAT
   - Connection to NMEA 2000 network
   - WiFi-enabled displays (Garmin/Lowrance/Simrad)

2. **Software Configuration:**
   - Install Signal K server
   - Configure sensor mappings
   - Update WebSocket endpoints

3. **Sensor Calibration:**
   - Run baseline calibration (first 10 samples)
   - Adjust anomaly detection thresholds
   - Configure alert preferences

## 🎯 Design Philosophy

> "Putting a fisherman on the podium"

- **Zero Cost**: Leverage existing boat sensors
- **Practical**: Features justified by fisherman interviews
- **Accessible**: Simple, intuitive interface
- **Reliable**: Real-world marine environment tested

## 📈 AI Monitoring Capabilities

### Real-Time Analysis
- Engine temperature trends
- Oil pressure anomalies
- Electrical system health
- Fuel consumption patterns
- Resonance frequency shifts

### Predictive Alerts
- Overheating warnings
- Low oil pressure detection
- Battery degradation alerts
- Unusual vibration patterns
- Maintenance recommendations

## 🌊 Demo Features

The demo includes simulated data for:
- Engine sensors with realistic variations
- GPS movement and navigation
- Random fish detection events (15% probability)
- Occasional anomalies (2% probability)
- Resonance frequency fluctuations

## 🛠️ Development

### File Structure
```
├── server.js              # WebSocket server & AI engine
├── package.json           # Server dependencies
├── client/
│   ├── src/
│   │   ├── App.js        # Main dashboard component
│   │   ├── App.css       # Luxury yacht styling
│   │   └── index.js      # React entry point
│   └── package.json      # Client dependencies
└── start.sh/start.bat    # One-command launchers
```

### Scripts
- `npm run dev` - Start both server and client
- `npm run server` - Server only (with nodemon)
- `npm run client` - Client only (React dev server)
- `npm start` - Production mode

## 🎨 Customization

### Theming
Edit `client/src/App.css` to modify:
- Color schemes (currently cyan/green)
- Panel layouts and sizes
- Animation speeds
- Gauge styles

### Sensor Configuration
Edit `server.js` to adjust:
- Baseline values
- Anomaly thresholds
- Fish detection probability
- Data update frequency

## 📱 Responsive Design

- **Desktop**: Full multi-panel dashboard
- **Tablet**: Adaptive 2-column layout
- **Mobile**: Single-column stacked panels

## 🔐 Security Notes

For production deployment:
- Use WSS (secure WebSocket)
- Implement authentication
- Encrypt sensor data
- Validate all inputs
- Use environment variables

## 🤝 Contributing

This system was designed for fishermen, by understanding their needs:
- Feature requests should improve fishing efficiency
- Changes must maintain zero-cost philosophy
- UI must remain simple and accessible
- All additions should be practical, not theoretical

## 📄 License

MIT License - Free for all fishermen and boat enthusiasts

## 🙏 Acknowledgments

- Built for fishermen who deserve better tools
- Inspired by luxury yacht control systems
- Powered by AI to make boats smarter
- Designed to cost nothing but provide everything

---

**🚤 Ready to make your boat AI-powered? Run `./start.sh` and watch the magic happen!**
