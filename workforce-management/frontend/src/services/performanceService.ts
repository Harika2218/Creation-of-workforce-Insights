import api from './api';
import { PerformanceReview } from '../types';

export const performanceService = {
  async getPerformanceReviews(): Promise<PerformanceReview[]> {
    const response = await api.get<PerformanceReview[]>('/performance');
    return response.data;
  },

  async getEmployeePerformance(employeeId: string): Promise<PerformanceReview[]> {
    const response = await api.get<PerformanceReview[]>(`/performance/${employeeId}`);
    return response.data;
  },

  async createPerformanceReview(payload: { employee_id: string; review_cycle: string; rating_score: number; kpis?: Record<string, number>; feedback: string; goals?: string[] }): Promise<PerformanceReview> {
    const response = await api.post<PerformanceReview>('/performance', payload);
    return response.data;
  }
};
