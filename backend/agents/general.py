import logging
from typing import Dict, Any
from nlp import IntentClassifier

logger = logging.getLogger(__name__)

class GeneralAgent:
    """General agent for handling fallback queries and clarifications."""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.capabilities = [
            "Voyage Planning & Optimization",
            "Cargo & Tonnage Matching", 
            "Market & Commercial Insights",
            "Port & Cargo Intelligence",
            "PDA & Cost Management"
        ]
    
    def process(self, message: str) -> Dict[str, Any]:
        """Process user message and provide appropriate response."""
        try:
            # Try to classify intent for better routing
            intent, confidence = self.intent_classifier.classify_intent(message)
            
            # If we can identify a specific intent with high confidence, suggest routing
            if confidence > 0.6 and intent != "general":
                return self._suggest_agent(message, intent, confidence)
            
            # Handle general queries
            return self._handle_general_query(message)
            
        except Exception as e:
            logger.error(f"Error in general agent: {e}")
            return self._error_response(str(e))
    
    def _suggest_agent(self, message: str, intent: str, confidence: float) -> Dict[str, Any]:
        """Suggest routing to a specific agent."""
        agent_names = {
            "voyage_planning": "Voyage Planner",
            "cargo_matching": "Cargo Matcher", 
            "market_insights": "Market Insights",
            "port_intelligence": "Port Intelligence",
            "pda_management": "PDA Management"
        }
        
        agent_name = agent_names.get(intent, "Specialized Agent")
        
        return {
            "agent": "General",
            "status": "success",
            "data": {
                "suggested_agent": agent_name,
                "intent": intent,
                "confidence": confidence,
                "message": message
            },
            "text": f"I understand you're asking about {intent.replace('_', ' ')}. Let me connect you with our {agent_name} for a more detailed response. You can also rephrase your question to get a direct response from that agent."
        }
    
    def _handle_general_query(self, message: str) -> Dict[str, Any]:
        """Handle general maritime queries."""
        message_lower = message.lower()
        
        # Help and capabilities
        if any(word in message_lower for word in ["help", "what can you do", "capabilities", "features"]):
            return {
                "agent": "General",
                "status": "success",
                "data": {
                    "capabilities": self.capabilities,
                    "message": message
                },
                "text": f"I'm your Maritime AI Assistant! I can help you with: {', '.join(self.capabilities)}. Just ask me about voyage planning, cargo matching, market insights, port information, or PDA management. What would you like to know?"
            }
        
        # Greetings
        elif any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            return {
                "agent": "General",
                "status": "success",
                "data": {
                    "greeting": True,
                    "message": message
                },
                "text": "Hello! I'm your Maritime AI Assistant, ready to help with all your maritime operations. How can I assist you today?"
            }
        
        # Maritime general knowledge
        elif any(word in message_lower for word in ["maritime", "shipping", "vessel", "port", "cargo"]):
            return {
                "agent": "General",
                "status": "success",
                "data": {
                    "topic": "maritime_general",
                    "message": message
                },
                "text": "I'm here to help with all aspects of maritime operations! I can assist with voyage planning, cargo optimization, market analysis, port intelligence, and cost management. What specific area would you like to explore?"
            }
        
        # Weather and conditions
        elif any(word in message_lower for word in ["weather", "storm", "sea conditions", "wave", "wind"]):
            return {
                "agent": "General",
                "status": "success",
                "data": {
                    "topic": "weather_conditions",
                    "message": message
                },
                "text": "I can help you with weather information and sea conditions for voyage planning. Please specify the coordinates or route you're interested in, and I'll connect you with our Voyage Planner for detailed weather analysis."
            }
        
        # Costs and economics
        elif any(word in message_lower for word in ["cost", "price", "fuel", "bunker", "expense", "budget"]):
            return {
                "agent": "General",
                "status": "success",
                "data": {
                    "topic": "costs_economics",
                    "message": message
                },
                "text": "I can help you with cost analysis, fuel prices, and budget planning. For detailed cost breakdowns, let me connect you with our PDA Management agent, or ask about specific costs like bunker prices or port fees."
            }
        
        # Default response
        else:
            return {
                "agent": "General",
                "status": "success",
                "data": {
                    "topic": "general",
                    "message": message,
                    "capabilities": self.capabilities
                },
                "text": "I'm here to help with maritime operations! I can assist with voyage planning, cargo matching, market insights, port intelligence, and cost management. Please let me know what specific information you need, or ask for help to see all my capabilities."
            }
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Return error response."""
        return {
            "agent": "General",
            "status": "error",
            "data": {"error": error},
            "text": "I encountered an error processing your request. Please try again or ask for help to see what I can do."
        } 