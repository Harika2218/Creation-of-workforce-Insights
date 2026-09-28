import api from './api';
import { ShiftSchedule, ShiftSwapRequest, ShiftTemplate } from '../types';

export const shiftService = {
  async getShifts(): Promise<ShiftTemplate[]> {
    const response = await api.get<ShiftTemplate[]>('/shifts');
    return response.data;
  },

  async getEmployeeShifts(employeeId: string): Promise<ShiftSchedule[]> {
    const response = await api.get<ShiftSchedule[]>(`/shifts/employee/${employeeId}`);
    return response.data;
  },

  async assignShift(payload: { employee_id: string; shift_id: string; start_date: string; end_date: string }): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/shifts/assign', payload);
    return response.data;
  },

  async getSwapRequests(): Promise<ShiftSwapRequest[]> {
    const response = await api.get<ShiftSwapRequest[]>('/shifts/swap-requests');
    return response.data;
  },

  async submitSwapRequest(payload: { target_employee_id: string; requestor_shift_date: string; target_shift_date: string; reason: string }): Promise<ShiftSwapRequest> {
    const response = await api.post<ShiftSwapRequest>('/shifts/swap-request', payload);
    return response.data;
  },

  async updateSwapRequest(swapId: string, status: 'Approved' | 'Rejected'): Promise<ShiftSwapRequest> {
    const response = await api.put<ShiftSwapRequest>(`/shifts/swap-requests/${swapId}`, { status });
    return response.data;
  }
};
