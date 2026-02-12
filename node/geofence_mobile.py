import logging
import math
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

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
        R = 6371.0  # Earth radius in km
        
        phi1, lam1 = math.radians(coord1.lat), math.radians(coord1.lon)
        phi2, lam2 = math.radians(coord2.lat), math.radians(coord2.lon)
        
        dphi = phi2 - phi1
        dlam = lam2 - lam1
        
        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

    def validate_node_location(self, node_loc: Coordinate, task_loc: Coordinate, mode: str = "mobile") -> bool:
        """
        Performs the boundary check.
        Returns True if the node is within the permissible range.
        """
        distance = self._haversine_distance(node_loc, task_loc)
        threshold = self.STATIONARY_DRIFT_THRESHOLD_KM if mode == "stationary" else self.DEFAULT_COURIER_RADIUS_KM
        
        if distance <= threshold:
            logging.info(f"✅ GEOFENCE_VALID: Node is {distance:.3f}km from target (Threshold: {threshold}km)")
            return True
        
        logging.error(f"🚨 GEOFENCE_VIOLATION: Node is {distance:.3f}km from target. Out of bounds!")
        return False

def initialize_geofence():
    """
    Entry point for the mobile SDK initialization.
    """
    logging.basicConfig(level=logging.INFO)
    logging.info("[*] Initializing Mobile Geofence Controller...")
    controller = GeofenceController()
    return controller

# --- Verification Status ---
# FIXED: The following lines are now properly commented to prevent SyntaxErrors:
# This file is now saved in your project structure at the specified path. 
# It is ready to be imported by your main task-dispatching logic!

if __name__ == "__main__":
    # Test initialization
    geo = initialize_geofence()
    # Mock check for London test case
    node = Coordinate(51.5074, -0.1278)
    task = Coordinate(51.5100, -0.1200)
    geo.validate_node_location(node, task)
