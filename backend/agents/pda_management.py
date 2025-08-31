import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from nlp import IntentClassifier

logger = logging.getLogger(__name__)

class PDAManagementAgent:
    """PDA (Port Disbursement Account) management agent."""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        
        # PDA cost categories
        self.cost_categories = {
            "port_charges": {
                "port_dues": {"description": "Port dues and tonnage charges", "unit": "per ton"},
                "pilotage": {"description": "Pilotage fees", "unit": "per call"},
                "towage": {"description": "Tug assistance fees", "unit": "per call"},
                "berth_fees": {"description": "Berth rental charges", "unit": "per day"}
            },
            "agency_services": {
                "agency_fees": {"description": "Ship agent commission", "unit": "per call"},
                "documentation": {"description": "Document processing fees", "unit": "per call"},
                "communications": {"description": "Communication and coordination", "unit": "per call"}
            },
            "cargo_operations": {
                "stevedoring": {"description": "Cargo handling labor", "unit": "per ton"},
                "equipment": {"description": "Cargo handling equipment", "unit": "per day"},
                "security": {"description": "Cargo security services", "unit": "per call"}
            },
            "supply_services": {
                "fresh_water": {"description": "Fresh water supply", "unit": "per ton"},
                "provisions": {"description": "Crew provisions", "unit": "per call"},
                "waste_disposal": {"description": "Garbage and waste removal", "unit": "per call"}
            }
        }
        
        # Regional cost multipliers
        self.regional_multipliers = {
            "asia": 1.0,      # Base (Singapore)
            "europe": 1.3,    # Higher costs
            "americas": 1.2,  # Moderate costs
            "middle_east": 0.9, # Lower costs
            "africa": 1.1     # Slightly higher
        }
    
    def process(self, message: str) -> Dict[str, Any]:
        """Process PDA management queries."""
        try:
            # Extract entities
            entities = self.intent_classifier.extract_entities(message)
            
            # Parse PDA request
            pda_request = self._parse_pda_request(message, entities)
            
            if not pda_request:
                return self._clarification_response(message)
            
            # Generate PDA analysis
            pda_analysis = self._generate_pda_analysis(pda_request)
            
            return {
                "agent": "PDA Management",
                "status": "success",
                "data": {
                    "request": pda_request,
                    "analysis": pda_analysis
                },
                "text": self._generate_pda_summary(pda_request, pda_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error in PDA management: {e}")
            return self._error_response(str(e))
    
    def _parse_pda_request(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Parse PDA management request."""
        message_lower = message.lower()
        
        # Extract ports
        ports = entities.get("ports", [])
        
        # Extract vessel type
        vessel_types = entities.get("vessels", [])
        
        # Extract cargo type
        cargo_types = entities.get("cargo", [])
        
        # Extract quantities
        quantities = entities.get("quantities", [])
        
        # Determine analysis type
        analysis_type = "estimate"
        if "track" in message_lower or "actual" in message_lower:
            analysis_type = "tracking"
        elif "compare" in message_lower or "vs" in message_lower:
            analysis_type = "comparison"
        elif "breakdown" in message_lower or "detail" in message_lower:
            analysis_type = "breakdown"
        
        # Extract time period
        time_period = "single_call"
        if "monthly" in message_lower or "quarterly" in message_lower:
            time_period = "monthly"
        elif "annual" in message_lower or "yearly" in message_lower:
            time_period = "annual"
        
        return {
            "ports": ports,
            "vessel_types": vessel_types,
            "cargo_types": cargo_types,
            "quantities": quantities,
            "analysis_type": analysis_type,
            "time_period": time_period
        }
    
    def _generate_pda_analysis(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive PDA analysis."""
        analysis = {}
        
        # Cost estimates
        if request["analysis_type"] in ["estimate", "breakdown"]:
            analysis["cost_estimates"] = self._estimate_pda_costs(request)
        
        # Cost tracking
        if request["analysis_type"] == "tracking":
            analysis["cost_tracking"] = self._track_pda_costs(request)
        
        # Port comparison
        if request["analysis_type"] == "comparison" and len(request["ports"]) > 1:
            analysis["port_comparison"] = self._compare_port_costs(request["ports"], request)
        
        # Cost breakdown
        if request["analysis_type"] == "breakdown":
            analysis["cost_breakdown"] = self._breakdown_pda_costs(request)
        
        # Budget planning
        if request["time_period"] in ["monthly", "annual"]:
            analysis["budget_planning"] = self._plan_budget(request)
        
        return analysis
    
    def _estimate_pda_costs(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate PDA costs for port calls."""
        estimates = {}
        
        for port in request["ports"]:
            port_lower = port.lower()
            
            # Determine region for cost multiplier
            region = self._get_port_region(port_lower)
            multiplier = self.regional_multipliers.get(region, 1.0)
            
            # Base costs (per call)
            base_costs = {
                "port_dues": 0.25 * multiplier,
                "pilotage": 0.15 * multiplier,
                "towage": 0.10 * multiplier,
                "berth_fees": 0.08 * multiplier,
                "agency_fees": 0.12 * multiplier,
                "documentation": 0.05 * multiplier,
                "communications": 0.03 * multiplier,
                "security": 0.06 * multiplier,
                "fresh_water": 0.04 * multiplier,
                "provisions": 0.07 * multiplier,
                "waste_disposal": 0.02 * multiplier
            }
            
            # Cargo-specific costs
            cargo_costs = {}
            if request["cargo_types"]:
                for cargo_type in request["cargo_types"]:
                    if cargo_type.lower() in ["coal", "iron_ore", "grain"]:
                        cargo_costs["stevedoring"] = 0.18 * multiplier
                        cargo_costs["equipment"] = 0.05 * multiplier
                    elif cargo_type.lower() in ["oil", "lng", "lpg"]:
                        cargo_costs["stevedoring"] = 0.22 * multiplier
                        cargo_costs["equipment"] = 0.08 * multiplier
                    else:
                        cargo_costs["stevedoring"] = 0.20 * multiplier
                        cargo_costs["equipment"] = 0.06 * multiplier
            
            # Vessel-specific adjustments
            vessel_adjustments = {}
            if request["vessel_types"]:
                for vessel_type in request["vessel_types"]:
                    vessel_lower = vessel_type.lower()
                    if vessel_lower in ["vlcc", "capesize"]:
                        vessel_adjustments["size_multiplier"] = 1.5
                    elif vessel_lower in ["panamax", "supramax"]:
                        vessel_adjustments["size_multiplier"] = 1.0
                    elif vessel_lower in ["handysize"]:
                        vessel_adjustments["size_multiplier"] = 0.8
            
            # Calculate total
            total_cost = sum(base_costs.values()) + sum(cargo_costs.values())
            
            # Apply vessel adjustments
            if vessel_adjustments:
                size_multiplier = vessel_adjustments.get("size_multiplier", 1.0)
                total_cost *= size_multiplier
            
            estimates[port] = {
                "base_costs": base_costs,
                "cargo_costs": cargo_costs,
                "vessel_adjustments": vessel_adjustments,
                "total_cost_per_call": round(total_cost, 2),
                "region": region,
                "multiplier": multiplier
            }
        
        return estimates
    
    def _track_pda_costs(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Track actual vs estimated PDA costs."""
        tracking = {}
        
        for port in request["ports"]:
            # Generate mock tracking data
            estimated = self._estimate_pda_costs({"ports": [port], "vessel_types": request["vessel_types"], "cargo_types": request["cargo_types"]})
            estimated_cost = estimated[port]["total_cost_per_call"]
            
            # Simulate actual costs with some variance
            import random
            variance = random.uniform(0.8, 1.2)
            actual_cost = estimated_cost * variance
            
            tracking[port] = {
                "estimated_cost": estimated_cost,
                "actual_cost": round(actual_cost, 2),
                "variance": round(((actual_cost - estimated_cost) / estimated_cost) * 100, 1),
                "status": "under_budget" if actual_cost <= estimated_cost else "over_budget",
                "recommendations": self._generate_cost_recommendations(actual_cost, estimated_cost)
            }
        
        return tracking
    
    def _compare_port_costs(self, ports: List[str], request: Dict[str, Any]) -> Dict[str, Any]:
        """Compare PDA costs across ports."""
        comparison = {}
        
        # Get cost estimates for all ports
        estimates = self._estimate_pda_costs(request)
        
        # Compare key metrics
        metrics = ["total_cost_per_call", "base_costs", "cargo_costs"]
        
        for metric in metrics:
            comparison[metric] = {}
            for port in ports:
                if port in estimates:
                    if metric == "total_cost_per_call":
                        comparison[metric][port] = estimates[port][metric]
                    else:
                        comparison[metric][port] = sum(estimates[port][metric].values())
                else:
                    comparison[metric][port] = "N/A"
        
        # Find cheapest and most expensive
        total_costs = {port: estimates[port]["total_cost_per_call"] for port in ports if port in estimates}
        if total_costs:
            cheapest_port = min(total_costs, key=total_costs.get)
            most_expensive_port = max(total_costs, key=total_costs.get)
            
            comparison["recommendations"] = [
                f"Most cost-effective: {cheapest_port} (${total_costs[cheapest_port]:.2f})",
                f"Highest cost: {most_expensive_port} (${total_costs[most_expensive_port]:.2f})",
                f"Cost range: ${min(total_costs.values()):.2f} - ${max(total_costs.values()):.2f}"
            ]
        
        return comparison
    
    def _breakdown_pda_costs(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Provide detailed cost breakdown."""
        breakdown = {}
        
        for port in request["ports"]:
            estimates = self._estimate_pda_costs({"ports": [port], "vessel_types": request["vessel_types"], "cargo_types": request["cargo_types"]})
            port_estimates = estimates[port]
            
            # Categorize costs
            categories = {
                "Port Charges": sum(port_estimates["base_costs"].values()),
                "Agency Services": 0,  # Would be calculated separately
                "Cargo Operations": sum(port_estimates["cargo_costs"].values()),
                "Supply Services": 0   # Would be calculated separately
            }
            
            # Calculate percentages
            total = sum(categories.values())
            percentages = {k: round((v / total) * 100, 1) if total > 0 else 0 for k, v in categories.items()}
            
            breakdown[port] = {
                "categories": categories,
                "percentages": percentages,
                "total": total,
                "cost_drivers": self._identify_cost_drivers(categories)
            }
        
        return breakdown
    
    def _plan_budget(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Plan budget for multiple port calls."""
        budget_plan = {}
        
        # Estimate costs for all ports
        estimates = self._estimate_pda_costs(request)
        
        # Calculate total budget
        total_budget = sum(estimates[port]["total_cost_per_call"] for port in estimates)
        
        # Apply time period multiplier
        if request["time_period"] == "monthly":
            time_multiplier = 4  # Assume 4 port calls per month
        elif request["time_period"] == "annual":
            time_multiplier = 48  # Assume 48 port calls per year
        else:
            time_multiplier = 1
        
        total_budget *= time_multiplier
        
        budget_plan = {
            "time_period": request["time_period"],
            "estimated_port_calls": time_multiplier,
            "total_budget": round(total_budget, 2),
            "monthly_average": round(total_budget / (time_multiplier / 4), 2) if time_multiplier > 4 else total_budget,
            "port_breakdown": estimates,
            "budget_recommendations": self._generate_budget_recommendations(total_budget, time_multiplier)
        }
        
        return budget_plan
    
    def _get_port_region(self, port: str) -> str:
        """Determine port region for cost calculations."""
        region_mapping = {
            "singapore": "asia",
            "shanghai": "asia",
            "mumbai": "asia",
            "rotterdam": "europe",
            "london": "europe",
            "houston": "americas",
            "santos": "americas",
            "fujairah": "middle_east",
            "cape_town": "africa"
        }
        
        return region_mapping.get(port, "asia")
    
    def _generate_cost_recommendations(self, actual: float, estimated: float) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        if actual > estimated * 1.1:  # 10% over budget
            recommendations.append("Review cost drivers and identify savings opportunities")
            recommendations.append("Negotiate better rates with service providers")
            recommendations.append("Optimize port call timing to reduce berth fees")
        
        if actual <= estimated * 0.9:  # 10% under budget
            recommendations.append("Excellent cost management - maintain current practices")
            recommendations.append("Consider if quality was compromised for cost savings")
        
        return recommendations
    
    def _identify_cost_drivers(self, categories: Dict[str, float]) -> List[str]:
        """Identify main cost drivers."""
        total = sum(categories.values())
        if total == 0:
            return []
        
        # Find categories above 25% of total
        drivers = []
        for category, cost in categories.items():
            if (cost / total) > 0.25:
                drivers.append(f"{category}: {round((cost / total) * 100, 1)}%")
        
        return drivers
    
    def _generate_budget_recommendations(self, total_budget: float, port_calls: int) -> List[str]:
        """Generate budget planning recommendations."""
        recommendations = []
        
        if port_calls > 20:
            recommendations.append("Consider annual contracts for volume discounts")
            recommendations.append("Implement standardized cost tracking across all ports")
        
        if total_budget > 10000:  # High budget threshold
            recommendations.append("Review high-cost ports for optimization opportunities")
            recommendations.append("Consider alternative routing to reduce port calls")
        
        recommendations.append("Monitor actual vs estimated costs monthly")
        recommendations.append("Maintain contingency budget of 10-15%")
        
        return recommendations
    
    def _generate_pda_summary(self, request: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate human-readable PDA summary."""
        summary = "PDA Management Summary\n"
        summary += "=" * 30 + "\n\n"
        
        # Cost estimates
        if "cost_estimates" in analysis:
            summary += "Cost Estimates:\n"
            for port, estimate in analysis["cost_estimates"].items():
                summary += f"• {port.title()}: ${estimate['total_cost_per_call']:.2f} per call\n"
                summary += f"  Region: {estimate['region'].title()}, Multiplier: {estimate['multiplier']:.1f}x\n"
            summary += "\n"
        
        # Cost tracking
        if "cost_tracking" in analysis:
            summary += "Cost Tracking:\n"
            for port, tracking in analysis["cost_tracking"].items():
                summary += f"• {port.title()}: Est. ${tracking['estimated_cost']:.2f}, Actual ${tracking['actual_cost']:.2f}\n"
                summary += f"  Variance: {tracking['variance']}% ({tracking['status']})\n"
            summary += "\n"
        
        # Port comparison
        if "port_comparison" in analysis:
            summary += "Port Cost Comparison:\n"
            comparison = analysis["port_comparison"]
            for metric, values in comparison.items():
                if metric != "recommendations":
                    summary += f"• {metric.replace('_', ' ').title()}:\n"
                    for port, value in values.items():
                        summary += f"  {port.title()}: ${value:.2f}\n"
            
            if comparison.get("recommendations"):
                summary += "\nRecommendations:\n"
                for rec in comparison["recommendations"]:
                    summary += f"• {rec}\n"
            summary += "\n"
        
        # Budget planning
        if "budget_planning" in analysis:
            budget = analysis["budget_planning"]
            summary += f"Budget Planning ({budget['time_period'].title()}):\n"
            summary += f"• Estimated Port Calls: {budget['estimated_port_calls']}\n"
            summary += f"• Total Budget: ${budget['total_budget']:,.2f}\n"
            summary += f"• Monthly Average: ${budget['monthly_average']:,.2f}\n"
            
            if budget.get("budget_recommendations"):
                summary += "\nBudget Recommendations:\n"
                for rec in budget["budget_recommendations"]:
                    summary += f"• {rec}\n"
        
        return summary
    
    def _clarification_response(self, message: str) -> Dict[str, Any]:
        """Request clarification for incomplete PDA requests."""
        return {
            "agent": "PDA Management",
            "status": "clarification_needed",
            "data": {
                "message": message,
                "analysis_types": ["estimate", "tracking", "comparison", "breakdown"]
            },
            "text": "I'd be happy to help with PDA management! Please specify which ports you're interested in and what type of analysis you need: cost estimates, cost tracking, port comparison, or detailed breakdown. For example: 'Estimate PDA costs for a Panamax vessel calling at Singapore and Rotterdam'."
        }
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Return error response."""
        return {
            "agent": "PDA Management",
            "status": "error",
            "data": {"error": error},
            "text": "I encountered an error analyzing PDA costs. Please try again with more specific details."
        } 