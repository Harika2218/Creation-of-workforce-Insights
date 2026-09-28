import api from './api';
import { Project } from '../types';

export const projectService = {
  async getProjects(): Promise<Project[]> {
    const response = await api.get<Project[]>('/projects');
    return response.data;
  },

  async getProject(projectId: string): Promise<Project> {
    const response = await api.get<Project>(`/projects/${projectId}`);
    return response.data;
  },

  async createProject(payload: Partial<Project>): Promise<Project> {
    const response = await api.post<Project>('/projects', payload);
    return response.data;
  },

  async updateProject(projectId: string, payload: Partial<Project>): Promise<Project> {
    const response = await api.put<Project>(`/projects/${projectId}`, payload);
    return response.data;
  }
};
