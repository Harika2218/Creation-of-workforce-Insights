import api from './api';
import { LeaveBalance, LeaveRequest, PaginatedResponse } from '../types';

export const leaveService = {
  async getLeaveTypes(): Promise<string[]> {
    const response = await api.get<string[]>('/leave/types');
    return response.data;
  },

  async getLeaveBalances(employeeId: string): Promise<LeaveBalance> {
    const response = await api.get<any[]>(`/leave/balance/${employeeId}`);
    const items = response.data || [];
    const balanceMap: any = {
      employee_id: employeeId,
      annual_leave: 18,
      sick_leave: 10,
      casual_leave: 8,
      emergency_leave: 5,
    };
    items.forEach((item) => {
      const type = (item.leave_type || '').toLowerCase();
      const remaining = item.remaining_days ?? item.allocated_days ?? 0;
      if (type.includes('annual')) balanceMap.annual_leave = remaining;
      else if (type.includes('sick')) balanceMap.sick_leave = remaining;
      else if (type.includes('casual')) balanceMap.casual_leave = remaining;
      else if (type.includes('emergency')) balanceMap.emergency_leave = remaining;
    });
    return balanceMap as LeaveBalance;
  },

  async getLeaveRequests(params: { page?: number; page_size?: number; employee_id?: string; status?: string } = {}): Promise<PaginatedResponse<LeaveRequest>> {
    const response = await api.get<PaginatedResponse<LeaveRequest>>('/leave/requests', { params });
    return response.data;
  },

  async applyLeave(payload: { employee_id: string; leave_type: string; start_date: string; end_date: string; reason: string }): Promise<LeaveRequest> {
    const response = await api.post<LeaveRequest>('/leave/requests', payload);
    return response.data;
  },

  async approveLeave(leaveId: string): Promise<LeaveRequest> {
    const response = await api.post<LeaveRequest>(`/leave/requests/${leaveId}/approve`);
    return response.data;
  },

  async rejectLeave(leaveId: string, rejectionReason: string): Promise<LeaveRequest> {
    const response = await api.post<LeaveRequest>(`/leave/requests/${leaveId}/reject`, { rejection_reason: rejectionReason });
    return response.data;
  }
};
