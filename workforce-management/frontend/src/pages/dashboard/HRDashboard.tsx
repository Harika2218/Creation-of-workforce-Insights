import React, { useState, useEffect } from 'react';
import {
  Users,
  UserCheck,
  Clock,
  Calendar,
  Banknote,
  AlertTriangle,
  TrendingUp,
  FileText,
  UserPlus,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { LoadingSkeleton } from '../../components/common/LoadingSkeleton';
import { ThreeDHero, ThreeDMetricCard, WorkforceScene } from '../../components/3d';
import { hrService } from '../../services/hrService';
import { attendanceService } from '../../services/attendanceService';
import { employeeService } from '../../services/employeeService';
import { HRSummaryMetrics, AttendanceSummary, Employee } from '../../types';

export const HRDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<HRSummaryMetrics | null>(null);
  const [attendanceSummary, setAttendanceSummary] = useState<AttendanceSummary | null>(null);
  const [empSummary, setEmpSummary] = useState<any>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [workforceViewMode, setWorkforceViewMode] = useState<'3d' | 'analytics'>('3d');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        const [hrData, attData, empData, empListRes] = await Promise.all([
          hrService.getHRSummary(),
          attendanceService.getAttendanceSummary(),
          hrService.getHREmployeeSummary(),
          employeeService.getEmployees({ page_size: 45 }).catch(() => ({ items: [] })),
        ]);
        setMetrics(hrData);
        setAttendanceSummary(attData);
        setEmpSummary(empData);
        if (empListRes && empListRes.items) {
          setEmployees(empListRes.items);
        }
      } catch (err) {
        console.error('Error loading HR dashboard:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (isLoading || !metrics) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <LoadingSkeleton lines={2} height="40px" />
        <div className="grid-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <LoadingSkeleton key={i} lines={3} height="80px" />
          ))}
        </div>
        <LoadingSkeleton lines={5} height="200px" />
      </div>
    );
  }

  // Format currency in Indian Lakhs / Crores
  const formatINR = (val: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(val);
  };

  // Chart data: Department distribution
  const deptData = empSummary?.department_distribution
    ? Object.entries(empSummary.department_distribution).map(([dept, count]) => ({
        name: dept,
        count,
      }))
    : [];

  // Chart data: Attendance breakdown
  const attChartData = attendanceSummary
    ? [
        { name: 'Present', value: attendanceSummary.present_count, color: '#10B981' },
        { name: 'Late', value: attendanceSummary.late_count, color: '#F59E0B' },
        { name: 'On Leave', value: attendanceSummary.on_leave_count, color: '#A855F7' },
        { name: 'Half Day', value: attendanceSummary.half_day_count, color: '#0EA5E9' },
        { name: 'Absent', value: attendanceSummary.absent_count, color: '#EF4444' },
      ].filter((x) => x.value > 0)
    : [];

  // Chart data: Attrition risk
  const attritionData = [
    { name: 'Low Risk', value: metrics.attrition_risk_low, color: '#10B981' },
    { name: 'Medium Risk', value: metrics.attrition_risk_medium, color: '#F59E0B' },
    { name: 'High Risk', value: metrics.attrition_risk_high, color: '#EF4444' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Page Title & Actions */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ margin: 0 }}>HR Executive Dashboard</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
            Real-time workforce intelligence across {metrics.departments_count} departments and {metrics.locations_count} operational hubs.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <Link to="/ai-assistant">
            <Button variant="outline" icon={<Sparkles size={16} color="var(--primary)" />}>
              Ask AI HR Assistant
            </Button>
          </Link>
          <Link to="/employees">
            <Button variant="primary" icon={<UserPlus size={16} />}>
              Add Employee
            </Button>
          </Link>
          <Link to="/reports">
            <Button variant="secondary" icon={<FileText size={16} />}>
              View Reports
            </Button>
          </Link>
        </div>
      </div>

      {/* Mobile Quick Action Pill Bar */}
      <div className="mobile-quick-actions">
        <Link to="/employees" className="quick-pill">
          <Users size={16} /> Directory
        </Link>
        <Link to="/attendance" className="quick-pill">
          <Clock size={16} /> Attendance
        </Link>
        <Link to="/leave" className="quick-pill">
          <Calendar size={16} /> Leaves
        </Link>
        <Link to="/payroll" className="quick-pill">
          <Banknote size={16} /> Payroll
        </Link>
        <Link to="/ai-intelligence" className="quick-pill">
          <TrendingUp size={16} /> AI Analytics
        </Link>
        <Link to="/reports" className="quick-pill">
          <FileText size={16} /> Reports
        </Link>
      </div>

      {/* Flagship 3D Hero Workforce Constellation Scene */}
      <ThreeDHero
        totalEmployees={metrics.total_employees}
        activeEmployees={metrics.active_employees}
        departmentCount={metrics.departments_count}
        locationCount={metrics.locations_count}
      />

      {/* 3D Elevated Metric Cards Grid */}
      <div className="grid-4">
        <ThreeDMetricCard
          label="Total Headcount"
          value={metrics.total_employees}
          badge="Active Roster"
          badgeVariant="success"
          subtext={
            <span style={{ color: 'var(--success)' }}>
              {metrics.active_employees} Active ({((metrics.active_employees / metrics.total_employees) * 100).toFixed(0)}%)
            </span>
          }
          icon={<Users size={24} />}
          iconBg="rgba(99, 102, 241, 0.15)"
          iconColor="var(--primary)"
          accentColor="var(--primary)"
        />

        <ThreeDMetricCard
          label="Daily Attendance"
          value={`${metrics.daily_attendance_rate}%`}
          badge="Live Today"
          badgeVariant="success"
          subtext={
            <span>
              {attendanceSummary?.present_count || 184} present today
            </span>
          }
          icon={<Clock size={24} />}
          iconBg="rgba(16, 185, 129, 0.15)"
          iconColor="var(--success)"
          accentColor="var(--success)"
        />

        <ThreeDMetricCard
          label="Pending Leaves"
          value={metrics.pending_leave_requests}
          badge="Needs Action"
          badgeVariant="warning"
          subtext={
            <span style={{ color: 'var(--warning)' }}>Requires HR / Manager sign-off</span>
          }
          icon={<Calendar size={24} />}
          iconBg="rgba(245, 158, 11, 0.15)"
          iconColor="var(--warning)"
          accentColor="var(--warning)"
        />

        <ThreeDMetricCard
          label="Monthly Payroll"
          value={formatINR(metrics.total_monthly_payroll)}
          badge="Disbursed"
          badgeVariant="purple"
          subtext={<span>Net disbursement</span>}
          icon={<Banknote size={24} />}
          iconBg="rgba(168, 85, 247, 0.15)"
          iconColor="var(--purple)"
          accentColor="var(--purple)"
        />
      </div>

      {/* Secondary Metrics Bar */}
      <div
        className="glass-card"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1.5rem',
          padding: '1.25rem 1.75rem',
        }}
      >
        <div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Notice Period</span>
          <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#FFF' }}>{metrics.notice_period_employees} Employees</div>
        </div>

        <div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Average Work Hours</span>
          <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#FFF' }}>{attendanceSummary?.avg_work_hours || 8.4} hrs/day</div>
        </div>

        <div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Total Overtime Logged</span>
          <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--primary)' }}>{attendanceSummary?.total_overtime_hours || 420} hrs</div>
        </div>

        <div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>High Attrition Risk</span>
          <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--danger)' }}>{metrics.attrition_risk_high} Staff</div>
        </div>
      </div>

      {/* Interactive 3D Workforce Topology Constellation */}
      {employees.length > 0 && (
        <WorkforceScene
          employees={employees}
        />
      )}

      {/* Visual Analytics Charts Grid */}
      <div className="grid-2">
        {/* Department Headcount Bar Chart */}
        <Card
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Users size={18} style={{ color: 'var(--primary)' }} />
              <span>Headcount by Department</span>
            </div>
          }
          subtitle="Real-time distribution across active business units"
        >
          <div style={{ height: '300px', width: '100%', marginTop: '1rem' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={deptData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <XAxis dataKey="name" stroke="var(--text-dim)" fontSize={11} interval={0} angle={-30} textAnchor="end" />
                <YAxis stroke="var(--text-dim)" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--bg-card-solid)',
                    border: 'var(--border-glass)',
                    borderRadius: 'var(--radius-md)',
                    color: '#FFF',
                  }}
                />
                <Bar dataKey="count" fill="url(#colorGrad)" radius={[4, 4, 0, 0]}>
                  {deptData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={index % 2 === 0 ? 'var(--primary)' : '#8B5CF6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Attendance Breakdown Donut */}
        <Card
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Clock size={18} style={{ color: 'var(--success)' }} />
              <span>Daily Attendance Distribution</span>
            </div>
          }
          subtitle="Current status breakdown across all employees"
        >
          <div style={{ height: '300px', width: '100%', marginTop: '1rem', display: 'flex', alignItems: 'center' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={attChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={65}
                  outerRadius={95}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {attChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--bg-card-solid)',
                    border: 'var(--border-glass)',
                    borderRadius: 'var(--radius-md)',
                    color: '#FFF',
                  }}
                />
                <Legend formatter={(value) => <span style={{ color: 'var(--text-main)', fontSize: '0.82rem' }}>{value}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Attrition Risk & Quick Navigation Links */}
      <div className="grid-2">
        {/* Attrition Risk Assessment */}
        <Card
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertTriangle size={18} style={{ color: 'var(--warning)' }} />
              <span>Workforce Attrition Risk Profiling</span>
            </div>
          }
          subtitle="Proactive employee turnover vulnerability segments"
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
            {attritionData.map((item) => (
              <div key={item.name} style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                  <span style={{ color: '#FFF', fontWeight: 500 }}>{item.name}</span>
                  <span style={{ color: item.color, fontWeight: 700 }}>
                    {item.value} ({((item.value / metrics.total_employees) * 100).toFixed(0)}%)
                  </span>
                </div>
                <div style={{ width: '100%', height: '8px', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${(item.value / metrics.total_employees) * 100}%`,
                      height: '100%',
                      backgroundColor: item.color,
                      borderRadius: '4px',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Quick Management Shortcuts */}
        <Card
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <TrendingUp size={18} style={{ color: 'var(--info)' }} />
              <span>Operational Management Hub</span>
            </div>
          }
          subtitle="Direct access to high-priority administrative tasks"
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
            <Link
              to="/ai-intelligence"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.85rem 1rem',
                backgroundColor: 'rgba(99, 102, 241, 0.08)',
                border: '1px solid rgba(99, 102, 241, 0.25)',
                borderRadius: 'var(--radius-md)',
                color: '#FFF',
              }}
            >
              <div>
                <div style={{ fontWeight: 600, color: 'var(--primary)' }}>AI Workforce Intelligence & Forecasting</div>
                <div style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>Predictive attrition, demand forecast & skill gap analysis</div>
              </div>
              <ArrowRight size={18} style={{ color: 'var(--primary)' }} />
            </Link>

            <Link
              to="/leave"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.85rem 1rem',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                color: '#FFF',
              }}
            >
              <div>
                <div style={{ fontWeight: 600 }}>Review Pending Leave Requests</div>
                <div style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>{metrics.pending_leave_requests} applications awaiting action</div>
              </div>
              <ArrowRight size={18} style={{ color: 'var(--primary)' }} />
            </Link>

            <Link
              to="/payroll"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.85rem 1rem',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                color: '#FFF',
              }}
            >
              <div>
                <div style={{ fontWeight: 600 }}>Execute Monthly Payroll Run</div>
                <div style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>Cycle: March 2026 • 200 eligible payslips</div>
              </div>
              <ArrowRight size={18} style={{ color: 'var(--primary)' }} />
            </Link>

            <Link
              to="/employees"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.85rem 1rem',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                color: '#FFF',
              }}
            >
              <div>
                <div style={{ fontWeight: 600 }}>Browse Employee Master Directory</div>
                <div style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>200 records with profile, skills and appraisals</div>
              </div>
              <ArrowRight size={18} style={{ color: 'var(--primary)' }} />
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};
