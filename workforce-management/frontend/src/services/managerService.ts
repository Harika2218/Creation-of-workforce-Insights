import api from './api';
import { AttendanceRecord, Employee, LeaveRequest, ManagerTeamSummary, ShiftSchedule } from '../types';

export const managerService = {
  async getTeam(): Promise<Employee[]> {
    const response = await api.get<Employee[]>('/manager/team');
    return response.data;
  },

  async getTeamSummary(): Promise<ManagerTeamSummary> {
    const response = await api.get<ManagerTeamSummary>('/manager/team/summary');
    return response.data;
  },

  async getTeamAttendance(): Promise<AttendanceRecord[]> {
    const response = await api.get<AttendanceRecord[]>('/manager/team/attendance');
    return response.data;
  },

  async getTeamLeave(): Promise<LeaveRequest[]> {
    const response = await api.get<LeaveRequest[]>('/manager/team/leave');
    return response.data;
  },

  async getTeamShifts(): Promise<ShiftSchedule[]> {
    const response = await api.get<ShiftSchedule[]>('/manager/team/shifts');
    return response.data;
  }
};
