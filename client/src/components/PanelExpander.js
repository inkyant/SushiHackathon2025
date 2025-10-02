import React from 'react';
import './PanelExpander.css';

function PanelExpander({ isExpanded, onClose, title, children }) {
  if (!isExpanded) return null;

  return (
    <div className="panel-expander-overlay" onClick={onClose}>
      <div className="panel-expander-content" onClick={(e) => e.stopPropagation()}>
        <div className="panel-expander-header">
          <h2>{title}</h2>
          <button className="panel-expander-close" onClick={onClose}>✕</button>
        </div>
        <div className="panel-expander-body">
          {children}
        </div>
      </div>
    </div>
  );
}

export default PanelExpander;
