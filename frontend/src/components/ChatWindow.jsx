import React, { useState, useRef, useEffect } from 'react';
import './ChatWindow.css';

const ChatWindow = ({ messages, onSendMessage, isLoading, currentAgent, systemStatus, conversationContext, uploadedDocuments }) => {
  const [inputMessage, setInputMessage] = useState('');
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputMessage.trim() && !isLoading) {
      onSendMessage(inputMessage);
      setInputMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const renderMessage = (message) => {
    const isUser = message.sender === 'user';
    
    return (
      <div key={message.id} className={`message-container ${isUser ? 'user-message' : 'agent-message'}`}>
        <div className="message-avatar">
          {isUser ? '👤' : '🤖'}
        </div>
        <div className="message-content">
          <div className="message-header">
            <span className="message-sender">
              {isUser ? 'You' : message.agent || 'AI Assistant'}
            </span>
            <span className="message-time">
              {formatTimestamp(message.timestamp)}
            </span>
          </div>
          <div className="message-text">
            {typeof message.text === 'string'
              ? message.text
              : typeof message.text === 'object'
                ? JSON.stringify(message.text, null, 2)
                : String(message.text || '')
            }
          </div>
          
          {/* Show confidence and intent if available */}
          {message.confidence && (
            <div className="message-meta">
              <span className={`confidence-badge ${getConfidenceClass(message.confidence)}`}>
                Confidence: {(message.confidence * 100).toFixed(1)}%
              </span>
            </div>
          )}
          
          {message.intent && (
            <div className="message-meta">
              <span className={`intent-badge ${getIntentClass(message.confidence)}`}>
                Intent: {message.intent}
              </span>
            </div>
          )}
        </div>
      </div>
    );
  };

  const getConfidenceClass = (confidence) => {
    if (confidence >= 0.8) return 'confidence-high';
    if (confidence >= 0.6) return 'confidence-medium';
    return 'confidence-low';
  };

  const getIntentClass = (confidence) => {
    if (confidence >= 0.8) return 'intent-high';
    if (confidence >= 0.6) return 'intent-medium';
    return 'intent-low';
  };

  return (
    <div className="chat-window">
      {/* Messages Area */}
      <div className="messages-area">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🚢</div>
            <h3>Welcome to IME Hub Maritime AI</h3>
            <p>Start a conversation to get maritime insights and assistance.</p>
          </div>
        ) : (
          messages.map(renderMessage)
        )}
        
        {isLoading && (
          <div className="message-container agent-message">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="message-header">
                <span className="message-sender">{currentAgent || 'AI Assistant'}</span>
              </div>
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

      {/* Input Area */}
      <div className="input-area">
        <form onSubmit={handleSubmit} className="input-form">
          <div className="input-container">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about maritime operations, voyage planning, cargo matching, market insights, port intelligence, or PDA management..."
              className="message-input"
              rows={1}
              disabled={isLoading}
            />
            <button
              type="submit"
              className="send-button"
              disabled={!inputMessage.trim() || isLoading}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
          
          <div className="input-footer">
            <span className="input-hint">
              Press Enter to send, Shift+Enter for new line
            </span>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatWindow; 