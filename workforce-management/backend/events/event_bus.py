"""
Event Bus Implementation
------------------------
Pub/Sub event bus for registering handlers, publishing events,
and logging all workflow events to MongoDB.
"""

import asyncio
from typing import Callable, Dict, List, Any
from datetime import datetime, timezone
import inspect
from database.mongodb import get_db
from backend.events.events import HREvent, HREventType

class EventBus:
    """
    Central event dispatch broker for HR automation events.
    """
    def __init__(self):
        self._handlers: Dict[str, List[Callable[[HREvent], Any]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[HREvent], Any]):
        """Subscribe a callable handler to an event type (or '*' for all events)."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[HREvent], Any]):
        """Remove a subscriber."""
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    def publish(self, event: HREvent) -> Dict[str, Any]:
        """
        Synchronously dispatch an event to all matching subscribers
        and persist the event in the database for auditability.
        """
        db = get_db()
        event_dict = event.model_dump()

        # Persist event in workflow_events collection
        try:
            db.workflow_events.insert_one(event_dict)
            event_dict.pop("_id", None)
        except Exception as e:
            print(f"[WARN] Failed to record event in workflow_events: {e}")

        # Gather targets: specific event handlers + wildcard handlers
        targets = list(self._handlers.get(str(event.event_type), []))
        targets.extend(self._handlers.get("*", []))

        results = []
        for handler in targets:
            try:
                if inspect.iscoroutinefunction(handler):
                    # In sync context, run loop or task
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.create_task(handler(event))
                            results.append({"handler": handler.__name__, "status": "scheduled_async"})
                        else:
                            loop.run_until_complete(handler(event))
                            results.append({"handler": handler.__name__, "status": "executed"})
                    except RuntimeError:
                        asyncio.run(handler(event))
                        results.append({"handler": handler.__name__, "status": "executed"})
                else:
                    res = handler(event)
                    results.append({"handler": handler.__name__, "status": "executed", "result": res})
            except Exception as e:
                print(f"[ERROR] Event handler '{getattr(handler, '__name__', str(handler))}' failed: {e}")
                results.append({"handler": getattr(handler, '__name__', str(handler)), "status": "failed", "error": str(e)})

        return {
            "event_id": event.event_id,
            "event_type": str(event.event_type),
            "handlers_executed": len(results),
            "details": results
        }

    async def publish_async(self, event: HREvent) -> Dict[str, Any]:
        """Asynchronously dispatch an event to all registered handlers."""
        db = get_db()
        event_dict = event.model_dump()
        try:
            db.workflow_events.insert_one(event_dict)
            event_dict.pop("_id", None)
        except Exception as e:
            print(f"[WARN] Failed to record event in workflow_events: {e}")

        targets = list(self._handlers.get(str(event.event_type), []))
        targets.extend(self._handlers.get("*", []))

        results = []
        for handler in targets:
            try:
                if inspect.iscoroutinefunction(handler):
                    res = await handler(event)
                else:
                    res = handler(event)
                results.append({"handler": getattr(handler, '__name__', str(handler)), "status": "executed", "result": res})
            except Exception as e:
                print(f"[ERROR] Event handler '{getattr(handler, '__name__', str(handler))}' failed: {e}")
                results.append({"handler": getattr(handler, '__name__', str(handler)), "status": "failed", "error": str(e)})

        return {
            "event_id": event.event_id,
            "event_type": str(event.event_type),
            "handlers_executed": len(results),
            "details": results
        }


# Global singleton instance
_event_bus = EventBus()

def get_event_bus() -> EventBus:
    return _event_bus
