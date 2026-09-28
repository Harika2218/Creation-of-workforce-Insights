"""
Integration Synchronization Engine
----------------------------------
Orchestrates background and manual data synchronization across external systems.
Maintains persistent synchronization audit history in MongoDB `integration_sync_history`.
"""

import time
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from database.mongodb import get_db
from backend.integrations.base.connector import BaseConnector
from backend.integrations.base.models import SyncResult

class SyncManager:
    """Manages execution and audit persistence of integration synchronization runs."""

    @staticmethod
    def execute_sync(connector: BaseConnector, options: Optional[Dict[str, Any]] = None) -> SyncResult:
        db = get_db()
        sync_id = f"SYNC_{connector.name.upper()}_{int(time.time())}_{uuid.uuid4().hex[:4].upper()}"
        started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # Record initial RUNNING state
        sync_record = {
            "sync_id": sync_id,
            "integration": connector.name,
            "status": "RUNNING",
            "started_at": started_at,
            "completed_at": None,
            "records_read": 0,
            "records_created": 0,
            "records_updated": 0,
            "records_failed": 0,
            "error_summary": None,
            "options": options or {}
        }
        db.integration_sync_history.insert_one(sync_record)

        try:
            # Execute connector sync logic
            result = connector.sync(options)
            completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            db.integration_sync_history.update_one(
                {"sync_id": sync_id},
                {"$set": {
                    "status": result.status,
                    "completed_at": completed_at,
                    "records_read": result.records_read,
                    "records_created": result.records_created,
                    "records_updated": result.records_updated,
                    "records_failed": result.records_failed,
                    "error_summary": result.error_summary
                }}
            )
            connector.record_success()
            result.sync_id = sync_id
            return result

        except Exception as e:
            completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            err_msg = str(e)
            db.integration_sync_history.update_one(
                {"sync_id": sync_id},
                {"$set": {
                    "status": "FAILED",
                    "completed_at": completed_at,
                    "error_summary": err_msg
                }}
            )
            connector.record_failure(err_msg)
            return SyncResult(
                sync_id=sync_id,
                integration=connector.name,
                status="FAILED",
                started_at=started_at,
                completed_at=completed_at,
                error_summary=err_msg
            )

    @staticmethod
    def get_sync_history(integration: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        db = get_db()
        query = {"integration": integration} if integration else {}
        records = list(db.integration_sync_history.find(query, {"_id": 0}).sort("started_at", -1).limit(limit))
        return records
