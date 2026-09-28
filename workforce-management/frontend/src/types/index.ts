// ============================================================================
// TypeScript Domain Models & API Types
// ============================================================================

export type Role = 'ADMIN' | 'HR' | 'MANAGER' | 'EMPLOYEE';

export interface User {
  user_id: string;
  employee_id: string;
  email: string;
  name: string;
  role: Role;
  department_id?: string;
  designation?: string;
  is_active: boolean;
  avatar_url?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  employee_id: string;
  email: string;
  role: Role;
}

export interface Employee {
  employee_id: string;
  name: string;
  email: string;
  phone: string;
  department_id: string;
  department_name?: string;
  designation: string;
  role: Role;
  manager_id: string | null;
  manager_name?: string;
  location_id: string;
  location_name?: string;
  date_of_joining: string;
  employment_type: string;
  employment_status: 'Active' | 'Notice Period' | 'Deactivated';
  base_salary: number;
}

export interface EmployeeProfile extends Employee {
  skills?: Array<{ skill_id: string; skill_name: string; proficiency: string }>;
  leave_balances?: Record<string, number>;
  total_experience_years?: number;
}

export interface Department {
  department_id: string;
  department_name: string;
  code: string;
  description: string;
  head_employee_id: string | null;
  active_employees_count?: number;
}

export interface AttendanceRecord {
  attendance_id: string;
  employee_id: string;
  employee_name?: string;
  date: string;
  shift_id: string;
  check_in_time: string | null;
  check_out_time: string | null;
  work_hours: number;
  late_minutes: number;
  overtime_hours: number;
  status: 'Present' | 'Absent' | 'Late' | 'Half-day' | 'On Leave';
  attendance_method: 'Biometric' | 'GPS' | 'Web' | 'Auto';
  anomaly_flag: boolean;
  latitude?: number;
  longitude?: number;
}

export interface AttendanceSummary {
  total_records: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  half_day_count: number;
  on_leave_count: number;
  attendance_rate_pct: number;
  avg_work_hours: number;
  total_overtime_hours: number;
}

export interface ShiftTemplate {
  shift_id: string;
  shift_name: string;
  start_time: string;
  end_time: string;
  grace_period_mins: number;
  break_duration_mins: number;
  is_active: boolean;
}

export interface ShiftSchedule {
  allocation_id: string;
  employee_id: string;
  shift_id: string;
  shift_name?: string;
  start_time?: string;
  end_time?: string;
  date: string;
  status: string;
}

export interface ShiftSwapRequest {
  swap_id: string;
  requestor_employee_id: string;
  target_employee_id: string;
  requestor_shift_date: string;
  target_shift_date: string;
  reason: string;
  status: 'Pending' | 'Approved' | 'Rejected';
  approved_by_manager_id?: string;
}

export interface LeaveRequest {
  leave_id: string;
  employee_id: string;
  employee_name?: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  days_count: number;
  reason: string;
  status: 'Pending' | 'Approved' | 'Rejected';
  applied_date: string;
  approved_by?: string;
  rejection_reason?: string;
}

export interface LeaveBalance {
  employee_id: string;
  annual_leave: number;
  sick_leave: number;
  casual_leave: number;
  emergency_leave: number;
  maternity_paternity_leave: number;
}

export interface TimesheetRecord {
  timesheet_id: string;
  employee_id: string;
  employee_name?: string;
  project_id: string;
  project_name?: string;
  date: string;
  hours_worked: number;
  billable_hours: number;
  non_billable_hours: number;
  task_description: string;
  status: 'Submitted' | 'Approved' | 'Rejected';
  approved_by?: string;
  rejection_reason?: string;
}

export interface Project {
  project_id: string;
  project_name: string;
  client_name: string;
  start_date: string;
  end_date: string | null;
  status: 'Active' | 'Completed' | 'On Hold';
  manager_id: string;
  manager_name?: string;
  budget_inr: number;
}

export interface PayrollRecord {
  payroll_id: string;
  employee_id: string;
  employee_name?: string;
  payroll_month: string;
  base_salary: number;
  hra: number;
  special_allowances: number;
  overtime_pay: number;
  bonuses: number;
  gross_salary: number;
  pf_deduction: number;
  tax_deduction: number;
  other_deductions: number;
  net_salary: number;
  payment_status: 'Paid' | 'Processing' | 'Pending';
  payment_date: string | null;
}

export interface PayrollSummary {
  month: string;
  total_employees: number;
  total_gross_disbursement: number;
  total_net_disbursement: number;
  total_deductions: number;
  avg_net_salary: number;
}

export interface PerformanceReview {
  review_id: string;
  employee_id: string;
  employee_name?: string;
  review_cycle: string;
  reviewer_id: string;
  rating_score: number; // 1-5
  kpis: Record<string, number>;
  feedback: string;
  goals: string[];
  submission_date: string;
}

export interface SkillItem {
  skill_id: string;
  name: string;
  category: string;
  description: string;
}

export interface EmployeeSkill {
  skill_id: string;
  skill_name: string;
  category: string;
  proficiency_level: 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert';
  years_experience: number;
}

export interface TrainingProgram {
  program_id: string;
  title: string;
  provider: string;
  duration_hours: number;
  category: string;
  description: string;
}

export interface TrainingRecord {
  enrollment_id: string;
  employee_id: string;
  program_id: string;
  program_title: string;
  status: 'Enrolled' | 'In Progress' | 'Completed';
  completion_date?: string;
  score?: number;
}

export interface Holiday {
  holiday_id: string;
  holiday_name: string;
  date: string;
  location_id: string | null;
  type: string;
}

export * from './notification';

export interface HRSummaryMetrics {
  total_employees: number;
  active_employees: number;
  notice_period_employees: number;
  departments_count: number;
  locations_count: number;
  daily_attendance_rate: number;
  pending_leave_requests: number;
  total_monthly_payroll: number;
  attrition_risk_high: number;
  attrition_risk_medium: number;
  attrition_risk_low: number;
}

export interface ManagerTeamSummary {
  manager_id: string;
  team_size: number;
  present_today: number;
  on_leave_today: number;
  absent_today: number;
  pending_leave_requests: number;
  pending_timesheets: number;
  avg_productivity_score: number;
  total_overtime_hours_month: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
