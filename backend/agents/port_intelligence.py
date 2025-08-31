import logging
from typing import Dict, Any, List
from nlp import IntentClassifier
from mocks import getBunkerPrice

logger = logging.getLogger(__name__)

class PortIntelligenceAgent:
    """Port and cargo intelligence agent."""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        
        # Port database (simplified)
        self.ports = {
            "singapore": {
                "country": "Singapore",
                "region": "Asia",
                "bunker_available": True,
                "bunker_types": ["IFO 380", "IFO 180", "MGO", "VLSFO"],
                "max_draft": 23.0,
                "facilities": ["bulk", "container", "tanker", "lng"],
                "fees": {"port_dues": 0.25, "pilotage": 0.15, "towage": 0.10}
            },
            "rotterdam": {
                "country": "Netherlands",
                "region": "Europe",
                "bunker_available": True,
                "bunker_types": ["IFO 380", "IFO 180", "MGO", "VLSFO", "ULSFO"],
                "max_draft": 24.0,
                "facilities": ["bulk", "container", "tanker", "lng", "lpg"],
                "fees": {"port_dues": 0.30, "pilotage": 0.20, "towage": 0.15}
            },
            "shanghai": {
                "country": "China",
                "region": "Asia",
                "bunker_available": True,
                "bunker_types": ["IFO 380", "IFO 180", "MGO", "VLSFO"],
                "max_draft": 17.5,
                "facilities": ["bulk", "container", "tanker"],
                "fees": {"port_dues": 0.20, "pilotage": 0.12, "towage": 0.08}
            },
            "houston": {
                "country": "USA",
                "region": "Americas",
                "bunker_available": True,
                "bunker_types": ["IFO 380", "IFO 180", "MGO", "VLSFO"],
                "max_draft": 14.0,
                "facilities": ["bulk", "container", "tanker", "lng"],
                "fees": {"port_dues": 0.35, "pilotage": 0.25, "towage": 0.20}
            },
            "fujairah": {
                "country": "UAE",
                "region": "Middle East",
                "bunker_available": True,
                "bunker_types": ["IFO 380", "IFO 180", "MGO", "VLSFO"],
                "max_draft": 20.0,
                "facilities": ["bulk", "tanker", "bunker"],
                "fees": {"port_dues": 0.18, "pilotage": 0.10, "towage": 0.08}
            }
        }
    
    def process(self, message: str) -> Dict[str, Any]:
        """Process port intelligence queries."""
        try:
            # Extract entities
            entities = self.intent_classifier.extract_entities(message)
            
            # Parse port request
            port_request = self._parse_port_request(message, entities)
            
            if not port_request:
                return self._clarification_response(message)
            
            # Generate port intelligence
            intelligence = self._generate_port_intelligence(port_request)
            
            return {
                "agent": "Port Intelligence",
                "status": "success",
                "data": {
                    "request": port_request,
                    "intelligence": intelligence
                },
                "text": self._generate_port_summary(port_request, intelligence)
            }
            
        except Exception as e:
            logger.error(f"Error in port intelligence: {e}")
            return self._error_response(str(e))
    
    def _parse_port_request(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Parse port intelligence request."""
        message_lower = message.lower()
        
        # Extract ports
        ports = entities.get("ports", [])
        
        # Determine focus areas
        focus_areas = []
        if any(word in message_lower for word in ["bunker", "fuel", "refuel"]):
            focus_areas.append("bunker_info")
        if any(word in message_lower for word in ["facility", "facilities", "infrastructure"]):
            focus_areas.append("facilities")
        if any(word in message_lower for word in ["fee", "cost", "charge", "dues"]):
            focus_areas.append("fees")
        if any(word in message_lower for word in ["draft", "depth", "restriction"]):
            focus_areas.append("restrictions")
        if any(word in message_lower for word in ["compare", "vs", "versus"]):
            focus_areas.append("comparison")
        
        # Extract vessel type for compatibility check
        vessel_types = entities.get("vessels", [])
        
        return {
            "ports": ports,
            "focus_areas": focus_areas,
            "vessel_types": vessel_types
        }
    
    def _generate_port_intelligence(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive port intelligence."""
        intelligence = {}
        
        # Port information
        if request["ports"]:
            intelligence["port_details"] = {}
            for port in request["ports"]:
                port_lower = port.lower()
                if port_lower in self.ports:
                    intelligence["port_details"][port] = self.ports[port_lower]
                else:
                    intelligence["port_details"][port] = {"status": "not_found"}
        
        # Bunker information
        if "bunker_info" in request["focus_areas"] or not request["focus_areas"]:
            intelligence["bunker_analysis"] = self._get_bunker_analysis(request["ports"])
        
        # Facilities analysis
        if "facilities" in request["focus_areas"] or request["vessel_types"]:
            intelligence["facilities_analysis"] = self._get_facilities_analysis(request["ports"], request["vessel_types"])
        
        # Fee analysis
        if "fees" in request["focus_areas"]:
            intelligence["fee_analysis"] = self._get_fee_analysis(request["ports"])
        
        # Restrictions analysis
        if "restrictions" in request["focus_areas"] or request["vessel_types"]:
            intelligence["restrictions_analysis"] = self._get_restrictions_analysis(request["ports"], request["vessel_types"])
        
        # Port comparison
        if "comparison" in request["focus_areas"] and len(request["ports"]) > 1:
            intelligence["port_comparison"] = self._compare_ports(request["ports"])
        
        return intelligence
    
    def _get_bunker_analysis(self, ports: List[str]) -> Dict[str, Any]:
        """Get bunker availability and pricing analysis."""
        analysis = {}
        
        for port in ports:
            port_lower = port.lower()
            if port_lower in self.ports:
                port_data = self.ports[port_lower]
                
                if port_data.get("bunker_available"):
                    # Get bunker prices for this port
                    try:
                        bunker_data = getBunkerPrice(port)
                        analysis[port] = {
                            "available": True,
                            "types": port_data["bunker_types"],
                            "prices": bunker_data,
                            "recommendation": "Good bunkering option"
                        }
                    except:
                        analysis[port] = {
                            "available": True,
                            "types": port_data["bunker_types"],
                            "prices": "Price data unavailable",
                            "recommendation": "Good bunkering option"
                        }
                else:
                    analysis[port] = {
                        "available": False,
                        "types": [],
                        "prices": None,
                        "recommendation": "Not recommended for bunkering"
                    }
            else:
                analysis[port] = {"status": "port_not_found"}
        
        return analysis
    
    def _get_facilities_analysis(self, ports: List[str], vessel_types: List[str]) -> Dict[str, Any]:
        """Analyze port facilities compatibility with vessel types."""
        analysis = {}
        
        for port in ports:
            port_lower = port.lower()
            if port_lower in self.ports:
                port_data = self.ports[port_lower]
                facilities = port_data.get("facilities", [])
                
                compatibility = {}
                if vessel_types:
                    for vessel_type in vessel_types:
                        vessel_lower = vessel_type.lower()
                        if "bulk" in vessel_lower and "bulk" in facilities:
                            compatibility[vessel_type] = "Fully compatible"
                        elif "tanker" in vessel_lower and "tanker" in facilities:
                            compatibility[vessel_type] = "Fully compatible"
                        elif "container" in vessel_lower and "container" in facilities:
                            compatibility[vessel_type] = "Fully compatible"
                        elif "lng" in vessel_lower and "lng" in facilities:
                            compatibility[vessel_type] = "Fully compatible"
                        else:
                            compatibility[vessel_type] = "Limited compatibility"
                else:
                    compatibility = "All vessel types supported"
                
                analysis[port] = {
                    "facilities": facilities,
                    "vessel_compatibility": compatibility,
                    "recommendation": "Good port for multiple vessel types"
                }
            else:
                analysis[port] = {"status": "port_not_found"}
        
        return analysis
    
    def _get_fee_analysis(self, ports: List[str]) -> Dict[str, Any]:
        """Analyze port fees and costs."""
        analysis = {}
        
        for port in ports:
            port_lower = port.lower()
            if port_lower in self.ports:
                port_data = self.ports[port_lower]
                fees = port_data.get("fees", {})
                
                # Calculate total fees per ton (estimated)
                total_fee_per_ton = sum(fees.values())
                
                # Categorize fee level
                if total_fee_per_ton < 0.4:
                    fee_level = "Low"
                elif total_fee_per_ton < 0.6:
                    fee_level = "Medium"
                else:
                    fee_level = "High"
                
                analysis[port] = {
                    "fees": fees,
                    "total_fee_per_ton": total_fee_per_ton,
                    "fee_level": fee_level,
                    "recommendation": f"Fee level: {fee_level}"
                }
            else:
                analysis[port] = {"status": "port_not_found"}
        
        return analysis
    
    def _get_restrictions_analysis(self, ports: List[str], vessel_types: List[str]) -> Dict[str, Any]:
        """Analyze port restrictions and vessel compatibility."""
        analysis = {}
        
        for port in ports:
            port_lower = port.lower()
            if port_lower in self.ports:
                port_data = self.ports[port_lower]
                max_draft = port_data.get("max_draft", 0)
                
                restrictions = {}
                if vessel_types:
                    for vessel_type in vessel_types:
                        vessel_lower = vessel_type.lower()
                        # Estimate vessel draft based on type
                        vessel_drafts = {
                            "panamax": 14.5,
                            "capesize": 18.5,
                            "supramax": 13.5,
                            "handysize": 11.5,
                            "vlcc": 22.0,
                            "aframax": 16.0
                        }
                        
                        vessel_draft = vessel_drafts.get(vessel_lower, 15.0)
                        
                        if vessel_draft <= max_draft:
                            restrictions[vessel_type] = "No draft restrictions"
                        else:
                            restrictions[vessel_type] = f"Draft exceeds port limit by {vessel_draft - max_draft:.1f}m"
                else:
                    restrictions = f"Port draft limit: {max_draft}m"
                
                analysis[port] = {
                    "max_draft": max_draft,
                    "vessel_restrictions": restrictions,
                    "recommendation": "Check vessel specifications against port limits"
                }
            else:
                analysis[port] = {"status": "port_not_found"}
        
        return analysis
    
    def _compare_ports(self, ports: List[str]) -> Dict[str, Any]:
        """Compare multiple ports."""
        comparison = {}
        
        # Compare key metrics
        metrics = ["bunker_available", "max_draft", "facilities_count"]
        
        for metric in metrics:
            comparison[metric] = {}
            for port in ports:
                port_lower = port.lower()
                if port_lower in self.ports:
                    port_data = self.ports[port_lower]
                    
                    if metric == "bunker_available":
                        comparison[metric][port] = port_data.get("bunker_available", False)
                    elif metric == "max_draft":
                        comparison[metric][port] = port_data.get("max_draft", 0)
                    elif metric == "facilities_count":
                        comparison[metric][port] = len(port_data.get("facilities", []))
                else:
                    comparison[metric][port] = "N/A"
        
        # Generate recommendations
        recommendations = []
        if len(ports) >= 2:
            # Find best bunkering port
            bunker_ports = [p for p in ports if comparison["bunker_available"].get(p, False)]
            if bunker_ports:
                recommendations.append(f"Best bunkering: {bunker_ports[0]}")
            
            # Find deepest port
            draft_ports = [(p, comparison["max_draft"].get(p, 0)) for p in ports if comparison["max_draft"].get(p, 0) != "N/A"]
            if draft_ports:
                deepest_port = max(draft_ports, key=lambda x: x[1])
                recommendations.append(f"Deepest draft: {deepest_port[0]} ({deepest_port[1]}m)")
        
        comparison["recommendations"] = recommendations
        
        return comparison
    
    def _generate_port_summary(self, request: Dict[str, Any], intelligence: Dict[str, Any]) -> str:
        """Generate human-readable port summary."""
        summary = "Port Intelligence Summary\n"
        summary += "=" * 30 + "\n\n"
        
        # Port details
        if "port_details" in intelligence:
            summary += "Port Information:\n"
            for port, details in intelligence["port_details"].items():
                if "status" not in details:
                    summary += f"• {port.title()}: {details['country']}, {details['region']}\n"
                    summary += f"  Max Draft: {details['max_draft']}m\n"
                    summary += f"  Facilities: {', '.join(details['facilities'])}\n"
                else:
                    summary += f"• {port.title()}: {details['status']}\n"
            summary += "\n"
        
        # Bunker analysis
        if "bunker_analysis" in intelligence:
            summary += "Bunker Analysis:\n"
            for port, analysis in intelligence["bunker_analysis"].items():
                if "status" not in analysis:
                    if analysis["available"]:
                        summary += f"• {port.title()}: Available - {', '.join(analysis['types'])}\n"
                        summary += f"  Recommendation: {analysis['recommendation']}\n"
                    else:
                        summary += f"• {port.title()}: Not available for bunkering\n"
                else:
                    summary += f"• {port.title()}: {analysis['status']}\n"
            summary += "\n"
        
        # Facilities analysis
        if "facilities_analysis" in intelligence:
            summary += "Facilities Analysis:\n"
            for port, analysis in intelligence["facilities_analysis"].items():
                if "status" not in analysis:
                    summary += f"• {port.title()}: {', '.join(analysis['facilities'])}\n"
                    summary += f"  Recommendation: {analysis['recommendation']}\n"
                else:
                    summary += f"• {port.title()}: {analysis['status']}\n"
            summary += "\n"
        
        # Fee analysis
        if "fee_analysis" in intelligence:
            summary += "Fee Analysis:\n"
            for port, analysis in intelligence["fee_analysis"].items():
                if "status" not in analysis:
                    summary += f"• {port.title()}: ${analysis['total_fee_per_ton']:.2f}/ton ({analysis['fee_level']})\n"
                else:
                    summary += f"• {port.title()}: {analysis['status']}\n"
            summary += "\n"
        
        # Port comparison
        if "port_comparison" in intelligence:
            summary += "Port Comparison:\n"
            comparison = intelligence["port_comparison"]
            for metric, values in comparison.items():
                if metric != "recommendations":
                    summary += f"• {metric.replace('_', ' ').title()}:\n"
                    for port, value in values.items():
                        summary += f"  {port.title()}: {value}\n"
            
            if comparison.get("recommendations"):
                summary += "\nRecommendations:\n"
                for rec in comparison["recommendations"]:
                    summary += f"• {rec}\n"
        
        return summary
    
    def _clarification_response(self, message: str) -> Dict[str, Any]:
        """Request clarification for incomplete port requests."""
        return {
            "agent": "Port Intelligence",
            "status": "clarification_needed",
            "data": {
                "message": message,
                "focus_areas": ["bunker_info", "facilities", "fees", "restrictions"]
            },
            "text": "I'd be happy to provide port intelligence! Please specify which ports you're interested in and what information you need: bunker availability, facilities, fees, or restrictions. For example: 'Show me bunker availability at Singapore and Rotterdam'."
        }
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Return error response."""
        return {
            "agent": "Port Intelligence",
            "status": "error",
            "data": {"error": error},
            "text": "I encountered an error generating port intelligence. Please try again with more specific details."
        } 