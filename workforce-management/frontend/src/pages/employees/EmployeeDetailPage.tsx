import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  User,
  ArrowLeft,
  Mail,
  Phone,
  Building,
  MapPin,
  Calendar,
  Award,
  Clock,
  Banknote,
  BookOpen,
  CheckCircle,
} from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Table, Column } from '../../components/common/Table';
import { LoadingSkeleton } from '../../components/common/LoadingSkeleton';
import { employeeService } from '../../services/employeeService';
import { attendanceService } from '../../services/attendanceService';
import { leaveService } from '../../services/leaveService';
import { payrollService } from '../../services/payrollService';
import { performanceService } from '../../services/performanceService';
import { skillService } from '../../services/skillService';
import { useAuth } from '../../context/AuthContext';
import {
  EmployeeProfile,
  AttendanceRecord,
  LeaveBalance,
  LeaveRequest,
  PayrollRecord,
  PerformanceReview,
  EmployeeSkill,
  TrainingRecord,
} from '../../types';

export const EmployeeDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();

  const [profile, setProfile] = useState<EmployeeProfile | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'attendance' | 'leave' | 'payroll' | 'performance' | 'skills'>('overview');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Tab Data States
  const [attendanceLogs, setAttendanceLogs] = useState<AttendanceRecord[]>([]);
  const [leaveBalance, setLeaveBalance] = useState<LeaveBalance | null>(null);
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [payrollLogs, setPayrollLogs] = useState<PayrollRecord[]>([]);
  const [appraisals, setAppraisals] = useState<PerformanceReview[]>([]);
  const [skills, setSkills] = useState<EmployeeSkill[]>([]);
  const [training, setTraining] = useState<TrainingRecord[]>([]);

  useEffect(() => {
    const fetchProfile = async () => {
      if (!id) return;
      try {
        setIsLoading(true);
        const data = await employeeService.getEmployeeProfile(id);
        setProfile(data);
      } catch (err) {
        console.error('Error fetching employee profile:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProfile();
  }, [id]);

  // Lazy fetch tab data on switch
  useEffect(() => {
    if (!id) return;

    if (activeTab === 'attendance' && attendanceLogs.length === 0) {
      attendanceService.getEmployeeAttendance(id, 20).then(setAttendanceLogs).catch(() => {});
    } else if (activeTab === 'leave' && !leaveBalance) {
      Promise.all([
        leaveService.getLeaveBalances(id),
        leaveService.getLeaveRequests({ employee_id: id, page_size: 10 }),
      ])
        .then(([bal, reqs]) => {
          setLeaveBalance(bal);
          setLeaveRequests(reqs.items);
        })
        .catch(() => {});
    } else if (activeTab === 'payroll' && payrollLogs.length === 0) {
      payrollService.getEmployeePayroll(id).then(setPayrollLogs).catch(() => {});
    } else if (activeTab === 'performance' && appraisals.length === 0) {
      performanceService.getEmployeePerformance(id).then(setAppraisals).catch(() => {});
    } else if (activeTab === 'skills' && skills.length === 0) {
      Promise.all([
        skillService.getEmployeeSkills(id),
        skillService.getEmployeeTraining(id),
      ])
        .then(([sk, tr]) => {
          setSkills(sk);
          setTraining(tr);
        })
        .catch(() => {});
    }
  }, [activeTab, id, attendanceLogs.length, leaveBalance, payrollLogs.length, appraisals.length, skills.length]);

  if (isLoading || !profile) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <LoadingSkeleton lines={2} height="40px" />
        <LoadingSkeleton lines={6} height="120px" />
      </div>
    );
  }

  const isSelfOrHR = user?.role === 'ADMIN' || user?.role === 'HR' || user?.employee_id === profile.employee_id;

  const attendanceColumns: Column<AttendanceRecord>[] = [
    { key: 'date', header: 'Date', width: '120px' },
    { key: 'check_in_time', header: 'Check In', render: (r) => r.check_in_time || '—' },
    { key: 'check_out_time', header: 'Check Out', render: (r) => r.check_out_time || '—' },
    { key: 'work_hours', header: 'Work Hours', render: (r) => `${r.work_hours} hrs` },
    { key: 'late_minutes', header: 'Late (Mins)', render: (r) => (r.late_minutes > 0 ? <span style={{ color: 'var(--warning)' }}>{r.late_minutes}m</span> : '0') },
    { key: 'status', header: 'Status', render: (r) => <Badge variant={r.status}>{r.status}</Badge> },
    { key: 'attendance_method', header: 'Method', render: (r) => <Badge variant="neutral">{r.attendance_method}</Badge> },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Back button */}
      <div>
        <Link to="/employees">
          <Button variant="ghost" size="sm" icon={<ArrowLeft size={16} />}>
            Back to Directory
          </Button>
        </Link>
      </div>

      {/* Header Profile Card */}
      <div
        className="glass-card"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1.5rem',
          padding: '2rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div
            style={{
              width: '80px',
              height: '80px',
              borderRadius: 'var(--radius-full)',
              background: 'var(--gradient-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '2rem',
              fontWeight: 800,
              color: '#FFF',
              boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)',
            }}
          >
            {profile.name.charAt(0)}
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <h1 style={{ margin: 0, fontSize: '1.75rem' }}>{profile.name}</h1>
              <Badge variant={profile.employment_status}>{profile.employment_status}</Badge>
              <Badge variant="purple">{profile.role}</Badge>
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginTop: '0.3rem' }}>
              {profile.designation} • {profile.department_name || profile.department_id}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', marginTop: '0.6rem', fontSize: '0.82rem', color: 'var(--text-dim)' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <Mail size={14} /> {profile.email}
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <Phone size={14} /> {profile.phone}
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <MapPin size={14} /> {profile.location_name || profile.location_id}
              </span>
            </div>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Employee ID</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--primary)' }}>{profile.employee_id}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Joined: {profile.date_of_joining}
          </div>
        </div>
      </div>

      {/* Profile Navigation Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border-subtle)', overflowX: 'auto', paddingBottom: '0.5rem' }}>
        {[
          { key: 'overview', label: 'Overview', icon: <User size={16} /> },
          { key: 'attendance', label: 'Attendance', icon: <Clock size={16} /> },
          { key: 'leave', label: 'Leave & PTO', icon: <Calendar size={16} /> },
          ...(isSelfOrHR ? [{ key: 'payroll', label: 'Payroll & Compensation', icon: <Banknote size={16} /> }] : []),
          { key: 'performance', label: 'Performance Appraisals', icon: <Award size={16} /> },
          { key: 'skills', label: 'Skills & Training', icon: <BookOpen size={16} /> },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.65rem 1.2rem',
              borderRadius: 'var(--radius-md)',
              background: activeTab === tab.key ? 'rgba(99, 102, 241, 0.18)' : 'transparent',
              border: activeTab === tab.key ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid transparent',
              color: activeTab === tab.key ? '#FFFFFF' : 'var(--text-muted)',
              fontWeight: 600,
              fontSize: '0.88rem',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
            }}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid-2">
          <Card title="Employment Details">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Department</span>
                <div style={{ fontWeight: 600, color: '#FFF' }}>{profile.department_name || profile.department_id}</div>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Direct Manager</span>
                <div style={{ fontWeight: 600, color: '#FFF' }}>{profile.manager_name || profile.manager_id || 'Executive Office'}</div>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Employment Type</span>
                <div style={{ fontWeight: 600, color: '#FFF' }}>{profile.employment_type}</div>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Date of Joining</span>
                <div style={{ fontWeight: 600, color: '#FFF' }}>{profile.date_of_joining}</div>
              </div>
            </div>
          </Card>

          <Card title="Compensation & Security">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Base Salary</span>
                <div style={{ fontWeight: 600, color: '#FFF' }}>
                  {isSelfOrHR ? `₹${profile.base_salary.toLocaleString('en-IN')} / yr` : 'Confidential'}
                </div>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>System Role</span>
                <div style={{ fontWeight: 600, color: '#FFF' }}>{profile.role}</div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'attendance' && (
        <Card title="Recent Attendance Records">
          <Table columns={attendanceColumns} data={attendanceLogs} emptyTitle="No attendance logs found" />
        </Card>
      )}

      {activeTab === 'leave' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <Card title="Current Leave Balances">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Annual Leave</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--success)' }}>{leaveBalance?.annual_leave ?? 18}</div>
              </div>
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Sick Leave</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--warning)' }}>{leaveBalance?.sick_leave ?? 10}</div>
              </div>
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Casual Leave</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--info)' }}>{leaveBalance?.casual_leave ?? 8}</div>
              </div>
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Emergency Leave</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--purple)' }}>{leaveBalance?.emergency_leave ?? 5}</div>
              </div>
            </div>
          </Card>

          <Card title="Leave Application History">
            <Table
              columns={[
                { key: 'leave_type', header: 'Leave Type' },
                { key: 'start_date', header: 'Start Date' },
                { key: 'end_date', header: 'End Date' },
                { key: 'days_count', header: 'Days' },
                { key: 'reason', header: 'Reason' },
                { key: 'status', header: 'Status', render: (l) => <Badge variant={l.status}>{l.status}</Badge> },
              ]}
              data={leaveRequests}
              emptyTitle="No leave applications on record"
            />
          </Card>
        </div>
      )}

      {activeTab === 'payroll' && (
        <Card title="Payslips & Compensation History">
          <Table
            columns={[
              { key: 'payroll_month', header: 'Cycle Month' },
              { key: 'base_salary', header: 'Base Pay', render: (p) => `₹${p.base_salary.toLocaleString('en-IN')}` },
              { key: 'gross_salary', header: 'Gross Salary', render: (p) => `₹${p.gross_salary.toLocaleString('en-IN')}` },
              { key: 'net_salary', header: 'Net Disbursement', render: (p) => <strong style={{ color: 'var(--success)' }}>₹{p.net_salary.toLocaleString('en-IN')}</strong> },
              { key: 'payment_status', header: 'Status', render: (p) => <Badge variant={p.payment_status}>{p.payment_status}</Badge> },
            ]}
            data={payrollLogs}
            emptyTitle="No payroll records available"
          />
        </Card>
      )}

      {activeTab === 'performance' && (
        <Card title="Appraisal Reviews & KPIs">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {appraisals.length === 0 ? (
              <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: '2rem 0' }}>No performance reviews logged</div>
            ) : (
              appraisals.map((rev) => (
                <div
                  key={rev.review_id}
                  style={{
                    padding: '1.25rem',
                    backgroundColor: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ fontWeight: 600, color: '#FFF' }}>Review Cycle: {rev.review_cycle}</div>
                    <Badge variant="purple">Rating: {rev.rating_score} / 5.0</Badge>
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
                    Feedback: <em>"{rev.feedback}"</em>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      )}

      {activeTab === 'skills' && (
        <div className="grid-2">
          <Card title="Skill Taxonomy & Proficiencies">
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
              {skills.map((s) => (
                <div
                  key={s.skill_id}
                  style={{
                    padding: '0.5rem 0.85rem',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    border: '1px solid rgba(99, 102, 241, 0.25)',
                    borderRadius: 'var(--radius-md)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                  }}
                >
                  <span style={{ fontWeight: 600, color: '#FFF' }}>{s.skill_name}</span>
                  <Badge variant="info">{s.proficiency_level}</Badge>
                </div>
              ))}
            </div>
          </Card>

          <Card title="Training & Upskilling Records">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {training.map((t) => (
                <div
                  key={t.enrollment_id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.75rem',
                    backgroundColor: 'rgba(255, 255, 255, 0.02)',
                    borderRadius: 'var(--radius-md)',
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, color: '#FFF' }}>{t.program_title}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Score: {t.score ? `${t.score}%` : 'In Progress'}</div>
                  </div>
                  <Badge variant={t.status}>{t.status}</Badge>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
