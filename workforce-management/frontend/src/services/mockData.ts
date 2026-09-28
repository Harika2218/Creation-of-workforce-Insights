/**
 * Comprehensive Mock Dataset for HRvantage Workforce Management
 * Used for seamless offline / Vercel preview demo mode.
 */

import { User, Employee, Department, HRSummaryMetrics, AttendanceSummary, ManagerTeamSummary } from '../types';
import { AbsenteeismPrediction, AttritionPrediction, AttendanceAnomaly } from '../types/ai';

export interface CampusLocation {
  location_id: string;
  location_name: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  latitude: number;
  longitude: number;
  geofence_radius_meters: number;
  is_active: boolean;
}

export const MOCK_USERS: Record<string, { user: User; token: string }> = {
  'admin@demo.com': {
    token: 'mock-jwt-token-admin-demo-2026',
    user: {
      user_id: 'USR0001',
      employee_id: 'EMP001',
      email: 'admin@demo.com',
      name: 'Vikramaditya Singhania',
      role: 'ADMIN',
      department_id: 'DEP001',
      designation: 'Chief Technology Officer',
      is_active: true,
      avatar_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150',
    },
  },
  'hr@demo.com': {
    token: 'mock-jwt-token-hr-demo-2026',
    user: {
      user_id: 'USR0003',
      employee_id: 'EMP003',
      email: 'hr@demo.com',
      name: 'Vihaan Reddy',
      role: 'HR',
      department_id: 'DEP002',
      designation: 'Head of Human Resources',
      is_active: true,
      avatar_url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150',
    },
  },
  'manager@demo.com': {
    token: 'mock-jwt-token-manager-demo-2026',
    user: {
      user_id: 'USR0002',
      employee_id: 'EMP002',
      email: 'manager@demo.com',
      name: 'Sarah Jenkins',
      role: 'MANAGER',
      department_id: 'DEP001',
      designation: 'Engineering Manager',
      is_active: true,
      avatar_url: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150',
    },
  },
  'employee@demo.com': {
    token: 'mock-jwt-token-employee-demo-2026',
    user: {
      user_id: 'USR0004',
      employee_id: 'EMP050',
      email: 'employee@demo.com',
      name: 'Rohan Verma',
      role: 'EMPLOYEE',
      department_id: 'DEP001',
      designation: 'Senior Full Stack Engineer',
      is_active: true,
      avatar_url: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150',
    },
  },
};

export const MOCK_DEPARTMENTS: Department[] = [
  { department_id: 'DEP001', department_name: 'Engineering & Technology', code: 'ENG', description: 'Core software engineering, architecture, and DevOps', head_employee_id: 'EMP001', active_employees_count: 72 },
  { department_id: 'DEP002', department_name: 'Human Resources', code: 'HR', description: 'People operations, talent acquisition, culture, and statutory compliance', head_employee_id: 'EMP003', active_employees_count: 14 },
  { department_id: 'DEP003', department_name: 'Product Management & Design', code: 'PROD', description: 'Product strategy, UX/UI research, user journey mapping', head_employee_id: 'EMP010', active_employees_count: 22 },
  { department_id: 'DEP004', department_name: 'Sales & Business Development', code: 'SALES', description: 'Enterprise solution sales, accounts, client onboarding', head_employee_id: 'EMP015', active_employees_count: 36 },
  { department_id: 'DEP005', department_name: 'Finance & Accounting', code: 'FIN', description: 'Corporate finance, payroll execution, statutory taxation, audit', head_employee_id: 'EMP020', active_employees_count: 12 },
  { department_id: 'DEP006', department_name: 'Operations & Facilities', code: 'OPS', description: 'Campus operations, safety, procurement, inventory management', head_employee_id: 'EMP025', active_employees_count: 18 },
  { department_id: 'DEP007', department_name: 'Marketing & Communications', code: 'MKT', description: 'Brand marketing, digital acquisition, events, analyst relations', head_employee_id: 'EMP030', active_employees_count: 16 },
  { department_id: 'DEP008', department_name: 'Legal & Enterprise Compliance', code: 'LEGAL', description: 'Labor contracts, regulatory compliance, IP protection', head_employee_id: 'EMP035', active_employees_count: 10 },
];

export const MOCK_LOCATIONS: CampusLocation[] = [
  { location_id: 'LOC001', location_name: 'Hyderabad Campus (HQ)', address: 'HITEC City, Madhapur, Hyderabad, Telangana 500081', city: 'Hyderabad', state: 'Telangana', country: 'India', postal_code: '500081', latitude: 17.4435, longitude: 78.3772, geofence_radius_meters: 250, is_active: true },
  { location_id: 'LOC002', location_name: 'Bengaluru Tech Park', address: 'Outer Ring Road, Bellandur, Bengaluru, Karnataka 560103', city: 'Bengaluru', state: 'Karnataka', country: 'India', postal_code: '560103', latitude: 12.9279, longitude: 77.6835, geofence_radius_meters: 300, is_active: true },
  { location_id: 'LOC003', location_name: 'Pune Development Center', address: 'Hinjawadi Phase 1, Pune, Maharashtra 411057', city: 'Pune', state: 'Maharashtra', country: 'India', postal_code: '411057', latitude: 18.5913, longitude: 73.7389, geofence_radius_meters: 200, is_active: true },
  { location_id: 'LOC004', location_name: 'Noida Cyber City', address: 'Sector 62, Noida, Uttar Pradesh 201309', city: 'Noida', state: 'Uttar Pradesh', country: 'India', postal_code: '201309', latitude: 28.628, longitude: 77.3649, geofence_radius_meters: 200, is_active: true },
];

export const MOCK_EMPLOYEES: Employee[] = [
  { employee_id: 'EMP001', name: 'Vikramaditya Singhania', email: 'admin@demo.com', phone: '+91-98765-43210', department_id: 'DEP001', department_name: 'Engineering & Technology', designation: 'Chief Technology Officer', role: 'ADMIN', manager_id: null, location_id: 'LOC001', location_name: 'Hyderabad Campus (HQ)', date_of_joining: '2021-03-15', employment_type: 'Full-time', employment_status: 'Active', base_salary: 2800000 },
  { employee_id: 'EMP002', name: 'Sarah Jenkins', email: 'manager@demo.com', phone: '+91-98765-43211', department_id: 'DEP001', department_name: 'Engineering & Technology', designation: 'Engineering Manager', role: 'MANAGER', manager_id: 'EMP001', manager_name: 'Vikramaditya Singhania', location_id: 'LOC001', location_name: 'Hyderabad Campus (HQ)', date_of_joining: '2022-01-10', employment_type: 'Full-time', employment_status: 'Active', base_salary: 2100000 },
  { employee_id: 'EMP003', name: 'Vihaan Reddy', email: 'hr@demo.com', phone: '+91-98765-43212', department_id: 'DEP002', department_name: 'Human Resources', designation: 'Head of Human Resources', role: 'HR', manager_id: 'EMP001', manager_name: 'Vikramaditya Singhania', location_id: 'LOC001', location_name: 'Hyderabad Campus (HQ)', date_of_joining: '2021-06-01', employment_type: 'Full-time', employment_status: 'Active', base_salary: 1950000 },
  { employee_id: 'EMP050', name: 'Rohan Verma', email: 'employee@demo.com', phone: '+91-98765-43250', department_id: 'DEP001', department_name: 'Engineering & Technology', designation: 'Senior Full Stack Engineer', role: 'EMPLOYEE', manager_id: 'EMP002', manager_name: 'Sarah Jenkins', location_id: 'LOC001', location_name: 'Hyderabad Campus (HQ)', date_of_joining: '2023-04-12', employment_type: 'Full-time', employment_status: 'Active', base_salary: 1450000 },
  { employee_id: 'EMP004', name: 'Priya Sharma', email: 'priya.s@innovatecorp.demo', phone: '+91-98765-43213', department_id: 'DEP003', department_name: 'Product Management & Design', designation: 'Lead Product Designer', role: 'EMPLOYEE', manager_id: 'EMP002', manager_name: 'Sarah Jenkins', location_id: 'LOC002', location_name: 'Bengaluru Tech Park', date_of_joining: '2022-08-15', employment_type: 'Full-time', employment_status: 'Active', base_salary: 1600000 },
  { employee_id: 'EMP005', name: 'Ananya Deshmukh', email: 'ananya.d@innovatecorp.demo', phone: '+91-98765-43214', department_id: 'DEP001', department_name: 'Engineering & Technology', designation: 'Staff AI/ML Engineer', role: 'EMPLOYEE', manager_id: 'EMP002', manager_name: 'Sarah Jenkins', location_id: 'LOC003', location_name: 'Pune Development Center', date_of_joining: '2023-01-20', employment_type: 'Full-time', employment_status: 'Active', base_salary: 1850000 },
  { employee_id: 'EMP006', name: 'Kavita Menon', email: 'kavita.m@innovatecorp.demo', phone: '+91-98765-43215', department_id: 'DEP004', department_name: 'Sales & Business Development', designation: 'Enterprise Account Executive', role: 'EMPLOYEE', manager_id: 'EMP002', manager_name: 'Sarah Jenkins', location_id: 'LOC004', location_name: 'Noida Cyber City', date_of_joining: '2022-11-05', employment_type: 'Full-time', employment_status: 'Active', base_salary: 1500000 },
  { employee_id: 'EMP007', name: 'Arjun Nair', email: 'arjun.n@innovatecorp.demo', phone: '+91-98765-43216', department_id: 'DEP001', department_name: 'Engineering & Technology', designation: 'DevOps & SRE Specialist', role: 'EMPLOYEE', manager_id: 'EMP002', manager_name: 'Sarah Jenkins', location_id: 'LOC001', location_name: 'Hyderabad Campus (HQ)', date_of_joining: '2023-09-01', employment_type: 'Full-time', employment_status: 'Notice Period', base_salary: 1400000 },
  { employee_id: 'EMP008', name: 'Meera Iyer', email: 'meera.i@innovatecorp.demo', phone: '+91-98765-43217', department_id: 'DEP005', department_name: 'Finance & Accounting', designation: 'Senior Financial Analyst', role: 'EMPLOYEE', manager_id: 'EMP003', manager_name: 'Vihaan Reddy', location_id: 'LOC001', location_name: 'Hyderabad Campus (HQ)', date_of_joining: '2022-04-18', employment_type: 'Full-time', employment_status: 'Active', base_salary: 1350000 },
  { employee_id: 'EMP009', name: 'Siddharth Rao', email: 'siddharth.r@innovatecorp.demo', phone: '+91-98765-43218', department_id: 'DEP001', department_name: 'Engineering & Technology', designation: 'Frontend React Architect', role: 'EMPLOYEE', manager_id: 'EMP002', manager_name: 'Sarah Jenkins', location_id: 'LOC002', location_name: 'Bengaluru Tech Park', date_of_joining: '2021-12-01', employment_type: 'Full-time', employment_status: 'Active', base_salary: 1750000 },
];

export const MOCK_HR_SUMMARY: HRSummaryMetrics = {
  total_employees: 200,
  active_employees: 194,
  notice_period_employees: 6,
  departments_count: 8,
  locations_count: 4,
  daily_attendance_rate: 94.8,
  pending_leave_requests: 12,
  total_monthly_payroll: 18450000,
  attrition_risk_high: 14,
  attrition_risk_medium: 32,
  attrition_risk_low: 154,
};

export const MOCK_ATTENDANCE_SUMMARY: AttendanceSummary = {
  total_records: 200,
  present_count: 182,
  absent_count: 7,
  late_count: 11,
  half_day_count: 4,
  on_leave_count: 7,
  attendance_rate_pct: 94.8,
  avg_work_hours: 8.4,
  total_overtime_hours: 34.5,
};

export const MOCK_MANAGER_SUMMARY: ManagerTeamSummary = {
  manager_id: 'EMP002',
  team_size: 18,
  present_today: 16,
  on_leave_today: 2,
  absent_today: 0,
  pending_leave_requests: 3,
  pending_timesheets: 4,
  avg_productivity_score: 88.5,
  total_overtime_hours_month: 42.0,
};

export const MOCK_LEAVE_REQUESTS = [
  {
    leave_id: 'LV001',
    employee_id: 'EMP050',
    employee_name: 'Rohan Verma',
    department_name: 'Engineering & Technology',
    leave_type: 'Annual Leave',
    start_date: '2026-10-05',
    end_date: '2026-10-09',
    days_count: 5,
    reason: 'Family vacation and personal travel',
    status: 'Pending',
    applied_at: '2026-09-25 10:30:00',
  },
  {
    leave_id: 'LV002',
    employee_id: 'EMP004',
    employee_name: 'Priya Sharma',
    department_name: 'Product Management & Design',
    leave_type: 'Casual Leave',
    start_date: '2026-10-02',
    end_date: '2026-10-02',
    days_count: 1,
    reason: 'Personal errand and doctor appointment',
    status: 'Pending',
    applied_at: '2026-09-26 14:15:00',
  },
  {
    leave_id: 'LV003',
    employee_id: 'EMP007',
    employee_name: 'Arjun Nair',
    department_name: 'Engineering & Technology',
    leave_type: 'Sick Leave',
    start_date: '2026-09-28',
    end_date: '2026-09-29',
    days_count: 2,
    reason: 'Seasonal viral fever',
    status: 'Approved',
    applied_at: '2026-09-27 08:45:00',
  },
];

export const MOCK_NOTIFICATIONS = [
  {
    notification_id: 'NOTIF001',
    user_id: 'USR0002',
    title: 'New Leave Request Pending Approval',
    message: 'Rohan Verma (EMP050) submitted a 5-day Annual Leave request starting Oct 5.',
    category: 'APPROVAL',
    priority: 'HIGH',
    is_read: false,
    created_at: '2026-09-28 09:15:00',
  },
  {
    notification_id: 'NOTIF002',
    user_id: 'USR0002',
    title: 'Monthly Shift Schedule Published',
    message: 'Engineering rotational shifts for October 2026 have been synchronized.',
    category: 'SCHEDULE',
    priority: 'MEDIUM',
    is_read: false,
    created_at: '2026-09-27 16:00:00',
  },
  {
    notification_id: 'NOTIF003',
    user_id: 'USR0002',
    title: 'AI Anomaly Detected',
    message: 'Isolation Forest flagged 1 irregular attendance punch for Hyderabad campus.',
    category: 'SYSTEM',
    priority: 'LOW',
    is_read: true,
    created_at: '2026-09-26 11:30:00',
  },
];

export const MOCK_AI_ATTRITION: AttritionPrediction[] = [
  {
    prediction_id: 'ATT001',
    employee_id: 'EMP007',
    department_id: 'DEP001',
    risk_score: 87.5,
    risk_band: 'HIGH',
    attrition_probability: 0.875,
    top_contributing_features: ['Frequent Overtime (>25h)', 'Recent Role Stagnation', 'Low Engagement Pulse'],
    model_version: 'v1.4.2-ensemble',
    disclaimer: 'Predictive assessment derived via Gradient Boosting classifier.',
  },
  {
    prediction_id: 'ATT002',
    employee_id: 'EMP006',
    department_id: 'DEP004',
    risk_score: 64.2,
    risk_band: 'MEDIUM',
    attrition_probability: 0.642,
    top_contributing_features: ['Travel Fatigue', 'Quota Pressure', 'Market Compensation Gap'],
    model_version: 'v1.4.2-ensemble',
    disclaimer: 'Predictive assessment derived via Gradient Boosting classifier.',
  },
];

export const MOCK_AI_ANOMALIES: AttendanceAnomaly[] = [
  {
    anomaly_id: 'ANOM001',
    attendance_id: 'ATT901',
    employee_id: 'EMP007',
    date: '2026-09-26',
    anomaly_score: 0.89,
    is_anomaly: true,
    reason: 'Punch-in timestamp occurred 2.4 hours earlier than assigned shift window with high distance delta.',
    severity: 'HIGH',
    status: 'Flagged for Review',
  },
];
