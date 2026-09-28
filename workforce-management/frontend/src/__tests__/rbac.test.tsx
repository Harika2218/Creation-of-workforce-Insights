import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from '../routes/ProtectedRoute';
import { UnauthorizedPage } from '../pages/errors/UnauthorizedPage';
import { NotFoundPage } from '../pages/errors/NotFoundPage';
import { AuthProvider } from '../context/AuthContext';
import { ToastProvider } from '../context/ToastContext';
import { authService } from '../services/authService';

vi.mock('../services/authService', () => ({
  authService: {
    getMe: vi.fn(),
    logout: vi.fn(),
  },
}));

describe('RBAC Route Protection & Access Control Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('redirects unauthenticated users to /login', async () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <ToastProvider>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={<div>Login Page Screen</div>} />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <div>Secret Dashboard</div>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </AuthProvider>
        </ToastProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Login Page Screen')).toBeInTheDocument();
      expect(screen.queryByText('Secret Dashboard')).not.toBeInTheDocument();
    });
  });

  it('blocks EMPLOYEE from accessing HR-only routes and redirects to /unauthorized', async () => {
    localStorage.setItem('hrvantage_token', 'mock-token');
    const mockUser = {
      user_id: 'USR050',
      employee_id: 'EMP050',
      email: 'employee@demo.com',
      name: 'John Employee',
      role: 'EMPLOYEE' as const,
      is_active: true,
    };
    localStorage.setItem('hrvantage_user', JSON.stringify(mockUser));
    (authService.getMe as any).mockResolvedValueOnce(mockUser);

    render(
      <MemoryRouter initialEntries={['/hr-admin-zone']}>
        <ToastProvider>
          <AuthProvider>
            <Routes>
              <Route path="/unauthorized" element={<UnauthorizedPage />} />
              <Route
                path="/hr-admin-zone"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN', 'HR']}>
                    <div>Admin Portal</div>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </AuthProvider>
        </ToastProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/403 - Access Denied/i)).toBeInTheDocument();
      expect(screen.getByText(/EMPLOYEE/i)).toBeInTheDocument();
      expect(screen.queryByText('Admin Portal')).not.toBeInTheDocument();
    });
  });

  it('allows HR users to access HR-only routes', async () => {
    localStorage.setItem('hrvantage_token', 'mock-token');
    const mockUser = {
      user_id: 'USR003',
      employee_id: 'EMP003',
      email: 'hr@demo.com',
      name: 'Anita Roy',
      role: 'HR' as const,
      is_active: true,
    };
    localStorage.setItem('hrvantage_user', JSON.stringify(mockUser));
    (authService.getMe as any).mockResolvedValueOnce(mockUser);

    render(
      <MemoryRouter initialEntries={['/hr-admin-zone']}>
        <ToastProvider>
          <AuthProvider>
            <Routes>
              <Route path="/unauthorized" element={<UnauthorizedPage />} />
              <Route
                path="/hr-admin-zone"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN', 'HR']}>
                    <div>Authorized HR Area</div>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </AuthProvider>
        </ToastProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Authorized HR Area')).toBeInTheDocument();
    });
  });

  it('renders 404 page for nonexistent routes', () => {
    render(
      <MemoryRouter initialEntries={['/some/unknown/route']}>
        <NotFoundPage />
      </MemoryRouter>
    );

    expect(screen.getByText(/404 - Page Not Found/i)).toBeInTheDocument();
  });
});
