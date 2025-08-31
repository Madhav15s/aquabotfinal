import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatWindow from './ChatWindow';
import DocumentUpload from './DocumentUpload';
import './Dashboard.css';

const AGENTS = [
  {
    id: 'general',
    name: 'Captain Router',
    avatar: '👨‍✈️',
    description: 'Intelligent routing and general assistance',
    color: '#4A90E2',
    capabilities: ['Route optimization', 'Multi-agent coordination', 'Context awareness', 'Document analysis']
  },
  {
    id: 'voyage_planner',
    name: 'Voyage Planner',
    avatar: '🧭',
    description: 'Smart route planning with weather & optimization',
    color: '#7ED321',
    capabilities: ['Weather routing', 'Fuel optimization', 'What-if scenarios', 'ETA calculation']
  },
  {
    id: 'cargo_matching',
    name: 'Cargo Matcher',
    avatar: '📦',
    description: 'Vessel-cargo pairing with profitability analysis',
    color: '#F5A623',
    capabilities: ['Cargo matching', 'Profitability estimates', 'Real-time tracking', 'Laycan optimization']
  },
  {
    id: 'market_insights',
    name: 'Market Insights',
    avatar: '📊',
    description: 'Freight rates, bunker trends & market analysis',
    color: '#D0021B',
    capabilities: ['Market trends', 'Freight rates', 'Bunker prices', 'Benchmarking']
  },
  {
    id: 'port_intelligence',
    name: 'Port Intelligence',
    avatar: '⚓',
    description: 'Port data, bunker availability & costs',
    color: '#9013FE',
    capabilities: ['Port information', 'Bunker ports', 'Cost analysis', 'Availability tracking']
  },
  {
    id: 'pda_management',
    name: 'PDA Management',
    avatar: '💰',
    description: 'Port disbursement & cost management',
    color: '#50E3C2',
    capabilities: ['PDA estimates', 'Cost tracking', 'Budget management', 'Variance analysis']
  }
];

// Organized Proactive Alerts by Category
const PROACTIVE_ALERTS = {
  weather: [
    {
      id: 1,
      title: 'Storm Warning - Bay of Biscay',
      message: 'Storm forecast may delay your vessel ETA by 36 hrs.',
      severity: 'high',
      timestamp: new Date().toISOString()
    },
    {
      id: 2,
      title: 'High Winds - English Channel',
      message: 'Gale force winds expected in next 24 hours.',
      severity: 'medium',
      timestamp: new Date().toISOString()
    }
  ],
  market: [
    {
      id: 3,
      title: 'Baltic Dry Index Up 5%',
      message: 'Consider fixing sooner - rates trending upward.',
      severity: 'medium',
      timestamp: new Date().toISOString()
    },
    {
      id: 4,
      title: 'Bunker Prices Stable',
      message: 'VLSFO prices remain steady across major ports.',
      severity: 'low',
      timestamp: new Date().toISOString()
    }
  ],
  vessel: [
    {
      id: 5,
      title: 'Vessel EVER GIVEN - Suez Canal',
      message: 'Approaching with 2-hour delay - monitor closely.',
      severity: 'low',
      timestamp: new Date().toISOString()
    }
  ]
};

function Dashboard({ onBackToLanding }) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentAgent, setCurrentAgent] = useState('Captain Router');
  const [systemStatus, setSystemStatus] = useState('operational');
  const [showDocumentUpload, setShowDocumentUpload] = useState(false);
  const [uploadedDocuments, setUploadedDocuments] = useState([]);
  const [conversationContext, setConversationContext] = useState({});
  const [showAlerts, setShowAlerts] = useState(false);
  const [showAgentSelector, setShowAgentSelector] = useState(false);
  const [selectedAgentId, setSelectedAgentId] = useState('general');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkSystemStatus();
    addWelcomeMessage();
    console.log('Dashboard component mounted - checking for changes');
    console.log('AGENTS array:', AGENTS);
    console.log('Current selected agent:', selectedAgentId);
    console.log('Current agent:', currentAgent);
  }, []);

  const checkSystemStatus = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      setSystemStatus(data.status);
    } catch (error) {
      setSystemStatus('error');
      console.error('System status check failed:', error);
    }
  };

  const addWelcomeMessage = () => {
    const welcomeMessage = {
      id: Date.now(),
      text: "🚢 Welcome to IME Hub Maritime AI Assistant! I'm your intelligent maritime operations companion.\n\n" +
            "**New Features Available:**\n" +
            "• 📄 **Document Upload & Analysis** - Upload voyage documents for AI analysis\n" +
            "• 🧠 **Context-Aware Chat** - I remember our conversation and can answer follow-ups\n" +
            "• 🔔 **Proactive Alerts** - Real-time notifications for weather, market, and vessel updates\n" +
            "• 📊 **Advanced Analytics** - TCE calculations, fuel optimization, and cost analysis\n\n" +
            "**Try asking:**\n" +
            "• \"Plan a voyage for a Panamax from Santos to Qingdao with 15-day laycan, compare via Suez vs Cape\"\n" +
            "• \"Analyze the uploaded charter party for laytime clauses\"\n" +
            "• \"What are the current bunker costs at VLSFO prices?\"",
      sender: 'agent',
      agent: 'Captain Router',
      data: { type: 'welcome', capabilities: AGENTS.map(a => a.name) },
      timestamp: new Date().toISOString()
    };
    setMessages([welcomeMessage]);
  };

  const sendMessage = async (message, useContext = true) => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: message,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const requestBody = {
        message: message,
        user_id: 'default',
        use_context: useContext,
        timestamp: new Date().toISOString(),
        conversation_context: conversationContext,
        uploaded_documents: uploadedDocuments.map(doc => ({
          name: doc.name,
          type: doc.type,
          content: doc.content
        }))
      };

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        const agentMessage = {
          id: Date.now() + 1,
          text: typeof data.text === 'string' ? data.text : JSON.stringify(data.text || 'No response text'),
          sender: 'agent',
          agent: data.agent,
          data: data.data,
          intent: data.intent,
          confidence: data.confidence,
          entities: data.entities,
          timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, agentMessage]);
        setCurrentAgent(data.agent);

        if (data.conversation_context) {
          setConversationContext(prev => ({
            ...prev,
            ...data.conversation_context
          }));
        }
      } else {
        const errorMessage = {
          id: Date.now() + 1,
          text: typeof data.text === 'string' ? data.text : 'An error occurred. Please try again.',
          sender: 'agent',
          agent: 'Captain Router',
          data: data.data,
          timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        agent: 'Captain Router',
        data: { error: error.message },
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDocumentUpload = (documents) => {
    setUploadedDocuments(prev => [...prev, ...documents]);
    setShowDocumentUpload(false);
    
    const uploadMessage = {
      id: Date.now(),
      text: `📄 **Documents Uploaded Successfully!**\n\n` +
            `I've analyzed ${documents.length} document(s) and can now answer questions about:\n` +
            documents.map(doc => `• ${doc.name} (${doc.type})`).join('\n') + `\n\n` +
            `**Try asking:**\n` +
            "• \"What are the laytime clauses in the charter party?\"\n" +
            "• \"Analyze the voyage costs from the documents\"\n" +
            "• \"What are the key terms and conditions?\"",
      sender: 'agent',
      agent: 'Captain Router',
      data: { type: 'document_upload', documents: documents },
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, uploadMessage]);
  };

  const clearChat = () => {
    setMessages([]);
    setCurrentAgent('Captain Router');
    setConversationContext({});
    addWelcomeMessage();
  };

  const handleAgentSelect = (agentId) => {
    console.log('Agent selected:', agentId);
    setSelectedAgentId(agentId);
    const agent = AGENTS.find(a => a.id === agentId);
    setCurrentAgent(agent?.name || 'Captain Router');
    setShowAgentSelector(false);
    
    // Add agent switch message
    const switchMessage = {
      id: Date.now(),
      text: `🤖 **Switched to ${agent?.name}**\n\n${agent?.description}\n\n**Capabilities:**\n${agent?.capabilities.map(cap => `• ${cap}`).join('\n')}\n\nHow can I help you with ${agent?.name.toLowerCase()} tasks?`,
      sender: 'agent',
      agent: agent?.name || 'Captain Router',
      data: { type: 'agent_switch', agent: agent },
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, switchMessage]);
  };

  const getCurrentAgent = () => AGENTS.find(a => a.id === selectedAgentId) || AGENTS[0];

  return (
    <div className="dashboard-container">
      {/* Top Navigation Bar */}
      <nav className="dashboard-nav">
        <div className="nav-left">
          <button className="back-btn" onClick={onBackToLanding}>
            ← Back
          </button>
          <h1 className="nav-title">IME Hub Maritime AI</h1>
        </div>
        
        <div className="nav-center">
          <div className="agent-selector">
            <button 
              className="agent-selector-btn"
              onClick={() => setShowAgentSelector(!showAgentSelector)}
            >
              <span className="agent-avatar">{getCurrentAgent().avatar}</span>
              <span className="agent-name">{getCurrentAgent().name}</span>
              <span className="selector-arrow">▼</span>
            </button>
            
            {showAgentSelector && (
              <div className="agent-dropdown">
                {AGENTS.map(agent => (
                  <button
                    key={agent.id}
                    className={`agent-option ${selectedAgentId === agent.id ? 'selected' : ''}`}
                    onClick={() => handleAgentSelect(agent.id)}
                  >
                    <span className="agent-avatar">{agent.avatar}</span>
                    <div className="agent-info">
                      <span className="agent-name">{agent.name}</span>
                      <span className="agent-description">{agent.description}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        
        <div className="nav-right">
          <button 
            className="upload-btn"
            onClick={() => setShowDocumentUpload(true)}
          >
            📤 Upload Documents
          </button>
          
          <button className="alerts-btn" onClick={() => setShowAlerts(!showAlerts)}>
            🔔 Alerts {showAlerts ? '▼' : '▶'}
          </button>
          
          <div className="status-indicator">
            <span className={`status-dot ${systemStatus}`}></span>
            <span className="status-text">{systemStatus}</span>
          </div>
        </div>
      </nav>

      {/* Alerts Section */}
      {showAlerts && (
        <div className="alerts-section">
          <div className="alerts-header">
            <h3>Proactive Alerts & Notifications</h3>
          </div>
          <div className="alerts-grid">
            {Object.entries(PROACTIVE_ALERTS).map(([category, alerts]) => (
              <div key={category} className="alert-category">
                <h4 className={`category-title ${category}`}>
                  {category === 'weather' ? '🌪️ Weather' : 
                   category === 'market' ? '📈 Market' : '🚢 Vessel'}
                </h4>
                <div className="alerts-list">
                  {alerts.map(alert => (
                    <div key={alert.id} className={`alert-item ${alert.severity}`}>
                      <div className="alert-content">
                        <h5>{alert.title}</h5>
                        <p>{alert.message}</p>
                      </div>
                      <span className={`severity-badge ${alert.severity}`}>
                        {alert.severity}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="chat-area">
        <div className="chat-header">
          <div className="chat-info">
            <h2>Chat with {getCurrentAgent().name}</h2>
            <p>{getCurrentAgent().description}</p>
          </div>
          
          <div className="chat-actions">
            <button className="clear-chat-btn" onClick={clearChat}>
              🗑️ Clear Chat
            </button>
            {uploadedDocuments.length > 0 && (
              <div className="documents-info">
                📋 {uploadedDocuments.length} Document{uploadedDocuments.length !== 1 ? 's' : ''} Available
              </div>
            )}
          </div>
        </div>
        
        <ChatWindow
          messages={messages}
          onSendMessage={sendMessage}
          isLoading={isLoading}
          currentAgent={currentAgent}
          systemStatus={systemStatus}
          conversationContext={conversationContext}
          uploadedDocuments={uploadedDocuments}
        />
      </div>

      {/* Document Upload Modal */}
      {showDocumentUpload && (
        <div className="modal-overlay" onClick={() => setShowDocumentUpload(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <DocumentUpload
              onUpload={handleDocumentUpload}
              onClose={() => setShowDocumentUpload(false)}
            />
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}

export default Dashboard; 