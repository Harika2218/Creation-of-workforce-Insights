import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Clock,
  Banknote,
  FileSpreadsheet,
  CalendarDays,
  ArrowRight,
  Plus,
  Sparkles,
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { PunchClockCard } from '../../components/attendance/PunchClockCard';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { ThreeDMetricCard } from '../../components/3d';
import { useAuth } from '../../context/AuthContext';
import { leaveService } from '../../services/leaveService';
import { shiftService } from '../../services/shiftService';
import { holidayService } from '../../services/holidayService';
import { LeaveBalance, ShiftSchedule, Holiday } from '../../types';

export const EmployeeDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [balance, setBalance] = useState<LeaveBalance | null>(null);
  const [shifts, setShifts] = useState<ShiftSchedule[]>([]);
  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchEmployeeData = async () => {
      if (!user?.employee_id) return;
      try {
        setIsLoading(true);
        const [balData, shiftData, holData] = await Promise.all([
          leaveService.getLeaveBalances(user.employee_id),
          shiftService.getEmployeeShifts(user.employee_id),
          holidayService.getHolidays(),
        ]);
        setBalance(balData);
        setShifts(shiftData);
        setHolidays(holData.slice(0, 3));
      } catch (err) {
        console.error('Error loading employee dashboard:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEmployeeData();
  }, [user?.employee_id]);

  const activeShift = shifts.length > 0 ? shifts[0] : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ margin: 0 }}>Welcome back, {user?.name}!</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
            Employee ID: <strong style={{ color: 'var(--primary)' }}>{user?.employee_id}</strong> • Role: {user?.role}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <Link to="/ai-assistant">
            <Button variant="outline" icon={<Sparkles size={16} color="var(--color-primary)" />}>
              Ask HR Assistant
            </Button>
          </Link>
          <Link to="/leave">
            <Button variant="primary" icon={<Plus size={16} />}>
              Apply for Leave
            </Button>
          </Link>
          <Link to="/timesheets">
            <Button variant="secondary" icon={<FileSpreadsheet size={16} />}>
              Log Timesheet
            </Button>
          </Link>
        </div>
      </div>

      {/* Mobile Quick Action Pill Bar */}
      <div className="mobile-quick-actions">
        <Link to="/attendance" className="quick-pill">
          <Clock size={16} /> Punch Clock
        </Link>
        <Link to="/leave" className="quick-pill">
          <Plus size={16} /> Apply Leave
        </Link>
        <Link to="/shifts" className="quick-pill">
          <CalendarDays size={16} /> My Shifts
        </Link>
        <Link to="/timesheets" className="quick-pill">
          <FileSpreadsheet size={16} /> Timesheets
        </Link>
        <Link to="/payroll" className="quick-pill">
          <Banknote size={16} /> My Payslip
        </Link>
        <Link to="/ai-assistant" className="quick-pill">
          <Sparkles size={16} /> AI Chatbot
        </Link>
      </div>

      {/* 3D Elevated Employee Overview Cards */}
      <div className="grid-4">
        <ThreeDMetricCard
          label="Annual Leave"
          value={`${balance?.annual_leave ?? 18} Days`}
          badge="Available PTO"
          badgeVariant="success"
          subtext={<span>Remaining for 2026 cycle</span>}
          icon={<Calendar size={22} />}
          iconBg="rgba(16, 185, 129, 0.15)"
          iconColor="var(--success)"
          accentColor="var(--success)"
        />
        <ThreeDMetricCard
          label="Sick Leave"
          value={`${balance?.sick_leave ?? 10} Days`}
          badge="Health & Wellness"
          badgeVariant="info"
          subtext={<span>Medical leave allowance</span>}
          icon={<Clock size={22} />}
          iconBg="rgba(14, 165, 233, 0.15)"
          iconColor="var(--info)"
          accentColor="var(--info)"
        />
        <ThreeDMetricCard
          label="Active Shift"
          value={activeShift?.shift_name || 'General Shift'}
          badge={activeShift ? 'Assigned' : 'Standard'}
          badgeVariant="purple"
          subtext={<span>{activeShift?.start_time ? `${activeShift.start_time} - ${activeShift.end_time}` : '09:00 - 18:00'}</span>}
          icon={<CalendarDays size={22} />}
          iconBg="rgba(168, 85, 247, 0.15)"
          iconColor="var(--purple)"
          accentColor="var(--purple)"
        />
        <ThreeDMetricCard
          label="Monthly Compensation"
          value="View Payslip"
          badge="March 2026"
          badgeVariant="info"
          subtext={<span>Confidential remuneration</span>}
          icon={<Banknote size={22} />}
          iconBg="rgba(99, 102, 241, 0.15)"
          iconColor="var(--primary)"
          accentColor="var(--primary)"
          onClick={() => navigate('/payroll')}
        />
      </div>

      {/* Main Grid: Punch Clock & Leave Balances */}
      <div className="grid-2">
        {/* Real-time GPS Punch Clock */}
        <PunchClockCard />

        {/* Leave Balances & Upcoming Holidays */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Leave Balances Card */}
          <Card
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Calendar size={18} style={{ color: 'var(--purple)' }} />
                <span>My Leave Balances</span>
              </div>
            }
            subtitle="Available paid time off for 2026"
            action={
              <Link to="/leave">
                <Button variant="ghost" size="sm" icon={<ArrowRight size={14} />}>
                  Details
                </Button>
              </Link>
            }
          >
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginTop: '0.5rem' }}>
              <div
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  padding: '1rem',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Annual Leave</div>
                <div style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--success)', marginTop: '0.2rem' }}>
                  {balance?.annual_leave ?? 18}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Days Left</div>
              </div>

              <div
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  padding: '1rem',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Sick Leave</div>
                <div style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--warning)', marginTop: '0.2rem' }}>
                  {balance?.sick_leave ?? 10}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Days Left</div>
              </div>

              <div
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  padding: '1rem',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Casual Leave</div>
                <div style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--info)', marginTop: '0.2rem' }}>
                  {balance?.casual_leave ?? 8}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Days Left</div>
              </div>
            </div>
          </Card>

          {/* Active Shift Details */}
          <Card
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Clock size={18} style={{ color: 'var(--info)' }} />
                <span>Assigned Shift Schedule</span>
              </div>
            }
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#FFF' }}>
                  {activeShift?.shift_name || 'General Office Shift'}
                </div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.2rem' }}>
                  Working Hours: {activeShift?.start_time || '09:00:00'} - {activeShift?.end_time || '18:00:00'}
                </div>
              </div>
              <Badge variant="active">Active Schedule</Badge>
            </div>
          </Card>
        </div>
      </div>

      {/* Upcoming Holidays & Quick Self-Service Links */}
      <div className="grid-2">
        <Card
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CalendarDays size={18} style={{ color: 'var(--warning)' }} />
              <span>Upcoming Official Holidays</span>
            </div>
          }
          action={
            <Link to="/holidays">
              <Button variant="ghost" size="sm" icon={<ArrowRight size={14} />}>
                Calendar
              </Button>
            </Link>
          }
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
            {holidays.map((h) => (
              <div
                key={h.holiday_id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.75rem 1rem',
                  backgroundColor: 'rgba(255, 255, 255, 0.02)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, color: '#FFF' }}>{h.holiday_name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{h.date}</div>
                </div>
                <Badge variant="purple">{h.type}</Badge>
              </div>
            ))}
          </div>
        </Card>

        {/* Self-service actions */}
        <Card
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Banknote size={18} style={{ color: 'var(--success)' }} />
              <span>Compensation & Self-Service</span>
            </div>
          }
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
            <Link
              to="/payroll"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.85rem 1rem',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)',
                color: '#FFF',
              }}
            >
              <div>
                <div style={{ fontWeight: 600 }}>Download Latest Payslip</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Month: March 2026 • Status: Paid</div>
              </div>
              <ArrowRight size={16} style={{ color: 'var(--primary)' }} />
            </Link>

            <Link
              to="/timesheets"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.85rem 1rem',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)',
                color: '#FFF',
              }}
            >
              <div>
                <div style={{ fontWeight: 600 }}>Weekly Timesheet Log</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Log billable and project activity</div>
              </div>
              <ArrowRight size={16} style={{ color: 'var(--primary)' }} />
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};
