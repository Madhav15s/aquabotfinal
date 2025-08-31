import logging
from typing import Dict, Any, Tuple
from nlp import classify_intent, extract_entities

class GeneralAgent:
    def __init__(self):
        self.name = "General Agent (Captain Router)"
        self.capabilities = [
            "Intent Classification & Routing",
            "General Maritime Queries",
            "AIS Vessel Tracking",
            "System Information",
            "Agent Coordination"
        ]
        self.conversation_context = []
        
    def is_operational(self) -> bool:
        return True
        
    async def classify_intent(self, message: str) -> Tuple[str, float]:
        """Classify user intent and return confidence score"""
        try:
            intent, confidence = classify_intent(message)
            
            # Boost confidence for AIS-related queries
            if any(keyword in message.lower() for keyword in ['ais', 'vessel', 'track', 'ship', 'location']):
                confidence = min(0.95, confidence + 0.2)
                
            return intent, confidence
        except Exception as e:
            logging.error(f"Intent classification error: {e}")
            return "general", 0.5
            
    async def process_request(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user request and return response"""
        try:
            # Extract entities
            entities = extract_entities(message)
            
            # Handle AIS-specific queries
            if any(keyword in message.lower() for keyword in ['ais', 'vessel', 'track', 'ship', 'location']):
                return await self._handle_ais_query(message, entities)
            
            # Handle general queries
            return await self._handle_general_query(message, entities, context)
            
        except Exception as e:
            logging.error(f"Request processing error: {e}")
            return {
                "data": {"error": str(e)},
                "text": "I encountered an error processing your request. Please try again."
            }
    
    async def _handle_ais_query(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AIS vessel tracking queries"""
        return {
            "data": {
                "query_type": "ais_tracking",
                "entities": entities,
                "message": message
            },
            "text": f"I can help you with AIS vessel tracking! I detected entities: {entities}. For specific vessel tracking, please provide the vessel name or MMSI number."
        }
    
    async def _handle_general_query(self, message: str, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general maritime queries"""
        # Store context for follow-up questions
        if context:
            self.conversation_context.append(context)
        
        return {
            "data": {
                "query_type": "general",
                "entities": entities,
                "context": self.conversation_context[-3:] if self.conversation_context else [],
                "message": message
            },
            "text": f"I'm your Maritime AI Assistant! I can help with voyage planning, cargo matching, market insights, port intelligence, and PDA management. What would you like to know about?"
        } 