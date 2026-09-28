import { describe, it, expect, vi } from 'vitest';
import api from '../services/api';

describe('API Error Handling Interceptors', () => {
  it('clears localStorage and redirects on 401 Unauthorized for protected endpoints', async () => {
    localStorage.setItem('hrvantage_token', 'expired-token');
    localStorage.setItem('hrvantage_user', JSON.stringify({ email: 'test@demo.com' }));

    // Mock an error object representing Axios 401 response
    const mockError: any = {
      config: { url: '/employees' },
      response: { status: 401, data: { detail: 'Token expired' } },
    };

    // Trigger the response interceptor error handler
    const responseInterceptor = (api.interceptors.response as any).handlers[0].rejected;

    await expect(responseInterceptor(mockError)).rejects.toEqual(mockError);
    expect(localStorage.getItem('hrvantage_token')).toBeNull();
    expect(localStorage.getItem('hrvantage_user')).toBeNull();
  });

  it('does NOT clear credentials when 401 happens on the login endpoint itself', async () => {
    localStorage.setItem('hrvantage_token', 'existing-token');

    const mockLoginError: any = {
      config: { url: '/auth/login' },
      response: { status: 401, data: { detail: 'Invalid credentials' } },
    };

    const responseInterceptor = (api.interceptors.response as any).handlers[0].rejected;
    await expect(responseInterceptor(mockLoginError)).rejects.toEqual(mockLoginError);

    // Existing token should remain intact
    expect(localStorage.getItem('hrvantage_token')).toBe('existing-token');
  });
});
