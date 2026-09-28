import api from './api';
import { HRSummaryMetrics } from '../types';

export const hrService = {
  async getHRSummary(): Promise<HRSummaryMetrics> {
    const response = await api.get<HRSummaryMetrics>('/hr/summary');
    return response.data;
  },

  async getHREmployeeSummary(): Promise<Record<string, unknown>> {
    const response = await api.get<Record<string, unknown>>('/hr/employee-summary');
    return response.data;
  }
};
