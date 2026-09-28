import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Clock,
  CalendarDays,
  FileSpreadsheet,
  Banknote,
  Award,
  BookOpen,
  BarChart3,
  Calendar,
  Briefcase,
  Bell,
  UserCheck,
  ShieldCheck,
  LogOut,
  ChevronRight,
  BrainCircuit,
  Sparkles,
  Settings,
  Plug,
  X,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Role } from '../types';

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  roles: Role[];
}

export const Sidebar: React.FC<{ isOpen: boolean; onClose?: () => void }> = ({ isOpen, onClose }) => {
  const { user, logout } = useAuth();

  const navItems: NavItem[] = [
    // Dashboards
    {
      label: 'HR Dashboard',
      path: '/dashboard',
      icon: <LayoutDashboard size={19} />,
      roles: ['ADMIN', 'HR'],
    },
    {
      label: 'Manager Dashboard',
      path: '/manager/dashboard',
      icon: <LayoutDashboard size={19} />,
      roles: ['MANAGER'],
    },
    {
      label: 'My Dashboard',
      path: '/employee/dashboard',
      icon: <LayoutDashboard size={19} />,
      roles: ['EMPLOYEE'],
    },

    // Manager Team Portal
    {
      label: 'My Team',
      path: '/manager/team',
      icon: <UserCheck size={19} />,
      roles: ['MANAGER'],
    },

    // Workforce & Employees
    {
      label: 'Employees',
      path: '/employees',
      icon: <Users size={19} />,
      roles: ['ADMIN', 'HR'],
    },

    // Attendance & Clocks
    {
      label: 'Attendance',
      path: '/attendance',
      icon: <Clock size={19} />,
      roles: ['ADMIN', 'HR', 'MANAGER', 'EMPLOYEE'],
    },

    // Shifts
    {
      label: 'Shifts & Schedules',
      path: '/shifts',
      icon: <CalendarDays size={19} />,
      roles: ['ADMIN', 'HR', 'MANAGER', 'EMPLOYEE'],
    },

    // Leaves
    {
      label: 'Leave Management',
      path: '/leave',
      icon: <Calendar size={19} />,
      roles: ['ADMIN', 'HR', 'MANAGER', 'EMPLOYEE'],
    },

    // Timesheets
    {
      label: 'Timesheets',
      path: '/timesheets',
      icon: <FileSpreadsheet size={19} />,
      roles: ['ADMIN', 'HR', 'MANAGER', 'EMPLOYEE'],
    },

    // Projects
    {
      label: 'Projects',
      path: '/projects',
      icon: <Briefcase size={19} />,
      roles: ['ADMIN', 'HR'],
    },

    // Payroll
    {
      label: 'Payroll & Payslips',
      path: '/payroll',
      icon: <Banknote size={19} />,
      roles: ['ADMIN', 'HR', 'EMPLOYEE'],
    },

    // Performance
    {
      label: 'Performance & KPIs',
      path: '/performance',
      icon: <Award size={19} />,
      roles: ['ADMIN', 'HR', 'MANAGER'],
    },

    // Skills & Training
    {
      label: 'Skills & Training',
      path: '/skills-training',
      icon: <BookOpen size={19} />,
      roles: ['ADMIN', 'HR'],
    },

    // Reports
    {
      label: 'Reports & Analytics',
      path: '/reports',
      icon: <BarChart3 size={19} />,
      roles: ['ADMIN', 'HR'],
    },

    // AI Intelligence
    {
      label: 'Workforce AI',
      path: '/ai-intelligence',
      icon: <BrainCircuit size={19} />,
      roles: ['ADMIN', 'HR', 'MANAGER'],
    },

    // AI HR Assistant (Chatbot & RAG)
    {
      label: 'AI HR Assistant',
      path: '/ai-assistant',
      icon: <Sparkles size={19} />,
      roles: ['ADMIN', 'HR', 'MANAGER', 'EMPLOYEE'],
    },

    // Holidays
    {
      label: 'Holiday Calendar',
      path: '/holidays',
      icon: <CalendarDays size={19} />,
      roles: ['ADMIN', 'HR', 'MANAGER', 'EMPLOYEE'],
    },

    // Notifications
    {
      label: 'Notifications',
      path: '/notifications',
      icon: <Bell size={19} />,
      roles: ['ADMIN', 'HR', 'MANAGER', 'EMPLOYEE'],
    },

    // Settings & Preferences
    {
      label: 'Settings',
      path: '/notifications',
      icon: <Settings size={19} />,
      roles: ['ADMIN', 'HR', 'MANAGER', 'EMPLOYEE'],
    },

    // Enterprise Integrations (Admin only)
    {
      label: 'Integrations',
      path: '/settings/integrations',
      icon: <Plug size={19} />,
      roles: ['ADMIN'],
    },
  ];

  const filteredItems = navItems.filter((item) =>
    user?.role ? item.roles.includes(user.role) : false
  );

  return (
    <aside
      className={`app-sidebar ${isOpen ? '' : 'sidebar-closed'}`}
      style={{
        width: 'var(--sidebar-width)',
        backgroundColor: 'var(--bg-sidebar)',
        borderRight: 'var(--border-glass)',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        transition: 'transform var(--transition-base)',
      }}
    >
      {/* Brand Header */}
      <div
        style={{
          padding: '1.25rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          borderBottom: 'var(--border-glass)',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--gradient-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF',
              fontWeight: 800,
              fontSize: '1.2rem',
              boxShadow: '0 2px 10px rgba(99, 102, 241, 0.4)',
            }}
          >
            <ShieldCheck size={22} />
          </div>
          <div>
            <div
              style={{
                fontFamily: 'var(--font-heading)',
                fontSize: '1.15rem',
                fontWeight: 800,
                background: 'linear-gradient(135deg, #FFFFFF 0%, #9CA3AF 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                letterSpacing: '0.02em',
              }}
            >
              HRvantage
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontWeight: 600 }}>
              Enterprise HRMS v1.0
            </div>
          </div>
        </div>

        {onClose && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Close menu drawer"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-dim)',
              cursor: 'pointer',
              padding: '6px',
              borderRadius: '6px',
            }}
          >
            <X size={20} />
          </button>
        )}
      </div>

      {/* Navigation List */}
      <nav
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '1rem 0.75rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.25rem',
        }}
      >
        <div
          style={{
            padding: '0.4rem 0.75rem',
            fontSize: '0.72rem',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            fontWeight: 700,
            color: 'var(--text-dim)',
          }}
        >
          Main Menu
        </div>

        {filteredItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            onClick={onClose}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '0.65rem 0.85rem',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.88rem',
              fontWeight: isActive ? 600 : 500,
              color: isActive ? '#FFFFFF' : 'var(--text-muted)',
              backgroundColor: isActive ? 'rgba(99, 102, 241, 0.16)' : 'transparent',
              border: isActive ? '1px solid rgba(99, 102, 241, 0.3)' : '1px solid transparent',
              transition: 'all var(--transition-fast)',
            })}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ display: 'flex', alignItems: 'center' }}>{item.icon}</span>
              <span>{item.label}</span>
            </div>
            <ChevronRight size={14} style={{ opacity: 0.4 }} />
          </NavLink>
        ))}
      </nav>

      {/* User Status Footer */}
      <div
        style={{
          padding: '1rem',
          borderTop: 'var(--border-glass)',
          background: 'rgba(0, 0, 0, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', overflow: 'hidden' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: 'var(--radius-full)',
              background: 'var(--gradient-accent)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: '0.9rem',
              color: '#0B0F19',
              flexShrink: 0,
            }}
          >
            {user?.name?.charAt(0) || 'U'}
          </div>
          <div style={{ overflow: 'hidden' }}>
            <div
              style={{
                fontSize: '0.85rem',
                fontWeight: 600,
                color: '#FFFFFF',
                whiteSpace: 'nowrap',
                textOverflow: 'ellipsis',
                overflow: 'hidden',
              }}
            >
              {user?.name || 'User'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
              {user?.role} • {user?.employee_id}
            </div>
          </div>
        </div>

        <button
          onClick={logout}
          title="Sign Out"
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-dim)',
            cursor: 'pointer',
            padding: '6px',
            borderRadius: 'var(--radius-sm)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <LogOut size={18} />
        </button>
      </div>
    </aside>
  );
};
