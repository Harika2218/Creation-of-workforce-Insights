import api from './api';

export const reportService = {
  async getAttendanceReport(): Promise<Record<string, unknown>> {
    const response = await api.get<Record<string, unknown>>('/reports/attendance');
    return response.data;
  },

  async getOvertimeReport(): Promise<Record<string, unknown>> {
    const response = await api.get<Record<string, unknown>>('/reports/overtime');
    return response.data;
  },

  async getLeaveReport(): Promise<Record<string, unknown>> {
    const response = await api.get<Record<string, unknown>>('/reports/leave');
    return response.data;
  },

  async getPayrollReport(): Promise<Record<string, unknown>> {
    const response = await api.get<Record<string, unknown>>('/reports/payroll');
    return response.data;
  },

  async getDepartmentPerformanceReport(): Promise<Record<string, unknown>> {
    const response = await api.get<Record<string, unknown>>('/reports/department-performance');
    return response.data;
  }
};
