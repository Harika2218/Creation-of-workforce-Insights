import api from './api';
import { PaginatedResponse, PayrollRecord, PayrollSummary } from '../types';

export const payrollService = {
  async getPayrollSummary(month?: string): Promise<PayrollSummary> {
    const response = await api.get<PayrollSummary>('/payroll/summary', { params: { month } });
    return response.data;
  },

  async getPayrollRecords(params: { page?: number; page_size?: number; month?: string; employee_id?: string } = {}): Promise<PaginatedResponse<PayrollRecord>> {
    const response = await api.get<PaginatedResponse<PayrollRecord>>('/payroll', { params });
    return response.data;
  },

  async getEmployeePayroll(employeeId: string): Promise<PayrollRecord[]> {
    const response = await api.get<PayrollRecord[]>(`/payroll/employee/${employeeId}`);
    return response.data;
  },

  async getPayslip(payrollId: string): Promise<PayrollRecord> {
    const response = await api.get<PayrollRecord>(`/payroll/${payrollId}`);
    return response.data;
  }
};
