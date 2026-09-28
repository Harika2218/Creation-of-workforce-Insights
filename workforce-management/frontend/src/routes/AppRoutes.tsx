import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ProtectedRoute } from './ProtectedRoute';
import { MainLayout } from '../layouts/MainLayout';

// Auth & Error Pages
import { LoginPage } from '../pages/auth/LoginPage';
import { NotFoundPage } from '../pages/errors/NotFoundPage';
import { UnauthorizedPage } from '../pages/errors/UnauthorizedPage';

// Dashboards
import { HRDashboard } from '../pages/dashboard/HRDashboard';
import { ManagerDashboard } from '../pages/dashboard/ManagerDashboard';
import { EmployeeDashboard } from '../pages/dashboard/EmployeeDashboard';

// Modules
import { EmployeeListPage } from '../pages/employees/EmployeeListPage';
import { EmployeeDetailPage } from '../pages/employees/EmployeeDetailPage';
import { AttendancePage } from '../pages/attendance/AttendancePage';
import { ShiftsPage } from '../pages/shifts/ShiftsPage';
import { LeavePage } from '../pages/leave/LeavePage';
import { TimesheetsPage } from '../pages/timesheets/TimesheetsPage';
import { ProjectsPage } from '../pages/projects/ProjectsPage';
import { PayrollPage } from '../pages/payroll/PayrollPage';
import { PerformancePage } from '../pages/performance/PerformancePage';
import { SkillsTrainingPage } from '../pages/skills/SkillsTrainingPage';
import { ManagerTeamPage } from '../pages/manager/ManagerTeamPage';
import { ReportsPage } from '../pages/reports/ReportsPage';
import { HolidaysPage } from '../pages/holidays/HolidaysPage';
import { NotificationsPage } from '../pages/notifications/NotificationsPage';
import { AIIntelligencePage } from '../pages/ai/AIIntelligencePage';
import { ChatbotPage } from '../pages/chatbot/ChatbotPage';
import { IntegrationsPage } from '../pages/settings/IntegrationsPage';

export const AppRoutes: React.FC = () => {
  const { user, isAuthenticated } = useAuth();

  // Root redirect based on role
  const getRootRedirect = () => {
    if (!isAuthenticated || !user) return <Navigate to="/login" replace />;
    if (user.role === 'ADMIN' || user.role === 'HR') return <Navigate to="/dashboard" replace />;
    if (user.role === 'MANAGER') return <Navigate to="/manager/dashboard" replace />;
    return <Navigate to="/employee/dashboard" replace />;
  };

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/unauthorized" element={<UnauthorizedPage />} />

      {/* Protected Routes inside MainLayout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={getRootRedirect()} />

        {/* Dashboards */}
        <Route
          path="dashboard"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'HR']}>
              <HRDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="manager/dashboard"
          element={
            <ProtectedRoute allowedRoles={['MANAGER']}>
              <ManagerDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="employee/dashboard"
          element={
            <ProtectedRoute allowedRoles={['EMPLOYEE']}>
              <EmployeeDashboard />
            </ProtectedRoute>
          }
        />

        {/* Manager Team View */}
        <Route
          path="manager/team"
          element={
            <ProtectedRoute allowedRoles={['MANAGER']}>
              <ManagerTeamPage />
            </ProtectedRoute>
          }
        />

        {/* Employee Directory & Profile */}
        <Route
          path="employees"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'HR']}>
              <EmployeeListPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="employees/:id"
          element={
            <ProtectedRoute>
              <EmployeeDetailPage />
            </ProtectedRoute>
          }
        />

        {/* Attendance */}
        <Route path="attendance" element={<AttendancePage />} />

        {/* Shifts */}
        <Route path="shifts" element={<ShiftsPage />} />

        {/* Leaves */}
        <Route path="leave" element={<LeavePage />} />

        {/* Timesheets */}
        <Route path="timesheets" element={<TimesheetsPage />} />

        {/* Projects */}
        <Route
          path="projects"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'HR']}>
              <ProjectsPage />
            </ProtectedRoute>
          }
        />

        {/* Payroll */}
        <Route
          path="payroll"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'HR', 'EMPLOYEE']}>
              <PayrollPage />
            </ProtectedRoute>
          }
        />

        {/* Performance */}
        <Route
          path="performance"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'HR', 'MANAGER']}>
              <PerformancePage />
            </ProtectedRoute>
          }
        />

        {/* Skills & Training */}
        <Route
          path="skills-training"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'HR']}>
              <SkillsTrainingPage />
            </ProtectedRoute>
          }
        />

        {/* Reports */}
        <Route
          path="reports"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'HR']}>
              <ReportsPage />
            </ProtectedRoute>
          }
        />

        {/* AI Workforce Intelligence */}
        <Route
          path="ai-intelligence"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'HR', 'MANAGER']}>
              <AIIntelligencePage />
            </ProtectedRoute>
          }
        />

        {/* Holidays & Notifications */}
        <Route path="holidays" element={<HolidaysPage />} />
        <Route path="notifications" element={<NotificationsPage />} />

        {/* AI HR Assistant & RAG */}
        <Route path="ai-assistant" element={<ChatbotPage />} />

        {/* Enterprise Integrations (Admin Only) */}
        <Route
          path="settings/integrations"
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <IntegrationsPage />
            </ProtectedRoute>
          }
        />
      </Route>

      {/* 404 Fallback */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};
