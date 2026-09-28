"""
Event Dispatcher Helper
-----------------------
Utility function for core routers and services to trigger HR events with minimal boilerplate.
"""

from typing import Optional, Dict, Any
from backend.events.events import HREvent, HREventType
from backend.events.event_bus import get_event_bus

def dispatch_event(
    event_type: HREventType,
    entity_type: str,
    entity_id: Optional[str] = None,
    target_employee_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    actor_id: Optional[str] = "SYSTEM",
    dedup_key: Optional[str] = None
) -> HREvent:
    """
    Constructs an HREvent and dispatches it through the global event bus.
    """
    bus = get_event_bus()
    event = HREvent(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        target_employee_id=target_employee_id,
        payload=payload or {},
        actor_id=actor_id or "SYSTEM",
        dedup_key=dedup_key
    )
    bus.publish(event)
    return event
