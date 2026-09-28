import api from './api';
import {
  NotificationItem,
  NotificationPreferences,
  WorkflowRuleItem,
  WorkflowStatusItem
} from '../types';

export interface NotificationQueryParams {
  unread_only?: boolean;
  category?: string;
  priority?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export const notificationService = {
  async getNotifications(params?: NotificationQueryParams): Promise<NotificationItem[]> {
    const response = await api.get<NotificationItem[]>('/notifications', { params });
    return response.data;
  },

  async getUnreadCount(): Promise<{ unread_count: number }> {
    const response = await api.get<{ unread_count: number }>('/notifications/unread-count');
    return response.data;
  },

  async getNotificationById(notificationId: string): Promise<NotificationItem> {
    const response = await api.get<NotificationItem>(`/notifications/${notificationId}`);
    return response.data;
  },

  async markAsRead(notificationId: string): Promise<{ message: string; success?: boolean }> {
    const response = await api.patch<{ message: string; success?: boolean }>(`/notifications/${notificationId}/read`);
    return response.data;
  },

  async markAllAsRead(): Promise<{ message: string; success?: boolean }> {
    const response = await api.patch<{ message: string; success?: boolean }>('/notifications/read-all');
    return response.data;
  },

  async getPreferences(): Promise<NotificationPreferences> {
    const response = await api.get<NotificationPreferences>('/notification-preferences');
    return response.data;
  },

  async updatePreferences(updates: Partial<NotificationPreferences>): Promise<NotificationPreferences> {
    const response = await api.put<NotificationPreferences>('/notification-preferences', updates);
    return response.data;
  },

  async getWorkflows(): Promise<WorkflowRuleItem[]> {
    const response = await api.get<WorkflowRuleItem[]>('/workflows');
    return response.data;
  },

  async getWorkflowStatus(): Promise<WorkflowStatusItem> {
    const response = await api.get<WorkflowStatusItem>('/workflows/status');
    return response.data;
  },

  async runScheduledWorkflows(): Promise<{ status: string; message: string; results: any }> {
    const response = await api.post<{ status: string; message: string; results: any }>('/workflows/run-scheduled');
    return response.data;
  },

  async sendNotification(payload: { employee_id: string; title: string; message: string; category?: string; priority?: string; type?: string }): Promise<NotificationItem> {
    const response = await api.post<NotificationItem>('/notifications', payload);
    return response.data;
  }
};
