import React, { useState, useEffect, useCallback } from 'react';
import {
  Bell,
  Check,
  CheckCheck,
  Search,
  Filter,
  Sparkles,
  ShieldAlert,
  Clock,
  Calendar,
  DollarSign,
  Award,
  BookOpen,
  Settings,
  X,
  ExternalLink,
  Info,
  Sliders,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { LoadingSkeleton } from '../../components/common/LoadingSkeleton';
import { notificationService, NotificationQueryParams } from '../../services/notificationService';
import { notificationSocket } from '../../services/notificationSocket';
import { useToast } from '../../context/ToastContext';
import { NotificationItem, NotificationPreferences, NotificationCategory } from '../../types';
import { useNavigate } from 'react-router-dom';

const TABS: { id: string; label: string; icon: React.ReactNode; category?: string }[] = [
  { id: 'all', label: 'All', icon: <Bell size={16} /> },
  { id: 'unread', label: 'Unread', icon: <Check size={16} /> },
  { id: 'attendance', label: 'Attendance', icon: <Clock size={16} />, category: 'attendance' },
  { id: 'leave', label: 'Leave', icon: <Calendar size={16} />, category: 'leave' },
  { id: 'shifts', label: 'Shifts', icon: <Clock size={16} />, category: 'shifts' },
  { id: 'payroll', label: 'Payroll', icon: <DollarSign size={16} />, category: 'payroll' },
  { id: 'performance', label: 'Performance', icon: <Award size={16} />, category: 'performance' },
  { id: 'training', label: 'Training', icon: <BookOpen size={16} />, category: 'training' },
  { id: 'ai_alerts', label: 'AI Alerts', icon: <Sparkles size={16} />, category: 'ai_alerts' },
  { id: 'compliance', label: 'Compliance', icon: <ShieldAlert size={16} />, category: 'compliance' },
  { id: 'preferences', label: 'Preferences', icon: <Settings size={16} /> },
];

export const NotificationsPage: React.FC = () => {
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<string>('all');
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [isLiveWs, setIsLiveWs] = useState<boolean>(false);

  // Selected notification for detail modal
  const [selectedNotif, setSelectedNotif] = useState<NotificationItem | null>(null);

  // Preferences State
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [isSavingPrefs, setIsSavingPrefs] = useState<boolean>(false);

  const fetchNotifications = useCallback(async () => {
    try {
      setIsLoading(true);
      const params: NotificationQueryParams = {
        page_size: 100,
      };

      if (activeTab === 'unread') {
        params.unread_only = true;
      } else if (activeTab !== 'all' && activeTab !== 'preferences') {
        const tabObj = TABS.find((t) => t.id === activeTab);
        if (tabObj?.category) {
          params.category = tabObj.category;
        }
      }

      if (priorityFilter !== 'all') {
        params.priority = priorityFilter;
      }

      if (searchQuery.trim()) {
        params.search = searchQuery.trim();
      }

      const data = await notificationService.getNotifications(params);
      setNotifications(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching notifications:', err);
      showToast('Could not load notifications.', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [activeTab, priorityFilter, searchQuery, showToast]);

  const fetchPreferences = useCallback(async () => {
    try {
      const prefs = await notificationService.getPreferences();
      setPreferences(prefs);
    } catch {
      // Handled silently
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'preferences') {
      fetchPreferences();
    } else {
      fetchNotifications();
    }
  }, [activeTab, fetchNotifications, fetchPreferences]);

  useEffect(() => {
    const unsubNotif = notificationSocket.subscribe((newNotif) => {
      setNotifications((prev) => [newNotif, ...prev]);
    });
    const unsubStatus = notificationSocket.subscribeStatus((connected) => {
      setIsLiveWs(connected);
    });
    return () => {
      unsubNotif();
      unsubStatus();
    };
  }, []);

  const handleMarkAsRead = async (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    try {
      await notificationService.markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.notification_id === id ? { ...n, is_read: 1 } : n))
      );
      if (selectedNotif && selectedNotif.notification_id === id) {
        setSelectedNotif({ ...selectedNotif, is_read: 1 });
      }
      showToast('Notification marked as read.', 'info');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to update notification.', 'error');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: 1 })));
      showToast('All notifications marked as read.', 'success');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to mark all as read.', 'error');
    }
  };

  const handleSavePreferences = async () => {
    if (!preferences) return;
    try {
      setIsSavingPrefs(true);
      const updated = await notificationService.updatePreferences(preferences);
      setPreferences(updated);
      showToast('Notification preferences successfully saved.', 'success');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to save preferences.', 'error');
    } finally {
      setIsSavingPrefs(false);
    }
  };

  const getPriorityBadgeVariant = (priority?: string) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
        return 'danger';
      case 'high':
        return 'danger';
      case 'normal':
        return 'warning';
      default:
        return 'info';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category?.toLowerCase()) {
      case 'attendance':
        return <Clock size={16} color="var(--primary)" />;
      case 'leave':
        return <Calendar size={16} color="#38bdf8" />;
      case 'shifts':
        return <Clock size={16} color="#f59e0b" />;
      case 'payroll':
        return <DollarSign size={16} color="#10b981" />;
      case 'performance':
        return <Award size={16} color="#a855f7" />;
      case 'training':
        return <BookOpen size={16} color="#ec4899" />;
      case 'ai_alerts':
        return <Sparkles size={16} color="#6366f1" />;
      case 'compliance':
        return <ShieldAlert size={16} color="#ef4444" />;
      default:
        return <Bell size={16} color="var(--text-muted)" />;
    }
  };

  const unreadTotal = (notifications || []).filter((n) => !n.is_read || n.is_read === 0).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <h1 style={{ margin: 0 }}>Notification Center</h1>
            <span
              style={{
                fontSize: '0.75rem',
                padding: '0.2rem 0.6rem',
                borderRadius: 'var(--radius-full)',
                background: isLiveWs ? 'rgba(16, 185, 129, 0.15)' : 'rgba(234, 179, 8, 0.15)',
                color: isLiveWs ? 'var(--success)' : '#eab308',
                border: isLiveWs ? '1px solid var(--success)' : '1px solid #eab308',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem'
              }}
            >
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: isLiveWs ? 'var(--success)' : '#eab308' }} />
              {isLiveWs ? 'WebSocket Live' : 'Polling Sync'}
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.25rem' }}>
            Automated event triggers, manager escalations, shift reminders, compliance notices, and AI workforce insights.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          {unreadTotal > 0 && activeTab !== 'preferences' && (
            <Button variant="secondary" size="sm" icon={<CheckCheck size={16} />} onClick={handleMarkAllAsRead}>
              Mark All as Read ({unreadTotal})
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            icon={<RefreshCw size={16} />}
            onClick={() => (activeTab === 'preferences' ? fetchPreferences() : fetchNotifications())}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div
        style={{
          display: 'flex',
          gap: '0.5rem',
          overflowX: 'auto',
          paddingBottom: '0.25rem',
          borderBottom: '1px solid var(--border-subtle)',
        }}
      >
        {TABS.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: isActive ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                border: 'none',
                borderBottom: isActive ? '2px solid var(--primary)' : '2px solid transparent',
                color: isActive ? '#FFFFFF' : 'var(--text-muted)',
                padding: '0.65rem 1rem',
                fontSize: '0.88rem',
                fontWeight: isActive ? 600 : 500,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                borderRadius: 'var(--radius-sm) var(--radius-sm) 0 0',
                whiteSpace: 'nowrap',
                transition: 'all 0.15s ease',
              }}
            >
              {tab.icon}
              <span>{tab.label}</span>
              {tab.id === 'unread' && unreadTotal > 0 && (
                <span
                  style={{
                    backgroundColor: 'var(--danger)',
                    color: '#FFF',
                    fontSize: '0.7rem',
                    padding: '0.1rem 0.45rem',
                    borderRadius: 'var(--radius-full)',
                    fontWeight: 700,
                  }}
                >
                  {unreadTotal}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Main Content Area */}
      {activeTab === 'preferences' ? (
        /* Notification Preferences Panel */
        <Card title="Notification Preferences & Delivery Controls">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '1.5rem' }}>
            Customize your notifications across operational modules and channels. Statutory compliance and mandatory audit notices are permanently enforced.
          </p>

          {!preferences ? (
            <LoadingSkeleton lines={6} height="40px" />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', maxWidth: '800px' }}>
              {/* Channel Controls */}
              <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <h3 style={{ fontSize: '1rem', margin: '0 0 0.75rem 0', color: '#FFF' }}>Delivery Channels</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={preferences.in_app_enabled}
                      onChange={(e) => setPreferences({ ...preferences, in_app_enabled: e.target.checked })}
                      style={{ width: '18px', height: '18px', accentColor: 'var(--primary)', cursor: 'pointer' }}
                    />
                    <div>
                      <div style={{ fontWeight: 600, color: '#FFF' }}>In-App Notifications</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Display real-time alerts in topbar and notification center</div>
                    </div>
                  </label>

                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={preferences.email_enabled}
                      onChange={(e) => setPreferences({ ...preferences, email_enabled: e.target.checked })}
                      style={{ width: '18px', height: '18px', accentColor: 'var(--primary)', cursor: 'pointer' }}
                    />
                    <div>
                      <div style={{ fontWeight: 600, color: '#FFF' }}>Email Notifications</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Dispatch summary digests and high-priority alerts to corporate email</div>
                    </div>
                  </label>
                </div>
              </div>

              {/* Module Specific Toggles */}
              <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <h3 style={{ fontSize: '1rem', margin: '0 0 0.75rem 0', color: '#FFF' }}>Operational Notification Categories</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
                  {[
                    { key: 'attendance_alerts', label: 'Attendance & Late Arrival Alerts', desc: 'Clock-in receipts, grace period warnings, missing checkouts' },
                    { key: 'leave_notifications', label: 'Leave Workflow Alerts', desc: 'Application submission, approval, and rejection updates' },
                    { key: 'shift_notifications', label: 'Shift Roster & Swap Alerts', desc: 'Pre-shift reminders and colleague shift swap requests' },
                    { key: 'timesheet_notifications', label: 'Timesheet Due Reminders', desc: 'Period closing alerts and manager submission reviews' },
                    { key: 'payroll_notifications', label: 'Payroll & Payslip Alerts', desc: 'Salary disbursement notices and tax statement receipts' },
                    { key: 'performance_notifications', label: 'Performance Review Cycles', desc: 'Quarterly review deadlines and goal target milestones' },
                    { key: 'training_notifications', label: 'Skill Training Assignments', desc: 'Required curriculum deadlines and certification receipts' },
                    { key: 'birthday_notifications', label: 'Celebrations & Anniversaries', desc: 'Birthday wishes and tenure service milestone recognitions' },
                    { key: 'ai_alerts', label: 'AI Workforce Intelligence Insights', desc: 'Ethical predictive alerts for absenteeism and retention' },
                  ].map((item) => (
                    <label key={item.key} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={Boolean((preferences as any)[item.key])}
                        onChange={(e) => setPreferences({ ...preferences, [item.key]: e.target.checked } as any)}
                        style={{ width: '18px', height: '18px', marginTop: '2px', accentColor: 'var(--primary)', cursor: 'pointer' }}
                      />
                      <div>
                        <div style={{ fontWeight: 600, color: '#FFF' }}>{item.label}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.desc}</div>
                      </div>
                    </label>
                  ))}

                  {/* Mandatory Compliance - Locked */}
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', opacity: 0.9 }}>
                    <input
                      type="checkbox"
                      checked={true}
                      disabled={true}
                      style={{ width: '18px', height: '18px', marginTop: '2px', cursor: 'not-allowed' }}
                    />
                    <div>
                      <div style={{ fontWeight: 600, color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <span>Statutory & Compliance Notices</span>
                        <Badge variant="danger">Mandatory</Badge>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Labor law compliance, workplace safety, and mandatory policy updates cannot be disabled.
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Save Button */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
                <Button variant="primary" onClick={handleSavePreferences} isLoading={isSavingPrefs} icon={<CheckCircle2 size={16} />}>
                  Save Preferences
                </Button>
              </div>
            </div>
          )}
        </Card>
      ) : (
        /* Notification List View */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Filter Bar */}
          <div
            style={{
              display: 'flex',
              gap: '1rem',
              alignItems: 'center',
              flexWrap: 'wrap',
              padding: '1rem',
              backgroundColor: 'var(--bg-card-solid)',
              border: 'var(--border-glass)',
              borderRadius: 'var(--radius-md)',
            }}
          >
            <div className="search-wrapper" style={{ flex: 1, minWidth: '220px' }}>
              <Search size={16} className="search-icon" />
              <input
                type="text"
                className="form-control search-input"
                placeholder="Search notification title or message..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{ height: '36px', fontSize: '0.85rem' }}
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Filter size={15} color="var(--text-muted)" />
              <select
                className="form-control"
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                style={{ height: '36px', fontSize: '0.82rem', minWidth: '140px' }}
              >
                <option value="all">All Priorities</option>
                <option value="low">Low Priority</option>
                <option value="normal">Normal Priority</option>
                <option value="high">High Priority</option>
                <option value="critical">Critical Priority</option>
              </select>
            </div>
          </div>

          {/* List of Notification Cards */}
          <Card title={`Active Notifications (${notifications.length})`}>
            {isLoading ? (
              <LoadingSkeleton lines={6} height="52px" />
            ) : notifications.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3.5rem 0', color: 'var(--text-dim)' }}>
                <Bell size={40} style={{ opacity: 0.25, marginBottom: '0.75rem' }} />
                <div style={{ fontSize: '0.95rem', fontWeight: 600, color: '#FFF' }}>No notifications found</div>
                <div style={{ fontSize: '0.82rem', marginTop: '0.25rem' }}>
                  There are currently no alerts matching this filter criteria.
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {notifications.map((item) => {
                  const isUnread = !item.is_read || item.is_read === 0;
                  const isAiAlert = item.category?.toLowerCase() === 'ai_alerts';
                  const isCompliance = item.category?.toLowerCase() === 'compliance';

                  return (
                    <div
                      key={item.notification_id}
                      onClick={() => setSelectedNotif(item)}
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        justifyContent: 'space-between',
                        padding: '1.1rem 1.25rem',
                        backgroundColor: isUnread
                          ? isAiAlert
                            ? 'rgba(99, 102, 241, 0.12)'
                            : 'rgba(99, 102, 241, 0.06)'
                          : 'rgba(255, 255, 255, 0.02)',
                        border: isUnread
                          ? isAiAlert
                            ? '1px solid rgba(99, 102, 241, 0.45)'
                            : '1px solid rgba(99, 102, 241, 0.3)'
                          : '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                        gap: '1rem',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                        boxShadow: isUnread && isAiAlert ? '0 0 15px rgba(99, 102, 241, 0.15)' : 'none',
                      }}
                    >
                      {/* Left Icon & Content */}
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', flex: 1 }}>
                        <div
                          style={{
                            width: '36px',
                            height: '36px',
                            borderRadius: 'var(--radius-sm)',
                            background: 'rgba(255, 255, 255, 0.04)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            border: '1px solid var(--border-subtle)',
                            flexShrink: 0,
                          }}
                        >
                          {getCategoryIcon(item.category)}
                        </div>

                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.3rem' }}>
                            <Badge variant={getPriorityBadgeVariant(item.priority)}>
                              {item.priority?.toUpperCase()}
                            </Badge>

                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'capitalize', fontWeight: 500 }}>
                              {item.category}
                            </span>

                            {isAiAlert && (
                              <Badge variant="purple">AI Decision-Support</Badge>
                            )}
                            {isCompliance && (
                              <Badge variant="danger">Mandatory Compliance</Badge>
                            )}
                          </div>

                          <div style={{ fontWeight: 600, color: '#FFF', fontSize: '0.95rem' }}>
                            {item.title}
                          </div>

                          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem', lineHeight: 1.5 }}>
                            {item.message}
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                            <span>{item.created_at}</span>
                            <span>•</span>
                            <span>ID: {item.notification_id}</span>
                            {item.action_url && (
                              <>
                                <span>•</span>
                                <span style={{ color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                                  Link: {item.action_url}
                                  <ExternalLink size={12} />
                                </span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Right Action Buttons */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexShrink: 0 }}>
                        {item.action_url && (
                          <Button
                            variant="secondary"
                            size="sm"
                            icon={<ExternalLink size={14} />}
                            onClick={(e) => {
                              e.stopPropagation();
                              if (isUnread) handleMarkAsRead(item.notification_id);
                              navigate(item.action_url!);
                            }}
                          >
                            Open
                          </Button>
                        )}
                        {isUnread && (
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={<Check size={14} />}
                            title="Mark as read"
                            onClick={(e) => handleMarkAsRead(item.notification_id, e)}
                          >
                            Read
                          </Button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </Card>
        </div>
      )}

      {/* Notification Details Modal */}
      {selectedNotif && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1rem',
          }}
          onClick={() => setSelectedNotif(null)}
        >
          <div
            style={{
              backgroundColor: 'var(--bg-card-solid)',
              border: 'var(--border-glass)',
              borderRadius: 'var(--radius-lg)',
              maxWidth: '600px',
              width: '100%',
              padding: '1.75rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '1.25rem',
              boxShadow: 'var(--shadow-xl)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Badge variant={getPriorityBadgeVariant(selectedNotif.priority)}>
                  {selectedNotif.priority?.toUpperCase()}
                </Badge>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)', textTransform: 'capitalize' }}>
                  {selectedNotif.category}
                </span>
              </div>
              <button
                onClick={() => setSelectedNotif(null)}
                style={{ background: 'none', border: 'none', color: 'var(--text-dim)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <div>
              <h2 style={{ margin: '0 0 0.5rem 0', fontSize: '1.2rem', color: '#FFF' }}>{selectedNotif.title}</h2>
              <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.6 }}>
                {selectedNotif.message}
              </p>
            </div>

            {selectedNotif.category?.toLowerCase() === 'ai_alerts' && (
              <div
                style={{
                  padding: '0.85rem',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'rgba(99, 102, 241, 0.08)',
                  border: '1px solid rgba(99, 102, 241, 0.25)',
                  fontSize: '0.8rem',
                  color: 'var(--text-main)',
                  display: 'flex',
                  gap: '0.6rem',
                }}
              >
                <Sparkles size={16} color="var(--primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong>Ethical AI Decision-Support Notice:</strong> This alert is generated using probabilistic machine learning. Human-in-the-loop review is required before taking any action. Protected attributes are hard-excluded.
                </div>
              </div>
            )}

            <div
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '0.75rem',
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '0.5rem',
                fontSize: '0.78rem',
              }}
            >
              <div>
                <span style={{ color: 'var(--text-dim)' }}>Notification ID:</span>{' '}
                <strong style={{ color: '#FFF' }}>{selectedNotif.notification_id}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)' }}>Delivered At:</span>{' '}
                <strong style={{ color: '#FFF' }}>{selectedNotif.created_at}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)' }}>Status:</span>{' '}
                <strong style={{ color: selectedNotif.is_read ? 'var(--success)' : 'var(--danger)' }}>
                  {selectedNotif.is_read ? 'Read' : 'Unread'}
                </strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)' }}>Target Module:</span>{' '}
                <strong style={{ color: 'var(--primary)' }}>{selectedNotif.action_url || 'N/A'}</strong>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              {(!selectedNotif.is_read || selectedNotif.is_read === 0) && (
                <Button variant="secondary" icon={<Check size={16} />} onClick={() => handleMarkAsRead(selectedNotif.notification_id)}>
                  Mark as Read
                </Button>
              )}
              {selectedNotif.action_url && (
                <Button
                  variant="primary"
                  icon={<ExternalLink size={16} />}
                  onClick={() => {
                    const url = selectedNotif.action_url!;
                    setSelectedNotif(null);
                    navigate(url);
                  }}
                >
                  Navigate to Module
                </Button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
