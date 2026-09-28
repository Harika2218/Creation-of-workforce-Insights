import api from './api';
import { Employee, EmployeeProfile, PaginatedResponse } from '../types';

export interface EmployeeFilters {
  page?: number;
  page_size?: number;
  department_id?: string;
  role?: string;
  location_id?: string;
  employment_status?: string;
  search?: string;
}

export const employeeService = {
  async getEmployees(params: EmployeeFilters = {}): Promise<PaginatedResponse<Employee>> {
    const response = await api.get<PaginatedResponse<Employee>>('/employees', { params });
    return response.data;
  },

  async getEmployee(employeeId: string): Promise<Employee> {
    const response = await api.get<Employee>(`/employees/${employeeId}`);
    return response.data;
  },

  async getEmployeeProfile(employeeId: string): Promise<EmployeeProfile> {
    const response = await api.get<EmployeeProfile>(`/employees/${employeeId}/profile`);
    return response.data;
  },

  async createEmployee(data: Partial<Employee>): Promise<Employee> {
    const response = await api.post<Employee>('/employees', data);
    return response.data;
  },

  async updateEmployee(employeeId: string, data: Partial<Employee>): Promise<Employee> {
    const response = await api.put<Employee>(`/employees/${employeeId}`, data);
    return response.data;
  },

  async deactivateEmployee(employeeId: string): Promise<{ message: string }> {
    const response = await api.delete<{ message: string }>(`/employees/${employeeId}`);
    return response.data;
  }
};
