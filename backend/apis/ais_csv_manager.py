"""
CSV-Based AIS Data Manager
Continuous vessel tracking with CSV storage and real-time updates
"""

import csv
import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import asyncio
import pandas as pd

logger = logging.getLogger(__name__)

class AISCSVManager:
    """Manages AIS data using CSV files with continuous updates"""
    
    def __init__(self, data_dir: str = "data/ais"):
        self.data_dir = data_dir
        self.vessels_file = os.path.join(data_dir, "vessels.csv")
        self.positions_file = os.path.join(data_dir, "positions.csv")
        self.routes_file = os.path.join(data_dir, "routes.csv")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize vessel database
        self.vessel_database = self._initialize_vessel_database()
        
        # Start continuous updates
        self.update_interval = 300  # 5 minutes
        self.is_updating = False
        
    def _initialize_vessel_database(self) -> List[Dict[str, Any]]:
        """Initialize vessel database with realistic data"""
        vessels = [
            {
                "mmsi": "123456789",
                "name": "EVER GIVEN",
                "imo": "9811000",
                "call_sign": "3EZA4",
                "vessel_type": "Container Ship",
                "length": 400.0,
                "width": 59.0,
                "max_draught": 16.0,
                "home_port": "Tokyo",
                "operator": "Evergreen Marine",
                "status": "active"
            },
            {
                "mmsi": "987654321",
                "name": "COSCO SHIPPING UNIVERSE",
                "imo": "9811001",
                "call_sign": "3EZA5",
                "vessel_type": "Container Ship",
                "length": 366.0,
                "width": 51.0,
                "max_draught": 16.8,
                "home_port": "Shanghai",
                "operator": "COSCO Shipping",
                "status": "active"
            },
            {
                "mmsi": "456789123",
                "name": "MSC OSCAR",
                "imo": "9811002",
                "call_sign": "3EZA6",
                "vessel_type": "Container Ship",
                "length": 395.0,
                "width": 59.0,
                "max_draught": 16.5,
                "home_port": "Geneva",
                "operator": "MSC",
                "status": "active"
            },
            {
                "mmsi": "789123456",
                "name": "CMA CGM MARCO POLO",
                "imo": "9811003",
                "call_sign": "3EZA7",
                "vessel_type": "Container Ship",
                "length": 396.0,
                "width": 53.0,
                "max_draught": 16.0,
                "home_port": "Marseille",
                "operator": "CMA CGM",
                "status": "active"
            },
            {
                "mmsi": "321654987",
                "name": "MAERSK MC-KINNEY MOLLER",
                "imo": "9811004",
                "call_sign": "3EZA8",
                "vessel_type": "Container Ship",
                "length": 400.0,
                "width": 59.0,
                "max_draught": 16.0,
                "home_port": "Copenhagen",
                "operator": "Maersk",
                "status": "active"
            }
        ]
        
        # Save vessels to CSV
        self._save_vessels_to_csv(vessels)
        return vessels
    
    def _save_vessels_to_csv(self, vessels: List[Dict[str, Any]]):
        """Save vessel database to CSV"""
        try:
            with open(self.vessels_file, 'w', newline='', encoding='utf-8') as csvfile:
                if vessels:
                    fieldnames = vessels[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(vessels)
            logger.info(f"Saved {len(vessels)} vessels to {self.vessels_file}")
        except Exception as e:
            logger.error(f"Error saving vessels to CSV: {e}")
    
    def _save_position_to_csv(self, position_data: Dict[str, Any]):
        """Save vessel position to CSV"""
        try:
            # Create file with headers if it doesn't exist
            file_exists = os.path.exists(self.positions_file)
            
            with open(self.positions_file, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = position_data.keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(position_data)
                
        except Exception as e:
            logger.error(f"Error saving position to CSV: {e}")
    
    def _save_route_to_csv(self, route_data: List[Dict[str, Any]]):
        """Save vessel route to CSV"""
        try:
            # Create file with headers if it doesn't exist
            file_exists = os.path.exists(self.routes_file)
            
            with open(self.routes_file, 'a', newline='', encoding='utf-8') as csvfile:
                if route_data:
                    fieldnames = route_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    if not file_exists:
                        writer.writeheader()
                    
                    writer.writerows(route_data)
                    
        except Exception as e:
            logger.error(f"Error saving route to CSV: {e}")
    
    def _generate_realistic_position(self, vessel: Dict[str, Any], base_position: Dict[str, float]) -> Dict[str, Any]:
        """Generate realistic vessel position with movement simulation"""
        try:
            # Simulate vessel movement based on time
            current_time = datetime.now()
            time_factor = (current_time.hour + current_time.minute / 60) / 24  # 0-1 over 24 hours
            
            # Calculate new position (simulate sailing)
            lat_offset = random.uniform(-0.01, 0.01) * time_factor
            lon_offset = random.uniform(-0.01, 0.01) * time_factor
            
            new_lat = base_position["latitude"] + lat_offset
            new_lon = base_position["longitude"] + lon_offset
            
            # Simulate realistic speed and course changes
            base_speed = random.uniform(15, 25)
            speed_variation = random.uniform(-2, 2)
            new_speed = max(0, base_speed + speed_variation)
            
            base_course = random.uniform(0, 360)
            course_variation = random.uniform(-5, 5)
            new_course = (base_course + course_variation) % 360
            
            return {
                "timestamp": current_time.isoformat(),
                "mmsi": vessel["mmsi"],
                "vessel_name": vessel["name"],
                "latitude": round(new_lat, 6),
                "longitude": round(new_lon, 6),
                "speed_over_ground": round(new_speed, 1),
                "course_over_ground": round(new_course, 1),
                "heading": round(new_course, 1),
                "draught": round(random.uniform(14, 16), 1),
                "destination": self._get_current_destination(vessel, new_lat, new_lon),
                "eta": self._calculate_eta(vessel, new_lat, new_lon, new_speed)
            }
            
        except Exception as e:
            logger.error(f"Error generating realistic position: {e}")
            return {}
    
    def _get_current_destination(self, vessel: Dict[str, Any], lat: float, lon: float) -> str:
        """Get current destination based on vessel position"""
        # Simple destination logic based on position
        if lat > 50:  # Northern Europe
            return "Rotterdam"
        elif lat > 30:  # Mediterranean
            return "Suez Canal"
        elif lat > 0:  # Asia
            return "Singapore"
        else:  # Southern Hemisphere
            return "Santos"
    
    def _calculate_eta(self, vessel: Dict[str, Any], lat: float, lon: float, speed: float) -> str:
        """Calculate estimated time of arrival"""
        try:
            # Simple ETA calculation (in real implementation, use actual route)
            base_time = datetime.now()
            estimated_hours = random.uniform(48, 168)  # 2-7 days
            eta_time = base_time + timedelta(hours=estimated_hours)
            return eta_time.isoformat()
        except Exception:
            return "Unknown"
    
    async def update_all_vessel_positions(self):
        """Update positions for all vessels"""
        try:
            current_time = datetime.now()
            logger.info(f"Updating vessel positions at {current_time}")
            
            for vessel in self.vessel_database:
                # Get base position for this vessel
                base_position = self._get_base_position(vessel["name"])
                if base_position:
                    # Generate new realistic position
                    new_position = self._generate_realistic_position(vessel, base_position)
                    if new_position:
                        # Save to CSV
                        self._save_position_to_csv(new_position)
                        
                        # Update vessel database
                        vessel["current_position"] = new_position
                        
                        logger.debug(f"Updated position for {vessel['name']}: {new_position['latitude']}, {new_position['longitude']}")
            
            logger.info("Vessel position update completed")
            
        except Exception as e:
            logger.error(f"Error updating vessel positions: {e}")
    
    def _get_base_position(self, vessel_name: str) -> Optional[Dict[str, float]]:
        """Get base position for vessel"""
        base_positions = {
            "EVER GIVEN": {"latitude": 1.3521, "longitude": 103.8198},  # Singapore
            "COSCO SHIPPING UNIVERSE": {"latitude": 31.2304, "longitude": 121.4737},  # Shanghai
            "MSC OSCAR": {"latitude": 51.9225, "longitude": 4.4792},  # Rotterdam
            "CMA CGM MARCO POLO": {"latitude": -23.9608, "longitude": -46.3339},  # Santos
            "MAERSK MC-KINNEY MOLLER": {"latitude": 35.6762, "longitude": 139.6503}  # Tokyo
        }
        return base_positions.get(vessel_name)
    
    async def start_continuous_updates(self):
        """Start continuous vessel position updates"""
        if self.is_updating:
            logger.warning("Continuous updates already running")
            return
        
        self.is_updating = True
        logger.info("Starting continuous vessel position updates")
        
        try:
            while self.is_updating:
                await self.update_all_vessel_positions()
                await asyncio.sleep(self.update_interval)
                
        except Exception as e:
            logger.error(f"Error in continuous updates: {e}")
            self.is_updating = False
    
    def stop_continuous_updates(self):
        """Stop continuous vessel position updates"""
        self.is_updating = False
        logger.info("Stopped continuous vessel position updates")
    
    def get_latest_positions(self) -> List[Dict[str, Any]]:
        """Get latest positions for all vessels"""
        try:
            if not os.path.exists(self.positions_file):
                return []
            
            # Read CSV and get latest position for each vessel
            df = pd.read_csv(self.positions_file)
            if df.empty:
                return []
            
            # Get latest position for each vessel
            latest_positions = []
            for vessel in self.vessel_database:
                vessel_positions = df[df['mmsi'] == vessel['mmsi']]
                if not vessel_positions.empty:
                    latest = vessel_positions.iloc[-1].to_dict()
                    latest_positions.append(latest)
            
            return latest_positions
            
        except Exception as e:
            logger.error(f"Error getting latest positions: {e}")
            return []
    
    def get_vessel_history(self, mmsi: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get vessel position history"""
        try:
            if not os.path.exists(self.positions_file):
                return []
            
            df = pd.read_csv(self.positions_file)
            if df.empty:
                return []
            
            # Filter by MMSI and time
            vessel_data = df[df['mmsi'] == mmsi]
            if vessel_data.empty:
                return []
            
            # Convert to list of dictionaries
            history = vessel_data.to_dict('records')
            
            # Limit to requested hours (simplified)
            return history[-min(hours * 12, len(history)):]  # Assume 5-minute intervals
            
        except Exception as e:
            logger.error(f"Error getting vessel history: {e}")
            return []
    
    def get_csv_stats(self) -> Dict[str, Any]:
        """Get CSV file statistics"""
        try:
            stats = {
                "vessels_file": {
                    "exists": os.path.exists(self.vessels_file),
                    "size_bytes": os.path.getsize(self.vessels_file) if os.path.exists(self.vessels_file) else 0
                },
                "positions_file": {
                    "exists": os.path.exists(self.positions_file),
                    "size_bytes": os.path.getsize(self.positions_file) if os.path.exists(self.positions_file) else 0
                },
                "routes_file": {
                    "exists": os.path.exists(self.routes_file),
                    "size_bytes": os.path.getsize(self.routes_file) if os.path.exists(self.routes_file) else 0
                },
                "total_vessels": len(self.vessel_database),
                "update_interval_seconds": self.update_interval,
                "continuous_updates_running": self.is_updating
            }
            
            # Calculate CSV row counts
            if os.path.exists(self.positions_file):
                try:
                    with open(self.positions_file, 'r') as f:
                        stats["positions_file"]["row_count"] = sum(1 for line in f) - 1  # Subtract header
                except:
                    stats["positions_file"]["row_count"] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting CSV stats: {e}")
            return {"error": str(e)}
    
    def export_to_json(self, output_file: str = "data/ais/export.json"):
        """Export all data to JSON format"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "vessels": self.vessel_database,
                "latest_positions": self.get_latest_positions(),
                "csv_stats": self.get_csv_stats()
            }
            
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False 