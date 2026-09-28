"""
Inbound Webhook Security & Dispatch Handler
-------------------------------------------
Verifies HMAC-SHA256 signatures, validates timestamp replay windows,
enforces deduplication idempotency, and dispatches external events.
"""

import hmac
import hashlib
import time
import json
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from database.mongodb import get_db
from backend.config import settings
from backend.events.event_bus import get_event_bus
from backend.events.events import HREvent, HREventType

class WebhookSecurity:
    @staticmethod
    def verify_signature(
        payload_bytes: bytes,
        signature: str,
        secret: Optional[str] = None
    ) -> bool:
        """
        Verifies HMAC-SHA256 signature against provided or configured secret.
        Uses constant-time comparison to prevent timing side-channel attacks.
        """
        key = (secret or settings.WEBHOOK_SIGNING_SECRET).encode("utf-8")
        computed = hmac.new(key, payload_bytes, hashlib.sha256).hexdigest()

        # Handle prefix e.g. "sha256=..."
        clean_sig = signature.replace("sha256=", "").strip()
        return hmac.compare_digest(computed, clean_sig)

    @staticmethod
    def verify_timestamp(timestamp_str: Optional[str], tolerance_seconds: int = 300) -> bool:
        """
        Validates that webhook timestamp is within tolerance window (default 5m)
        to prevent replay attacks.
        """
        if not timestamp_str:
            return True  # If provider does not pass timestamp header, rely on signature
        try:
            ts = float(timestamp_str)
            now = time.time()
            return abs(now - ts) <= tolerance_seconds
        except ValueError:
            return False

class WebhookDispatcher:
    @staticmethod
    def process_incoming_webhook(
        provider: str,
        event_type: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None,
        timestamp_header: Optional[str] = None,
        raw_body: Optional[bytes] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates and ingests an inbound webhook from an external system.
        """
        db = get_db()

        # 1. Signature Verification
        if signature and raw_body:
            if not WebhookSecurity.verify_signature(raw_body, signature):
                return False, "INVALID_SIGNATURE: HMAC verification failed.", {}

        # 2. Replay Protection
        if timestamp_header and not WebhookSecurity.verify_timestamp(timestamp_header):
            return False, "TIMESTAMP_EXPIRED: Webhook exceeds replay window.", {}

        # 3. Deduplication Check
        event_id = payload.get("event_id") or payload.get("id") or f"{provider}_{int(time.time())}_{hash(json.dumps(payload, sort_keys=True))}"
        dedup_key = f"WH_{provider}_{event_id}"

        existing = db.webhook_inbound_logs.find_one({"dedup_key": dedup_key})
        if existing:
            return True, "IDEMPOTENT_SKIP: Event already processed.", {"dedup_key": dedup_key}

        # 4. Record inbound log
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        db.webhook_inbound_logs.insert_one({
            "dedup_key": dedup_key,
            "provider": provider,
            "event_type": event_type,
            "payload": payload,
            "received_at": now_str,
            "status": "PROCESSED"
        })

        # 5. Dispatch to internal EventBus if mapped
        if provider == "biometric" or event_type == "biometric_punch":
            from backend.integrations.biometric.biometric_connector import BiometricDeviceConnector
            result = BiometricDeviceConnector().process_punch(payload)
            return True, f"Punch processed: {result.get('status')}", result

        return True, "Webhook accepted and logged.", {"dedup_key": dedup_key, "event_id": event_id}
