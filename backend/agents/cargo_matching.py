nimport logging
from typing import Dict, Any, List
from nlp import IntentClassifier
from mocks import getBunkerPrice

logger = logging.getLogger(__name__)

class CargoMatchingAgent:
    """Cargo and tonnage matching agent."""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        
        # Cargo types and characteristics
        self.cargo_types = {
            "coal": {"density": 0.8, "stowage_factor": 1.25, "handling": "bulk"},
            "iron_ore": {"density": 2.5, "stowage_factor": 0.4, "handling": "bulk"},
            "grain": {"density": 0.75, "stowage_factor": 1.33, "handling": "bulk"},
            "oil": {"density": 0.85, "stowage_factor": 1.18, "handling": "liquid"},
            "lng": {"density": 0.45, "stowage_factor": 2.22, "handling": "gas"},
            "lpg": {"density": 0.55, "stowage_factor": 1.82, "handling": "gas"},
            "containers": {"density": 0.15, "stowage_factor": 6.67, "handling": "container"}
        }
        
        # Vessel types and capacities
        self.vessel_capacities = {
            "panamax": {"dwt": 75000, "cargo_holds": 7, "max_draft": 14.5},
            "capesize": {"dwt": 180000, "cargo_holds": 9, "max_draft": 18.5},
            "supramax": {"dwt": 58000, "cargo_holds": 5, "max_draft": 13.5},
            "handysize": {"dwt": 35000, "cargo_holds": 4, "max_draft": 11.5},
            "vlcc": {"dwt": 300000, "cargo_holds": 12, "max_draft": 22.0},
            "aframax": {"dwt": 120000, "cargo_holds": 8, "max_draft": 16.0}
        }
    
    def process(self, message: str) -> Dict[str, Any]:
        """Process cargo matching queries."""
        try:
            # Extract entities
            entities = self.intent_classifier.extract_entities(message)
            
            # Parse cargo request
            cargo_request = self._parse_cargo_request(message, entities)
            
            if not cargo_request:
                return self._clarification_response(message)
            
            # Match cargo with vessels
            matches = self._match_cargo_vessels(cargo_request)
            
            # Calculate profitability
            profitability = self._calculate_profitability(matches, cargo_request)
            
            return {
                "agent": "Cargo Matcher",
                "status": "success",
                "data": {
                    "request": cargo_request,
                    "matches": matches,
                    "profitability": profitability
                },
                "text": self._generate_cargo_summary(cargo_request, matches, profitability)
            }
            
        except Exception as e:
            logger.error(f"Error in cargo matcher: {e}")
            return self._error_response(str(e))
    
    def _parse_cargo_request(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Parse cargo matching request."""
        message_lower = message.lower()
        
        # Extract cargo type
        cargo_type = None
        for cargo in entities.get("cargo", []):
            if cargo.lower() in self.cargo_types:
                cargo_type = cargo.lower()
                break
        
        if not cargo_type:
            # Try to infer from message
            for ct in self.cargo_types:
                if ct in message_lower:
                    cargo_type = ct
                    break
        
        # Extract quantity
        quantity = None
        if "ton" in message_lower or "mt" in message_lower:
            # Look for numbers followed by ton/mt
            import re
            ton_match = re.search(r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:ton|mt)", message_lower)
            if ton_match:
                quantity = float(ton_match.group(1).replace(",", ""))
        
        # Extract ports
        ports = entities.get("ports", [])
        
        # Extract laycan
        laycan_days = None
        if "laycan" in message_lower:
            import re
            laycan_match = re.search(r"(\d+)\s*day", message_lower)
            if laycan_match:
                laycan_days = int(laycan_match.group(1))
        
        return {
            "cargo_type": cargo_type,
            "quantity": quantity,
            "ports": ports,
            "laycan_days": laycan_days
        }
    
    def _match_cargo_vessels(self, request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Match cargo with suitable vessels."""
        matches = []
        cargo_type = request["cargo_type"]
        quantity = request["quantity"]
        
        if not cargo_type:
            return matches
        
        cargo_data = self.cargo_types.get(cargo_type, {})
        
        for vessel_type, vessel_data in self.vessel_capacities.items():
            # Check if vessel can carry this cargo
            if self._can_carry_cargo(vessel_type, cargo_type, quantity):
                match_score = self._calculate_match_score(vessel_type, cargo_type, quantity)
                
                match = {
                    "vessel_type": vessel_type,
                    "cargo_type": cargo_type,
                    "match_score": match_score,
                    "capacity_utilization": min(100, (quantity / vessel_data["dwt"]) * 100) if quantity else None,
                    "vessel_specs": vessel_data,
                    "cargo_specs": cargo_data
                }
                
                matches.append(match)
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches
    
    def _can_carry_cargo(self, vessel_type: str, cargo_type: str, quantity: float) -> bool:
        """Check if vessel can carry specified cargo."""
        vessel_data = self.vessel_capacities[vessel_type]
        cargo_data = self.cargo_types[cargo_type]
        
        # Check capacity
        if quantity and quantity > vessel_data["dwt"]:
            return False
        
        # Check cargo handling compatibility
        if cargo_type == "containers" and vessel_type not in ["panamax", "capesize"]:
            return False
        
        if cargo_type in ["lng", "lpg"] and vessel_type not in ["vlcc", "aframax"]:
            return False
        
        return True
    
    def _calculate_match_score(self, vessel_type: str, cargo_type: str, quantity: float) -> float:
        """Calculate match score (0-100)."""
        score = 50  # Base score
        
        vessel_data = self.vessel_capacities[vessel_type]
        cargo_data = self.cargo_types[cargo_type]
        
        # Capacity utilization bonus
        if quantity:
            utilization = (quantity / vessel_data["dwt"]) * 100
            if 70 <= utilization <= 95:
                score += 20  # Optimal utilization
            elif 50 <= utilization < 70:
                score += 10  # Good utilization
            elif utilization > 95:
                score -= 10  # Over-utilization
        
        # Cargo type compatibility
        if cargo_type in ["coal", "iron_ore", "grain"] and vessel_type in ["panamax", "capesize", "supramax"]:
            score += 15  # Perfect match for bulk carriers
        
        if cargo_type == "oil" and vessel_type in ["vlcc", "aframax"]:
            score += 15  # Perfect match for tankers
        
        if cargo_type == "containers" and vessel_type in ["panamax", "capesize"]:
            score += 10  # Good for container ships
        
        # Vessel efficiency
        if vessel_type in ["panamax", "supramax"]:
            score += 5  # Versatile vessels
        
        return min(100, max(0, score))
    
    def _calculate_profitability(self, matches: List[Dict[str, Any]], request: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate profitability analysis."""
        if not matches:
            return {"error": "No matches found"}
        
        best_match = matches[0]
        vessel_type = best_match["vessel_type"]
        cargo_type = request["cargo_type"]
        quantity = request["quantity"]
        
        # Get bunker prices
        try:
            bunker_data = getBunkerPrice()
            fuel_price = bunker_data.get("current_price", 500)
        except:
            fuel_price = 500
        
        # Estimate freight rate (simplified)
        freight_rates = {
            "coal": 15,      # USD per ton
            "iron_ore": 18,
            "grain": 20,
            "oil": 25,
            "lng": 30,
            "lpg": 28,
            "containers": 35
        }
        
        freight_rate = freight_rates.get(cargo_type, 20)
        
        # Calculate revenue
        revenue = quantity * freight_rate if quantity else 0
        
        # Calculate costs
        vessel_data = self.vessel_capacities[vessel_type]
        
        # Fuel costs (estimated)
        fuel_consumption = vessel_data["dwt"] * 0.001  # tons per day
        daily_fuel_cost = fuel_consumption * fuel_price
        
        # Port costs (estimated)
        port_costs = 15000
        
        # Crew and other costs
        other_costs = 5000
        
        # Total costs
        total_costs = daily_fuel_cost + port_costs + other_costs
        
        # Profit
        profit = revenue - total_costs
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0
        
        return {
            "revenue": round(revenue, 2),
            "total_costs": round(total_costs, 2),
            "profit": round(profit, 2),
            "profit_margin": round(profit_margin, 2),
            "freight_rate": freight_rate,
            "fuel_cost_per_day": round(daily_fuel_cost, 2),
            "port_costs": port_costs,
            "other_costs": other_costs
        }
    
    def _generate_cargo_summary(self, request: Dict[str, Any], matches: List[Dict[str, Any]], 
                               profitability: Dict[str, Any]) -> str:
        """Generate human-readable cargo summary."""
        if not matches:
            return "No suitable vessels found for the specified cargo requirements."
        
        best_match = matches[0]
        cargo_type = request["cargo_type"] or "Unknown"
        quantity = request["quantity"] or "Unknown"
        
        summary = f"Cargo Matching Results for {cargo_type.title()}\n"
        summary += f"Quantity: {quantity} tons\n\n"
        
        summary += f"Best Match: {best_match['vessel_type'].title()}\n"
        summary += f"Match Score: {best_match['match_score']}/100\n"
        
        if best_match.get("capacity_utilization"):
            summary += f"Capacity Utilization: {best_match['capacity_utilization']:.1f}%\n"
        
        if "profit" in profitability:
            summary += f"\nProfitability Analysis:\n"
            summary += f"Revenue: ${profitability['revenue']:,.2f}\n"
            summary += f"Total Costs: ${profitability['total_costs']:,.2f}\n"
            summary += f"Profit: ${profitability['profit']:,.2f}\n"
            summary += f"Profit Margin: {profitability['profit_margin']:.1f}%\n"
        
        if len(matches) > 1:
            summary += f"\nAlternative Vessels: {len(matches) - 1} other options available"
        
        return summary
    
    def _clarification_response(self, message: str) -> Dict[str, Any]:
        """Request clarification for incomplete cargo requests."""
        return {
            "agent": "Cargo Matcher",
            "status": "clarification_needed",
            "data": {
                "message": message,
                "required_info": ["cargo type", "quantity", "ports"]
            },
            "text": "I'd be happy to help match your cargo with suitable vessels! Please provide the cargo type, quantity, and ports. For example: 'Find vessels for 50,000 tons of coal from Australia to China'."
        }
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Return error response."""
        return {
            "agent": "Cargo Matcher",
            "status": "error",
            "data": {"error": error},
            "text": "I encountered an error matching your cargo. Please try again with more specific details."
        } 