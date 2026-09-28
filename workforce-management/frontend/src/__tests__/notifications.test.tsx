import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { NotificationsPage } from '../pages/notifications/NotificationsPage';
import { notificationService } from '../services/notificationService';
import { ToastProvider } from '../context/ToastContext';

// Mock notification service
vi.mock('../services/notificationService', () => ({
  notificationService: {
    getNotifications: vi.fn(),
    markAsRead: vi.fn(),
    markAllAsRead: vi.fn(),
    getPreferences: vi.fn(),
    updatePreferences: vi.fn(),
  },
}));

// Mock notification socket
vi.mock('../services/notificationSocket', () => ({
  notificationSocket: {
    connect: vi.fn(),
    disconnect: vi.fn(),
    subscribe: vi.fn(() => () => {}),
    subscribeStatus: vi.fn((cb) => {
      cb(true);
      return () => {};
    }),
    getIsConnected: vi.fn(() => true),
  },
}));

describe('NotificationsPage & Workflow UI', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(notificationService.getNotifications).mockResolvedValue([]);
  });

  it('renders Notification Center header and category tabs', async () => {
    vi.mocked(notificationService.getNotifications).mockResolvedValueOnce([
      {
        notification_id: 'NOT_TEST_01',
        title: 'Late Clock-In Recorded',
        message: 'Employee clocked in 20 minutes late.',
        priority: 'high',
        category: 'attendance',
        is_read: 0,
        created_at: '2026-09-26 10:00:00',
        action_url: '/attendance',
      },
    ]);

    render(
      <MemoryRouter>
        <ToastProvider>
          <NotificationsPage />
        </ToastProvider>
      </MemoryRouter>
    );

    expect(screen.getByText('Notification Center')).toBeInTheDocument();
    expect(screen.getByText('All')).toBeInTheDocument();
    expect(screen.getByText('Attendance')).toBeInTheDocument();
    expect(screen.getByText('AI Alerts')).toBeInTheDocument();
    expect(screen.getByText('Preferences')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Late Clock-In Recorded')).toBeInTheDocument();
      expect(screen.getByText('Employee clocked in 20 minutes late.')).toBeInTheDocument();
    });
  });

  it('renders notification preferences tab with locked compliance notice', async () => {
    vi.mocked(notificationService.getPreferences).mockResolvedValueOnce({
      employee_id: 'EMP050',
      attendance_alerts: true,
      leave_notifications: true,
      shift_notifications: true,
      timesheet_notifications: true,
      payroll_notifications: true,
      performance_notifications: true,
      training_notifications: true,
      birthday_notifications: true,
      anniversary_notifications: true,
      ai_alerts: true,
      compliance_notifications: true,
      email_enabled: true,
      in_app_enabled: true,
    });

    render(
      <MemoryRouter>
        <ToastProvider>
          <NotificationsPage />
        </ToastProvider>
      </MemoryRouter>
    );

    // Click Preferences tab
    fireEvent.click(screen.getByText('Preferences'));

    await waitFor(() => {
      expect(screen.getByText('Notification Preferences & Delivery Controls')).toBeInTheDocument();
      expect(screen.getByText('Statutory & Compliance Notices')).toBeInTheDocument();
      expect(screen.getByText('Mandatory')).toBeInTheDocument();
    });
  });
});
