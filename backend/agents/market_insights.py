import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from nlp import IntentClassifier
from mocks import getBunkerPrice

logger = logging.getLogger(__name__)

class MarketInsightsAgent:
    """Market and commercial insights agent."""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        
        # Market indices and trends
        self.market_indices = {
            "bdi": {"current": 1250, "trend": "rising", "change": "+5.2%"},
            "ccfi": {"current": 1250, "trend": "stable", "change": "+0.8%"},
            "bcti": {"current": 850, "trend": "falling", "change": "-2.1%"}
        }
        
        # Freight rate benchmarks
        self.freight_benchmarks = {
            "panamax": {"coal": 18.5, "grain": 22.0, "iron_ore": 20.5},
            "capesize": {"iron_ore": 25.0, "coal": 22.5, "bauxite": 24.0},
            "supramax": {"grain": 19.5, "coal": 17.0, "fertilizer": 18.5},
            "handysize": {"grain": 16.5, "coal": 15.0, "steel": 17.0}
        }
    
    def process(self, message: str) -> Dict[str, Any]:
        """Process market insights queries."""
        try:
            # Extract entities
            entities = self.intent_classifier.extract_entities(message)
            
            # Parse market request
            market_request = self._parse_market_request(message, entities)
            
            if not market_request:
                return self._clarification_response(message)
            
            # Generate market insights
            insights = self._generate_market_insights(market_request)
            
            return {
                "agent": "Market Insights",
                "status": "success",
                "data": {
                    "request": market_request,
                    "insights": insights
                },
                "text": self._generate_market_summary(market_request, insights)
            }
            
        except Exception as e:
            logger.error(f"Error in market insights: {e}")
            return self._error_response(str(e))
    
    def _parse_market_request(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Parse market insights request."""
        message_lower = message.lower()
        
        # Determine market focus
        focus_areas = []
        if any(word in message_lower for word in ["freight", "rate", "charter"]):
            focus_areas.append("freight_rates")
        if any(word in message_lower for word in ["bunker", "fuel", "price"]):
            focus_areas.append("bunker_prices")
        if any(word in message_lower for word in ["market", "trend", "index"]):
            focus_areas.append("market_indices")
        if any(word in message_lower for word in ["vessel", "type", "size"]):
            focus_areas.append("vessel_analysis")
        
        # Extract vessel types
        vessel_types = entities.get("vessels", [])
        
        # Extract cargo types
        cargo_types = entities.get("cargo", [])
        
        # Extract time period
        time_period = "current"
        if "trend" in message_lower or "history" in message_lower:
            time_period = "trend"
        elif "forecast" in message_lower or "outlook" in message_lower:
            time_period = "forecast"
        
        return {
            "focus_areas": focus_areas,
            "vessel_types": vessel_types,
            "cargo_types": cargo_types,
            "time_period": time_period
        }
    
    def _generate_market_insights(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive market insights."""
        insights = {}
        
        # Market indices
        if "market_indices" in request["focus_areas"] or not request["focus_areas"]:
            insights["indices"] = self._get_market_indices()
        
        # Freight rates
        if "freight_rates" in request["focus_areas"] or not request["focus_areas"]:
            insights["freight_rates"] = self._get_freight_rates(request["vessel_types"], request["cargo_types"])
        
        # Bunker prices
        if "bunker_prices" in request["focus_areas"] or not request["focus_areas"]:
            insights["bunker_prices"] = self._get_bunker_insights()
        
        # Vessel analysis
        if "vessel_analysis" in request["focus_areas"] or request["vessel_types"]:
            insights["vessel_analysis"] = self._get_vessel_analysis(request["vessel_types"])
        
        # Market trends
        if request["time_period"] in ["trend", "forecast"]:
            insights["trends"] = self._get_market_trends()
        
        return insights
    
    def _get_market_indices(self) -> Dict[str, Any]:
        """Get current market indices."""
        return {
            "bdi": self.market_indices["bdi"],
            "ccfi": self.market_indices["ccfi"],
            "bcti": self.market_indices["bcti"],
            "summary": "Mixed market conditions with dry bulk showing strength"
        }
    
    def _get_freight_rates(self, vessel_types: List[str], cargo_types: List[str]) -> Dict[str, Any]:
        """Get freight rate analysis."""
        rates = {}
        
        # If specific vessel types requested
        if vessel_types:
            for vessel_type in vessel_types:
                if vessel_type.lower() in self.freight_benchmarks:
                    rates[vessel_type] = self.freight_benchmarks[vessel_type.lower()]
        else:
            # Show all vessel types
            rates = self.freight_benchmarks
        
        # Add market commentary
        rates["commentary"] = "Freight rates remain stable with seasonal variations expected"
        
        return rates
    
    def _get_bunker_insights(self) -> Dict[str, Any]:
        """Get bunker price insights."""
        try:
            bunker_data = getBunkerPrice()
            
            # Analyze trends
            price_history = bunker_data.get("price_history", [])
            if len(price_history) >= 7:
                week_ago = price_history[-7]["price"]
                current = bunker_data["current_price"]
                weekly_change = ((current - week_ago) / week_ago) * 100
                trend = "rising" if weekly_change > 0 else "falling" if weekly_change < 0 else "stable"
            else:
                weekly_change = 0
                trend = "stable"
            
            return {
                "current_price": bunker_data["current_price"],
                "fuel_type": bunker_data["fuel_type"],
                "weekly_change": round(weekly_change, 2),
                "trend": trend,
                "market_trend": bunker_data.get("market_trend", "stable"),
                "availability": bunker_data.get("availability", "Good"),
                "commentary": f"Bunker prices {trend} with {abs(weekly_change):.1f}% weekly change"
            }
            
        except Exception as e:
            logger.error(f"Error getting bunker insights: {e}")
            return {"error": "Bunker data unavailable"}
    
    def _get_vessel_analysis(self, vessel_types: List[str]) -> Dict[str, Any]:
        """Get vessel market analysis."""
        analysis = {}
        
        # Vessel type performance
        vessel_performance = {
            "panamax": {"demand": "high", "supply": "balanced", "outlook": "positive"},
            "capesize": {"demand": "moderate", "supply": "high", "outlook": "stable"},
            "supramax": {"demand": "high", "supply": "moderate", "outlook": "positive"},
            "handysize": {"demand": "stable", "supply": "balanced", "outlook": "neutral"}
        }
        
        if vessel_types:
            for vessel_type in vessel_types:
                if vessel_type.lower() in vessel_performance:
                    analysis[vessel_type] = vessel_performance[vessel_type.lower()]
        else:
            analysis = vessel_performance
        
        analysis["summary"] = "Panamax and Supramax vessels showing strong demand"
        
        return analysis
    
    def _get_market_trends(self) -> Dict[str, Any]:
        """Get market trends and forecasts."""
        return {
            "dry_bulk": {
                "trend": "rising",
                "drivers": ["Grain exports", "Iron ore demand", "Coal trade"],
                "outlook": "Positive for next quarter"
            },
            "tankers": {
                "trend": "stable",
                "drivers": ["Oil demand", "Geopolitical factors", "Fleet supply"],
                "outlook": "Stable with upside potential"
            },
            "containers": {
                "trend": "falling",
                "drivers": ["Consumer demand", "Inventory levels", "Economic growth"],
                "outlook": "Continued pressure expected"
            }
        }
    
    def _generate_market_summary(self, request: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """Generate human-readable market summary."""
        summary = "Market Insights Summary\n"
        summary += "=" * 30 + "\n\n"
        
        # Market indices
        if "indices" in insights:
            summary += "Market Indices:\n"
            indices = insights["indices"]
            for key, data in indices.items():
                if key != "summary":
                    summary += f"• {key.upper()}: {data['current']} ({data['change']})\n"
            summary += f"Summary: {indices.get('summary', '')}\n\n"
        
        # Freight rates
        if "freight_rates" in insights:
            summary += "Freight Rates:\n"
            rates = insights["freight_rates"]
            for vessel_type, cargo_rates in rates.items():
                if vessel_type != "commentary":
                    summary += f"• {vessel_type.title()}: "
                    for cargo, rate in cargo_rates.items():
                        summary += f"{cargo} ${rate}/ton, "
                    summary = summary.rstrip(", ") + "\n"
            summary += f"Commentary: {rates.get('commentary', '')}\n\n"
        
        # Bunker prices
        if "bunker_prices" in insights:
            bunker = insights["bunker_prices"]
            if "error" not in bunker:
                summary += f"Bunker Prices:\n"
                summary += f"• {bunker['fuel_type']}: ${bunker['current_price']}/ton\n"
                summary += f"• Weekly Change: {bunker['weekly_change']}% ({bunker['trend']})\n"
                summary += f"• Market: {bunker['market_trend']}, Availability: {bunker['availability']}\n"
                summary += f"• Commentary: {bunker['commentary']}\n\n"
        
        # Vessel analysis
        if "vessel_analysis" in insights:
            summary += "Vessel Market Analysis:\n"
            vessels = insights["vessel_analysis"]
            for vessel_type, analysis in vessels.items():
                if vessel_type != "summary":
                    summary += f"• {vessel_type.title()}: Demand {analysis['demand']}, Supply {analysis['supply']}, Outlook {analysis['outlook']}\n"
            summary += f"Summary: {vessels.get('summary', '')}\n\n"
        
        # Trends
        if "trends" in insights:
            summary += "Market Trends:\n"
            trends = insights["trends"]
            for sector, data in trends.items():
                summary += f"• {sector.title()}: {data['trend'].title()} - {data['outlook']}\n"
        
        return summary
    
    def _clarification_response(self, message: str) -> Dict[str, Any]:
        """Request clarification for incomplete market requests."""
        return {
            "agent": "Market Insights",
            "status": "clarification_needed",
            "data": {
                "message": message,
                "focus_areas": ["freight_rates", "bunker_prices", "market_indices", "vessel_analysis"]
            },
            "text": "I'd be happy to provide market insights! Please specify what you'd like to know about: freight rates, bunker prices, market indices, or vessel analysis. For example: 'Show me current freight rates for Panamax vessels'."
        }
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Return error response."""
        return {
            "agent": "Market Insights",
            "status": "error",
            "data": {"error": error},
            "text": "I encountered an error generating market insights. Please try again with more specific details."
        } 