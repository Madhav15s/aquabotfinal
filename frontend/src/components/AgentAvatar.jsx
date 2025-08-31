import React from 'react';
import './AgentAvatar.css';

const AgentAvatar = ({ agent, isActive, onClick }) => {
  const handleClick = () => {
    onClick();
  };

  return (
    <div 
      className={`agent-avatar ${isActive ? 'active' : ''}`}
      onClick={handleClick}
      style={{ borderColor: isActive ? agent.color : 'transparent' }}
    >
      <span className="agent-avatar-icon">{agent.avatar}</span>
      <div className="agent-avatar-name">{agent.name}</div>
      <div className="agent-avatar-description">{agent.description}</div>
      
      {agent.capabilities && (
        <div className="agent-avatar-capabilities">
          {agent.capabilities.slice(0, 3).map((capability, index) => (
            <span key={index}>{capability}</span>
          ))}
          {agent.capabilities.length > 3 && (
            <span>+{agent.capabilities.length - 3} more</span>
          )}
        </div>
      )}
    </div>
  );
};

export default AgentAvatar; 