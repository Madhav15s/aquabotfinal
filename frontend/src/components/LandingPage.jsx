import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './LandingPage.css';

const LandingPage = ({ onEnterDashboard }) => {
  const [currentFeature, setCurrentFeature] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  const features = [
    {
      icon: "🧭",
      title: "Smart Voyage Planning",
      description: "AI-powered route optimization with weather integration and fuel cost analysis"
    },
    {
      icon: "📦",
      title: "Cargo Matching",
      description: "Intelligent vessel-cargo pairing with profitability optimization"
    },
    {
      icon: "📊",
      title: "Market Intelligence",
      description: "Real-time freight rates, bunker trends, and market analysis"
    },
    {
      icon: "⚓",
      title: "Port Intelligence",
      description: "Comprehensive port data, bunker availability, and cost analysis"
    },
    {
      icon: "💰",
      title: "Cost Management",
      description: "Automated PDA calculations and voyage cost optimization"
    }
  ];

  useEffect(() => {
    setIsVisible(true);
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % features.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [features.length]);

  const handleEnterDashboard = () => {
    setIsVisible(false);
    setTimeout(() => {
      onEnterDashboard();
    }, 500);
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="landing-page"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Background Elements */}
          <div className="background-elements">
            <div className="floating-shape shape-1"></div>
            <div className="floating-shape shape-2"></div>
            <div className="floating-shape shape-3"></div>
            <div className="floating-shape shape-4"></div>
          </div>

          {/* Main Content */}
          <div className="landing-content">
            {/* Header */}
            <motion.header
              className="landing-header"
              initial={{ y: -50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              <div className="ime-logo">
                <span className="logo-icon">🚢</span>
                <h1 className="logo-text">IME HUB</h1>
              </div>
              <div className="tagline">Maritime Intelligence Platform</div>
            </motion.header>

            {/* Hero Section */}
            <motion.section
              className="hero-section"
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              <h2 className="hero-title">
                Maritime AI Assistant
                <span className="hero-subtitle">Powered by Advanced Intelligence</span>
              </h2>
              <p className="hero-description">
                Transform your maritime operations with AI-driven insights, real-time data integration, 
                and intelligent decision support. From voyage planning to cost optimization, 
                IME Hub delivers the competitive edge you need in today's dynamic shipping market.
              </p>
            </motion.section>

            {/* Features Showcase */}
            <motion.section
              className="features-showcase"
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              <div className="feature-display">
                <motion.div
                  key={currentFeature}
                  className="feature-card"
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.8, opacity: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  <div className="feature-icon">{features[currentFeature].icon}</div>
                  <h3 className="feature-title">{features[currentFeature].title}</h3>
                  <p className="feature-description">{features[currentFeature].description}</p>
                </motion.div>
              </div>
              
              <div className="feature-indicators">
                {features.map((_, index) => (
                  <motion.div
                    key={index}
                    className={`indicator ${index === currentFeature ? 'active' : ''}`}
                    onClick={() => setCurrentFeature(index)}
                    whileHover={{ scale: 1.2 }}
                    whileTap={{ scale: 0.9 }}
                  />
                ))}
              </div>
            </motion.section>

            {/* Key Benefits */}
            <motion.section
              className="key-benefits"
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.8 }}
            >
              <h3 className="benefits-title">Why Choose IME Hub?</h3>
              <div className="benefits-grid">
                <motion.div
                  className="benefit-item"
                  whileHover={{ y: -10, scale: 1.05 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <div className="benefit-icon">⚡</div>
                  <h4>Real-time Intelligence</h4>
                  <p>Live AIS data, weather feeds, and market updates</p>
                </motion.div>
                
                <motion.div
                  className="benefit-item"
                  whileHover={{ y: -10, scale: 1.05 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <div className="benefit-icon">🧠</div>
                  <h4>AI-Powered Insights</h4>
                  <p>Advanced LLM reasoning for complex maritime decisions</p>
                </motion.div>
                
                <motion.div
                  className="benefit-item"
                  whileHover={{ y: -10, scale: 1.05 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <div className="benefit-icon">📱</div>
                  <h4>Seamless Integration</h4>
                  <p>Connect with existing systems and workflows</p>
                </motion.div>
              </div>
            </motion.section>

            {/* Call to Action */}
            <motion.section
              className="cta-section"
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 1.0 }}
            >
              <motion.button
                className="cta-button"
                onClick={handleEnterDashboard}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
                transition={{ type: "spring", stiffness: 400 }}
              >
                <span className="button-text">Enter Dashboard</span>
                <span className="button-icon">→</span>
              </motion.button>
              <p className="cta-subtitle">Experience the future of maritime operations</p>
            </motion.section>
          </div>

          {/* Footer */}
          <motion.footer
            className="landing-footer"
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 1.2 }}
          >
            <p>&copy; 2024 IME Hub. Advanced Maritime Intelligence Platform.</p>
          </motion.footer>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default LandingPage; 