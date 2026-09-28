"""
Notifications & Preferences Router
-----------------------------------
REST & WebSocket endpoints for in-app alerts, unread counts, mark-as-read,
notification preferences, and live delivery.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, HTTPException, status, Depends, Query, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from database.mongodb import get_db
from backend.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUnreadCountResponse,
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate
)
from backend.schemas.common import MessageResponse
from backend.auth.dependencies import get_current_user
from backend.auth.security import decode_access_token
from backend.notifications.service import NotificationService
from backend.notifications.preferences import NotificationPreferencesService
from backend.notifications.channels import ws_manager

router = APIRouter(prefix="/notifications", tags=["Notifications"])

_service = NotificationService()
_pref_service = NotificationPreferencesService()

# -------------------------------------------------------------------
# 1. Query Notifications
# -------------------------------------------------------------------
@router.get("", response_model=List[NotificationResponse], summary="Get current user notifications")
async def get_my_notifications(
    unread_only: bool = False,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    emp_id = current_user.get("employee_id") or current_user.get("user_id")
    items, _ = _service.get_user_notifications(
        employee_id=emp_id,
        unread_only=unread_only,
        category=category,
        priority=priority,
        search=search,
        page=page,
        page_size=page_size
    )
    return items

@router.get("/unread-count", response_model=NotificationUnreadCountResponse, summary="Get unread notifications count")
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    emp_id = current_user.get("employee_id") or current_user.get("user_id")
    count = _service.get_unread_count(emp_id)
    return {"unread_count": count}

@router.get("/{notification_id}", response_model=NotificationResponse, summary="Get notification by ID")
async def get_notification_details(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    emp_id = current_user.get("employee_id") or current_user.get("user_id")
    role = current_user.get("role", "EMPLOYEE")
    notif = _service.get_notification_by_id(notification_id, emp_id, role)
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification '{notification_id}' not found or access denied."
        )
    return notif

# -------------------------------------------------------------------
# 2. Mutate Notifications (Send & Read Markers)
# -------------------------------------------------------------------
@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED, summary="Send notification to employee")
async def send_notification(payload: NotificationCreate, current_user: dict = Depends(get_current_user)):
    notif = _service.create_notification(
        recipient_employee_id=payload.employee_id,
        event_type=payload.type or "INFO",
        title=payload.title,
        message=payload.message,
        priority=payload.priority,
        category=payload.category,
        action_url=payload.action_url,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id
    )
    if not notif:
        # If user preferences blocked it, still record minimally for API response
        db = get_db()
        notif_id = f"NOT_{uuid.uuid4().hex[:8].upper()}"
        notif = {
            "notification_id": notif_id,
            "employee_id": payload.employee_id,
            "category": payload.category,
            "title": payload.title,
            "message": payload.message,
            "priority": payload.priority or "normal",
            "type": payload.type or "INFO",
            "action_url": payload.action_url,
            "is_read": 0,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        }
        db.notifications.insert_one(notif)
        notif.pop("_id", None)
    return notif

@router.put("/{notification_id}/read", response_model=MessageResponse, summary="Mark notification as read (PUT)")
async def mark_as_read_put(notification_id: str, current_user: dict = Depends(get_current_user)):
    emp_id = current_user.get("employee_id") or current_user.get("user_id")
    success = _service.mark_as_read(notification_id, emp_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return {"message": "Notification marked as read.", "success": True}

@router.patch("/{notification_id}/read", response_model=MessageResponse, summary="Mark notification as read (PATCH)")
async def mark_as_read_patch(notification_id: str, current_user: dict = Depends(get_current_user)):
    emp_id = current_user.get("employee_id") or current_user.get("user_id")
    success = _service.mark_as_read(notification_id, emp_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return {"message": "Notification marked as read.", "success": True}

@router.patch("/read-all", response_model=MessageResponse, summary="Mark all notifications as read (PATCH)")
async def mark_all_as_read_patch(current_user: dict = Depends(get_current_user)):
    emp_id = current_user.get("employee_id") or current_user.get("user_id")
    count = _service.mark_all_as_read(emp_id)
    return {"message": f"Marked {count} notifications as read.", "success": True}

@router.post("/read-all", response_model=MessageResponse, summary="Mark all notifications as read (POST)")
async def mark_all_as_read_post(current_user: dict = Depends(get_current_user)):
    emp_id = current_user.get("employee_id") or current_user.get("user_id")
    count = _service.mark_all_as_read(emp_id)
    return {"message": f"Marked {count} notifications as read.", "success": True}

# -------------------------------------------------------------------
# 3. Notification Preferences (also under /notifications/preferences)
# -------------------------------------------------------------------
@router.get("/preferences", response_model=NotificationPreferencesResponse, summary="Get notification preferences")
async def get_my_preferences(current_user: dict = Depends(get_current_user)):
    emp_id = current_user.get("employee_id") or current_user.get("user_id")
    return _pref_service.get_preferences(emp_id)

@router.put("/preferences", response_model=NotificationPreferencesResponse, summary="Update notification preferences")
async def update_my_preferences(
    payload: NotificationPreferencesUpdate,
    current_user: dict = Depends(get_current_user)
):
    emp_id = current_user.get("employee_id") or current_user.get("user_id")
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    return _pref_service.update_preferences(emp_id, updates)

# -------------------------------------------------------------------
# 4. Real-Time WebSocket Delivery
# -------------------------------------------------------------------
@router.websocket("/ws")
async def notification_websocket(websocket: WebSocket, token: Optional[str] = Query(None)):
    """
    WebSocket endpoint for instant live push delivery of user notifications.
    Authenticates client using JWT token query parameter.
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    emp_id = payload.get("employee_id") or payload.get("sub")
    await ws_manager.connect(emp_id, websocket)

    try:
        # Send initial connection handshake confirmation
        unread = _service.get_unread_count(emp_id)
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "employee_id": emp_id,
            "unread_count": unread,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        })

        # Keep socket open and process any incoming ping/pong
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(emp_id, websocket)
    except Exception:
        ws_manager.disconnect(emp_id, websocket)
