/**
 * Phase 7: Notifications & Workflow Types
 */

export type NotificationPriority = 'low' | 'normal' | 'high' | 'critical';

export type NotificationCategory =
  | 'attendance'
  | 'leave'
  | 'shifts'
  | 'timesheets'
  | 'payroll'
  | 'performance'
  | 'training'
  | 'celebration'
  | 'ai_alerts'
  | 'compliance'
  | 'system';

export interface NotificationItem {
  notification_id: string;
  employee_id?: string;
  recipient_employee_id?: string;
  recipient_user_id?: string;
  title: string;
  message: string;
  priority: NotificationPriority;
  category: NotificationCategory | string;
  type?: string;
  entity_type?: string;
  entity_id?: string;
  action_url?: string;
  channels?: string[];
  is_read: boolean | number;
  created_at: string;
  read_at?: string | null;
  metadata?: Record<string, any>;
}

export interface NotificationPreferences {
  employee_id: string;
  attendance_alerts: boolean;
  leave_notifications: boolean;
  shift_notifications: boolean;
  timesheet_notifications: boolean;
  payroll_notifications: boolean;
  performance_notifications: boolean;
  training_notifications: boolean;
  birthday_notifications: boolean;
  anniversary_notifications: boolean;
  ai_alerts: boolean;
  compliance_notifications: boolean;
  email_enabled: boolean;
  in_app_enabled: boolean;
}

export interface WorkflowRuleItem {
  rule_id: string;
  name: string;
  description: string;
  event_type: string;
  is_active: boolean;
  actions: string[];
  conditions?: Record<string, any>;
}

export interface WorkflowStatusItem {
  is_running: boolean;
  interval_seconds: number;
  last_run_timestamp?: string | null;
  stats?: {
    total_runs: number;
    alerts_generated: number;
    last_error?: string | null;
  };
}
