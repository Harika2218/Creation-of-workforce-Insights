import api from './api';
import { AttendanceRecord, AttendanceSummary, PaginatedResponse } from '../types';

export interface AttendanceFilters {
  page?: number;
  page_size?: number;
  employee_id?: string;
  department_id?: string;
  date?: string;
  status?: string;
  attendance_method?: string;
}

export interface CheckInPayload {
  employee_id: string;
  attendance_method: 'Biometric' | 'GPS' | 'Web';
  latitude?: number;
  longitude?: number;
}

export interface CheckOutPayload {
  employee_id: string;
}

export const attendanceService = {
  async getAttendance(params: AttendanceFilters = {}): Promise<PaginatedResponse<AttendanceRecord>> {
    const response = await api.get<PaginatedResponse<AttendanceRecord>>('/attendance', { params });
    return response.data;
  },

  async getAttendanceSummary(date?: string): Promise<AttendanceSummary> {
    const response = await api.get<AttendanceSummary>('/attendance/summary', { params: { date } });
    return response.data;
  },

  async getEmployeeAttendance(employeeId: string, limit: number = 30): Promise<AttendanceRecord[]> {
    const response = await api.get<AttendanceRecord[]>(`/attendance/${employeeId}`, { params: { limit } });
    return response.data;
  },

  async checkIn(payload: CheckInPayload): Promise<AttendanceRecord> {
    const response = await api.post<AttendanceRecord>('/attendance/check-in', payload);
    return response.data;
  },

  async checkOut(payload: CheckOutPayload): Promise<AttendanceRecord> {
    const response = await api.post<AttendanceRecord>('/attendance/check-out', payload);
    return response.data;
  }
};
