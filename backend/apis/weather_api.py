"""
Weather API Connector for Phase 3
Route optimization using OpenWeatherMap
"""

import aiohttp
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import math
import asyncio

logger = logging.getLogger(__name__)

class OpenWeatherMapAPI:
    """Weather data connector using OpenWeatherMap API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geo_url = "http://api.openweathermap.org/geo/1.0"
        self.cache = {}
        self.cache_duration = 1800  # 30 minutes
        
    async def get_current_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get current weather conditions for specific coordinates"""
        try:
            cache_key = f"current_{lat:.2f}_{lon:.2f}"
            
            # Check cache
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now().timestamp() - cached_data["timestamp"] < self.cache_duration:
                    return cached_data["data"]
            
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"  # Use metric units for maritime operations
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        weather_data = self._parse_current_weather(data)
                        
                        # Cache the result
                        self.cache[cache_key] = {
                            "data": weather_data,
                            "timestamp": datetime.now().timestamp()
                        }
                        
                        return weather_data
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
            return None
    
    async def get_forecast(self, lat: float, lon: float, days: int = 5) -> Optional[Dict[str, Any]]:
        """Get weather forecast for specific coordinates"""
        try:
            cache_key = f"forecast_{lat:.2f}_{lon:.2f}_{days}"
            
            # Check cache
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now().timestamp() - cached_data["timestamp"] < self.cache_duration:
                    return cached_data["data"]
            
            url = f"{self.base_url}/forecast"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "cnt": min(days * 8, 40)  # 3-hour intervals, max 40
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        forecast_data = self._parse_forecast(data)
                        
                        # Cache the result
                        self.cache[cache_key] = {
                            "data": forecast_data,
                            "timestamp": datetime.now().timestamp()
                        }
                        
                        return forecast_data
                    else:
                        logger.error(f"Weather forecast API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting weather forecast: {e}")
            return None
    
    async def get_marine_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get marine-specific weather data including waves and currents"""
        try:
            cache_key = f"marine_{lat:.2f}_{lon:.2f}"
            
            # Check cache
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now().timestamp() - cached_data["timestamp"] < self.cache_duration:
                    return cached_data["data"]
            
            # Get current weather and forecast
            current = await self.get_current_weather(lat, lon)
            forecast = await self.get_forecast(lat, lon, 3)
            
            if current and forecast:
                marine_data = self._combine_marine_data(current, forecast)
                
                # Cache the result
                self.cache[cache_key] = {
                    "data": marine_data,
                    "timestamp": datetime.now().timestamp()
                }
                
                return marine_data
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting marine weather: {e}")
            return None
    
    async def get_route_weather(self, route_points: List[Tuple[float, float]], 
                               interval_hours: int = 6) -> List[Dict[str, Any]]:
        """Get weather data along a route at specified intervals"""
        try:
            route_weather = []
            
            for i, (lat, lon) in enumerate(route_points):
                # Get weather for this point
                weather = await self.get_current_weather(lat, lon)
                if weather:
                    route_weather.append({
                        "point_index": i,
                        "coordinates": {"lat": lat, "lon": lon},
                        "weather": weather,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Add delay to avoid rate limiting
                if i < len(route_points) - 1:
                    await asyncio.sleep(0.1)
            
            return route_weather
            
        except Exception as e:
            logger.error(f"Error getting route weather: {e}")
            return []
    
    async def get_storm_alerts(self, lat: float, lon: float, radius_km: float = 500) -> List[Dict[str, Any]]:
        """Get storm and severe weather alerts for an area"""
        try:
            # This would use OpenWeatherMap's OneCall API for alerts
            # For now, we'll simulate based on current conditions
            current = await self.get_current_weather(lat, lon)
            
            alerts = []
            if current:
                # Check for severe conditions
                wind_speed = current.get("wind", {}).get("speed", 0)
                visibility = current.get("visibility", 10000)
                
                if wind_speed > 25:  # > 25 m/s (Beaufort 10+)
                    alerts.append({
                        "type": "high_wind",
                        "severity": "warning",
                        "description": f"High winds: {wind_speed} m/s",
                        "coordinates": {"lat": lat, "lon": lon},
                        "timestamp": datetime.now().isoformat()
                    })
                
                if visibility < 5000:  # < 5km
                    alerts.append({
                        "type": "low_visibility",
                        "severity": "caution",
                        "description": f"Low visibility: {visibility/1000:.1f} km",
                        "coordinates": {"lat": lat, "lon": lon},
                        "timestamp": datetime.now().isoformat()
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting storm alerts: {e}")
            return []
    
    def _parse_current_weather(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse current weather data into standardized format"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "coordinates": {
                    "lat": raw_data.get("coord", {}).get("lat"),
                    "lon": raw_data.get("coord", {}).get("lon")
                },
                "temperature": {
                    "current": raw_data.get("main", {}).get("temp"),
                    "feels_like": raw_data.get("main", {}).get("feels_like"),
                    "min": raw_data.get("main", {}).get("temp_min"),
                    "max": raw_data.get("main", {}).get("temp_max")
                },
                "humidity": raw_data.get("main", {}).get("humidity"),
                "pressure": raw_data.get("main", {}).get("pressure"),
                "visibility": raw_data.get("visibility"),
                "wind": {
                    "speed": raw_data.get("wind", {}).get("speed"),
                    "direction": raw_data.get("wind", {}).get("deg"),
                    "gust": raw_data.get("wind", {}).get("gust")
                },
                "weather": {
                    "main": raw_data.get("weather", [{}])[0].get("main"),
                    "description": raw_data.get("weather", [{}])[0].get("description"),
                    "icon": raw_data.get("weather", [{}])[0].get("icon")
                },
                "clouds": raw_data.get("clouds", {}).get("all"),
                "rain": raw_data.get("rain", {}).get("1h", 0),
                "snow": raw_data.get("snow", {}).get("1h", 0)
            }
        except Exception as e:
            logger.error(f"Error parsing current weather: {e}")
            return {}
    
    def _parse_forecast(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse forecast data into standardized format"""
        try:
            forecasts = []
            for item in raw_data.get("list", []):
                forecast = {
                    "timestamp": item.get("dt"),
                    "datetime": datetime.fromtimestamp(item.get("dt")).isoformat(),
                    "temperature": {
                        "current": item.get("main", {}).get("temp"),
                        "feels_like": item.get("main", {}).get("feels_like"),
                        "min": item.get("main", {}).get("temp_min"),
                        "max": item.get("main", {}).get("temp_max")
                    },
                    "humidity": item.get("main", {}).get("humidity"),
                    "pressure": item.get("main", {}).get("pressure"),
                    "wind": {
                        "speed": item.get("wind", {}).get("speed"),
                        "direction": item.get("wind", {}).get("deg")
                    },
                    "weather": {
                        "main": item.get("weather", [{}])[0].get("main"),
                        "description": item.get("weather", [{}])[0].get("description")
                    },
                    "clouds": item.get("clouds", {}).get("all"),
                    "rain": item.get("rain", {}).get("3h", 0),
                    "snow": item.get("snow", {}).get("3h", 0)
                }
                forecasts.append(forecast)
            
            return {
                "location": {
                    "name": raw_data.get("city", {}).get("name"),
                    "country": raw_data.get("city", {}).get("country"),
                    "coordinates": {
                        "lat": raw_data.get("city", {}).get("coord", {}).get("lat"),
                        "lon": raw_data.get("city", {}).get("coord", {}).get("lon")
                    }
                },
                "forecasts": forecasts
            }
            
        except Exception as e:
            logger.error(f"Error parsing forecast: {e}")
            return {}
    
    def _combine_marine_data(self, current: Dict[str, Any], forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Combine current and forecast data for marine operations"""
        try:
            return {
                "current": current,
                "forecast": forecast,
                "marine_conditions": {
                    "wind_conditions": self._assess_wind_conditions(current, forecast),
                    "visibility_conditions": self._assess_visibility_conditions(current, forecast),
                    "storm_risk": self._assess_storm_risk(current, forecast),
                    "route_recommendation": self._get_route_recommendation(current, forecast)
                }
            }
        except Exception as e:
            logger.error(f"Error combining marine data: {e}")
            return {}
    
    def _assess_wind_conditions(self, current: Dict[str, Any], forecast: Dict[str, Any]) -> str:
        """Assess wind conditions for maritime operations"""
        try:
            wind_speed = current.get("wind", {}).get("speed", 0)
            
            if wind_speed < 5:
                return "calm"
            elif wind_speed < 10:
                return "light"
            elif wind_speed < 20:
                return "moderate"
            elif wind_speed < 30:
                return "strong"
            else:
                return "severe"
        except Exception:
            return "unknown"
    
    def _assess_visibility_conditions(self, current: Dict[str, Any], forecast: Dict[str, Any]) -> str:
        """Assess visibility conditions for maritime operations"""
        try:
            visibility = current.get("visibility", 10000)
            
            if visibility > 10000:
                return "excellent"
            elif visibility > 5000:
                return "good"
            elif visibility > 2000:
                return "moderate"
            elif visibility > 1000:
                return "poor"
            else:
                return "very_poor"
        except Exception:
            return "unknown"
    
    def _assess_storm_risk(self, current: Dict[str, Any], forecast: Dict[str, Any]) -> str:
        """Assess storm risk for maritime operations"""
        try:
            wind_speed = current.get("wind", {}).get("speed", 0)
            rain = current.get("rain", 0)
            
            if wind_speed > 25 or rain > 10:
                return "high"
            elif wind_speed > 15 or rain > 5:
                return "medium"
            else:
                return "low"
        except Exception:
            return "unknown"
    
    def _get_route_recommendation(self, current: Dict[str, Any], forecast: Dict[str, Any]) -> str:
        """Get route recommendation based on weather conditions"""
        try:
            wind_conditions = self._assess_wind_conditions(current, forecast)
            visibility_conditions = self._assess_visibility_conditions(current, forecast)
            storm_risk = self._assess_storm_risk(current, forecast)
            
            if storm_risk == "high" or wind_conditions == "severe":
                return "avoid_area"
            elif wind_conditions == "strong" or visibility_conditions == "poor":
                return "exercise_caution"
            elif wind_conditions == "moderate" or visibility_conditions == "moderate":
                return "proceed_with_care"
            else:
                return "safe_to_proceed"
        except Exception:
            return "unknown"
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_entries": len(self.cache),
            "cache_size_mb": sum(len(json.dumps(v)) for v in self.cache.values()) / 1024 / 1024,
            "oldest_entry": min(v["timestamp"] for v in self.cache.values()) if self.cache else None,
            "newest_entry": max(v["timestamp"] for v in self.cache.values()) if self.cache else None
        }
    
    def clear_cache(self):
        """Clear weather cache"""
        self.cache.clear()
        logger.info("Weather cache cleared") 