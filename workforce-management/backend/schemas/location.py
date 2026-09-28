"""
Pydantic Schemas for Multi-Location Workforce Management
--------------------------------------------------------
"""

from typing import Optional, List
from pydantic import BaseModel, Field

class LocationBase(BaseModel):
    name: str = Field(..., description="Office or campus name")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State or province")
    country: str = Field(default="India", description="Country")
    latitude: float = Field(..., description="Geofence center latitude")
    longitude: float = Field(..., description="Geofence center longitude")
    geofence_radius_meters: float = Field(default=500.0, description="Allowed punch radius in meters")
    timezone: str = Field(default="Asia/Kolkata", description="Local timezone")

class LocationResponse(LocationBase):
    location_id: str
    employee_count: Optional[int] = 0
    active_shifts_count: Optional[int] = 0

class LocationCreate(LocationBase):
    location_id: str = Field(..., description="Unique location identifier (e.g. LOC06)")

class LocationGeofenceUpdate(BaseModel):
    latitude: float
    longitude: float
    geofence_radius_meters: float = Field(ge=50.0, le=5000.0, description="Radius between 50m and 5000m")

class LocationDetailResponse(LocationResponse):
    departments: List[str] = Field(default_factory=list, description="Departments present at location")
    holidays_count: int = 0
