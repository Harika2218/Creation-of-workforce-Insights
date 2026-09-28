"""
HR Event Handlers
-----------------
Registers specialized event handlers with the EventBus to bridge domain actions.
"""

from backend.events.events import HREvent, HREventType
from backend.events.event_bus import get_event_bus
from backend.workflows.engine import get_workflow_engine

def initialize_event_handlers():
    """
    Subscribes the WorkflowEngine to all HR events.
    """
    engine = get_workflow_engine()
    engine.initialize()
    print("[EventHandlers] HR Event Handlers and Workflow Engine initialized.")
