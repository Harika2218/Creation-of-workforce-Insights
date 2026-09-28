import api from './api';
import { PaginatedResponse, TimesheetRecord } from '../types';

export const timesheetService = {
  async getTimesheets(params: { page?: number; page_size?: number; employee_id?: string; project_id?: string; status?: string } = {}): Promise<PaginatedResponse<TimesheetRecord>> {
    const response = await api.get<PaginatedResponse<TimesheetRecord>>('/timesheets', { params });
    return response.data;
  },

  async createTimesheet(payload: { employee_id: string; project_id: string; date: string; hours_worked: number; billable_hours: number; non_billable_hours: number; task_description: string }): Promise<TimesheetRecord> {
    const response = await api.post<TimesheetRecord>('/timesheets', payload);
    return response.data;
  },

  async approveTimesheet(timesheetId: string): Promise<TimesheetRecord> {
    const response = await api.post<TimesheetRecord>(`/timesheets/${timesheetId}/approve`);
    return response.data;
  },

  async rejectTimesheet(timesheetId: string, rejectionReason: string): Promise<TimesheetRecord> {
    const response = await api.post<TimesheetRecord>(`/timesheets/${timesheetId}/reject`, { rejection_reason: rejectionReason });
    return response.data;
  }
};
