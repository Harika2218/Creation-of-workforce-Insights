import React, { useState, useEffect, useCallback } from 'react';
import { Menu, Bell, Search, LogOut, User as UserIcon, Check, CheckCheck, ExternalLink, Zap, Sun, Moon, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { useTheme } from '../context/ThemeContext';
import { Badge } from '../components/common/Badge';
import { notificationService } from '../services/notificationService';
import { notificationSocket } from '../services/notificationSocket';
import { NotificationItem } from '../types';
import { Link, useNavigate } from 'react-router-dom';

interface TopbarProps {
  onToggleSidebar: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({ onToggleSidebar }) => {
  const { user, token, logout } = useAuth();
  const { showToast } = useToast();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [showNotifications, setShowNotifications] = useState<boolean>(false);
  const [showProfileMenu, setShowProfileMenu] = useState<boolean>(false);
  const [isLiveWs, setIsLiveWs] = useState<boolean>(false);

  const fetchNotifications = useCallback(async () => {
    try {
      const list = await notificationService.getNotifications({ page_size: 15 });
      setNotifications(list);
    } catch {
      // Handled silently
    }
  }, []);

  useEffect(() => {
    fetchNotifications();

    // 1. Establish WebSocket connection if token available
    const activeToken = token || localStorage.getItem('token');
    if (activeToken) {
      notificationSocket.connect(activeToken);
    }

    // 2. Subscribe to incoming live push notifications
    const unsubNotif = notificationSocket.subscribe((newNotif: NotificationItem) => {
      setNotifications((prev) => {
        // Prevent duplicate in UI state
        if (prev.some((n) => n.notification_id === newNotif.notification_id)) {
          return prev;
        }
        return [newNotif, ...prev];
      });
      showToast(`[${newNotif.category.toUpperCase()}] ${newNotif.title}`, 'info');
    });

    // 3. Subscribe to WebSocket status
    const unsubStatus = notificationSocket.subscribeStatus((connected: boolean) => {
      setIsLiveWs(connected);
    });

    // 4. Periodic polling fallback every 30s
    const pollInterval = setInterval(() => {
      if (!notificationSocket.getIsConnected()) {
        fetchNotifications();
      }
    }, 30000);

    return () => {
      unsubNotif();
      unsubStatus();
      clearInterval(pollInterval);
    };
  }, [token, fetchNotifications, showToast]);

  const unreadCount = notifications.filter((n) => !n.is_read || n.is_read === 0).length;

  const handleMarkAsRead = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await notificationService.markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.notification_id === id ? { ...n, is_read: 1 } : n))
      );
    } catch {
      // Handled silently
    }
  };

  const handleMarkAllAsRead = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await notificationService.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: 1 })));
      showToast('All notifications marked as read.', 'success');
    } catch {
      showToast('Failed to mark all as read.', 'error');
    }
  };

  const handleNotificationClick = (n: NotificationItem) => {
    if (!n.is_read || n.is_read === 0) {
      notificationService.markAsRead(n.notification_id).catch(() => {});
      setNotifications((prev) =>
        prev.map((item) => (item.notification_id === n.notification_id ? { ...item, is_read: 1 } : item))
      );
    }
    setShowNotifications(false);
    if (n.action_url) {
      navigate(n.action_url);
    } else {
      navigate('/notifications');
    }
  };

  const getPriorityBadgeVariant = (priority?: string) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'danger';
      case 'normal':
        return 'warning';
      default:
        return 'info';
    }
  };

  return (
    <header
      style={{
        height: 'var(--topbar-height)',
        backgroundColor: 'var(--bg-topbar)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderBottom: 'var(--border-glass)',
        padding: '0 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 40,
      }}
    >
      {/* Left section: Hamburger & Search */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1, maxWidth: '480px' }}>
        <button
          onClick={onToggleSidebar}
          className="btn btn-ghost btn-icon"
          aria-label="Toggle navigation"
        >
          <Menu size={20} />
        </button>

        <div className="search-wrapper" style={{ flex: 1 }}>
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="form-control search-input"
            placeholder="Search employees, departments, projects... (Ctrl + K)"
            style={{ height: '38px', fontSize: '0.85rem' }}
          />
        </div>
      </div>

      {/* Right section: System Status, Notifications & Profile */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {/* Real-time connection status indicator */}
        <div
          title={isLiveWs ? 'Connected to live real-time WebSocket' : 'Polling mode (30s interval)'}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            fontSize: '0.78rem',
            color: 'var(--text-dim)',
            padding: '0.2rem 0.6rem',
            borderRadius: 'var(--radius-full)',
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid var(--border-subtle)'
          }}
        >
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: isLiveWs ? 'var(--success)' : '#eab308',
              boxShadow: isLiveWs ? '0 0 8px var(--success)' : '0 0 6px #eab308',
            }}
          />
          <span style={{ fontWeight: 500 }}>{isLiveWs ? 'Real-Time' : 'System Live'}</span>
        </div>

        {/* AI Assistant Quick Shortcut */}
        <Link
          to="/ai-assistant"
          className="btn btn-ghost btn-icon"
          title="Launch 3D AI HR Assistant"
          aria-label="Launch AI Assistant"
          style={{ position: 'relative', color: 'var(--primary)' }}
        >
          <Sparkles size={19} />
        </Link>

        {/* Dark / Light Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="btn btn-ghost btn-icon"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          aria-label="Toggle Theme"
        >
          {theme === 'dark' ? <Sun size={19} color="#F59E0B" /> : <Moon size={19} color="#6366F1" />}
        </button>

        {/* Notifications Bell & Dropdown */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => {
              setShowNotifications(!showNotifications);
              setShowProfileMenu(false);
            }}
            className="btn btn-ghost btn-icon"
            style={{ position: 'relative' }}
            aria-label="View notifications"
          >
            <Bell size={20} />
            {unreadCount > 0 && (
              <span
                style={{
                  position: 'absolute',
                  top: '4px',
                  right: '4px',
                  width: '18px',
                  height: '18px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--danger)',
                  color: '#FFFFFF',
                  fontSize: '0.68rem',
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {showNotifications && (
            <div
              style={{
                position: 'absolute',
                right: 0,
                top: 'calc(100% + 8px)',
                width: '380px',
                backgroundColor: 'var(--bg-card-solid)',
                border: 'var(--border-glass)',
                borderRadius: 'var(--radius-lg)',
                boxShadow: 'var(--shadow-lg)',
                padding: '1rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.75rem',
                zIndex: 100,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontWeight: 600, color: '#FFF' }}>Notifications</span>
                  {unreadCount > 0 && (
                    <Badge variant="primary">{unreadCount} unread</Badge>
                  )}
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={handleMarkAllAsRead}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--primary)',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.25rem',
                      padding: 0
                    }}
                  >
                    <CheckCheck size={14} />
                    <span>Mark all read</span>
                  </button>
                )}
              </div>

              <div style={{ maxHeight: '320px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {notifications.length === 0 ? (
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-dim)', textAlign: 'center', padding: '1.5rem 0' }}>
                    No notifications
                  </div>
                ) : (
                  notifications.slice(0, 6).map((n) => {
                    const isUnread = !n.is_read || n.is_read === 0;
                    return (
                      <div
                        key={n.notification_id}
                        onClick={() => handleNotificationClick(n)}
                        style={{
                          padding: '0.75rem',
                          borderRadius: 'var(--radius-sm)',
                          backgroundColor: isUnread ? 'rgba(99, 102, 241, 0.08)' : 'transparent',
                          border: isUnread ? '1px solid rgba(99, 102, 241, 0.3)' : '1px solid var(--border-subtle)',
                          fontSize: '0.82rem',
                          display: 'flex',
                          alignItems: 'flex-start',
                          justifyContent: 'space-between',
                          gap: '0.6rem',
                          cursor: 'pointer',
                          transition: 'background-color 0.15s ease'
                        }}
                      >
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem' }}>
                            <Badge variant={getPriorityBadgeVariant(n.priority)}>
                              {n.priority?.toUpperCase() || 'INFO'}
                            </Badge>
                            <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'capitalize' }}>
                              {n.category}
                            </span>
                          </div>
                          <div style={{ fontWeight: 600, color: '#FFF', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {n.title}
                          </div>
                          <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem', marginTop: '0.15rem', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                            {n.message}
                          </div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '0.3rem' }}>
                            {n.created_at}
                          </div>
                        </div>

                        {isUnread && (
                          <button
                            onClick={(e) => handleMarkAsRead(n.notification_id, e)}
                            title="Mark as read"
                            style={{
                              background: 'none',
                              border: 'none',
                              color: 'var(--primary)',
                              cursor: 'pointer',
                              padding: '0.2rem'
                            }}
                          >
                            <Check size={16} />
                          </button>
                        )}
                      </div>
                    );
                  })
                )}
              </div>

              <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.6rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Link
                  to="/notifications"
                  onClick={() => setShowNotifications(false)}
                  style={{
                    fontSize: '0.82rem',
                    color: 'var(--primary)',
                    fontWeight: 600,
                    textDecoration: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.3rem'
                  }}
                >
                  <span>Open Notification Center</span>
                  <ExternalLink size={13} />
                </Link>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                  {isLiveWs ? 'Live WS' : 'Auto-polling'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* User Pill & Profile Dropdown */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => {
              setShowProfileMenu(!showProfileMenu);
              setShowNotifications(false);
            }}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: 'var(--border-glass)',
              borderRadius: 'var(--radius-full)',
              padding: '0.35rem 0.75rem 0.35rem 0.4rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              cursor: 'pointer',
              color: '#FFFFFF',
            }}
          >
            <div
              style={{
                width: '30px',
                height: '30px',
                borderRadius: '50%',
                background: 'var(--gradient-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.82rem',
                fontWeight: 700,
              }}
            >
              {user?.name?.charAt(0) || 'U'}
            </div>
            <div style={{ textAlign: 'left', lineHeight: 1.2 }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 600 }}>{user?.name}</div>
              <Badge variant={user?.role === 'ADMIN' ? 'danger' : user?.role === 'HR' ? 'purple' : user?.role === 'MANAGER' ? 'info' : 'success'}>
                {user?.role}
              </Badge>
            </div>
          </button>

          {showProfileMenu && (
            <div
              style={{
                position: 'absolute',
                right: 0,
                top: 'calc(100% + 8px)',
                width: '210px',
                backgroundColor: 'var(--bg-card-solid)',
                border: 'var(--border-glass)',
                borderRadius: 'var(--radius-lg)',
                boxShadow: 'var(--shadow-lg)',
                padding: '0.5rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.25rem',
                zIndex: 100,
              }}
            >
              <div style={{ padding: '0.5rem 0.75rem', borderBottom: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Signed in as</div>
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#FFF', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {user?.email}
                </div>
              </div>

              {user?.employee_id && (
                <Link
                  to={`/employees/${user.employee_id}`}
                  onClick={() => setShowProfileMenu(false)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.6rem',
                    padding: '0.6rem 0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.85rem',
                    color: 'var(--text-main)',
                  }}
                >
                  <UserIcon size={16} />
                  <span>My Profile</span>
                </Link>
              )}

              <Link
                to="/notifications"
                onClick={() => setShowProfileMenu(false)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.6rem',
                  padding: '0.6rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.85rem',
                  color: 'var(--text-main)',
                }}
              >
                <Bell size={16} />
                <span>Notification Center</span>
              </Link>

              <button
                onClick={logout}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.6rem',
                  padding: '0.6rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.85rem',
                  color: 'var(--danger)',
                  background: 'none',
                  border: 'none',
                  width: '100%',
                  textAlign: 'left',
                  cursor: 'pointer',
                }}
              >
                <LogOut size={16} />
                <span>Sign Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
