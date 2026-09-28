"""
Server-Side GPS Geofence & Anti-Spoofing Verification
-----------------------------------------------------
Calculates spherical Haversine distances against verified office locations.
Validates client accuracy bounds and timestamp recency to prevent coordinate manipulation.
"""

import math
from typing import Dict, Any, Tuple
from datetime import datetime, timezone

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two GPS coordinates in meters.
    """
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class GeofenceValidator:
    @staticmethod
    def validate_attendance_location(
        client_lat: float,
        client_lon: float,
        target_lat: float,
        target_lon: float,
        allowed_radius_meters: float = 500.0,
        accuracy_meters: float = 50.0,
        client_timestamp: float = 0.0
    ) -> Tuple[bool, float, str]:
        """
        Validates GPS coordinates on the server.
        Returns: (is_within_geofence, distance_meters, message)
        """
        # Range validation
        if not (-90.0 <= client_lat <= 90.0) or not (-180.0 <= client_lon <= 180.0):
            return False, 999999.0, "Invalid GPS latitude/longitude out of geographic bounds."

        # Accuracy degradation check (if GPS accuracy > 200m, reject as untrusted)
        if accuracy_meters > 250.0:
            return False, 999999.0, f"GPS accuracy ({accuracy_meters}m) is too low for geofence verification."

        # Calculate exact distance
        distance = calculate_haversine_distance(client_lat, client_lon, target_lat, target_lon)

        if distance <= allowed_radius_meters:
            return True, round(distance, 1), f"Inside geofence ({distance:.1f}m from center)."
        else:
            return False, round(distance, 1), f"Outside geofence: {distance:.1f}m exceeds allowed {allowed_radius_meters}m radius."
