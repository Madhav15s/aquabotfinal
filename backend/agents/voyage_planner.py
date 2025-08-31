import logging
import re
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from nlp import IntentClassifier
from mocks import getWeather, getAISData, getBunkerPrice

logger = logging.getLogger(__name__)

class VoyagePlannerAgent:
    """Voyage planning and optimization agent."""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        
        # Major shipping routes and distances (nautical miles)
        self.routes = {
            ("singapore", "rotterdam"): {"distance": 8500, "via_suez": True, "via_cape": False},
            ("singapore", "houston"): {"distance": 10500, "via_panama": True, "via_cape": False},
            ("shanghai", "rotterdam"): {"distance": 11000, "via_suez": True, "via_cape": False},
            ("shanghai", "houston"): {"distance": 12000, "via_panama": True, "via_cape": False},
            ("santos", "qingdao"): {"distance": 13000, "via_panama": True, "via_cape": False},
            ("mumbai", "rotterdam"): {"distance": 6500, "via_suez": True, "via_cape": False},
            ("mumbai", "houston"): {"distance": 9500, "via_suez": True, "via_cape": False}
        }
        
        # Canal fees and restrictions
        self.canal_fees = {
            "suez": {"fee_per_ton": 8.5, "min_fee": 5000, "max_draft": 20.1},
            "panama": {"fee_per_ton": 5.25, "min_fee": 800, "max_draft": 15.2}
        }
        
        # Vessel performance data
        self.vessel_types = {
            "panamax": {"speed": 14, "fuel_consumption": 30, "draft": 14.5},
            "capesize": {"speed": 15, "fuel_consumption": 45, "draft": 18.5},
            "supramax": {"speed": 13, "fuel_consumption": 25, "draft": 13.5},
            "handysize": {"speed": 12, "fuel_consumption": 20, "draft": 11.5},
            "vlcc": {"speed": 16, "fuel_consumption": 80, "draft": 22.0},
            "aframax": {"speed": 14, "fuel_consumption": 35, "draft": 16.0}
        }
    
    def process(self, message: str) -> Dict[str, Any]:
        """Process voyage planning queries."""
        try:
            # Extract entities from message
            entities = self.intent_classifier.extract_entities(message)
            
            # Parse voyage request
            voyage_request = self._parse_voyage_request(message, entities)
            
            if not voyage_request:
                return self._clarification_response(message)
            
            # Plan voyage
            voyage_plan = self._plan_voyage(voyage_request)
            
            return {
                "agent": "Voyage Planner",
                "status": "success",
                "data": voyage_plan,
                "text": self._generate_voyage_summary(voyage_plan)
            }
            
        except Exception as e:
            logger.error(f"Error in voyage planner: {e}")
            return self._error_response(str(e))
    
    def _parse_voyage_request(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Parse voyage request from message and entities."""
        message_lower = message.lower()
        
        # Extract ports
        ports = entities.get("ports", [])
        if len(ports) < 2:
            # Try to extract from message using common patterns
            port_patterns = [
                r"from\s+(\w+)",
                r"to\s+(\w+)",
                r"between\s+(\w+)\s+and\s+(\w+)",
                r"(\w+)\s*-\s*(\w+)"
            ]
            
            for pattern in port_patterns:
                matches = re.findall(pattern, message_lower)
                if matches:
                    if isinstance(matches[0], tuple):
                        ports.extend(matches[0])
                    else:
                        ports.extend(matches)
                    break
        
        # Extract vessel type
        vessel_type = None
        for vessel in entities.get("vessels", []):
            if vessel.lower() in self.vessel_types:
                vessel_type = vessel.lower()
                break
        
        if not vessel_type:
            # Try to infer from message
            for vt in self.vessel_types:
                if vt in message_lower:
                    vessel_type = vt
                    break
        
        # Extract cargo type
        cargo_type = entities.get("cargo", [])
        
        # Extract laycan dates
        laycan_days = None
        if "laycan" in message_lower:
            laycan_match = re.search(r"(\d+)\s*day", message_lower)
            if laycan_match:
                laycan_days = int(laycan_match.group(1))
        
        # Check for route comparison requests
        compare_routes = any(word in message_lower for word in ["compare", "vs", "versus", "alternative", "what if"])
        
        # Check for specific canal routing
        via_suez = "suez" in message_lower
        via_panama = "panama" in message_lower
        via_cape = "cape" in message_lower
        
        if len(ports) >= 2:
            return {
                "origin": ports[0],
                "destination": ports[1],
                "vessel_type": vessel_type or "panamax",
                "cargo_type": cargo_type,
                "laycan_days": laycan_days,
                "compare_routes": compare_routes,
                "via_suez": via_suez,
                "via_panama": via_panama,
                "via_cape": via_cape
            }
        
        return None
    
    def _plan_voyage(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive voyage plan."""
        origin = request["origin"]
        destination = request["destination"]
        vessel_type = request["vessel_type"]
        compare_routes = request["compare_routes"]
        
        # Get vessel performance data
        vessel_data = self.vessel_types.get(vessel_type, self.vessel_types["panamax"])
        
        # Find route
        route_key = self._find_route_key(origin, destination)
        if not route_key:
            # Generate estimated route
            route_data = self._estimate_route(origin, destination)
        else:
            route_data = self.routes[route_key]
        
        # Calculate route options
        routes = self._calculate_route_options(origin, destination, route_data, vessel_data, request)
        
        # Get weather data for route
        weather_data = self._get_route_weather(routes[0])  # Use primary route for weather
        
        # Calculate costs
        cost_analysis = self._calculate_voyage_costs(routes[0], vessel_data, weather_data)
        
        return {
            "request": request,
            "vessel": vessel_data,
            "routes": routes,
            "weather": weather_data,
            "costs": cost_analysis,
            "recommendations": self._generate_recommendations(routes, cost_analysis, weather_data)
        }
    
    def _find_route_key(self, origin: str, destination: str) -> Tuple[str, str]:
        """Find exact route key in routes dictionary."""
        origin_lower = origin.lower()
        dest_lower = destination.lower()
        
        for (orig, dest), data in self.routes.items():
            if (origin_lower in orig or orig in origin_lower) and (dest_lower in dest or dest in dest_lower):
                return (orig, dest)
        
        return None
    
    def _estimate_route(self, origin: str, destination: str) -> Dict[str, Any]:
        """Estimate route data for unknown port pairs."""
        # Simple estimation based on typical distances
        estimated_distance = 8000  # Default estimate
        
        return {
            "distance": estimated_distance,
            "via_suez": True,
            "via_cape": False
        }
    
    def _calculate_route_options(self, origin: str, destination: str, route_data: Dict[str, Any], 
                                vessel_data: Dict[str, Any], request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate different route options."""
        routes = []
        
        # Primary route (most common)
        primary_route = {
            "name": f"{origin.title()} to {destination.title()}",
            "distance": route_data["distance"],
            "via_canal": "Suez" if route_data.get("via_suez") else "Panama" if route_data.get("via_panama") else "None",
            "estimated_days": route_data["distance"] / (vessel_data["speed"] * 24),
            "fuel_consumption": (route_data["distance"] / vessel_data["speed"]) * vessel_data["fuel_consumption"] / 24,
            "canal_fees": self._calculate_canal_fees(vessel_data, route_data),
            "type": "primary"
        }
        routes.append(primary_route)
        
        # Alternative routes if comparison requested
        if request["compare_routes"]:
            # Cape route (longer but no canal fees)
            if route_data.get("via_suez") or route_data.get("via_panama"):
                cape_distance = route_data["distance"] * 1.4  # 40% longer
                cape_route = {
                    "name": f"{origin.title()} to {destination.title()} via Cape",
                    "distance": int(cape_distance),
                    "via_canal": "None",
                    "estimated_days": cape_distance / (vessel_data["speed"] * 24),
                    "fuel_consumption": (cape_distance / vessel_data["speed"]) * vessel_data["fuel_consumption"] / 24,
                    "canal_fees": 0,
                    "type": "alternative"
                }
                routes.append(cape_route)
            
            # What-if scenarios
            if request.get("via_suez") and not route_data.get("via_suez"):
                suez_route = primary_route.copy()
                suez_route["name"] = f"{origin.title()} to {destination.title()} via Suez"
                suez_route["distance"] = int(route_data["distance"] * 0.8)  # 20% shorter
                suez_route["via_canal"] = "Suez"
                suez_route["estimated_days"] = suez_route["distance"] / (vessel_data["speed"] * 24)
                suez_route["fuel_consumption"] = (suez_route["distance"] / vessel_data["speed"]) * vessel_data["fuel_consumption"] / 24
                suez_route["canal_fees"] = self._calculate_canal_fees(vessel_data, {"via_suez": True})
                suez_route["type"] = "what_if"
                routes.append(suez_route)
        
        return routes
    
    def _calculate_canal_fees(self, vessel_data: Dict[str, Any], route_data: Dict[str, Any]) -> float:
        """Calculate canal fees for route."""
        if route_data.get("via_suez"):
            # Estimate vessel tonnage based on draft
            estimated_tonnage = (vessel_data["draft"] / 20) * 100000  # Rough estimate
            fee = max(self.canal_fees["suez"]["min_fee"], 
                     estimated_tonnage * self.canal_fees["suez"]["fee_per_ton"])
            return round(fee, 2)
        elif route_data.get("via_panama"):
            estimated_tonnage = (vessel_data["draft"] / 15) * 80000  # Rough estimate
            fee = max(self.canal_fees["panama"]["min_fee"], 
                     estimated_tonnage * self.canal_fees["panama"]["fee_per_ton"])
            return round(fee, 2)
        
        return 0.0
    
    def _get_route_weather(self, route: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather data for route."""
        # Sample weather data for route midpoint
        sample_lat = 30.0  # Sample latitude
        sample_lon = 0.0   # Sample longitude
        
        try:
            weather = getWeather(sample_lat, sample_lon)
            return weather
        except Exception as e:
            logger.warning(f"Could not get weather data: {e}")
            return {"error": "Weather data unavailable"}
    
    def _calculate_voyage_costs(self, route: Dict[str, Any], vessel_data: Dict[str, Any], 
                               weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive voyage costs."""
        # Fuel costs (using mock bunker price)
        try:
            bunker_price = getBunkerPrice()
            fuel_cost = (route["fuel_consumption"] * bunker_price.get("current_price", 500)) / 1000  # Convert to tons
        except:
            fuel_cost = route["fuel_consumption"] * 0.5  # Fallback calculation
        
        # Canal fees
        canal_fees = route["canal_fees"]
        
        # Port charges (estimated)
        port_charges = 15000  # Estimated average
        
        # Crew and provisions
        crew_cost = route["estimated_days"] * 500  # $500 per day
        
        # Insurance and other
        other_costs = 10000
        
        total_cost = fuel_cost + canal_fees + port_charges + crew_cost + other_costs
        
        return {
            "fuel_cost": round(fuel_cost, 2),
            "canal_fees": canal_fees,
            "port_charges": port_charges,
            "crew_cost": round(crew_cost, 2),
            "other_costs": other_costs,
            "total_cost": round(total_cost, 2),
            "cost_per_day": round(total_cost / route["estimated_days"], 2)
        }
    
    def _generate_recommendations(self, routes: List[Dict[str, Any]], costs: Dict[str, Any], 
                                 weather: Dict[str, Any]) -> List[str]:
        """Generate voyage recommendations."""
        recommendations = []
        
        # Route recommendations
        if len(routes) > 1:
            primary = routes[0]
            alternatives = [r for r in routes if r["type"] != "primary"]
            
            if alternatives:
                best_alternative = min(alternatives, key=lambda x: x["total_cost"] if "total_cost" in x else float('inf'))
                if best_alternative.get("total_cost", float('inf')) < costs["total_cost"]:
                    recommendations.append(f"Consider {best_alternative['name']} for potential cost savings")
        
        # Weather considerations
        if "marine" in weather and "wave_height" in weather["marine"]:
            wave_height = weather["marine"]["wave_height"]
            if wave_height > 3.0:
                recommendations.append("High wave conditions detected - consider route adjustment or speed reduction")
            elif wave_height < 1.0:
                recommendations.append("Favorable sea conditions - optimal for fuel efficiency")
        
        # Fuel optimization
        if costs["fuel_cost"] > costs["total_cost"] * 0.6:
            recommendations.append("Fuel costs represent high percentage of total voyage cost - consider speed optimization")
        
        # Canal optimization
        if costs["canal_fees"] > 0:
            recommendations.append("Canal fees significant - verify vessel dimensions and tonnage for accurate fee calculation")
        
        return recommendations
    
    def _generate_voyage_summary(self, voyage_plan: Dict[str, Any]) -> str:
        """Generate human-readable voyage summary."""
        primary_route = voyage_plan["routes"][0]
        costs = voyage_plan["costs"]
        
        summary = f"Voyage Plan: {primary_route['name']}\n"
        summary += f"Distance: {primary_route['distance']} nautical miles\n"
        summary += f"Estimated Duration: {primary_route['estimated_days']:.1f} days\n"
        summary += f"Route: Via {primary_route['via_canal'] if primary_route['via_canal'] != 'None' else 'Direct'}\n"
        summary += f"Fuel Consumption: {primary_route['fuel_consumption']:.1f} tons\n"
        summary += f"Total Cost: ${costs['total_cost']:,.2f}\n"
        
        if voyage_plan["recommendations"]:
            summary += "\nRecommendations:\n"
            for rec in voyage_plan["recommendations"]:
                summary += f"• {rec}\n"
        
        return summary
    
    def _clarification_response(self, message: str) -> Dict[str, Any]:
        """Request clarification for incomplete voyage requests."""
        return {
            "agent": "Voyage Planner",
            "status": "clarification_needed",
            "data": {
                "message": message,
                "required_info": ["origin port", "destination port", "vessel type"]
            },
            "text": "I'd be happy to help plan your voyage! Please provide the origin port, destination port, and vessel type. For example: 'Plan a voyage from Singapore to Rotterdam using a Panamax vessel'."
        }
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Return error response."""
        return {
            "agent": "Voyage Planner",
            "status": "error",
            "data": {"error": error},
            "text": "I encountered an error planning your voyage. Please try again with more specific details."
        } 