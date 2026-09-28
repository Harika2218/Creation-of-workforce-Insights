import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { handleMockRequest } from './mockAdapter';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Hybrid Adapter: Seamlessly handles offline Vercel demo showcase
const defaultAdapter = axios.getAdapter(axios.defaults.adapter || 'xhr');

api.defaults.adapter = async (config: InternalAxiosRequestConfig): Promise<AxiosResponse> => {
  // If running on HTTPS (e.g. Vercel) and backend URL is local HTTP or offline, serve mock immediately
  const isHttpsToLocalHttp =
    typeof window !== 'undefined' &&
    window.location.protocol === 'https:' &&
    (!config.baseURL || config.baseURL.includes('127.0.0.1') || config.baseURL.includes('localhost'));

  if (isHttpsToLocalHttp) {
    const mock = handleMockRequest(config);
    return {
      data: mock,
      status: 200,
      statusText: 'OK (Demo Mode)',
      headers: {},
      config,
    };
  }

  try {
    return await defaultAdapter(config);
  } catch (err: any) {
    // If backend is offline or network fails, fallback to mock data
    if (!err.response || err.code === 'ERR_NETWORK') {
      const mock = handleMockRequest(config);
      if (mock !== null && mock !== undefined) {
        return {
          data: mock,
          status: 200,
          statusText: 'OK (Demo Mode)',
          headers: {},
          config,
        };
      }
    }
    throw err;
  }
};

// Request Interceptor: Attach JWT Bearer Token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('hrvantage_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Handle 401 Session Expiry
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response && error.response.status === 401) {
      // Don't auto-redirect on login attempt failure
      if (!error.config?.url?.includes('/auth/login')) {
        localStorage.removeItem('hrvantage_token');
        localStorage.removeItem('hrvantage_user');
        if (window.location.pathname !== '/login') {
          window.location.href = '/login?expired=true';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
