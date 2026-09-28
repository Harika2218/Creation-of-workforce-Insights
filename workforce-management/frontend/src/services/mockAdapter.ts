/**
 * Mock API Adapter for HRvantage
 * Intercepts network calls when the backend API server is offline or unreachable.
 * Allows the live Vercel deployment to function completely as an interactive showcase.
 */

import { InternalAxiosRequestConfig } from 'axios';
import { CitationSource } from '../types/chatbot';
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

  // 12. Chatbot & RAG Assistant
  if (cleanUrl.includes('/chatbot/chat') && method === 'POST') {
    let message = '';
    try {
      const body = typeof config.data === 'string' ? JSON.parse(config.data) : config.data;
      message = (body?.message || '').toLowerCase();
    } catch {
      // fallback
    }

    let answer = '';
    let sources: CitationSource[] = [
      {
        title: 'InnovateCorp Employee Handbook & HR Policy 2026',
        source_type: 'policy_document' as const,
        section: 'Section 4.1: General Workforce Guidelines',
      },
    ];
    let intent = 'GENERAL_QUERY';
    const suggestions = [
      'How many leaves do I have left?',
      'Explain overtime and rest period rules',
      'What are our campus core working hours?',
    ];

    if (
      message.includes('leave') ||
      message.includes('vacation') ||
      message.includes('holiday') ||
      message.includes('off')
    ) {
      intent = 'LEAVE_QUERY';
      answer = `Based on your official employee records (2026 Entitlement Year):

• **Leaves Taken So Far:** **4 days** (2 Annual, 1 Casual, 1 Sick Leave)
• **Annual Leave Remaining:** **14 days** (out of 18 days annual quota)
• **Sick Leave Remaining:** **10 days** (out of 12 days medical quota)
• **Casual / Personal Leave:** **5 days** (out of 8 days quota)
• **Total Usable Balance:** **29 days**

You can submit a new leave request or view manager approval status directly under the **Leave Management** tab.`;
      sources = [
        {
          title: 'Employee Leave Quota & Balances (HR Database)',
          source_type: 'database_record' as const,
          section: 'Section 4.2: Annual Leave Accrual Register',
        },
        {
          title: 'InnovateCorp Statutory Leave Guidelines 2026',
          source_type: 'policy_document' as const,
          section: 'Clause 6: Medical & Casual Leave Entitlements',
        },
      ];
    } else if (
      message.includes('hi') ||
      message.includes('hello') ||
      message.includes('hey') ||
      message.includes('greetings')
    ) {
      intent = 'GREETING';
      answer = `Hello! I am your **AI Workforce Assistant**, powered by enterprise RAG and company HR policies.

I can help you with:
• 📅 **Leave Management:** Check balances, taken leaves, and holiday calendars
• ⏱️ **Attendance & Clock-In:** Telemetry logs, punch times, and geofence locations
• 💰 **Payroll & Compensation:** Payslip status, tax deductions, and PF details
• 🔄 **Shift Schedules:** Shift timings, rotational rosters, and peer shift swaps
• 📚 **Company Policies:** Maternity/paternity benefits, insurance, and code of conduct

What would you like to know today?`;
      sources = [
        {
          title: 'Enterprise AI Assistant System Guide',
          source_type: 'policy_document' as const,
          section: 'Workforce Intelligence Overview',
        },
      ];
    } else if (
      message.includes('attendance') ||
      message.includes('punch') ||
      message.includes('clock') ||
      message.includes('hours')
    ) {
      intent = 'ATTENDANCE_QUERY';
      answer = `Here is your current attendance summary for this month:

• **Overall Attendance Rate:** **94.8%** (Optimal standing)
• **Average Daily Work Hours:** **8.4 hours/day**
• **Today's Status:** Marked **Present** via Campus GPS Check-In
• **Overtime Logged:** 3.5 hours recorded this pay cycle

Your biometric and GPS validations are fully compliant with campus security policies.`;
      sources = [
        {
          title: 'Campus Geofenced Attendance Telemetry',
          source_type: 'database_record' as const,
          section: 'Daily Attendance Audit Log',
        },
      ];
    } else if (
      message.includes('salary') ||
      message.includes('pay') ||
      message.includes('payroll') ||
      message.includes('payslip')
    ) {
      intent = 'PAYROLL_QUERY';
      answer = `Your **September 2026** payroll has been fully processed:

• **Base Monthly Earnings:** ₹1,75,000 / month
• **Total Deductions (PF, Tax, ESI):** ₹26,800
• **Net Disbursement:** **₹1,48,200**
• **Disbursement Status:** Deposited to your registered salary account

You can review your detailed digital payslip and tax declarations in the **Payroll** tab.`;
      sources = [
        {
          title: 'Corporate Payroll & Statutory Deductions Register',
          source_type: 'database_record' as const,
          section: 'FIN-PR-2026-09',
        },
      ];
    } else if (
      message.includes('maternity') ||
      message.includes('paternity') ||
      message.includes('parental')
    ) {
      intent = 'POLICY_QUERY';
      answer = `Under InnovateCorp's **Parental Benefits Policy 2026**:

• **Maternity Leave:** 26 continuous weeks of fully paid leave for eligible female employees, with optional gradual return-to-work flexibility.
• **Paternity Leave:** 2 weeks (10 working days) of fully paid leave, valid within 6 months of childbirth or legal adoption.
• **Healthcare Coverage:** All maternity hospitalization expenses are covered under the ₹10,00,000 family health insurance plan.`;
      sources = [
        {
          title: 'InnovateCorp Statutory Benefits & Parental Policy',
          source_type: 'policy_document' as const,
          section: 'Policy Doc REF-HC-2026, Page 22',
        },
      ];
    } else if (
      message.includes('shift') ||
      message.includes('swap') ||
      message.includes('schedule')
    ) {
      intent = 'SHIFT_QUERY';
      answer = `You are scheduled on the **General Shift (09:00 – 18:00)** across standard weekdays.

• **Core Collaboration Hours:** 10:00 AM – 04:00 PM
• **Grace Period:** 15 minutes before mark-as-late
• **Peer Shift Swaps:** You can submit a shift swap request up to 24 hours in advance under **Shifts > Swap Requests**.`;
      sources = [
        {
          title: 'Rotational Shift & Fatigue Prevention Policy',
          source_type: 'policy_document' as const,
          section: 'Standard Operating Procedures Section 3.1',
        },
      ];
    } else {
      intent = 'GENERAL_QUERY';
      answer = `I have analyzed your query: *"**${message}**"* against InnovateCorp's enterprise HR knowledge base and policy records.

All employee policies, statutory records, and self-service administration can be managed directly through the portal:
• Check your attendance, leave balances, or timesheets in their respective tabs.
• For confidential grievances or statutory inquiries, you can also contact HR directly at **hr@demo.com**.

How else can I assist you with your workforce needs?`;
      sources = [
        {
          title: 'InnovateCorp Master HR Knowledge Base',
          source_type: 'policy_document' as const,
          section: 'General Enterprise Services',
        },
      ];
    }

    return {
      answer,
      sources,
      intent,
      conversation_id: 'conv-demo-session-2026',
      grounded: true,
      timestamp: new Date().toISOString(),
      follow_up_suggestions: suggestions,
    };
  }

  if (cleanUrl.match(/\/chatbot\/conversations\/[^/]+/) && method === 'GET') {
    return {
      conversation_id: 'conv-demo-session-2026',
      user_id: 'USR0002',
      title: 'HR Policies & Team Analytics',
      created_at: '2026-09-28T09:00:00Z',
      updated_at: '2026-09-28T10:00:00Z',
      messages: [
        {
          role: 'user',
          content: "What is our team's leave policy and pending approvals?",
          timestamp: '2026-09-28T09:15:00Z',
        },
        {
          role: 'assistant',
          content: 'As Engineering Manager, you have 3 pending leave requests requiring review. Your team presence is 16/18 active today.',
          timestamp: '2026-09-28T09:15:04Z',
          intent: 'LEAVE_APPROVAL_QUERY',
          sources: [
            {
              title: 'Manager Operations Telemetry',
              source_type: 'database_record' as const,
              section: 'Team Attendance & Leaves',
            },
          ],
        },
      ],
    };
  }

  if (cleanUrl.includes('/chatbot/conversations') && method === 'POST') {
    return {
      conversation_id: `conv-${Date.now()}`,
      user_id: 'USR0002',
      title: 'New Discussion',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      message_count: 0,
    };
  }

  if (cleanUrl.includes('/chatbot/conversations') && method === 'DELETE') {
    return { status: 'success', message: 'Conversation deleted' };
  }

  if (cleanUrl.includes('/chatbot/conversations') && method === 'GET') {
    return [
      {
        conversation_id: 'conv-demo-session-2026',
        user_id: 'USR0002',
        title: 'HR Policies & Team Analytics',
        created_at: '2026-09-28T09:00:00Z',
        updated_at: '2026-09-28T10:00:00Z',
        message_count: 2,
      },
    ];
  }

  if (cleanUrl.includes('/chatbot/suggestions')) {
    return {
      suggestions: [
        'How many leaves did I take till now?',
        'What is my current leave balance?',
        'Explain the maternity/paternity policy',
        'How is overtime calculated?',
        'What are our campus core hours?',
      ],
    };
  }

  if (cleanUrl.includes('/chatbot/sources')) {
    return [
      {
        document_id: 'DOC001',
        document_name: 'InnovateCorp_HR_Policy_Handbook_2026.pdf',
        title: 'Enterprise HR Policy Handbook 2026',
        category: 'Policy',
        file_type: 'PDF',
        total_pages: 48,
        chunk_count: 142,
        indexed_at: '2026-09-01T00:00:00Z',
      },
      {
        document_id: 'DOC002',
        document_name: 'Statutory_Leave_and_Attendance_Guidelines.pdf',
        title: 'Statutory Leave & Attendance Guidelines',
        category: 'Compliance',
        file_type: 'PDF',
        total_pages: 24,
        chunk_count: 68,
        indexed_at: '2026-09-01T00:00:00Z',
      },
    ];
  }

  // Fallback for mutations or unhandled routes
  return {
    success: true,
    message: 'Operation processed successfully in demo showcase mode.',
  };
}
