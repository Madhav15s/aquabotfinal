"""
LLM API Connector for Phase 3
Advanced reasoning using Google Gemini
"""

import aiohttp
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class GeminiLLMAPI:
    """Advanced reasoning using Google Gemini API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-pro"
        self.cache = {}
        self.cache_duration = 3600  # 1 hour
        
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None, 
                              temperature: float = 0.7) -> Optional[Dict[str, Any]]:
        """Generate LLM response for complex maritime queries"""
        try:
            cache_key = f"llm_{hash(prompt)}_{hash(str(context))}"
            
            # Check cache
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now().timestamp() - cached_data["timestamp"] < self.cache_duration:
                    return cached_data["data"]
            
            # Prepare the request
            request_data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": self._build_maritime_prompt(prompt, context)
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
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
                        logger.error(f"Gemini API error: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return None
    
    async def analyze_maritime_scenario(self, scenario: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze complex maritime scenarios using LLM reasoning"""
        try:
            prompt = f"""
            Analyze the following maritime scenario and provide detailed insights:
            
            Scenario: {scenario}
            
            Available Data: {json.dumps(data, indent=2)}
            
            Please provide:
            1. Risk assessment
            2. Recommendations
            3. Alternative options
            4. Cost implications
            5. Timeline considerations
            
            Focus on maritime safety, efficiency, and commercial viability.
            """
            
            return await self.generate_response(prompt, {"scenario": scenario, "data": data})
            
        except Exception as e:
            logger.error(f"Error analyzing maritime scenario: {e}")
            return None
    
    async def optimize_route(self, origin: Dict[str, Any], destination: Dict[str, Any], 
                           constraints: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Optimize shipping route using LLM reasoning"""
        try:
            prompt = f"""
            Optimize a shipping route with the following parameters:
            
            Origin: {json.dumps(origin, indent=2)}
            Destination: {json.dumps(destination, indent=2)}
            Constraints: {json.dumps(constraints, indent=2)}
            
            Consider:
            1. Weather conditions
            2. Fuel efficiency
            3. Time constraints
            4. Safety factors
            5. Cost optimization
            
            Provide multiple route options with pros/cons for each.
            """
            
            return await self.generate_response(prompt, {
                "origin": origin,
                "destination": destination,
                "constraints": constraints
            })
            
        except Exception as e:
            logger.error(f"Error optimizing route: {e}")
            return None
    
    async def analyze_market_trends(self, market_data: Dict[str, Any], 
                                  analysis_type: str = "freight_rates") -> Optional[Dict[str, Any]]:
        """Analyze market trends using LLM reasoning"""
        try:
            prompt = f"""
            Analyze maritime market trends for {analysis_type}:
            
            Market Data: {json.dumps(market_data, indent=2)}
            
            Provide:
            1. Trend analysis
            2. Key drivers
            3. Future predictions
            4. Risk factors
            5. Strategic recommendations
            
            Focus on actionable insights for maritime operations.
            """
            
            return await self.generate_response(prompt, {
                "market_data": market_data,
                "analysis_type": analysis_type
            })
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {e}")
            return None
    
    async def generate_voyage_report(self, voyage_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate comprehensive voyage report using LLM"""
        try:
            prompt = f"""
            Generate a comprehensive voyage report based on:
            
            Voyage Data: {json.dumps(voyage_data, indent=2)}
            
            Include:
            1. Executive summary
            2. Route analysis
            3. Performance metrics
            4. Cost breakdown
            5. Recommendations
            6. Risk assessment
            
            Format as a professional maritime report.
            """
            
            return await self.generate_response(prompt, {"voyage_data": voyage_data})
            
        except Exception as e:
            logger.error(f"Error generating voyage report: {e}")
            return None
    
    def _build_maritime_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Build comprehensive maritime prompt with context"""
        base_prompt = f"""
        You are an expert maritime AI assistant with deep knowledge of:
        - Shipping operations and logistics
        - Maritime regulations and safety
        - Route optimization and navigation
        - Market analysis and commercial operations
        - Port operations and cargo handling
        
        User Query: {prompt}
        """
        
        if context:
            base_prompt += f"\n\nContext Information:\n{json.dumps(context, indent=2)}"
        
        base_prompt += """
        
        Please provide:
        1. Clear, actionable advice
        2. Maritime industry best practices
        3. Safety considerations
        4. Cost and efficiency analysis
        5. Alternative options when applicable
        
        Use maritime terminology appropriately and provide specific, practical recommendations.
        """
        
        return base_prompt
    
    def _parse_llm_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into standardized format"""
        try:
            candidates = raw_data.get("candidates", [])
            if not candidates:
                return {"error": "No response generated"}
            
            candidate = candidates[0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            
            if not parts:
                return {"error": "No content in response"}
            
            text = parts[0].get("text", "")
            
            # Try to extract structured information
            structured_data = self._extract_structured_data(text)
            
            return {
                "text": text,
                "structured_data": structured_data,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "usage": {
                    "prompt_tokens": raw_data.get("usageMetadata", {}).get("promptTokenCount", 0),
                    "response_tokens": raw_data.get("usageMetadata", {}).get("candidatesTokenCount", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return {"error": f"Failed to parse response: {str(e)}"}
    
    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from LLM text response"""
        try:
            structured_data = {}
            
            # Look for common patterns in maritime responses
            if "risk assessment" in text.lower():
                structured_data["risk_assessment"] = self._extract_section(text, "risk assessment")
            
            if "recommendations" in text.lower():
                structured_data["recommendations"] = self._extract_section(text, "recommendations")
            
            if "cost implications" in text.lower():
                structured_data["cost_analysis"] = self._extract_section(text, "cost")
            
            if "timeline" in text.lower():
                structured_data["timeline"] = self._extract_section(text, "timeline")
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return {}
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract specific section from text"""
        try:
            lines = text.split('\n')
            section_start = -1
            section_end = -1
            
            for i, line in enumerate(lines):
                if section_name.lower() in line.lower():
                    section_start = i
                    break
            
            if section_start == -1:
                return ""
            
            # Find end of section (next numbered item or end)
            for i in range(section_start + 1, len(lines)):
                if lines[i].strip().startswith(('1.', '2.', '3.', '4.', '5.')) or \
                   lines[i].strip().startswith(('•', '-', '*')) or \
                   lines[i].strip().upper() in ['RECOMMENDATIONS:', 'RISK ASSESSMENT:', 'COST ANALYSIS:']:
                    section_end = i
                    break
            
            if section_end == -1:
                section_end = len(lines)
            
            return '\n'.join(lines[section_start:section_end]).strip()
            
        except Exception as e:
            logger.error(f"Error extracting section: {e}")
            return ""
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_entries": len(self.cache),
            "cache_size_mb": sum(len(json.dumps(v)) for v in self.cache.values()) / 1024 / 1024,
            "oldest_entry": min(v["timestamp"] for v in self.cache.values()) if self.cache else None,
            "newest_entry": max(v["timestamp"] for v in self.cache.values()) if self.cache else None
        }
    
    def clear_cache(self):
        """Clear LLM cache"""
        self.cache.clear()
        logger.info("LLM cache cleared") 