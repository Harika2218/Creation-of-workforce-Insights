/**
 * Mock API Adapter for HRvantage
 * Intercepts network calls when the backend API server is offline or unreachable.
 * Allows the live Vercel deployment to function completely as an interactive showcase.
 */

import { InternalAxiosRequestConfig } from 'axios';
import {
  MOCK_USERS,
  MOCK_DEPARTMENTS,
  MOCK_LOCATIONS,
  MOCK_EMPLOYEES,
  MOCK_HR_SUMMARY,
  MOCK_ATTENDANCE_SUMMARY,
  MOCK_MANAGER_SUMMARY,
  MOCK_LEAVE_REQUESTS,
  MOCK_NOTIFICATIONS,
  MOCK_AI_ATTRITION,
  MOCK_AI_ANOMALIES,
} from './mockData';

export function handleMockRequest(config?: InternalAxiosRequestConfig): any {
  if (!config) return null;

  const url = config.url || '';
  const method = (config.method || 'GET').toUpperCase();
  const cleanUrl = url.replace(/^https?:\/\/[^/]+/, '').replace(/^\/api\/v1/, '');

  // 1. Authentication
  if (cleanUrl.includes('/auth/login') && method === 'POST') {
    let email = 'manager@demo.com';
    try {
      const body = typeof config.data === 'string' ? JSON.parse(config.data) : config.data;
      if (body?.email) email = body.email.toLowerCase();
    } catch {
      // fallback
    }

    const matched = MOCK_USERS[email] || MOCK_USERS['manager@demo.com'];
    return {
      access_token: matched.token,
      token_type: 'bearer',
      user_id: matched.user.user_id,
      employee_id: matched.user.employee_id,
      email: matched.user.email,
      role: matched.user.role,
    };
  }

  if (cleanUrl.includes('/auth/me')) {
    const saved = localStorage.getItem('hrvantage_user');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        // fallback
      }
    }
    const token = localStorage.getItem('hrvantage_token');
    const matched = Object.values(MOCK_USERS).find((u) => u.token === token);
    return matched ? matched.user : MOCK_USERS['manager@demo.com'].user;
  }

  // 2. HR Endpoints
  if (cleanUrl.includes('/hr/summary')) {
    return MOCK_HR_SUMMARY;
  }

  if (cleanUrl.includes('/hr/employee-summary')) {
    return {
      departments: MOCK_DEPARTMENTS.map((d) => ({ name: d.department_name, count: d.active_employees_count || 15 })),
      roles: [
        { role: 'Engineering', count: 72 },
        { role: 'Sales', count: 36 },
        { role: 'Product', count: 22 },
        { role: 'Operations', count: 18 },
        { role: 'Marketing', count: 16 },
        { role: 'HR', count: 14 },
        { role: 'Finance', count: 12 },
        { role: 'Legal', count: 10 },
      ],
      attendance_distribution: [
        { status: 'Present', count: 182 },
        { status: 'Late', count: 11 },
        { status: 'Absent', count: 7 },
        { status: 'On Leave', count: 7 },
      ],
    };
  }

  // 3. Attendance Endpoints
  if (cleanUrl.includes('/attendance/summary')) {
    return MOCK_ATTENDANCE_SUMMARY;
  }

  if (cleanUrl.startsWith('/attendance') && method === 'GET') {
    return {
      items: [
        { attendance_id: 'ATT001', employee_id: 'EMP001', date: '2026-09-28', clock_in: '09:02:14', clock_out: '18:15:30', status: 'Present', total_hours: 8.5, overtime_hours: 0.5, attendance_method: 'Web' },
        { attendance_id: 'ATT002', employee_id: 'EMP002', date: '2026-09-28', clock_in: '08:58:22', clock_out: '17:45:10', status: 'Present', total_hours: 8.2, overtime_hours: 0.2, attendance_method: 'GPS' },
        { attendance_id: 'ATT003', employee_id: 'EMP003', date: '2026-09-28', clock_in: '09:12:05', clock_out: '18:00:00', status: 'Late', total_hours: 8.0, overtime_hours: 0.0, attendance_method: 'Biometric' },
        { attendance_id: 'ATT004', employee_id: 'EMP050', date: '2026-09-28', clock_in: '09:05:40', clock_out: null, status: 'Present', total_hours: 6.2, overtime_hours: 0.0, attendance_method: 'Web' },
      ],
      total: 200,
      page: 1,
      page_size: 20,
      total_pages: 10,
    };
  }

  // 4. Manager Endpoints
  if (cleanUrl.includes('/manager/team/summary')) {
    return MOCK_MANAGER_SUMMARY;
  }

  if (cleanUrl.includes('/manager/team/leave')) {
    return MOCK_LEAVE_REQUESTS;
  }

  if (cleanUrl.includes('/manager/team/attendance')) {
    return [
      { attendance_id: 'MATT01', employee_id: 'EMP050', employee_name: 'Rohan Verma', clock_in: '09:05', status: 'Present', total_hours: 8.0 },
      { attendance_id: 'MATT02', employee_id: 'EMP004', employee_name: 'Priya Sharma', clock_in: '08:55', status: 'Present', total_hours: 8.2 },
      { attendance_id: 'MATT03', employee_id: 'EMP005', employee_name: 'Ananya Deshmukh', clock_in: '09:30', status: 'Late', total_hours: 7.5 },
    ];
  }

  if (cleanUrl.includes('/manager/team/shifts')) {
    return [
      { allocation_id: 'SHF001', employee_id: 'EMP050', shift_id: 'SH01', shift_name: 'General Shift (09:00 - 18:00)', date: '2026-09-28', status: 'Scheduled' },
      { allocation_id: 'SHF002', employee_id: 'EMP004', shift_id: 'SH01', shift_name: 'General Shift (09:00 - 18:00)', date: '2026-09-28', status: 'Scheduled' },
    ];
  }

  if (cleanUrl.includes('/manager/team')) {
    return MOCK_EMPLOYEES.slice(1, 9);
  }

  // 5. Employees & Departments & Locations
  if (cleanUrl.startsWith('/employees') && method === 'GET') {
    return {
      items: MOCK_EMPLOYEES,
      total: 200,
      page: 1,
      page_size: 20,
      total_pages: 10,
    };
  }

  if (cleanUrl.includes('/departments')) {
    return MOCK_DEPARTMENTS;
  }

  if (cleanUrl.includes('/locations')) {
    return MOCK_LOCATIONS;
  }

  // 6. Leave Endpoints
  if (cleanUrl.includes('/leave/types')) {
    return ['Annual Leave', 'Sick Leave', 'Casual Leave', 'Maternity Leave', 'Paternity Leave', 'Unpaid Leave'];
  }

  if (cleanUrl.includes('/leave/balance')) {
    return [
      { leave_type: 'Annual Leave', total: 18, used: 4, balance: 14 },
      { leave_type: 'Sick Leave', total: 12, used: 2, balance: 10 },
      { leave_type: 'Casual Leave', total: 8, used: 3, balance: 5 },
    ];
  }

  if (cleanUrl.includes('/leave')) {
    return MOCK_LEAVE_REQUESTS;
  }

  // 7. Notifications
  if (cleanUrl.includes('/notifications/unread-count')) {
    return { unread_count: 2 };
  }

  if (cleanUrl.includes('/notifications')) {
    return MOCK_NOTIFICATIONS;
  }

  // 8. AI Intelligence
  if (cleanUrl.includes('/ai/attrition')) {
    return MOCK_AI_ATTRITION;
  }

  if (cleanUrl.includes('/ai/attendance-anomalies')) {
    return MOCK_AI_ANOMALIES;
  }

  if (cleanUrl.includes('/ai/absenteeism')) {
    return [
      {
        employee_id: 'EMP007',
        prediction: 1,
        probability: 0.74,
        risk_level: 'HIGH',
        important_features: [{ feature: 'Overtime Hours (>25h)', importance: 0.42 }],
        prediction_date: '2026-09-28',
        model_version: 'v1.2.0-rf',
        disclaimer: 'Random Forest absenteeism classifier output.',
      },
    ];
  }

  if (cleanUrl.includes('/ai/productivity')) {
    return [
      {
        employee_id: 'EMP050',
        composite_score: 91.2,
        rank_tier: 'Exceeding Expectations',
        factors: { attendance: 95.0, task_completion: 92.0, peer_review: 88.0 },
      },
    ];
  }

  // 9. Payroll Endpoints
  if (cleanUrl.includes('/payroll/summary')) {
    return {
      month: '2026-09',
      total_gross: 21500000,
      total_deductions: 3050000,
      total_net: 18450000,
      processed_count: 200,
      status: 'Finalized',
    };
  }

  if (cleanUrl.includes('/payroll')) {
    return {
      items: [
        { payroll_id: 'PAY001', employee_id: 'EMP050', employee_name: 'Rohan Verma', month: '2026-09', base_salary: 120833, net_pay: 104500, status: 'Paid' },
        { payroll_id: 'PAY002', employee_id: 'EMP002', employee_name: 'Sarah Jenkins', month: '2026-09', base_salary: 175000, net_pay: 148200, status: 'Paid' },
      ],
      total: 200,
      page: 1,
      page_size: 20,
      total_pages: 10,
    };
  }

  // 10. Shifts Endpoints
  if (cleanUrl.includes('/shifts/swap-requests')) {
    return [];
  }

  if (cleanUrl.includes('/shifts')) {
    return [
      { shift_id: 'SH01', shift_name: 'Morning Shift', start_time: '08:00', end_time: '16:30', grace_period_mins: 15, break_duration_mins: 45, is_active: true },
      { shift_id: 'SH02', shift_name: 'General Shift', start_time: '09:00', end_time: '17:30', grace_period_mins: 15, break_duration_mins: 45, is_active: true },
      { shift_id: 'SH03', shift_name: 'Evening Shift', start_time: '14:00', end_time: '22:30', grace_period_mins: 15, break_duration_mins: 45, is_active: true },
    ];
  }

  // 11. Timesheets & Projects & Skills
  if (cleanUrl.includes('/timesheets')) {
    return {
      items: [
        { timesheet_id: 'TS001', employee_id: 'EMP050', week_start_date: '2026-09-21', total_hours: 40.0, billable_hours: 36.0, status: 'Approved' },
      ],
      total: 50,
      page: 1,
      page_size: 20,
      total_pages: 3,
    };
  }

  if (cleanUrl.includes('/projects')) {
    return [
      { project_id: 'PRJ001', project_name: 'Enterprise Cloud Modernization', client_name: 'Acme Corp', status: 'In Progress', budget: 15000000 },
      { project_id: 'PRJ002', project_name: 'AI Workforce Analytics Suite', client_name: 'InnovateCorp Internal', status: 'In Progress', budget: 8500000 },
    ];
  }

  if (cleanUrl.includes('/skills')) {
    return [
      { skill_id: 'SK01', skill_name: 'React 19 & TypeScript', category: 'Frontend' },
      { skill_id: 'SK02', skill_name: 'FastAPI & Python', category: 'Backend' },
      { skill_id: 'SK03', skill_name: 'Machine Learning & Scikit-learn', category: 'Data Science' },
      { skill_id: 'SK04', skill_name: 'MongoDB & Cloud Architecture', category: 'Database' },
    ];
  }

  // Fallback for mutations or unhandled routes
  return {
    success: true,
    message: 'Operation processed successfully in demo showcase mode.',
  };
}
