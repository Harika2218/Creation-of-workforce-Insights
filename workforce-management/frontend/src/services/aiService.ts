/**
 * Frontend Service for AI Workforce Intelligence Endpoints
 */

import api from './api';
import {
  AbsenteeismPrediction,
  AttritionPrediction,
  AttendanceAnomaly,
  ProductivityEvaluation,
  WorkforceForecast,
  StaffingRecommendation,
  SkillGap,
  TrainingRecommendation,
  ShiftRecommendation,
  ResourceRecommendation,
  AIModelMetrics,
} from '../types/ai';

export const aiService = {
  // 1. Absenteeism
  getAbsenteeism: async (departmentId?: string): Promise<AbsenteeismPrediction[]> => {
    const params = departmentId ? { department_id: departmentId } : {};
    const res = await api.get<AbsenteeismPrediction[]>('/ai/absenteeism', { params });
    return res.data;
  },

  getEmployeeAbsenteeism: async (employeeId: string): Promise<AbsenteeismPrediction> => {
    const res = await api.get<AbsenteeismPrediction>(`/ai/absenteeism/${employeeId}`);
    return res.data;
  },

  // 2. Attrition
  getAttrition: async (departmentId?: string): Promise<AttritionPrediction[]> => {
    const params = departmentId ? { department_id: departmentId } : {};
    const res = await api.get<AttritionPrediction[]>('/ai/attrition', { params });
    return res.data;
  },

  getEmployeeAttrition: async (employeeId: string): Promise<AttritionPrediction> => {
    const res = await api.get<AttritionPrediction>(`/ai/attrition/${employeeId}`);
    return res.data;
  },

  // 3. Attendance Anomalies
  getAttendanceAnomalies: async (limit: number = 100, severity?: string): Promise<AttendanceAnomaly[]> => {
    const params: Record<string, any> = { limit };
    if (severity) params.severity = severity;
    const res = await api.get<AttendanceAnomaly[]>('/ai/attendance-anomalies', { params });
    return res.data;
  },

  // 4. Productivity
  getProductivity: async (): Promise<ProductivityEvaluation[]> => {
    const res = await api.get<ProductivityEvaluation[]>('/ai/productivity');
    return res.data;
  },

  getEmployeeProductivity: async (employeeId: string): Promise<ProductivityEvaluation> => {
    const res = await api.get<ProductivityEvaluation>(`/ai/productivity/${employeeId}`);
    return res.data;
  },

  // 5. Workforce Forecast
  getWorkforceForecast: async (period?: string): Promise<WorkforceForecast[]> => {
    const params = period ? { period } : {};
    const res = await api.get<WorkforceForecast[]>('/ai/workforce-forecast', { params });
    return res.data;
  },

  // 6. Staffing Recommendations
  getStaffingRecommendations: async (departmentId?: string): Promise<StaffingRecommendation[]> => {
    const params = departmentId ? { department_id: departmentId } : {};
    const res = await api.get<StaffingRecommendation[]>('/ai/staffing-recommendations', { params });
    return res.data;
  },

  // 7. Skill Gaps
  getSkillGaps: async (departmentId?: string): Promise<SkillGap[]> => {
    const params = departmentId ? { department_id: departmentId } : {};
    const res = await api.get<SkillGap[]>('/ai/skill-gaps', { params });
    return res.data;
  },

  // 8. Training Recommendations
  getTrainingRecommendations: async (employeeId: string): Promise<TrainingRecommendation[]> => {
    const res = await api.get<TrainingRecommendation[]>(`/ai/training-recommendations/${employeeId}`);
    return res.data;
  },

  // 9. Shift Recommendations
  getShiftRecommendations: async (departmentId?: string): Promise<ShiftRecommendation[]> => {
    const params = departmentId ? { department_id: departmentId } : {};
    const res = await api.get<ShiftRecommendation[]>('/ai/shift-recommendations', { params });
    return res.data;
  },

  // 10. Resource Recommendations
  getResourceRecommendations: async (projectId?: string): Promise<ResourceRecommendation[]> => {
    const params = projectId ? { project_id: projectId } : {};
    const res = await api.get<ResourceRecommendation[]>('/ai/resource-recommendations', { params });
    return res.data;
  },

  // 11. Model Metrics & Governance
  getModelMetrics: async (): Promise<AIModelMetrics> => {
    const res = await api.get<AIModelMetrics>('/ai/model-metrics');
    return res.data;
  },
};
