import api from './api';
import { Department } from '../types';

export const departmentService = {
  async getDepartments(): Promise<Department[]> {
    const response = await api.get<Department[]>('/departments');
    return response.data;
  },

  async getDepartment(departmentId: string): Promise<Department> {
    const response = await api.get<Department>(`/departments/${departmentId}`);
    return response.data;
  },

  async createDepartment(data: Partial<Department>): Promise<Department> {
    const response = await api.post<Department>('/departments', data);
    return response.data;
  },

  async updateDepartment(departmentId: string, data: Partial<Department>): Promise<Department> {
    const response = await api.put<Department>(`/departments/${departmentId}`, data);
    return response.data;
  }
};
