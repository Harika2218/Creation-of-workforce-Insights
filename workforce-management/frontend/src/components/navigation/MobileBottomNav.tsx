import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Clock,
  Calendar,
  CalendarDays,
  Sparkles,
  UserCheck,
  Users,
  BarChart3,
  Menu,
  FileSpreadsheet,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface MobileBottomNavProps {
  onOpenDrawer: () => void;
}

export const MobileBottomNav: React.FC<MobileBottomNavProps> = ({ onOpenDrawer }) => {
  const { user } = useAuth();
  const role = user?.role || 'EMPLOYEE';

  // Role-Aware Navigation Tabs
  const getNavTabs = () => {
    if (role === 'EMPLOYEE') {
      return [
        { label: 'Home', path: '/employee/dashboard', icon: <LayoutDashboard size={20} /> },
        { label: 'Clock', path: '/attendance', icon: <Clock size={20} /> },
        { label: 'Leaves', path: '/leave', icon: <Calendar size={20} /> },
        { label: 'Shifts', path: '/shifts', icon: <CalendarDays size={20} /> },
        { label: 'AI Help', path: '/ai-assistant', icon: <Sparkles size={20} /> },
      ];
    } else if (role === 'MANAGER') {
      return [
        { label: 'Home', path: '/manager/dashboard', icon: <LayoutDashboard size={20} /> },
        { label: 'Team', path: '/manager/team', icon: <UserCheck size={20} /> },
        { label: 'Leaves', path: '/leave', icon: <Calendar size={20} /> },
        { label: 'Timesheets', path: '/timesheets', icon: <FileSpreadsheet size={20} /> },
        { label: 'AI Help', path: '/ai-assistant', icon: <Sparkles size={20} /> },
      ];
    } else {
      // HR or ADMIN
      return [
        { label: 'Home', path: '/dashboard', icon: <LayoutDashboard size={20} /> },
        { label: 'Staff', path: '/employees', icon: <Users size={20} /> },
        { label: 'Attendance', path: '/attendance', icon: <Clock size={20} /> },
        { label: 'Analytics', path: '/reports', icon: <BarChart3 size={20} /> },
        { label: 'AI Help', path: '/ai-assistant', icon: <Sparkles size={20} /> },
      ];
    }
  };

  const tabs = getNavTabs();

  return (
    <nav
      aria-label="Mobile Navigation"
      className="mobile-bottom-nav"
      style={{
        display: 'none', // Controlled via CSS media queries (<768px -> flex)
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        height: '62px',
        backgroundColor: 'var(--bg-topbar)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderTop: 'var(--border-glass)',
        zIndex: 1000,
        paddingBottom: 'env(safe-area-inset-bottom, 0px)',
        justifyContent: 'space-around',
        alignItems: 'center',
      }}
    >
      {tabs.map((tab) => (
        <NavLink
          key={tab.path}
          to={tab.path}
          className={({ isActive }) =>
            `mobile-nav-item ${isActive ? 'active' : ''}`
          }
          style={({ isActive }) => ({
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            flex: 1,
            height: '100%',
            minWidth: '48px',
            color: isActive ? 'var(--primary)' : 'var(--text-dim)',
            textDecoration: 'none',
            fontSize: '0.68rem',
            fontWeight: isActive ? 600 : 500,
            transition: 'color var(--transition-fast)',
            gap: '2px',
          })}
        >
          {tab.icon}
          <span>{tab.label}</span>
        </NavLink>
      ))}

      {/* More / Menu Drawer Trigger */}
      <button
        type="button"
        onClick={onOpenDrawer}
        aria-label="Open complete menu"
        className="mobile-nav-item"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          flex: 1,
          height: '100%',
          minWidth: '48px',
          background: 'none',
          border: 'none',
          color: 'var(--text-dim)',
          cursor: 'pointer',
          fontSize: '0.68rem',
          fontWeight: 500,
          gap: '2px',
        }}
      >
        <Menu size={20} />
        <span>Menu</span>
      </button>
    </nav>
  );
};

export default MobileBottomNav;
