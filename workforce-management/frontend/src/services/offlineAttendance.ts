/**
 * Offline Attendance Safety & Queue Management
 * --------------------------------------------
 * Strict Safety Invariant:
 * 1. An offline punch is NEVER marked as 'Present' or 'Approved' locally.
 * 2. It is saved with status 'PENDING_SERVER_VERIFICATION'.
 * 3. The employee is explicitly informed that official attendance requires
 *    server-side identity, timestamp, shift, and GPS geofence validation.
 * 4. When connectivity is restored, events are securely synchronized.
 */

import { CheckInPayload, CheckOutPayload, attendanceService } from './attendanceService';

export interface PendingPunchEvent {
  event_id: string;
  employee_id: string;
  action_type: 'CHECK_IN' | 'CHECK_OUT';
  attendance_method: 'GPS' | 'Biometric' | 'Web';
  local_timestamp: string;
  latitude?: number;
  longitude?: number;
  status: 'PENDING_SERVER_VERIFICATION' | 'SYNC_FAILED';
  error_message?: string;
  attempts: number;
}

export interface SyncOutcome {
  event_id: string;
  success: boolean;
  message: string;
  attendance_record?: any;
}

const STORAGE_KEY = 'hrvantage_pending_attendance_v1';

class OfflineAttendanceManager {
  public getPendingPunches(): PendingPunchEvent[] {
    if (typeof window === 'undefined') return [];
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  public enqueuePendingPunch(
    employeeId: string,
    actionType: 'CHECK_IN' | 'CHECK_OUT',
    method: 'GPS' | 'Biometric' | 'Web',
    coords?: { latitude: number; longitude: number }
  ): PendingPunchEvent {
    const event: PendingPunchEvent = {
      event_id: `PENDING_${Date.now()}_${Math.random().toString(36).substring(2, 7).toUpperCase()}`,
      employee_id: employeeId,
      action_type: actionType,
      attendance_method: method,
      local_timestamp: new Date().toISOString(),
      latitude: coords?.latitude,
      longitude: coords?.longitude,
      status: 'PENDING_SERVER_VERIFICATION',
      attempts: 0,
    };

    const current = this.getPendingPunches();
    current.push(event);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(current));
    return event;
  }

  public removePendingPunch(eventId: string): void {
    const current = this.getPendingPunches().filter((p) => p.event_id !== eventId);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(current));
  }

  public updatePendingPunch(eventId: string, updates: Partial<PendingPunchEvent>): void {
    const current = this.getPendingPunches().map((p) => {
      if (p.event_id === eventId) {
        return { ...p, ...updates };
      }
      return p;
    });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(current));
  }

  public clearAllPending(): void {
    localStorage.removeItem(STORAGE_KEY);
  }

  /**
   * Synchronizes all queued punches through the authoritative backend.
   */
  public async syncPendingQueue(): Promise<SyncOutcome[]> {
    const pending = this.getPendingPunches();
    if (pending.length === 0) return [];

    const outcomes: SyncOutcome[] = [];

    for (const punch of pending) {
      try {
        let res: any = null;
        if (punch.action_type === 'CHECK_IN') {
          const payload: CheckInPayload = {
            employee_id: punch.employee_id,
            attendance_method: punch.attendance_method,
            latitude: punch.latitude,
            longitude: punch.longitude,
          };
          res = await attendanceService.checkIn(payload);
        } else {
          const payload: CheckOutPayload = {
            employee_id: punch.employee_id,
          };
          res = await attendanceService.checkOut(payload);
        }

        // Successfully verified by server
        this.removePendingPunch(punch.event_id);
        outcomes.push({
          event_id: punch.event_id,
          success: true,
          message: `Official ${punch.action_type} confirmed by server.`,
          attendance_record: res,
        });
      } catch (err: any) {
        const errorDetail = err.response?.data?.detail || err.message || 'Server verification failed';
        this.updatePendingPunch(punch.event_id, {
          status: 'SYNC_FAILED',
          error_message: errorDetail,
          attempts: (punch.attempts || 0) + 1,
        });

        outcomes.push({
          event_id: punch.event_id,
          success: false,
          message: errorDetail,
        });
      }
    }

    return outcomes;
  }
}

export const offlineAttendanceManager = new OfflineAttendanceManager();
export default offlineAttendanceManager;
