import React, { useState, useRef, useEffect } from 'react';
import './ChatWindow.css';

function ChatWindow({ isOpen, onClose, sensorData, anomalies, embedded = false }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI maintenance assistant. I can help diagnose issues and provide maintenance recommendations based on your boat\'s sensor data.',
      timestamp: Date.now()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Call backend multimodal inference API with structured context
    try {
      // Derive engine_stats array expected by backend maintenance model
      const engine_stats = [
        // Engine rpm, Lub oil pressure, Fuel pressure, Coolant pressure, lub oil temp, Coolant temp
        Number(sensorData?.engine?.rpm ?? 0),
        Number(sensorData?.engine?.oilPressure ?? 0),
        Number(sensorData?.fuel?.pressure ?? 0),
        Number(sensorData?.engine?.coolantPressure ?? 0),
        Number(sensorData?.engine?.oilTemp ?? sensorData?.engine?.temperature ?? 0),
        Number(sensorData?.engine?.coolantTemp ?? sensorData?.engine?.temperature ?? 0)
      ];

      const context = {
        location: sensorData?.navigation?.gps || null,
        water_body: 'unknown',
        datetime: new Date(sensorData?.timestamp || Date.now()).toISOString(),
        season: 'unknown',
        temperature: sensorData?.engine?.temperature ?? null,
        anomalies: anomalies || []
      };

      const response = await fetch(`http://127.0.0.1:7001/mm_infer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_path: sensorData?.sonar?.imagePath || null,
          engine_stats,
          context,
          user_prompt: input,
          save_annotated_to: sensorData?.sonar?.annotatedOutputPath || null,
          sensor_data: sensorData,
          anomalies
        })
      });

      let contentText = 'Awaiting backend response...';
      try {
        const data = await response.json();
        if (data && typeof data === 'object') {
          const llmText = data.llm_output || data.output || null;
          const sonarCounts = data?.sonar?.counts_by_class;
          const engineDiag = data?.engine?.diagnosis;
          const engineConf = data?.engine?.confidence;

          const parts = [];
          if (llmText) parts.push(String(llmText));
          if (engineDiag) parts.push(`\n\nEngine: ${engineDiag}${typeof engineConf === 'number' ? ` (${(engineConf * 100).toFixed(1)}%)` : ''}`);
          if (sonarCounts && typeof sonarCounts === 'object') {
            const summary = Object.entries(sonarCounts)
              .map(([k, v]) => `${k}: ${v}`)
              .join(', ');
            parts.push(`\n\nSonar: ${summary}`);
          }
          contentText = parts.join('');
        }
      } catch (e) {
        // ignore JSON parse errors; keep contentText default
      }

      if (!response.ok) {
        contentText = `The assistant is temporarily unavailable (${response.status}). I will respond once the backend is online.`;
      }

      const assistantMessage = {
        role: 'assistant',
        content: contentText,
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      // Fallback placeholder response when backend not connected
      const assistantMessage = {
        role: 'assistant',
        content: `I understand you're asking about: "${input}". The LLM backend is not yet connected. Once integrated, I'll provide context-aware maintenance advice based on your current sensor readings.`,
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen && !embedded) return null;

  const chatContent = (
    <div className={embedded ? "chat-window embedded" : "chat-window"} onClick={(e) => embedded ? null : e.stopPropagation()}>
        {/* Header */}
        <div className="chat-header">
          <div className="chat-header-left">
            <span className="chat-icon-text">MAINT</span>
            <div>
              <h3>Maintenance Assistant</h3>
              <p className="chat-status">
                <span className="status-indicator"></span>
                AI-Powered
              </p>
            </div>
          </div>
          {!embedded && <button className="chat-close-btn" onClick={onClose}>×</button>}
        </div>

        {/* Context Info */}
        {anomalies && anomalies.length > 0 && (
          <div className="chat-context-alert">
            <span className="alert-symbol">!</span>
            <span>{anomalies.length} active anomaly detected - Ask me about it!</span>
          </div>
        )}

        {/* Messages */}
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.role}`}>
              <div className="message-content">
                {msg.content}
              </div>
              <div className="message-timestamp">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="chat-message assistant">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="chat-input-container">
          <textarea
            className="chat-input"
            placeholder="Ask about maintenance, diagnostics, or sensor readings..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows="2"
          />
          <button
            className="chat-send-btn"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
          >
            Send
          </button>
        </div>
      </div>
  );

  if (embedded) {
    return chatContent;
  }

  return (
    <div className="chat-modal-overlay" onClick={onClose}>
      {chatContent}
    </div>
  );
}

export default ChatWindow;
