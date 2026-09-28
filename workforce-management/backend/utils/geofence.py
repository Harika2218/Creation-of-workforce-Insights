"""
Advanced Geofencing & Telemetry Anomaly Utility
----------------------------------------------
Calculates distances using the Haversine formula, verifies multi-campus
geofences, and detects suspicious / impossible travel velocity between punches.
"""

import math
from typing import Tuple, Optional, Dict, Any, List
from datetime import datetime

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great circle distance between two points in meters.
    """
    R = 6371000.0  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2

    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def is_within_geofence(
    user_lat: float, user_lon: float,
    target_lat: float, target_lon: float,
    radius_meters: float = 500.0
) -> Tuple[bool, float]:
    """
    Checks if a user is within the allowed geofence radius.
    Returns (is_within, distance_in_meters).
    """
    dist = haversine_distance_meters(user_lat, user_lon, target_lat, target_lon)
    return (dist <= radius_meters), round(dist, 2)

def validate_multi_campus_geofence(
    user_lat: float, user_lon: float,
    assigned_location: Dict[str, Any],
    all_locations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Checks if user is at their assigned campus or at another authorized company campus.
    Returns structured verification result with closest campus.
    """
    assigned_lat = assigned_location.get("latitude", 0.0)
    assigned_lon = assigned_location.get("longitude", 0.0)
    assigned_radius = assigned_location.get("geofence_radius_meters", 500.0)
    
    is_at_home, home_dist = is_within_geofence(user_lat, user_lon, assigned_lat, assigned_lon, assigned_radius)
    if is_at_home:
        return {
            "valid": True,
            "campus_type": "HOME_CAMPUS",
            "location_id": assigned_location.get("location_id"),
            "distance_meters": home_dist,
            "allowed_radius": assigned_radius
        }
    
    # Check if visiting another valid branch campus
    closest_loc = None
    min_dist = float("inf")
    for loc in all_locations:
        l_lat = loc.get("latitude", 0.0)
        l_lon = loc.get("longitude", 0.0)
        l_radius = loc.get("geofence_radius_meters", 500.0)
        is_in, dist = is_within_geofence(user_lat, user_lon, l_lat, l_lon, l_radius)
        if dist < min_dist:
            min_dist = dist
            closest_loc = loc
        if is_in:
            return {
                "valid": True,
                "campus_type": "BRANCH_CAMPUS_VISIT",
                "location_id": loc.get("location_id"),
                "distance_meters": dist,
                "allowed_radius": l_radius
            }
            
    # Outside all company campuses
    return {
        "valid": False,
        "campus_type": "OUTSIDE_GEOFENCE",
        "closest_location_id": closest_loc.get("location_id") if closest_loc else None,
        "distance_meters": round(min_dist, 2),
        "allowed_radius": assigned_radius
    }

def detect_impossible_movement(
    prev_lat: float, prev_lon: float, prev_timestamp_iso: str,
    curr_lat: float, curr_lon: float, curr_timestamp_iso: str,
    max_realistic_kmh: float = 800.0
) -> Tuple[bool, float, float]:
    """
    Detects impossible physical movement / mock GPS teleportation between consecutive punches.
    Returns (is_impossible, speed_kmh, distance_km).
    """
    try:
        t1 = datetime.fromisoformat(prev_timestamp_iso.replace("Z", "+00:00"))
        t2 = datetime.fromisoformat(curr_timestamp_iso.replace("Z", "+00:00"))
        delta_seconds = abs((t2 - t1).total_seconds())
        if delta_seconds < 1.0:
            delta_seconds = 1.0  # avoid division by zero
    except Exception:
        return False, 0.0, 0.0

    dist_meters = haversine_distance_meters(prev_lat, prev_lon, curr_lat, curr_lon)
    dist_km = dist_meters / 1000.0
    time_hours = delta_seconds / 3600.0
    speed_kmh = dist_km / time_hours

    # Flag as impossible if travel speed exceeds realistic commercial flight velocity
    is_impossible = (speed_kmh > max_realistic_kmh and dist_km > 5.0)
    return is_impossible, round(speed_kmh, 1), round(dist_km, 2)
