import api from './api';
import { EmployeeSkill, SkillItem, TrainingProgram, TrainingRecord } from '../types';

export const skillService = {
  async getSkills(): Promise<SkillItem[]> {
    const response = await api.get<SkillItem[]>('/skills');
    return response.data;
  },

  async getEmployeeSkills(employeeId: string): Promise<EmployeeSkill[]> {
    const response = await api.get<EmployeeSkill[]>(`/skills/employee/${employeeId}`);
    return response.data;
  },

  async addEmployeeSkill(employeeId: string, payload: { skill_id: string; proficiency_level: string; years_experience: number }): Promise<EmployeeSkill> {
    const response = await api.post<EmployeeSkill>(`/skills/employee/${employeeId}`, payload);
    return response.data;
  },

  async getTrainingPrograms(): Promise<TrainingProgram[]> {
    const response = await api.get<TrainingProgram[]>('/training/programs');
    return response.data;
  },

  async getTrainingRecords(): Promise<TrainingRecord[]> {
    const response = await api.get<TrainingRecord[]>('/training');
    return response.data;
  },

  async getEmployeeTraining(employeeId: string): Promise<TrainingRecord[]> {
    const response = await api.get<TrainingRecord[]>(`/training/employee/${employeeId}`);
    return response.data;
  }
};
