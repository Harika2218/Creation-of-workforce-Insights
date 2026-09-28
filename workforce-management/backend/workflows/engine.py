"""
Workflow Engine Implementation
------------------------------
Listens to HR events from the EventBus, evaluates workflow rules,
executes associated actions, and records execution audit trails.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from database.mongodb import get_db
from backend.events.events import HREvent
from backend.events.event_bus import get_event_bus
from backend.workflows.rules import WorkflowRule, DEFAULT_WORKFLOW_RULES, evaluate_condition
from backend.workflows.actions import action_notify_employee, action_notify_manager, action_notify_hr

class WorkflowEngine:
    def __init__(self):
        self._rules: Dict[str, List[WorkflowRule]] = {}
        self._load_default_rules()
        self.initialize()

    def _load_default_rules(self):
        for rule in DEFAULT_WORKFLOW_RULES:
            self.register_rule(rule)

    def register_rule(self, rule: WorkflowRule):
        ev_type = rule.event_type
        if ev_type not in self._rules:
            self._rules[ev_type] = []
        self._rules[ev_type].append(rule)

    def get_all_rules(self) -> List[Dict[str, Any]]:
        rules = []
        for rule_list in self._rules.values():
            for r in rule_list:
                rules.append(r.model_dump())
        return rules

    def process_event(self, event: HREvent) -> Dict[str, Any]:
        """
        Matches event against active rules and executes actions.
        """
        ev_type_str = str(event.event_type)
        matching_rules = self._rules.get(ev_type_str, [])
        executed_actions = []

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        target_emp = event.target_employee_id or event.payload.get("employee_id")
        dedup_base = event.dedup_key or f"{ev_type_str}_{event.entity_id or target_emp}_{now_str[:10]}"

        for rule in matching_rules:
            if not rule.is_active:
                continue

            if not evaluate_condition(rule.conditions, event.payload):
                continue

            for action_name in rule.actions:
                try:
                    if action_name == "notify_employee" and target_emp:
                        res = action_notify_employee(
                            event_type=ev_type_str,
                            target_employee_id=target_emp,
                            payload=event.payload,
                            dedup_key=f"{rule.rule_id}_EMP_{dedup_base}"
                        )
                        executed_actions.append({"rule_id": rule.rule_id, "action": action_name, "status": "executed", "notification": res.get("notification_id") if res else None})

                    elif action_name == "notify_manager" and target_emp:
                        # If late arrival rule, only notify manager if late_minutes >= 15
                        if ev_type_str == "LATE_ARRIVAL" and event.payload.get("late_minutes", 0) < 15:
                            continue
                        res = action_notify_manager(
                            event_type=ev_type_str,
                            target_employee_id=target_emp,
                            payload=event.payload,
                            dedup_key=f"{rule.rule_id}_MGR_{dedup_base}"
                        )
                        executed_actions.append({"rule_id": rule.rule_id, "action": action_name, "status": "executed", "notification": res.get("notification_id") if res else None})

                    elif action_name == "notify_hr":
                        res = action_notify_hr(
                            event_type=ev_type_str,
                            payload=event.payload,
                            dedup_key=f"{rule.rule_id}_HR_{dedup_base}"
                        )
                        executed_actions.append({"rule_id": rule.rule_id, "action": action_name, "status": "executed", "notification": res.get("notification_id") if res else None})

                except Exception as e:
                    print(f"[ERROR] Workflow action '{action_name}' failed on rule '{rule.rule_id}': {e}")
                    executed_actions.append({"rule_id": rule.rule_id, "action": action_name, "status": "failed", "error": str(e)})

        # Record execution log in database
        db = get_db()
        try:
            db.workflow_executions.insert_one({
                "execution_id": f"WF_{uuid.uuid4().hex[:8].upper()}",
                "event_id": event.event_id,
                "event_type": ev_type_str,
                "timestamp": now_str,
                "rules_evaluated": len(matching_rules),
                "actions_executed": executed_actions
            })
        except Exception:
            pass

        return {
            "event_id": event.event_id,
            "rules_matched": len(matching_rules),
            "actions": executed_actions
        }

    def initialize(self):
        """Connects engine to listen to all events from the event bus."""
        bus = get_event_bus()
        bus.subscribe("*", self.process_event)


# Global singleton instance
_engine = WorkflowEngine()

def get_workflow_engine() -> WorkflowEngine:
    return _engine
