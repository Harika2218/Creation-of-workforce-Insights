import api from './api';
import { Holiday } from '../types';

export const holidayService = {
  async getHolidays(): Promise<Holiday[]> {
    const response = await api.get<Holiday[]>('/holidays');
    return response.data;
  },

  async createHoliday(payload: { holiday_id: string; holiday_name: string; date: string; location_id?: string | null; type: string }): Promise<Holiday> {
    const response = await api.post<Holiday>('/holidays', payload);
    return response.data;
  },

  async deleteHoliday(holidayId: string): Promise<{ message: string }> {
    const response = await api.delete<{ message: string }>(`/holidays/${holidayId}`);
    return response.data;
  }
};
