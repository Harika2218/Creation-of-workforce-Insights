"""
HR Event System Package
-----------------------
Event definitions, event bus, and dispatcher.
"""

from backend.events.events import HREventType, HREvent
from backend.events.event_bus import get_event_bus, EventBus
from backend.events.dispatcher import dispatch_event

__all__ = [
    "HREventType",
    "HREvent",
    "get_event_bus",
    "EventBus",
    "dispatch_event"
]
