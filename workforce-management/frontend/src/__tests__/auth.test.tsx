import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { LoginPage } from '../pages/auth/LoginPage';
import { AuthProvider } from '../context/AuthContext';
import { ToastProvider } from '../context/ToastContext';
import { authService } from '../services/authService';

vi.mock('../services/authService', () => ({
  authService: {
    login: vi.fn(),
    getMe: vi.fn().mockResolvedValue({}),
    logout: vi.fn(),
  },
}));

describe('Authentication & Login Page Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders login page with enterprise branding and demo buttons', () => {
    render(
      <BrowserRouter>
        <ToastProvider>
          <AuthProvider>
            <LoginPage />
          </AuthProvider>
        </ToastProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('HRvantage')).toBeInTheDocument();
    expect(screen.getByText(/1-Click Demo Accounts/i)).toBeInTheDocument();
    expect(screen.getByText('Admin')).toBeInTheDocument();
    expect(screen.getByText('HR Lead')).toBeInTheDocument();
    expect(screen.getByText('Manager')).toBeInTheDocument();
    expect(screen.getByText('Employee')).toBeInTheDocument();
  });

  it('populates credentials when a demo account is clicked', () => {
    render(
      <BrowserRouter>
        <ToastProvider>
          <AuthProvider>
            <LoginPage />
          </AuthProvider>
        </ToastProvider>
      </BrowserRouter>
    );

    const managerDemoBtn = screen.getByText('Manager');
    fireEvent.click(managerDemoBtn);

    const emailInput = screen.getByPlaceholderText('user@demo.com') as HTMLInputElement;
    expect(emailInput.value).toBe('manager@demo.com');
  });

  it('authenticates successfully and saves JWT token to localStorage', async () => {
    (authService.login as any).mockResolvedValueOnce({
      access_token: 'mock-jwt-token-xyz',
      token_type: 'bearer',
      user_id: 'USR001',
      employee_id: 'EMP003',
      email: 'hr@demo.com',
      role: 'HR',
    });
    (authService.getMe as any).mockResolvedValue({
      user_id: 'USR001',
      employee_id: 'EMP003',
      email: 'hr@demo.com',
      name: 'Anita Roy',
      role: 'HR',
      is_active: true,
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <AuthProvider>
            <LoginPage />
          </AuthProvider>
        </ToastProvider>
      </BrowserRouter>
    );

    const submitBtn = screen.getByRole('button', { name: /Sign In to Enterprise Portal/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith('hr@demo.com', 'Demo@2026');
      expect(localStorage.getItem('hrvantage_token')).toBe('mock-jwt-token-xyz');
    });
  });

  it('displays error message on invalid credentials (401)', async () => {
    (authService.login as any).mockRejectedValueOnce({
      response: {
        status: 401,
        data: { detail: 'Invalid corporate email or password.' },
      },
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <AuthProvider>
            <LoginPage />
          </AuthProvider>
        </ToastProvider>
      </BrowserRouter>
    );

    const submitBtn = screen.getByRole('button', { name: /Sign In to Enterprise Portal/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      const errorElements = screen.getAllByText('Invalid corporate email or password.');
      expect(errorElements.length).toBeGreaterThan(0);
    });
  });
});
