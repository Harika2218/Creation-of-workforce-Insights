import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { offlineAttendanceManager } from '../services/offlineAttendance';
import { pwaService } from '../services/pwaService';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { MobileBottomNav } from '../components/navigation/MobileBottomNav';
import { AuthContext } from '../context/AuthContext';
import { User } from '../types';

describe('Phase 11: PWA, Mobile Navigation & Advanced Accessibility Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    offlineAttendanceManager.clearAllPending();
  });

  describe('Offline Attendance Safety Invariants', () => {
    it('enqueues punch with strict PENDING_SERVER_VERIFICATION status', () => {
      const punch = offlineAttendanceManager.enqueuePendingPunch(
        'EMP050',
        'CHECK_IN',
        'GPS',
        { latitude: 12.9716, longitude: 77.5946 }
      );

      expect(punch).toBeDefined();
      expect(punch.employee_id).toBe('EMP050');
      expect(punch.action_type).toBe('CHECK_IN');
      expect(punch.attendance_method).toBe('GPS');
      // Critical Invariant: Must never be silently approved or marked as Present offline
      expect(punch.status).toBe('PENDING_SERVER_VERIFICATION');
      expect(punch.status).not.toBe('Present');
      expect(punch.status).not.toBe('Approved');
    });

    it('persists and retrieves pending punches from local storage', () => {
      offlineAttendanceManager.enqueuePendingPunch('EMP001', 'CHECK_IN', 'Web');
      offlineAttendanceManager.enqueuePendingPunch('EMP002', 'CHECK_OUT', 'GPS');

      const queue = offlineAttendanceManager.getPendingPunches();
      expect(queue.length).toBe(2);
      expect(queue[0].employee_id).toBe('EMP001');
      expect(queue[1].employee_id).toBe('EMP002');
    });

    it('removes pending punches upon successful sync or dismissal', () => {
      const p1 = offlineAttendanceManager.enqueuePendingPunch('EMP001', 'CHECK_IN', 'Web');
      offlineAttendanceManager.enqueuePendingPunch('EMP002', 'CHECK_OUT', 'GPS');

      offlineAttendanceManager.removePendingPunch(p1.event_id);
      const queue = offlineAttendanceManager.getPendingPunches();
      expect(queue.length).toBe(1);
      expect(queue[0].employee_id).toBe('EMP002');
    });
  });

  describe('PWA Service Capabilities', () => {
    it('detects notification support and permissions safely', () => {
      const isSupported = pwaService.isPushSupported();
      expect(typeof isSupported).toBe('boolean');

      const perm = pwaService.getNotificationPermission();
      expect(['default', 'granted', 'denied']).toContain(perm);
    });

    it('manages install state and prompt availability', () => {
      expect(pwaService.canInstall()).toBe(false);
      expect(typeof pwaService.isInstalled()).toBe('boolean');
    });
  });

  describe('Advanced Accessibility (WCAG 2.1 AA)', () => {
    it('renders Badge with role=status and accessible aria-label', () => {
      render(<Badge variant="Approved">Approved</Badge>);
      const badge = screen.getByRole('status');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveAttribute('aria-label', 'Status: Approved');
    });

    it('renders Modal with role=dialog, aria-modal=true, and aria-labelledby', () => {
      render(
        <Modal isOpen={true} onClose={() => {}} title="Onboard Employee Modal">
          <div>Modal Dialog Content</div>
        </Modal>
      );

      const dialog = screen.getByRole('dialog');
      expect(dialog).toBeInTheDocument();
      expect(dialog).toHaveAttribute('aria-modal', 'true');
      expect(dialog).toHaveAttribute('aria-labelledby', 'modal-dialog-title');
      expect(screen.getByText('Onboard Employee Modal')).toBeInTheDocument();
    });
  });

  describe('Role-Aware Mobile Navigation', () => {
    const renderWithRole = (role: 'EMPLOYEE' | 'MANAGER' | 'HR' | 'ADMIN') => {
      const mockUser: User = {
        user_id: 'USR001',
        employee_id: 'EMP001',
        name: 'Test User',
        email: 'test@demo.com',
        role,
        is_active: true,
      };

      return render(
        <MemoryRouter>
          <AuthContext.Provider
            value={{
              user: mockUser,
              token: 'mock-token',
              isAuthenticated: true,
              isLoading: false,
              login: vi.fn(),
              logout: vi.fn(),
            }}
          >
            <MobileBottomNav onOpenDrawer={vi.fn()} />
          </AuthContext.Provider>
        </MemoryRouter>
      );
    };

    it('renders Employee tabs: Home, Clock, Leaves, Shifts, AI Help', () => {
      renderWithRole('EMPLOYEE');
      expect(screen.getByText('Clock')).toBeInTheDocument();
      expect(screen.getByText('Shifts')).toBeInTheDocument();
      expect(screen.getByText('Leaves')).toBeInTheDocument();
      expect(screen.getByText('AI Help')).toBeInTheDocument();
    });

    it('renders Manager tabs: Home, Team, Leaves, Timesheets, AI Help', () => {
      renderWithRole('MANAGER');
      expect(screen.getByText('Team')).toBeInTheDocument();
      expect(screen.getByText('Timesheets')).toBeInTheDocument();
      expect(screen.getByText('AI Help')).toBeInTheDocument();
    });

    it('renders HR/Admin tabs: Home, Staff, Attendance, Analytics, AI Help', () => {
      renderWithRole('HR');
      expect(screen.getByText('Staff')).toBeInTheDocument();
      expect(screen.getByText('Attendance')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
      expect(screen.getByText('AI Help')).toBeInTheDocument();
    });
  });
});
