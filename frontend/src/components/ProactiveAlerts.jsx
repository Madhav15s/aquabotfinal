import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ProactiveAlerts.css';

const ProactiveAlerts = ({ alerts, onClose }) => {
  const [visibleAlerts, setVisibleAlerts] = useState([]);
  const [currentAlertIndex, setCurrentAlertIndex] = useState(0);

  useEffect(() => {
    if (alerts.length > 0) {
      setVisibleAlerts(alerts);
      startAlertRotation();
    }
  }, [alerts]);

  const startAlertRotation = () => {
    const interval = setInterval(() => {
      setCurrentAlertIndex(prev => (prev + 1) % visibleAlerts.length);
    }, 5000); // Rotate every 5 seconds

    return () => clearInterval(interval);
  };

  const getAlertIcon = (type) => {
    switch (type) {
      case 'weather': return '🌪️';
      case 'market': return '📈';
      case 'ais': return '🚢';
      case 'port': return '⚓';
      case 'cost': return '💰';
      default: return '🔔';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getSeverityLabel = (severity) => {
    switch (severity) {
      case 'high': return 'Critical';
      case 'medium': return 'Important';
      case 'low': return 'Info';
      default: return 'Notice';
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  const handleAlertAction = (alert) => {
    // Handle different alert actions
    switch (alert.type) {
      case 'weather':
        // Navigate to weather routing
        console.log('Navigate to weather routing');
        break;
      case 'market':
        // Navigate to market analysis
        console.log('Navigate to market analysis');
        break;
      case 'ais':
        // Navigate to vessel tracking
        console.log('Navigate to vessel tracking');
        break;
      default:
        console.log('Handle alert:', alert);
    }
  };

  if (visibleAlerts.length === 0) return null;

  return (
    <motion.div
      className="proactive-alerts"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
    >
      <div className="alerts-header">
        <div className="alerts-title">
          <span className="alerts-icon">🔔</span>
          <span>Proactive Alerts</span>
          <span className="alerts-count">{visibleAlerts.length}</span>
        </div>
        <button className="close-alerts-btn" onClick={onClose}>
          ×
        </button>
      </div>

      <div className="alerts-content">
        <AnimatePresence mode="wait">
          {visibleAlerts.map((alert, index) => (
            <motion.div
              key={alert.id}
              className={`alert-item ${index === currentAlertIndex ? 'active' : ''}`}
              initial={{ opacity: 0, x: 20 }}
              animate={{ 
                opacity: index === currentAlertIndex ? 1 : 0.7,
                x: 0,
                scale: index === currentAlertIndex ? 1 : 0.95
              }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              style={{
                borderLeftColor: getSeverityColor(alert.severity)
              }}
            >
              <div className="alert-header">
                <div className="alert-icon">
                  {getAlertIcon(alert.type)}
                </div>
                <div className="alert-info">
                  <h4 className="alert-title">{alert.title}</h4>
                  <span className="alert-time">{formatTimestamp(alert.timestamp)}</span>
                </div>
                <div className="alert-severity">
                  <span 
                    className="severity-badge"
                    style={{ backgroundColor: getSeverityColor(alert.severity) }}
                  >
                    {getSeverityLabel(alert.severity)}
                  </span>
                </div>
              </div>
              
              <p className="alert-message">{alert.message}</p>
              
              <div className="alert-actions">
                <button
                  className="action-btn primary"
                  onClick={() => handleAlertAction(alert)}
                >
                  Take Action
                </button>
                <button className="action-btn secondary">
                  Dismiss
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Alert Navigation Dots */}
      {visibleAlerts.length > 1 && (
        <div className="alert-navigation">
          {visibleAlerts.map((_, index) => (
            <motion.button
              key={index}
              className={`nav-dot ${index === currentAlertIndex ? 'active' : ''}`}
              onClick={() => setCurrentAlertIndex(index)}
              whileHover={{ scale: 1.2 }}
              whileTap={{ scale: 0.9 }}
              transition={{ type: "spring", stiffness: 400 }}
            />
          ))}
        </div>
      )}

      {/* Quick Actions */}
      <div className="quick-actions">
        <button className="quick-action-btn" onClick={() => console.log('View all alerts')}>
          📋 View All
        </button>
        <button className="quick-action-btn" onClick={() => console.log('Alert settings')}>
          ⚙️ Settings
        </button>
        <button className="quick-action-btn" onClick={() => console.log('Alert history')}>
          📊 History
        </button>
      </div>
    </motion.div>
  );
};

export default ProactiveAlerts; 