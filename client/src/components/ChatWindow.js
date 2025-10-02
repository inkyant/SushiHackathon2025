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

    // Placeholder for backend chat API
    // In the future, this will call your LLM model with context
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          context: {
            sensorData,
            anomalies
          }
        })
      });

      let contentText = 'Backend model integration pending. This is a placeholder response.';
      try {
        const data = await response.json();
        contentText = data.response || contentText;
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
