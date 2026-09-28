-- AI-Powered Workforce Management Automation System
-- Database Schema (SQLite / PostgreSQL Compatible DDL)
-- Version 1.0 (Phase 1)

PRAGMA foreign_keys = ON;

-- 1. Locations
CREATE TABLE IF NOT EXISTS locations (
    location_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'India',
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    geofence_radius_meters REAL NOT NULL DEFAULT 500.0,
    timezone TEXT NOT NULL DEFAULT 'Asia/Kolkata'
);

-- 2. Departments
CREATE TABLE IF NOT EXISTS departments (
    department_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL UNIQUE,
    description TEXT,
    head_employee_id TEXT,
    budget REAL NOT NULL DEFAULT 0.0
);

-- 3. Shifts
CREATE TABLE IF NOT EXISTS shifts (
    shift_id TEXT PRIMARY KEY,
    shift_name TEXT NOT NULL UNIQUE,
    start_time TEXT NOT NULL, -- HH:MM (24-hr)
    end_time TEXT NOT NULL,   -- HH:MM (24-hr)
    grace_period_mins INTEGER NOT NULL DEFAULT 15,
    is_rotational INTEGER NOT NULL DEFAULT 0
);

-- 4. Employees (Strictly 200 Employees EMP001 to EMP200)
CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    gender TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    joining_date TEXT NOT NULL,
    employment_type TEXT NOT NULL, -- 'Full-Time', 'Contract', 'Intern'
    designation TEXT NOT NULL,
    department_id TEXT NOT NULL,
    manager_id TEXT,               -- Nullable for the CEO
    location_id TEXT NOT NULL,
    salary REAL NOT NULL,          -- Annual base salary
    experience REAL NOT NULL,      -- Years of experience
    employment_status TEXT NOT NULL DEFAULT 'Active', -- 'Active', 'On Notice', 'On Leave'
    role TEXT NOT NULL DEFAULT 'EMPLOYEE',            -- 'ADMIN', 'HR', 'MANAGER', 'EMPLOYEE'
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE RESTRICT,
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL,
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE RESTRICT
);

-- Circular foreign key from departments to employees for Department Head
-- Handled after employee creation or deferred in SQLite

-- 5. Skills
CREATE TABLE IF NOT EXISTS skills (
    skill_id TEXT PRIMARY KEY,
    skill_name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL -- 'Technical', 'Data & AI', 'Management', 'Operations', 'Soft Skills'
);

-- 6. Employee Skills
CREATE TABLE IF NOT EXISTS employee_skills (
    employee_id TEXT NOT NULL,
    skill_id TEXT NOT NULL,
    proficiency_level TEXT NOT NULL, -- 'Beginner', 'Intermediate', 'Advanced', 'Expert'
    years_experience REAL NOT NULL DEFAULT 1.0,
    PRIMARY KEY (employee_id, skill_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

-- 7. Projects
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    client_name TEXT NOT NULL,
    department_id TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT,
    status TEXT NOT NULL DEFAULT 'Active', -- 'Active', 'Completed', 'Planning'
    budget REAL NOT NULL DEFAULT 0.0,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE RESTRICT
);

-- 8. Employee Project Assignments
CREATE TABLE IF NOT EXISTS employee_projects (
    assignment_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    role TEXT NOT NULL,
    allocation_percentage REAL NOT NULL DEFAULT 100.0,
    start_date TEXT NOT NULL,
    end_date TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

-- 9. Employee Shift Assignments
CREATE TABLE IF NOT EXISTS employee_shifts (
    schedule_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    shift_id TEXT NOT NULL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (shift_id) REFERENCES shifts(shift_id) ON DELETE RESTRICT
);

-- 10. Attendance Records (~6 months history)
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    date TEXT NOT NULL,
    check_in TEXT,
    check_out TEXT,
    attendance_status TEXT NOT NULL, -- 'Present', 'Absent', 'Late', 'Half Day', 'Work From Home', 'Holiday', 'Leave'
    attendance_method TEXT,          -- 'Biometric', 'Face Recognition', 'GPS', 'QR Code'
    location_id TEXT,
    late_minutes INTEGER NOT NULL DEFAULT 0,
    overtime_hours REAL NOT NULL DEFAULT 0.0,
    shift_id TEXT NOT NULL,
    anomaly_flag INTEGER NOT NULL DEFAULT 0,
    anomaly_reason TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL,
    FOREIGN KEY (shift_id) REFERENCES shifts(shift_id) ON DELETE RESTRICT
);

-- 11. Leave Balances
CREATE TABLE IF NOT EXISTS leave_balances (
    balance_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    leave_type TEXT NOT NULL, -- 'Annual Leave', 'Sick Leave', 'Casual Leave', 'Emergency Leave', 'Maternity/Paternity Leave'
    allocated_days REAL NOT NULL,
    used_days REAL NOT NULL DEFAULT 0.0,
    remaining_days REAL NOT NULL,
    year INTEGER NOT NULL DEFAULT 2026,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    UNIQUE (employee_id, leave_type, year)
);

-- 12. Leave Requests
CREATE TABLE IF NOT EXISTS leave_requests (
    leave_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    leave_type TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    days_count REAL NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
    approved_by TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES employees(employee_id) ON DELETE SET NULL
);

-- 13. Timesheets
CREATE TABLE IF NOT EXISTS timesheets (
    timesheet_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    date TEXT NOT NULL,
    project_id TEXT NOT NULL,
    hours_worked REAL NOT NULL,
    billable_hours REAL NOT NULL,
    non_billable_hours REAL NOT NULL DEFAULT 0.0,
    overtime_hours REAL NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT 'Submitted', -- 'Submitted', 'Approved', 'Rejected'
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT
);

-- 14. Payroll Inputs & Records
CREATE TABLE IF NOT EXISTS payroll (
    payroll_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    month TEXT NOT NULL, -- 'YYYY-MM'
    base_salary REAL NOT NULL,
    overtime_pay REAL NOT NULL DEFAULT 0.0,
    leave_deduction REAL NOT NULL DEFAULT 0.0,
    incentives REAL NOT NULL DEFAULT 0.0,
    bonuses REAL NOT NULL DEFAULT 0.0,
    gross_salary REAL NOT NULL,
    deductions REAL NOT NULL,
    net_salary REAL NOT NULL,
    payment_status TEXT NOT NULL DEFAULT 'Processed', -- 'Pending', 'Processed', 'Paid'
    payment_date TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    UNIQUE (employee_id, month)
);

-- 15. Performance Reviews
CREATE TABLE IF NOT EXISTS performance_reviews (
    review_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    kpi_score REAL NOT NULL,            -- 0 to 100
    goal_completion REAL NOT NULL,     -- 0 to 100 percentage
    productivity_score REAL NOT NULL,   -- 0 to 100
    manager_feedback TEXT NOT NULL,
    performance_rating TEXT NOT NULL,   -- 'Outstanding', 'Exceeds Expectations', 'Meets Expectations', 'Needs Improvement', 'Unsatisfactory'
    review_date TEXT NOT NULL,
    reviewer_id TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES employees(employee_id) ON DELETE RESTRICT
);

-- 16. Training Records
CREATE TABLE IF NOT EXISTS training_records (
    training_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    training_name TEXT NOT NULL,
    skill TEXT NOT NULL,
    completion_status TEXT NOT NULL, -- 'Completed', 'In Progress', 'Assigned'
    start_date TEXT NOT NULL,
    completion_date TEXT,
    score REAL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- 17. Training Recommendations
CREATE TABLE IF NOT EXISTS training_recommendations (
    recommendation_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    recommended_course TEXT NOT NULL,
    target_skill TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- 18. Company Holidays
CREATE TABLE IF NOT EXISTS company_holidays (
    holiday_id TEXT PRIMARY KEY,
    holiday_name TEXT NOT NULL,
    date TEXT NOT NULL,
    location_id TEXT NOT NULL DEFAULT 'ALL' -- 'ALL' or specific location_id
);

-- 19. Notifications
CREATE TABLE IF NOT EXISTS notifications (
    notification_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    category TEXT NOT NULL, -- 'Shift reminder', 'Leave approval', 'Attendance alert', 'Timesheet reminder', 'Birthday', 'Work anniversary', 'Payroll notification'
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- 20. User Accounts (Authentication & RBAC)
CREATE TABLE IF NOT EXISTS user_accounts (
    user_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL, -- 'ADMIN', 'HR', 'MANAGER', 'EMPLOYEE'
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_employees_manager ON employees(manager_id);
CREATE INDEX IF NOT EXISTS idx_employees_location ON employees(location_id);
CREATE INDEX IF NOT EXISTS idx_attendance_employee_date ON attendance(employee_id, date);
CREATE INDEX IF NOT EXISTS idx_attendance_anomaly ON attendance(anomaly_flag);
CREATE INDEX IF NOT EXISTS idx_payroll_employee_month ON payroll(employee_id, month);
CREATE INDEX IF NOT EXISTS idx_timesheets_employee_date ON timesheets(employee_id, date);
CREATE INDEX IF NOT EXISTS idx_leave_requests_employee ON leave_requests(employee_id);
CREATE INDEX IF NOT EXISTS idx_notifications_employee ON notifications(employee_id, is_read);
