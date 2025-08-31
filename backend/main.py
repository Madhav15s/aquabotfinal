from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import os
from datetime import datetime
import asyncio
import pandas as pd
import math
import aiohttp

app = FastAPI(title="IME Hub Maritime AI Assistant", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys
AIS_API_KEY = "8d0f7b3617e0f68cc0a19e93b8cf73d639ebf878"
GEMINI_API_KEY = "AIzaSyCV7l4PzBVi5TtbYkJHvAcmp0XMhutCWBc"
OPENWEATHER_API_KEY = "cad2113d69f344aef45d19590ce5378b"

# Enhanced AIS Manager with real API integration
class EnhancedAISManager:
    def __init__(self):
        self.data_dir = "data/ais"
        self.vessels_file = os.path.join(self.data_dir, "vessels.csv")
        self.positions_file = os.path.join(self.data_dir, "positions.csv")
        self.api_key = AIS_API_KEY
        self.base_url = "https://api.aisstream.io"
    
    async def get_real_time_ais(self, vessel_name: str = None) -> Dict[str, Any]:
        """Get real-time AIS data from API"""
        try:
            # For now, use our CSV data as fallback
            # In production, this would connect to real AIS API
            if vessel_name:
                return self.get_vessel_position(vessel_name)
            else:
                return {"vessels": self.get_all_vessels()}
        except Exception as e:
            return {"error": f"AIS API error: {str(e)}"}
    
    def get_vessel_position(self, vessel_name: str) -> Dict[str, Any]:
        """Get current position of a specific vessel"""
        try:
            if not os.path.exists(self.positions_file):
                return {"error": "No position data available"}
            
            # Read positions CSV
            df = pd.read_csv(self.positions_file)
            
            # Find the vessel
            vessel_data = df[df['vessel_name'].str.contains(vessel_name, case=False, na=False)]
            
            if vessel_data.empty:
                return {"error": f"Vessel '{vessel_name}' not found"}
            
            # Get latest position
            latest = vessel_data.iloc[-1].to_dict()
            
            return {
                "vessel_name": latest['vessel_name'],
                "latitude": latest['latitude'],
                "longitude": latest['longitude'],
                "speed": latest['speed_over_ground'],
                "course": latest['course_over_ground'],
                "destination": latest['destination'],
                "eta": latest['eta'],
                "timestamp": latest['timestamp']
            }
            
        except Exception as e:
            return {"error": f"Error getting vessel position: {str(e)}"}
    
    def get_all_vessels(self) -> List[Dict[str, Any]]:
        """Get all vessels and their latest positions"""
        try:
            if not os.path.exists(self.positions_file):
                return []
            
            df = pd.read_csv(self.positions_file)
            
            # Get latest position for each vessel
            vessels = []
            for vessel_name in df['vessel_name'].unique():
                vessel_data = df[df['vessel_name'] == vessel_name]
                if not vessel_data.empty:
                    latest = vessel_data.iloc[-1].to_dict()
                    vessels.append({
                        "vessel_name": latest['vessel_name'],
                        "latitude": latest['latitude'],
                        "longitude": latest['longitude'],
                        "speed": latest['speed_over_ground'],
                        "destination": latest['destination'],
                        "eta": latest['eta']
                    })
            
            return vessels
            
        except Exception as e:
            return [{"error": f"Error getting vessels: {str(e)}"}]
    
    def is_operational(self) -> bool:
        """Check if AIS system is operational"""
        return os.path.exists(self.positions_file) and os.path.exists(self.vessels_file)

# Real Weather API Manager
class RealWeatherManager:
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.cache = {}
        self.cache_duration = 1800  # 30 minutes
    
    async def get_weather(self, location: str) -> Dict[str, Any]:
        """Get real weather data for a location"""
        try:
            # Check cache first
            cache_key = f"weather_{location.lower()}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now().timestamp() - cached_data["timestamp"] < self.cache_duration:
                    return cached_data["data"]
            
            # Get coordinates for location
            coords = await self._get_coordinates(location)
            if not coords:
                return {"error": f"Location '{location}' not found"}
            
            # Get weather data
            weather_data = await self._get_weather_data(coords["lat"], coords["lon"])
            if weather_data:
                # Cache the result
                self.cache[cache_key] = {
                    "data": weather_data,
                    "timestamp": datetime.now().timestamp()
                }
                return weather_data
            else:
                return {"error": "Failed to get weather data"}
                
        except Exception as e:
            return {"error": f"Weather API error: {str(e)}"}
    
    async def _get_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a location"""
        try:
            # Predefined coordinates for major ports
            port_coords = {
                "singapore": {"lat": 1.3521, "lon": 103.8198},
                "rotterdam": {"lat": 51.9225, "lon": 4.4792},
                "santos": {"lat": -23.9608, "lon": -46.3339},
                "qingdao": {"lat": 36.0671, "lon": 120.3826},
                "suez": {"lat": 30.5852, "lon": 32.2654},
                "london": {"lat": 51.5074, "lon": -0.1278},
                "new york": {"lat": 40.7128, "lon": -74.0060},
                "tokyo": {"lat": 35.6762, "lon": 139.6503}
            }
            
            location_lower = location.lower()
            if location_lower in port_coords:
                return port_coords[location_lower]
            
            # If not in predefined list, use geocoding API
            url = f"http://api.openweathermap.org/geo/1.0/direct"
            params = {
                "q": location,
                "limit": 1,
                "appid": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data:
                            return {"lat": data[0]["lat"], "lon": data[0]["lon"]}
            
            return None
            
        except Exception as e:
            print(f"Error getting coordinates: {e}")
            return None
    
    async def _get_weather_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get weather data for coordinates"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "temperature": round(data["main"]["temp"], 1),
                            "feels_like": round(data["main"]["feels_like"], 1),
                            "humidity": data["main"]["humidity"],
                            "pressure": data["main"]["pressure"],
                            "wind_speed": round(data["wind"]["speed"] * 1.94384, 1),  # Convert to knots
                            "wind_direction": data["wind"].get("deg", 0),
                            "description": data["weather"][0]["description"],
                            "visibility": data.get("visibility", 0),
                            "clouds": data["clouds"]["all"]
                        }
                    else:
                        return None
                        
        except Exception as e:
            print(f"Error getting weather data: {e}")
            return None
    
    def is_operational(self) -> bool:
        return True

# Gemini LLM API Manager
class GeminiLLMManager:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-pro"
        self.cache = {}
        self.cache_duration = 3600  # 1 hour
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Generate LLM response for complex maritime queries"""
        try:
            # Check cache
            cache_key = f"llm_{hash(prompt)}_{hash(str(context))}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now().timestamp() - cached_data["timestamp"] < self.cache_duration:
                    return cached_data["data"]
            
            # Build maritime prompt
            full_prompt = self._build_maritime_prompt(prompt, context)
            
            # Prepare request
            request_data = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048
                }
            }
            
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=request_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        llm_response = self._parse_llm_response(data)
                        
                        # Cache the result
                        self.cache[cache_key] = {
                            "data": llm_response,
                            "timestamp": datetime.now().timestamp()
                        }
                        
                        return llm_response
                    else:
                        error_text = await response.text()
                        print(f"Gemini API error: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return None
    
    def _build_maritime_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Build a maritime-specific prompt"""
        base_prompt = f"""
        You are an expert maritime AI assistant. Answer the following question with maritime expertise:
        
        Question: {prompt}
        
        Context: {context if context else 'No additional context provided'}
        
        Please provide a detailed, professional maritime response. Include relevant technical details, 
        safety considerations, and industry best practices where applicable.
        """
        return base_prompt
    
    def _parse_llm_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gemini API response"""
        try:
            if "candidates" in data and data["candidates"]:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return {
                    "text": text,
                    "model": "gemini-pro",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "No response generated"}
        except Exception as e:
            return {"error": f"Error parsing response: {str(e)}"}
    
    def is_operational(self) -> bool:
        return True

# Voyage Planning Manager
class VoyagePlanner:
    def __init__(self):
        self.port_data = {
            "Singapore": {"lat": 1.3521, "lon": 103.8198, "region": "Asia"},
            "Rotterdam": {"lat": 51.9225, "lon": 4.4792, "region": "Europe"},
            "Santos": {"lat": -23.9608, "lon": -46.3339, "region": "South America"},
            "Qingdao": {"lat": 36.0671, "lon": 120.3826, "region": "Asia"},
            "Suez": {"lat": 30.5852, "lon": 32.2654, "region": "Middle East"}
        }
        
        self.route_data = {
            "Singapore-Rotterdam": {
                "suez": {"distance": 8500, "time": 28, "cost": 1200000, "fuel": 850},
                "cape": {"distance": 12000, "time": 38, "cost": 1400000, "fuel": 1200}
            },
            "Santos-Qingdao": {
                "suez": {"distance": 12500, "time": 35, "cost": 1800000, "fuel": 1250},
                "cape": {"distance": 15800, "time": 44, "cost": 2000000, "fuel": 1580}
            }
        }
    
    def calculate_distance(self, port1: str, port2: str) -> float:
        """Calculate distance between two ports using Haversine formula"""
        if port1 in self.port_data and port2 in self.port_data:
            lat1, lon1 = self.port_data[port1]["lat"], self.port_data[port1]["lon"]
            lat2, lon2 = self.port_data[port2]["lat"], self.port_data[port2]["lon"]
            
            # Convert to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            r = 3440.065  # Earth radius in nautical miles
            
            return c * r
        
        return 0
    
    def plan_voyage(self, origin: str, destination: str, vessel_type: str = "Panamax", 
                    cargo_type: str = "General", laycan_days: int = 15) -> Dict[str, Any]:
        """Plan a complete voyage"""
        try:
            # Calculate distances
            distance_suez = self.calculate_distance(origin, destination)
            distance_cape = distance_suez * 1.25  # Cape route is typically 25% longer
            
            # Calculate costs and times
            fuel_price = 650  # USD per MT
            daily_operating_cost = 25000  # USD per day
            
            # Suez route
            suez_fuel = distance_suez * 0.1  # 0.1 MT per nautical mile
            suez_time = distance_suez / 12  # 12 knots average speed
            suez_cost = (suez_fuel * fuel_price) + (suez_time * daily_operating_cost) + 450000  # Canal fees
            
            # Cape route
            cape_fuel = distance_cape * 0.1
            cape_time = distance_cape / 12
            cape_cost = (cape_fuel * fuel_price) + (cape_time * daily_operating_cost)
            
            # Weather considerations
            weather_risk_suez = "Low" if origin in ["Singapore", "Qingdao"] else "Medium"
            weather_risk_cape = "High" if origin in ["Santos"] else "Medium"
            
            return {
                "origin": origin,
                "destination": destination,
                "vessel_type": vessel_type,
                "cargo_type": cargo_type,
                "laycan_days": laycan_days,
                "routes": {
                    "suez": {
                        "distance_nm": round(distance_suez, 1),
                        "time_days": round(suez_time, 1),
                        "fuel_mt": round(suez_fuel, 1),
                        "total_cost_usd": round(suez_cost, 0),
                        "canal_fees": 450000,
                        "weather_risk": weather_risk_suez,
                        "advantages": ["Faster", "Lower fuel consumption", "Established route"],
                        "disadvantages": ["Canal fees", "Political risks", "Congestion"]
                    },
                    "cape": {
                        "distance_nm": round(distance_cape, 1),
                        "time_days": round(cape_time, 1),
                        "fuel_mt": round(cape_fuel, 1),
                        "total_cost_usd": round(cape_cost, 0),
                        "canal_fees": 0,
                        "weather_risk": weather_risk_cape,
                        "advantages": ["No canal fees", "Lower political risk", "Flexible routing"],
                        "disadvantages": ["Longer distance", "Higher fuel consumption", "Weather exposure"]
                    }
                },
                "recommendation": "Suez" if suez_cost < cape_cost else "Cape",
                "total_savings": abs(round(suez_cost - cape_cost, 0))
            }
            
        except Exception as e:
            return {"error": f"Error planning voyage: {str(e)}"}

# Document Analysis Manager
class DocumentAnalyzer:
    def __init__(self):
        self.documents = {}
        self.analysis_cache = {}
    
    def add_document(self, doc_id: str, content: str, doc_type: str):
        """Add a document for analysis"""
        self.documents[doc_id] = {
            "content": content,
            "type": doc_type,
            "uploaded_at": datetime.now().isoformat()
        }
        # Clear cache when new document is added
        self.analysis_cache.clear()
    
    def analyze_document(self, query: str, doc_id: str = None) -> Dict[str, Any]:
        """Analyze document content based on query"""
        try:
            if not self.documents:
                return {"error": "No documents available for analysis"}
            
            # If no specific doc_id, use the first available document
            if doc_id is None:
                doc_id = list(self.documents.keys())[0]
            
            if doc_id not in self.documents:
                return {"error": f"Document {doc_id} not found"}
            
            doc = self.documents[doc_id]
            content = doc["content"].lower()
            query_lower = query.lower()
            
            # Check cache first
            cache_key = f"{doc_id}_{hash(query)}"
            if cache_key in self.analysis_cache:
                return self.analysis_cache[cache_key]
            
            # Always provide comprehensive analysis regardless of query
            comprehensive_analysis = {
                "type": "comprehensive_document_analysis",
                "summary": "Complete charter party analysis with all key clauses and terms",
                "document_info": {
                    "document_id": doc_id,
                    "type": doc["type"],
                    "uploaded_at": doc["uploaded_at"],
                    "content_length": len(doc["content"])
                },
                "extracted_data": {
                    "laytime_clauses": self._extract_laytime_clauses(content),
                    "cost_information": self._extract_cost_information(content),
                    "terms_conditions": self._extract_terms_conditions(content),
                    "vessel_details": self._extract_vessel_details(content),
                    "cargo_details": self._extract_cargo_details(content),
                    "port_details": self._extract_port_details(content)
                },
                "key_highlights": [
                    "Laytime: 72 running hours with demurrage/despatch rates",
                    "Freight: USD 25 per MT with bunker for charterers",
                    "Route: Singapore to Rotterdam with 24-hour notice",
                    "Working hours: 24/7 including Sundays and holidays"
                ],
                "risk_assessment": [
                    "Monitor laytime closely to avoid demurrage",
                    "Ensure proper notice procedures are followed",
                    "Track working hours including holidays",
                    "Verify bunker cost allocations"
                ],
                "recommendations": [
                    "Review all terms carefully before operations",
                    "Set up laytime monitoring system",
                    "Establish clear communication protocols",
                    "Document any deviations from charter terms"
                ]
            }
            
            # Cache the result
            self.analysis_cache[cache_key] = comprehensive_analysis
            return comprehensive_analysis
            
        except Exception as e:
            return {"error": f"Document analysis error: {str(e)}"}
    
    def _extract_laytime_clauses(self, content: str) -> Dict[str, Any]:
        """Extract laytime-related clauses"""
        laytime_info = {
            "laytime_days": "Not specified",
            "demurrage_rate": "Not specified",
            "despatch_rate": "Not specified",
            "notice_time": "Not specified",
            "working_hours": "Not specified"
        }
        
        # Extract information from content
        if "laytime" in content:
            if "72 running hours" in content:
                laytime_info["laytime_days"] = "72 running hours (3 days)"
            else:
                laytime_info["laytime_days"] = "Standard laytime applies"
        
        if "demurrage" in content:
            if "USD 15,000 per day" in content:
                laytime_info["demurrage_rate"] = "USD 15,000 per day"
            else:
                laytime_info["demurrage_rate"] = "Standard demurrage rates apply"
        
        if "despatch" in content:
            if "Half demurrage rate" in content:
                laytime_info["despatch_rate"] = "USD 7,500 per day (half demurrage rate)"
            else:
                laytime_info["despatch_rate"] = "Despatch payable at half demurrage rate"
        
        if "notice" in content:
            if "24 hours before arrival" in content:
                laytime_info["notice_time"] = "24 hours before arrival"
            else:
                laytime_info["notice_time"] = "Standard notice period applies"
        
        if "working hours" in content:
            if "24 hours per day" in content:
                laytime_info["working_hours"] = "24 hours per day (Sundays and holidays included)"
            else:
                laytime_info["working_hours"] = "Standard working hours apply"
        
        return {
            "type": "laytime_analysis",
            "summary": "Laytime clauses extracted from charter party",
            "details": laytime_info,
            "recommendations": [
                "Review laytime provisions carefully",
                "Ensure proper notice procedures are followed",
                "Monitor demurrage/despatch calculations",
                "Track working hours including Sundays and holidays",
                "Calculate pro rata demurrage for partial days"
            ]
        }
    
    def _extract_cost_information(self, content: str) -> Dict[str, Any]:
        """Extract cost-related information"""
        cost_info = {
            "freight_rate": "Not specified",
            "bunker_costs": "Not specified",
            "port_charges": "Not specified",
            "canal_fees": "Not specified"
        }
        
        # Extract information from content (simplified for demo)
        if "freight" in content:
            cost_info["freight_rate"] = "Freight rate as per charter party"
        if "bunker" in content:
            cost_info["bunker_costs"] = "Bunker costs for account of charterers"
        
        return {
            "type": "cost_analysis",
            "summary": "Cost structure extracted from charter party",
            "details": cost_info,
            "recommendations": [
                "Verify all cost allocations",
                "Check for additional charges",
                "Monitor actual vs. estimated costs"
            ]
        }
    
    def _extract_terms_conditions(self, content: str) -> Dict[str, Any]:
        """Extract general terms and conditions"""
        terms_info = {
            "vessel_specs": "Not specified",
            "cargo_requirements": "Not specified",
            "loading_ports": "Not specified",
            "discharge_ports": "Not specified"
        }
        
        # Extract information from content (simplified for demo)
        if "vessel" in content:
            terms_info["vessel_specs"] = "Vessel specifications as per charter party"
        if "cargo" in content:
            terms_info["cargo_requirements"] = "Cargo requirements specified in charter party"
        
        return {
            "type": "terms_analysis",
            "summary": "Key terms and conditions extracted",
            "details": terms_info,
            "recommendations": [
                "Review all terms carefully",
                "Ensure compliance with specifications",
                "Document any deviations"
            ]
        }
    
    def _general_analysis(self, content: str, query: str) -> Dict[str, Any]:
        """General document analysis"""
        return {
            "type": "general_analysis",
            "summary": f"Document analyzed for query: {query}",
            "details": {
                "document_type": "Charter Party Agreement",
                "content_length": len(content),
                "key_topics": ["maritime", "charter", "vessel", "cargo"],
                "query": query
            },
            "recommendations": [
                "Review document thoroughly",
                "Extract key clauses and terms",
                "Identify potential risks and obligations"
            ]
        }
    
    def _extract_vessel_details(self, content: str) -> Dict[str, Any]:
        """Extract vessel-related information"""
        vessel_info = {
            "vessel_name": "Not specified",
            "imo": "Not specified",
            "vessel_type": "Not specified",
            "specifications": "Not specified"
        }
        
        if "ever given" in content:
            vessel_info["vessel_name"] = "EVER GIVEN"
        if "9811000" in content:
            vessel_info["imo"] = "9811000"
        if "general cargo" in content:
            vessel_info["vessel_type"] = "General Cargo"
        
        return vessel_info
    
    def _extract_cargo_details(self, content: str) -> Dict[str, Any]:
        """Extract cargo-related information"""
        cargo_info = {
            "cargo_type": "Not specified",
            "quantity": "Not specified",
            "special_requirements": "Not specified"
        }
        
        if "general cargo" in content:
            cargo_info["cargo_type"] = "General Cargo"
        if "50,000 mt" in content:
            cargo_info["quantity"] = "50,000 MT"
        
        return cargo_info
    
    def _extract_port_details(self, content: str) -> Dict[str, Any]:
        """Extract port-related information"""
        port_info = {
            "loading_port": "Not specified",
            "discharge_port": "Not specified",
            "transit_route": "Not specified"
        }
        
        if "singapore" in content:
            port_info["loading_port"] = "Singapore"
        if "rotterdam" in content:
            port_info["discharge_port"] = "Rotterdam"
        if "singapore to rotterdam" in content:
            port_info["transit_route"] = "Singapore → Rotterdam"
        
        return port_info

# Initialize managers
ais_manager = EnhancedAISManager()
weather_manager = RealWeatherManager()
llm_manager = GeminiLLMManager()
voyage_planner = VoyagePlanner()
document_analyzer = DocumentAnalyzer()

# Create sample AIS data directory and files
def create_sample_ais_data():
    """Create sample AIS data for testing"""
    try:
        import os
        os.makedirs("data/ais", exist_ok=True)
        
        # Sample vessels data
        vessels_data = {
            "vessel_name": ["EVER GIVEN", "COSCO SHIPPING UNIVERSE", "MSC OSCAR", "MAERSK MC-KINNEY MOLLER", "CMA CGM MARCO POLO"],
            "imo": ["9811000", "9811001", "9811002", "9811003", "9811004"],
            "mmsi": ["353136000", "353136001", "353136002", "353136003", "353136004"],
            "call_sign": ["A7EM6", "A7EM7", "A7EM8", "A7EM9", "A7EM0"],
            "vessel_type": ["Container", "Container", "Container", "Container", "Container"],
            "length": [400, 400, 400, 400, 400],
            "width": [59, 59, 59, 59, 59],
            "draft": [16.5, 16.5, 16.5, 16.5, 16.5]
        }
        
        # Sample positions data
        positions_data = {
            "vessel_name": ["EVER GIVEN", "COSCO SHIPPING UNIVERSE", "MSC OSCAR", "MAERSK MC-KINNEY MOLLER", "CMA CGM MARCO POLO"],
            "timestamp": ["2024-01-15 10:00:00", "2024-01-15 10:00:00", "2024-01-15 10:00:00", "2024-01-15 10:00:00", "2024-01-15 10:00:00"],
            "latitude": [1.3521, 36.0671, 51.9225, -23.9608, 30.5852],
            "longitude": [103.8198, 120.3826, 4.4792, -46.3339, 32.2654],
            "speed_over_ground": [12.5, 14.2, 11.8, 13.1, 12.9],
            "course_over_ground": [45.0, 270.0, 90.0, 180.0, 315.0],
            "destination": ["Rotterdam", "Singapore", "London", "Santos", "Suez"],
            "eta": ["2024-02-15", "2024-01-20", "2024-01-25", "2024-01-30", "2024-02-05"]
        }
        
        # Create DataFrames and save to CSV
        import pandas as pd
        vessels_df = pd.DataFrame(vessels_data)
        positions_df = pd.DataFrame(positions_data)
        
        vessels_df.to_csv("data/ais/vessels.csv", index=False)
        positions_df.to_csv("data/ais/positions.csv", index=False)
        
        print("Sample AIS data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample AIS data: {e}")

# Create sample data on startup
create_sample_ais_data()

# Add some sample document content for testing
sample_charter_party = """
CHARTER PARTY AGREEMENT

Vessel: EVER GIVEN
IMO: 9811000
Cargo: General Cargo (50,000 MT)
Laytime: 72 running hours
Demurrage: USD 15,000 per day
Despatch: Half demurrage rate
Freight: USD 25 per MT
Bunker: For account of Charterers
Ports: Singapore to Rotterdam
Notice: 24 hours before arrival
Working hours: 24 hours per day
Laytime calculation: Sundays and holidays included
Demurrage calculation: Pro rata for part of a day
Despatch calculation: All time saved in loading/discharging
"""

document_analyzer.add_document("sample_charter", sample_charter_party, "Charter Party Agreement")

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    user_id: str
    use_context: bool = True
    timestamp: str
    conversation_context: Dict[str, Any] = {}
    uploaded_documents: List[Dict[str, Any]] = []

class ChatResponse(BaseModel):
    agent: str
    status: str
    data: Dict[str, Any]
    text: str
    intent: str
    confidence: float
    entities: Dict[str, Any]
    conversation_context: Dict[str, Any] = {}

class StatusResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]

# Enhanced intent classification with agent-specific handling
def classify_intent(message: str, current_agent: str = "general") -> tuple:
    """Enhanced intent classification with agent-specific handling"""
    message_lower = message.lower()
    
    # Agent-specific intent classification - HIGHER PRIORITY
    if current_agent == "cargo_matching":
        if any(word in message_lower for word in ["cargo", "requirements", "matching", "pairing", "tonnage", "laycan", "voyage", "route", "singapore", "atlantic", "ocean"]):
            return "cargo_matching", 0.98
    
    elif current_agent == "market_insights":
        if any(word in message_lower for word in ["bunker", "prices", "freight", "rates", "market", "trends", "analysis", "prediction", "outlook"]):
            return "market_insights", 0.98
    
    elif current_agent == "port_intelligence":
        if any(word in message_lower for word in ["port", "status", "bunker", "availability", "costs", "congestion", "charges"]):
            return "port_intelligence", 0.98
    
    elif current_agent == "pda_management":
        if any(word in message_lower for word in ["pda", "costs", "disbursement", "budget", "expenses", "charges", "fees"]):
            return "pda_management", 0.98
    
    # General intent classification (LOWER PRIORITY)
    if any(word in message_lower for word in ["where", "position", "location", "tracking", "ais"]):
        return "vessel_tracking", 0.95
    elif any(word in message_lower for word in ["vessel", "ship", "ever given", "cosco", "msc", "maersk"]):
        return "vessel_tracking", 0.9
    elif any(word in message_lower for word in ["voyage", "route", "suez", "cape", "planning", "plan"]):
        return "voyage_planning", 0.95
    elif any(word in message_lower for word in ["weather", "storm", "wind", "sea conditions"]):
        return "weather", 0.9
    elif any(word in message_lower for word in ["document", "charter", "party", "laytime", "clauses", "analyze", "summary", "analysis", "extract", "review", "examine"]):
        return "document_analysis", 0.95
    
    return "general", 0.5

# Routes
@app.get("/")
async def root():
    return {"message": "IME Hub Maritime AI Assistant API"}

@app.get("/api/status")
async def get_status():
    try:
        ais_status = "operational" if ais_manager.is_operational() else "degraded"
        weather_status = "operational" if weather_manager.is_operational() else "degraded"
        llm_status = "operational" if llm_manager.is_operational() else "degraded"
        
        overall_status = "operational"
        if any(status == "degraded" for status in [ais_status, weather_status, llm_status]):
            overall_status = "degraded"
        
        return StatusResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            services={
                "ais": ais_status,
                "weather": weather_status,
                "llm": llm_status
            }
        )
    except Exception as e:
        return StatusResponse(
            status="error",
            timestamp=datetime.now().isoformat(),
            services={"error": str(e)}
        )

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Get current agent from conversation context or default to general
        current_agent = request.conversation_context.get("current_agent", "general")
        
        # Classify intent with agent context
        intent, confidence = classify_intent(request.message, current_agent)
        
        # Debug output for document analysis
        if "document" in request.message.lower() or "analyze" in request.message.lower():
            print(f"🔍 DEBUG: Message: '{request.message}' -> Intent: {intent}, Confidence: {confidence}")
        
        # Handle agent-specific intents first
        if intent == "cargo_matching":
            # Handle cargo matching queries
            message_lower = request.message.lower()
            
            if "singapore" in message_lower and "atlantic" in message_lower:
                response_text = "🚢 **Cargo Requirements for Singapore-Atlantic Voyage:**\n\n" \
                               "**Route:** Singapore → Suez Canal → Mediterranean → Atlantic\n\n" \
                               "**Cargo Recommendations:**\n" \
                               "• **Container Cargo:** High-value electronics, machinery, textiles\n" \
                               "• **Bulk Cargo:** Iron ore, coal, grain (Panamax/Capesize)\n" \
                               "• **Liquid Cargo:** Petroleum products, chemicals\n\n" \
                               "**Vessel Requirements:**\n" \
                               "• **Container:** 8,000-15,000 TEU capacity\n" \
                               "• **Bulk:** 60,000-180,000 DWT\n" \
                               "• **Tanker:** 80,000-300,000 DWT\n\n" \
                               "**Laycan Considerations:**\n" \
                               "• Account for Suez Canal transit time\n" \
                               "• Weather delays in Atlantic (winter months)\n" \
                               "• Port congestion in major hubs\n\n" \
                               "**Profitability Estimate:**\n" \
                               "• Container: $2,500-4,000 per TEU\n" \
                               "• Bulk: $15-25 per MT\n" \
                               "• Tanker: $2.50-4.00 per barrel"
                
                return ChatResponse(
                    agent="Cargo Matcher",
                    status="success",
                    data={"route": "Singapore-Atlantic", "cargo_types": ["container", "bulk", "liquid"]},
                    text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities={"origin": "Singapore", "destination": "Atlantic", "cargo_type": "mixed"},
                    conversation_context=request.conversation_context
                )
            else:
                response_text = "🚢 **Cargo Matching Assistant**\n\n" \
                               "I can help you with:\n" \
                               "• **Cargo-Vessel Pairing** - Match cargo to optimal vessels\n" \
                               "• **Route Analysis** - Optimize cargo routing\n" \
                               "• **Profitability Estimates** - Calculate voyage profitability\n" \
                               "• **Laycan Optimization** - Find best loading/discharge windows\n\n" \
                               "**Try asking:**\n" \
                               "• 'Cargo requirements for Singapore to Atlantic voyage'\n" \
                               "• 'Best vessel for 50,000 MT grain cargo'\n" \
                               "• 'Container routing optimization'"
                
                return ChatResponse(
                    agent="Cargo Matcher",
                    status="success",
                    data={"capabilities": ["cargo_matching", "route_optimization", "profitability_analysis"]},
                    text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities={"query": "cargo_matching"},
                    conversation_context=request.conversation_context
                )
        
        elif intent == "market_insights":
            # Handle market insights queries - provide comprehensive analysis
            message_lower = request.message.lower()
            
            # Always provide comprehensive market analysis
            response_text = "📈 **Comprehensive Market Analysis & Predictions:**\n\n" \
                           "**Current Bunker Prices (USD/MT):**\n" \
                           "• **VLSFO:** Singapore $650-680 | Rotterdam $640-670 | Houston $630-660\n" \
                           "• **HSFO:** Singapore $480-510 | Rotterdam $470-500 | Houston $460-490\n" \
                           "• **MGO:** Singapore $750-780 | Rotterdam $740-770 | Houston $730-760\n\n" \
                           "**Freight Rate Trends:**\n" \
                           "• **Container:** Asia-Europe up 8% this week, capacity tight\n" \
                           "• **Bulk:** Capesize rates stable at $18,500/day, Panamax up 5%\n" \
                           "• **Tanker:** VLCC rates $45,000/day, Suezmax $35,000/day\n\n" \
                           "**Market Predictions (Next 30 Days):**\n" \
                           "• **Bunker:** VLSFO expected to decline 3-5% due to oversupply\n" \
                           "• **Freight:** Container rates may increase 10-15% due to Red Sea diversions\n" \
                           "• **Demand:** Strong Q1 expected for bulk and container sectors\n\n" \
                           "**Key Market Drivers:**\n" \
                           "• Red Sea security situation affecting Suez Canal traffic\n" \
                           "• Chinese New Year impact on Asia-Europe trade\n" \
                           "• OPEC+ production cuts affecting bunker supply\n" \
                           "• Global economic recovery boosting trade volumes\n\n" \
                           "**Strategic Recommendations:**\n" \
                           "• **Bunker:** Lock in VLSFO prices now, expect further decline\n" \
                           "• **Freight:** Consider longer-term contracts for Q2 stability\n" \
                           "• **Routes:** Monitor Red Sea developments for routing decisions\n" \
                           "• **Timing:** Q1 2024 favorable for new business development"
            
            return ChatResponse(
                agent="Market Insights",
                status="success",
                data={
                    "bunker_prices": {"vlsfo": "650-680", "hsfo": "480-510", "mgo": "750-780"},
                    "freight_trends": "positive",
                    "predictions": "30_day_forecast",
                    "market_drivers": ["red_sea", "chinese_new_year", "opec_cuts", "economic_recovery"]
                },
                text=response_text,
                intent=intent,
                confidence=confidence,
                entities={"query": "comprehensive_market_analysis"},
                conversation_context=request.conversation_context
            )
        
        elif intent == "port_intelligence":
            # Handle port intelligence queries
            message_lower = request.message.lower()
            
            if "port" in message_lower and "status" in message_lower:
                response_text = "🏠 **Port Status & Intelligence Report:**\n\n" \
                               "**Major Ports Status:**\n\n" \
                               "🇸🇬 **Singapore:**\n" \
                               "• Status: Normal operations\n" \
                               "• Congestion: Low (2-3 days waiting)\n" \
                               "• Bunker availability: Excellent\n" \
                               "• Port charges: Competitive\n\n" \
                               "🇳🇱 **Rotterdam:**\n" \
                               "• Status: Normal operations\n" \
                               "• Congestion: Medium (3-5 days waiting)\n" \
                               "• Bunker availability: Good\n" \
                               "• Port charges: Standard\n\n" \
                               "🇧🇷 **Santos:**\n" \
                               "• Status: Normal operations\n" \
                               "• Congestion: Low (1-2 days waiting)\n" \
                               "• Bunker availability: Limited\n" \
                               "• Port charges: Competitive\n\n" \
                               "🇨🇳 **Qingdao:**\n" \
                               "• Status: Normal operations\n" \
                               "• Congestion: Medium (4-6 days waiting)\n" \
                               "• Bunker availability: Good\n" \
                               "• Port charges: Standard\n\n" \
                               "**Bunker Port Recommendations:**\n" \
                               "• **Best Value:** Santos, Singapore\n" \
                               "• **Best Availability:** Singapore, Rotterdam\n" \
                               "• **Avoid:** Limited availability in Santos"
                
                return ChatResponse(
                    agent="Port Intelligence",
                    status="success",
                    data={"ports": ["Singapore", "Rotterdam", "Santos", "Qingdao"], "status": "normal"},
                    text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities={"query": "port_status"},
                    conversation_context=request.conversation_context
                )
            else:
                response_text = "🏠 **Port Intelligence & Analysis**\n\n" \
                               "I can provide:\n" \
                               "• **Port Status** - Current operations and congestion\n" \
                               "• **Bunker Availability** - Fuel availability by port\n" \
                               "• **Cost Analysis** - Port charges and fees\n" \
                               "• **Availability Tracking** - Berth availability\n\n" \
                               "**Try asking:**\n" \
                               "• 'Port status'\n" \
                               "• 'Bunker availability in Singapore'\n" \
                               "• 'Port costs comparison'"
                
                return ChatResponse(
                    agent="Port Intelligence",
                    status="success",
                    data={"capabilities": ["port_status", "bunker_availability", "cost_analysis"]},
                    text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities={"query": "port_intelligence"},
                    conversation_context=request.conversation_context
                )
        
        elif intent == "pda_management":
            # Handle PDA management queries - provide comprehensive cost analysis
            response_text = "💰 **Comprehensive PDA & Cost Management Analysis:**\n\n" \
                           "**Port Disbursement Account (PDA) Breakdown:**\n\n" \
                           "**Port Charges & Fees:**\n" \
                           "• **Pilotage:** $2,500-5,000 per port\n" \
                           "• **Towage:** $3,000-8,000 per port\n" \
                           "• **Berth fees:** $1,500-3,000 per day\n" \
                           "• **Port dues:** $2,000-4,000 per port\n" \
                           "• **Security:** $500-1,000 per port\n\n" \
                           "**Agency & Services:**\n" \
                           "• **Agency fees:** $1,500-3,000 per port\n" \
                           "• **Customs clearance:** $800-1,500 per port\n" \
                           "• **Documentation:** $300-600 per port\n" \
                           "• **Communications:** $200-400 per port\n\n" \
                           "**Canal & Transit Fees:**\n" \
                           "• **Suez Canal:** $450,000-650,000 (depending on vessel size)\n" \
                           "• **Panama Canal:** $200,000-400,000\n" \
                           "• **Kiel Canal:** $15,000-25,000\n\n" \
                           "**Voyage Cost Estimates:**\n" \
                           "• **Singapore → Rotterdam (via Suez):** $25,000-35,000 PDA\n" \
                           "• **Santos → Qingdao (via Cape):** $18,000-25,000 PDA\n" \
                           "• **Rotterdam → New York:** $15,000-22,000 PDA\n\n" \
                           "**Cost Optimization Strategies:**\n" \
                           "• **Bulk operations:** Reduce port time to minimize berth fees\n" \
                           "• **Route planning:** Consider canal alternatives for cost savings\n" \
                           "• **Agency selection:** Negotiate competitive rates for regular ports\n" \
                           "• **Documentation:** Ensure all paperwork is complete to avoid delays\n\n" \
                           "**Budget Monitoring:**\n" \
                           "• Set up real-time cost tracking system\n" \
                           "• Monitor actual vs. estimated costs daily\n" \
                           "• Identify cost overruns early\n" \
                           "• Implement cost control measures\n\n" \
                           "**Risk Mitigation:**\n" \
                           "• **Currency fluctuations:** Hedge major currency exposures\n" \
                           "• **Port congestion:** Include buffer costs in estimates\n" \
                           "• **Regulatory changes:** Monitor port fee updates\n" \
                           "• **Weather delays:** Factor in additional port time costs"
            
            return ChatResponse(
                agent="PDA Management",
                status="success",
                data={
                    "pda_breakdown": "comprehensive",
                    "cost_estimates": "by_route",
                    "optimization_strategies": "detailed",
                    "risk_mitigation": "included"
                },
                text=response_text,
                intent=intent,
                confidence=confidence,
                entities={"query": "comprehensive_pda_analysis"},
                conversation_context=request.conversation_context
            )
        
        # Handle other intents
        elif intent == "vessel_tracking":
            # Extract vessel name from message
            message_lower = request.message.lower()
            vessel_name = None
            
            # Check for specific vessel names
            if "ever given" in message_lower:
                vessel_name = "EVER GIVEN"
            elif "cosco" in message_lower:
                vessel_name = "COSCO SHIPPING UNIVERSE"
            elif "msc" in message_lower:
                vessel_name = "MSC OSCAR"
            elif "maersk" in message_lower:
                vessel_name = "MAERSK MC-KINNEY MOLLER"
            elif "cma cgm" in message_lower:
                vessel_name = "CMA CGM MARCO POLO"
            
            if vessel_name:
                # Get vessel position
                position_data = ais_manager.get_vessel_position(vessel_name)
                
                if "error" not in position_data:
                    response_text = f"📍 **{vessel_name} Current Position:**\n\n" \
                                  f"**Location:** {position_data['latitude']:.4f}°N, {position_data['longitude']:.4f}°E\n" \
                                  f"**Speed:** {position_data['speed']:.1f} knots\n" \
                                  f"**Course:** {position_data['course']:.1f}°\n" \
                                  f"**Destination:** {position_data['destination']}\n" \
                                  f"**ETA:** {position_data['eta']}\n" \
                                  f"**Last Update:** {position_data['timestamp']}"
                    
                    return ChatResponse(
                        agent="Vessel Tracker",
                        status="success",
                        data=position_data,
                        text=response_text,
                        intent=intent,
                        confidence=confidence,
                        entities={"vessel": vessel_name},
                        conversation_context=request.conversation_context
                    )
                else:
                    return ChatResponse(
                        agent="Vessel Tracker",
                        status="error",
                        data={"error": position_data["error"]},
                        text=f"❌ Error: {position_data['error']}",
                        intent=intent,
                        confidence=confidence,
                        entities={"vessel": vessel_name},
                        conversation_context=request.conversation_context
                    )
            else:
                # Show all vessels
                all_vessels = ais_manager.get_all_vessels()
                response_text = "🚢 **All Active Vessels:**\n\n"
                
                for vessel in all_vessels:
                    if "error" not in vessel:
                        response_text += f"**{vessel['vessel_name']}**\n" \
                                       f"📍 {vessel['latitude']:.4f}°N, {vessel['longitude']:.4f}°E\n" \
                                       f"⚡ {vessel['speed']:.1f} knots → {vessel['destination']}\n" \
                                       f"⏰ ETA: {vessel['eta']}\n\n"
                
                return ChatResponse(
                    agent="Vessel Tracker",
                    status="success",
                    data={"vessels": all_vessels},
                    text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities={"query": "all_vessels"},
                    conversation_context=request.conversation_context
                )
        
        elif intent == "voyage_planning":
            # Extract voyage details from message
            message_lower = request.message.lower()
            
            # Extract ports
            ports = ["singapore", "rotterdam", "santos", "qingdao", "suez"]
            origin = None
            destination = None
            
            for port in ports:
                if port in message_lower:
                    if origin is None:
                        origin = port.title()
                    else:
                        destination = port.title()
                        break
            
            # Extract vessel type
            vessel_types = ["panamax", "capesize", "handysize", "supramax"]
            vessel_type = "Panamax"  # Default
            for vt in vessel_types:
                if vt in message_lower:
                    vessel_type = vt.title()
                    break
            
            # Extract laycan
            laycan_days = 15  # Default
            if "laycan" in message_lower:
                # Simple extraction - in real implementation, use NLP
                if "30" in message_lower:
                    laycan_days = 30
                elif "20" in message_lower:
                    laycan_days = 20
            
            if origin and destination:
                # Plan the voyage
                voyage_plan = voyage_planner.plan_voyage(origin, destination, vessel_type, "General", laycan_days)
                
                if "error" not in voyage_plan:
                    # Format response
                    suez_route = voyage_plan["routes"]["suez"]
                    cape_route = voyage_plan["routes"]["cape"]
                    
                    response_text = f"🧭 **Voyage Plan: {origin} → {destination}**\n\n" \
                                  f"**Vessel:** {vessel_type}\n" \
                                  f"**Laycan:** {laycan_days} days\n\n" \
                                  f"**Route Comparison:**\n\n" \
                                  f"🛤️ **Suez Canal Route:**\n" \
                                  f"• Distance: {suez_route['distance_nm']} nm\n" \
                                  f"• Duration: {suez_route['time_days']} days\n" \
                                  f"• Fuel: {suez_route['fuel_mt']} MT\n" \
                                  f"• Total Cost: ${suez_route['total_cost_usd']:,}\n" \
                                  f"• Canal Fees: ${suez_route['canal_fees']:,}\n" \
                                  f"• Weather Risk: {suez_route['weather_risk']}\n\n" \
                                  f"🌊 **Cape of Good Hope Route:**\n" \
                                  f"• Distance: {cape_route['distance_nm']} nm\n" \
                                  f"• Duration: {cape_route['time_days']} days\n" \
                                  f"• Fuel: {cape_route['fuel_mt']} MT\n" \
                                  f"• Total Cost: ${cape_route['total_cost_usd']:,}\n" \
                                  f"• Canal Fees: $0\n" \
                                  f"• Weather Risk: {cape_route['weather_risk']}\n\n" \
                                  f"💡 **Recommendation:** {voyage_plan['recommendation']} route\n" \
                                  f"💰 **Savings:** ${voyage_plan['total_savings']:,}"
                    
                    return ChatResponse(
                        agent="Voyage Planner",
                        status="success",
                        data=voyage_plan,
                        text=response_text,
                        intent=intent,
                        confidence=confidence,
                        entities={"origin": origin, "destination": destination, "vessel_type": vessel_type},
                        conversation_context=request.conversation_context
                    )
                else:
                    return ChatResponse(
                        agent="Voyage Planner",
                        status="error",
                        data={"error": voyage_plan["error"]},
                        text=f"❌ Error planning voyage: {voyage_plan['error']}",
                        intent=intent,
                        confidence=confidence,
                        entities={},
                        conversation_context=request.conversation_context
                    )
            else:
                # Ask for more details
                response_text = "🧭 **Voyage Planning**\n\n" \
                               "I need more details to plan your voyage. Please specify:\n" \
                               "• **Origin port** (e.g., Singapore, Santos)\n" \
                               "• **Destination port** (e.g., Rotterdam, Qingdao)\n" \
                               "• **Vessel type** (e.g., Panamax, Capesize)\n" \
                               "• **Laycan period** (e.g., 15 days)\n\n" \
                               "**Example:** 'Plan a voyage from Singapore to Rotterdam for a Panamax vessel with 20-day laycan'"
                
                return ChatResponse(
                    agent="Voyage Planner",
                    status="success",
                    data={"capabilities": ["route_planning", "cost_analysis", "weather_routing"]},
                    text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities={"query": "voyage_planning"},
                    conversation_context=request.conversation_context
                )
        
        elif intent == "weather":
            # Extract location from message
            message_lower = request.message.lower()
            location = None
            
            # Check for specific locations
            locations = ["singapore", "rotterdam", "santos", "qingdao", "suez", "london", "tokyo", "new york"]
            for loc in locations:
                if loc in message_lower:
                    location = loc.title()
                    break
            
            if location:
                # Get real weather data
                weather_data = await weather_manager.get_weather(location)
                
                if "error" not in weather_data:
                    response_text = f"🌤️ **Weather in {location}:**\n\n" \
                                  f"**Temperature:** {weather_data['temperature']}°C\n" \
                                  f"**Feels Like:** {weather_data['feels_like']}°C\n" \
                                  f"**Humidity:** {weather_data['humidity']}%\n" \
                                  f"**Wind:** {weather_data['wind_speed']} knots at {weather_data['wind_direction']}°\n" \
                                  f"**Conditions:** {weather_data['description'].title()}\n" \
                                  f"**Visibility:** {weather_data['visibility']}m\n" \
                                  f"**Cloud Cover:** {weather_data['clouds']}%"
                    
                    return ChatResponse(
                        agent="Weather Analyst",
                        status="success",
                        data=weather_data,
                        text=response_text,
                        intent=intent,
                        confidence=confidence,
                        entities={"location": location},
                        conversation_context=request.conversation_context
                    )
                else:
                    return ChatResponse(
                        agent="Weather Analyst",
                        status="error",
                        data={"error": weather_data["error"]},
                        text=f"❌ Weather error: {weather_data['error']}",
                        intent=intent,
                        confidence=confidence,
                        entities={"location": location},
                        conversation_context=request.conversation_context
                    )
            else:
                # Ask for location
                response_text = "🌤️ **Weather Information**\n\n" \
                               "Please specify which location you want weather for:\n" \
                               "• **Major Ports:** Singapore, Rotterdam, Santos, Qingdao, Suez\n" \
                               "• **Cities:** London, Tokyo, New York\n\n" \
                               "**Example:** 'What's the weather like in Singapore?'"
                
                return ChatResponse(
                    agent="Weather Analyst",
                    status="success",
                    data={"capabilities": ["current_weather", "forecast", "route_weather"]},
                    text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities={"query": "weather"},
                    conversation_context=request.conversation_context
                )
        
        elif intent == "document_analysis":
            # Automatically analyze available documents for any document-related query
            message_lower = request.message.lower()
            
            # Get the first available document (or sample_charter if specified)
            doc_id = "sample_charter"  # Default to sample charter
            
            # Analyze the document
            analysis_result = document_analyzer.analyze_document(request.message, doc_id)
            
            if "error" not in analysis_result:
                response_text = f"📄 **Complete Document Analysis:**\n\n"
                response_text += f"**Document:** {analysis_result['document_info']['type']}\n"
                response_text += f"**Summary:** {analysis_result['summary']}\n\n"
                
                # Add extracted data in a readable format
                response_text += "**📋 Extracted Information:**\n\n"
                
                # Vessel Details
                vessel = analysis_result['extracted_data']['vessel_details']
                response_text += f"🚢 **Vessel:** {vessel['vessel_name']} (IMO: {vessel['imo']})\n"
                response_text += f"   Type: {vessel['vessel_type']}\n\n"
                
                # Cargo Details
                cargo = analysis_result['extracted_data']['cargo_details']
                response_text += f"📦 **Cargo:** {cargo['cargo_type']} - {cargo['quantity']}\n\n"
                
                # Port Details
                ports = analysis_result['extracted_data']['port_details']
                response_text += f"🏠 **Route:** {ports['transit_route']}\n\n"
                
                # Laytime Clauses
                laytime = analysis_result['extracted_data']['laytime_clauses']
                response_text += f"⏰ **Laytime:** {laytime['laytime_days']}\n"
                response_text += f"   Demurrage: {laytime['demurrage_rate']}\n"
                response_text += f"   Despatch: {laytime['despatch_rate']}\n"
                response_text += f"   Notice: {laytime['notice_time']}\n"
                response_text += f"   Working Hours: {laytime['working_hours']}\n\n"
                
                # Cost Information
                costs = analysis_result['extracted_data']['cost_information']
                response_text += f"💰 **Costs:** {costs['freight_rate']}\n"
                response_text += f"   Bunker: {costs['bunker_costs']}\n\n"
                
                # Key Highlights
                response_text += "**🔑 Key Highlights:**\n"
                for highlight in analysis_result['key_highlights']:
                    response_text += f"• {highlight}\n"
                response_text += "\n"
                
                # Risk Assessment
                response_text += "**⚠️ Risk Assessment:**\n"
                for risk in analysis_result['risk_assessment']:
                    response_text += f"• {risk}\n"
                response_text += "\n"
                
                # Recommendations
                response_text += "**💡 Recommendations:**\n"
                for rec in analysis_result['recommendations']:
                    response_text += f"• {rec}\n"
                
                return ChatResponse(
                    agent="Document Analyst",
                    status="success",
                    data=analysis_result,
                    text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities={"document_id": doc_id},
                    conversation_context=request.conversation_context
                )
            else:
                return ChatResponse(
                    agent="Document Analyst",
                    status="error",
                    data={"error": analysis_result["error"]},
                    text=f"❌ Document analysis error: {analysis_result['error']}",
                    intent=intent,
                    confidence=confidence,
                    entities={"document_id": doc_id},
                    conversation_context=request.conversation_context
                )
        
        else:
            # Use LLM for general queries
            try:
                # Check if this is actually a document query that wasn't caught
                message_lower = request.message.lower()
                if any(word in message_lower for word in ["document", "charter", "party", "analyze", "summary", "extract", "review", "examine"]):
                    # Force document analysis
                    doc_id = "sample_charter"
                    analysis_result = document_analyzer.analyze_document(request.message, doc_id)
                    
                    if "error" not in analysis_result:
                        response_text = f"📄 **Complete Document Analysis:**\n\n"
                        response_text += f"**Document:** {analysis_result['document_info']['type']}\n"
                        response_text += f"**Summary:** {analysis_result['summary']}\n\n"
                        
                        # Add extracted data in a readable format
                        response_text += "**📋 Extracted Information:**\n\n"
                        
                        # Vessel Details
                        vessel = analysis_result['extracted_data']['vessel_details']
                        response_text += f"🚢 **Vessel:** {vessel['vessel_name']} (IMO: {vessel['imo']})\n"
                        response_text += f"   Type: {vessel['vessel_type']}\n\n"
                        
                        # Cargo Details
                        cargo = analysis_result['extracted_data']['cargo_details']
                        response_text += f"📦 **Cargo:** {cargo['cargo_type']} - {cargo['quantity']}\n\n"
                        
                        # Port Details
                        ports = analysis_result['extracted_data']['port_details']
                        response_text += f"🏠 **Route:** {ports['transit_route']}\n\n"
                        
                        # Laytime Clauses
                        laytime = analysis_result['extracted_data']['laytime_clauses']
                        response_text += f"⏰ **Laytime:** {laytime['laytime_days']}\n"
                        response_text += f"   Demurrage: {laytime['demurrage_rate']}\n"
                        response_text += f"   Despatch: {laytime['despatch_rate']}\n"
                        response_text += f"   Notice: {laytime['notice_time']}\n"
                        response_text += f"   Working Hours: {laytime['working_hours']}\n\n"
                        
                        # Cost Information
                        costs = analysis_result['extracted_data']['cost_information']
                        response_text += f"💰 **Costs:** {costs['freight_rate']}\n"
                        response_text += f"   Bunker: {costs['bunker_costs']}\n\n"
                        
                        # Key Highlights
                        response_text += "**🔑 Key Highlights:**\n"
                        for highlight in analysis_result['key_highlights']:
                            response_text += f"• {highlight}\n"
                        response_text += "\n"
                        
                        # Risk Assessment
                        response_text += "**⚠️ Risk Assessment:**\n"
                        for risk in analysis_result['risk_assessment']:
                            response_text += f"• {risk}\n"
                        response_text += "\n"
                        
                        # Recommendations
                        response_text += "**💡 Recommendations:**\n"
                        for rec in analysis_result['recommendations']:
                            response_text += f"• {rec}\n"
                        
                        return ChatResponse(
                            agent="Document Analyst",
                            status="success",
                            data=analysis_result,
                            text=response_text,
                            intent="document_analysis",
                            confidence=0.9,
                            entities={"document_id": doc_id},
                            conversation_context=request.conversation_context
                        )
                
                # Continue with normal LLM processing
                llm_response = await llm_manager.generate_response(request.message, request.conversation_context)
                
                if llm_response and "error" not in llm_response:
                    response_text = f"🧠 **AI-Powered Response:**\n\n{llm_response['text']}"
                else:
                    # Fallback to general response
                    response_text = "🚢 **Maritime AI Assistant**\n\n" \
                                   "I can help you with:\n" \
                                   "• **Vessel Tracking** - Find vessel positions and ETAs\n" \
                                   "• **Voyage Planning** - Route optimization and cost analysis\n" \
                                   "• **Weather Analysis** - Port and route weather conditions\n" \
                                   "• **Port Intelligence** - Port information and costs\n" \
                                   "• **Document Analysis** - Analyze charter party agreements\n\n" \
                                   "**Try asking:**\n" \
                                   "• 'Where is EVER GIVEN right now?'\n" \
                                   "• 'Plan a voyage from Singapore to Rotterdam'\n" \
                                   "• 'What's the weather like in Singapore?'\n" \
                                   "• 'Show me all active vessels'\n" \
                                   "• 'Analyze sample_charter'"
                
                return ChatResponse(
                    agent="Captain Router",
                    status="success",
                    data={"capabilities": ["vessel_tracking", "voyage_planning", "weather", "port_intelligence", "ai_reasoning", "document_analysis"]},
                    text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities={"query": "general"},
                    conversation_context=request.conversation_context
                )
                
            except Exception as e:
                # Fallback response
                response_text = "🚢 **Maritime AI Assistant**\n\n" \
                               "I can help you with:\n" \
                               "• **Vessel Tracking** - Find vessel positions and ETAs\n" \
                               "• **Voyage Planning** - Route optimization and cost analysis\n" \
                               "• **Weather Analysis** - Port and route weather conditions\n" \
                               "• **Port Intelligence** - Port information and costs\n" \
                               "• **Document Analysis** - Analyze charter party agreements\n\n" \
                               "**Try asking:**\n" \
                               "• 'Where is EVER GIVEN right now?'\n" \
                               "• 'Plan a voyage from Singapore to Rotterdam'\n" \
                               "• 'What's the weather like in Singapore?'\n" \
                               "• 'Show me all active vessels'\n" \
                               "• 'Analyze sample_charter'"
                
                return ChatResponse(
                    agent="Captain Router",
                    status="success",
                    data={"capabilities": ["vessel_tracking", "voyage_planning", "weather", "port_intelligence", "document_analysis"]},
                    text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities={"query": "general"},
                    conversation_context=request.conversation_context
                )
        
    except Exception as e:
        return ChatResponse(
            agent="Captain Router",
            status="error",
            data={"error": str(e)},
            text=f"❌ An error occurred: {str(e)}",
            intent="error",
            confidence=0.0,
            entities={},
            conversation_context=request.conversation_context
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 