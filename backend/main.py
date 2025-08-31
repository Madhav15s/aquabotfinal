from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import os

# Import agents
from agents.general import GeneralAgent
from agents.voyage_planner import VoyagePlannerAgent
from agents.cargo_matching import CargoMatchingAgent
from agents.market_insights import MarketInsightsAgent
from agents.port_intelligence import PortIntelligenceAgent
from agents.pda_management import PDAManagementAgent

# Import API wrappers
from apis.weather_api import WeatherAPI
from apis.ais_csv_manager import AISCSVManager
from apis.llm_api import LLMAPI

app = FastAPI(title="IME Hub Maritime AI Assistant", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
general_agent = GeneralAgent()
voyage_planner = VoyagePlannerAgent()
cargo_matcher = CargoMatchingAgent()
market_insights = MarketInsightsAgent()
port_intelligence = PortIntelligenceAgent()
pda_management = PDAManagementAgent()

# Initialize API wrappers
weather_api = WeatherAPI()
ais_manager = AISCSVManager()
llm_api = LLMAPI()

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    agent: str
    status: str
    data: Dict[str, Any]
    text: str

@app.get("/")
async def root():
    return {"message": "IME Hub Maritime AI Assistant API"}

@app.get("/api/status")
async def get_status():
    return {
        "status": "operational",
        "agents": {
            "general": general_agent.is_operational(),
            "voyage_planner": voyage_planner.is_operational(),
            "cargo_matcher": cargo_matcher.is_operational(),
            "market_insights": market_insights.is_operational(),
            "port_intelligence": port_intelligence.is_operational(),
            "pda_management": pda_management.is_operational()
        },
        "apis": {
            "weather": weather_api.is_operational(),
            "ais": ais_manager.is_operational(),
            "llm": llm_api.is_operational()
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Use general agent to classify intent and route
        intent, confidence = await general_agent.classify_intent(request.message)
        
        # Route to appropriate agent based on intent
        if intent == "voyage_planning" and confidence > 0.7:
            agent = voyage_planner
        elif intent == "cargo_matching" and confidence > 0.7:
            agent = cargo_matcher
        elif intent == "market_insights" and confidence > 0.7:
            agent = market_insights
        elif intent == "port_intelligence" and confidence > 0.7:
            agent = port_intelligence
        elif intent == "pda_management" and confidence > 0.7:
            agent = pda_management
        else:
            agent = general_agent
        
        # Process request with selected agent
        response = await agent.process_request(request.message, request.context)
        
        return ChatResponse(
            agent=agent.name,
            status="success",
            data=response.get("data", {}),
            text=response.get("text", "Request processed successfully")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 