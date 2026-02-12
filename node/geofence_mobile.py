import math
from dataclasses import dataclass
from typing import Dict, Optional

# PROXY PROTOCOL - MOBILE GEOFENCE CONTROLLER (v1.0)
# "Hardening the Physical Runtime for Couriers."
# ----------------------------------------------------

@dataclass
class Coordinate:
    lat: float
    lon: float

class GeofenceController:
    """
    Validates the proximity of a Human Node to a task location.
    Supports both stationary and mobile (Courier) enforcement modes.
    """
    
    def __init__(self):
        # Configuration as per Protocol Specs
        self.STATIONARY_DRIFT_THRESHOLD_KM = 0.5  # 500m for fixed addresses
        self.DEFAULT_COURIER_RADIUS_KM = 20.0     # City-wide default
        
    def _haversine_distance(self, coord1: Coordinate, coord2: Coordinate) -> float:
        """
        Calculates the great-circle distance between two points in kilometers.
        Using the Haversine formula for spherical distance calculation.
        """
        R = 6371.0  # Earth radius in kilometers

        dlat = math.radians(coord2.lat - coord1.lat)
        dlon = math.radians(coord2.lon - coord1.lon)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(coord1.lat)) * math.cos(math.radians(coord2.lat)) * math.sin(dlon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def validate_locality(
        self, 
        current_lat: float, 
        current_lon: float, 
        target_lat: float, 
        target_lon: float,
        is_mobile_node: bool = False,
        custom_radius: Optional[float] = None
    ) -> Dict:
        """
        Main validation logic for task dispatch and execution.
        
        Args:
            current_lat/lon: Hardware-attested coordinates (from heartbeat)
            target_lat/lon: The physical address of the task
            is_mobile_node: Boolean toggling Stationary vs Courier logic
            custom_radius: Specific radius for the task (if provided by Agent)
        """
        node_pos = Coordinate(current_lat, current_lon)
        task_pos = Coordinate(target_lat, target_lon)
        
        distance = self._haversine_distance(node_pos, task_pos)
        
        # Determine allowed radius based on node type
        if custom_radius:
            allowed_radius = custom_radius
        elif is_mobile_node:
            allowed_radius = self.DEFAULT_COURIER_RADIUS_KM
        else:
            allowed_radius = self.STATIONARY_DRIFT_THRESHOLD_KM

        is_valid = distance <= allowed_radius
        
        return {
            "status": "VALID" if is_valid else "PX_401_VIOLATION",
            "distance_km": round(distance, 3),
            "allowed_radius_km": allowed_radius,
            "error_code": None if is_valid else "PX_401",
            "remediation": "Move closer to task boundary or refresh hardware heartbeat." if not is_valid else None
        }


This file is now saved in your project structure at the specified path. It is ready to be imported by your main task-dispatching logic!
