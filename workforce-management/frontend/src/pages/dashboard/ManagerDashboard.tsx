import React, { useState, useEffect } from 'react';
import {
  Users,
  Clock,
  Calendar,
  FileCheck,
  Award,
  AlertCircle,
  CheckCircle,
  XCircle,
  ArrowRight,
  TrendingUp,
  BrainCircuit,
  Sparkles,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Table, Column } from '../../components/common/Table';
import { LoadingSkeleton } from '../../components/common/LoadingSkeleton';
import { ThreeDMetricCard, WorkforceScene } from '../../components/3d';
import { managerService } from '../../services/managerService';
import { leaveService } from '../../services/leaveService';
import { useToast } from '../../context/ToastContext';
import { ManagerTeamSummary, Employee, LeaveRequest } from '../../types';

export const ManagerDashboard: React.FC = () => {
  const { showToast } = useToast();
  const [summary, setSummary] = useState<ManagerTeamSummary | null>(null);
  const [team, setTeam] = useState<Employee[]>([]);
  const [pendingLeaves, setPendingLeaves] = useState<LeaveRequest[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchManagerData = async () => {
    try {
      setIsLoading(true);
      const [sum, teamList, leaves] = await Promise.all([
        managerService.getTeamSummary(),
        managerService.getTeam(),
        managerService.getTeamLeave(),
      ]);
      setSummary(sum);
      setTeam(teamList);
      setPendingLeaves(leaves.filter((l) => l.status === 'Pending'));
    } catch (err) {
      console.error('Error loading manager dashboard:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchManagerData();
  }, []);

  const handleApproveLeave = async (leaveId: string) => {
    try {
      await leaveService.approveLeave(leaveId);
      showToast('Leave request approved successfully!', 'success');
      fetchManagerData();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to approve leave.', 'error');
    }
  };

  const handleRejectLeave = async (leaveId: string) => {
    const reason = prompt('Please enter rejection reason:');
    if (!reason) return;
    try {
      await leaveService.rejectLeave(leaveId, reason);
      showToast('Leave request rejected.', 'info');
      fetchManagerData();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to reject leave.', 'error');
    }
  };

  if (isLoading || !summary) {
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

  const teamColumns: Column<Employee>[] = [
    {
      key: 'employee_id',
      header: 'EMP ID',
      render: (emp) => <strong style={{ color: 'var(--primary)' }}>{emp.employee_id}</strong>,
    },
    {
      key: 'name',
      header: 'Name',
      render: (emp) => (
        <div>
          <div style={{ fontWeight: 600, color: '#FFF' }}>{emp.name}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{emp.email}</div>
        </div>
      ),
    },
    {
      key: 'designation',
      header: 'Designation',
    },
    {
      key: 'employment_status',
      header: 'Status',
      render: (emp) => <Badge variant={emp.employment_status}>{emp.employment_status}</Badge>,
    },
    {
      key: 'actions',
      header: 'Action',
      render: (emp) => (
        <Link to={`/employees/${emp.employee_id}`}>
          <Button variant="ghost" size="sm">
            Profile
          </Button>
        </Link>
      ),
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ margin: 0 }}>Manager Operations Center</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
            Real-time monitoring of your direct reporting team ({summary.team_size} members).
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <Link to="/ai-assistant">
            <Button variant="outline" icon={<Sparkles size={16} color="var(--color-primary)" />}>
              Ask about my team
            </Button>
          </Link>
          <Link to="/manager/team">
            <Button variant="primary" icon={<Users size={16} />}>
              Team Directory
            </Button>
          </Link>
          <Link to="/attendance">
            <Button variant="secondary" icon={<Clock size={16} />}>
              Team Attendance
            </Button>
          </Link>
        </div>
      </div>

      {/* Mobile Quick Action Pill Bar */}
      <div className="mobile-quick-actions">
        <Link to="/manager/team" className="quick-pill">
          <Users size={16} /> My Team
        </Link>
        <Link to="/leave" className="quick-pill">
          <Calendar size={16} /> Pending Leaves ({summary.pending_leave_requests})
        </Link>
        <Link to="/timesheets" className="quick-pill">
          <FileCheck size={16} /> Timesheets
        </Link>
        <Link to="/attendance" className="quick-pill">
          <Clock size={16} /> Attendance
        </Link>
        <Link to="/ai-intelligence" className="quick-pill">
          <BrainCircuit size={16} /> AI Insights
        </Link>
      </div>

      {/* 3D Elevated KPI Cards */}
      <div className="grid-4">
        <ThreeDMetricCard
          label="Direct Reports"
          value={summary.team_size}
          badge="Reporting Team"
          badgeVariant="info"
          subtext={<span>Reporting team members</span>}
          icon={<Users size={24} />}
          iconBg="rgba(99, 102, 241, 0.15)"
          iconColor="var(--primary)"
          accentColor="var(--primary)"
        />

        <ThreeDMetricCard
          label="Present Today"
          value={summary.present_today}
          badge="Active Today"
          badgeVariant="success"
          subtext={
            <span style={{ color: 'var(--success)' }}>
              {summary.team_size > 0 ? ((summary.present_today / summary.team_size) * 100).toFixed(0) : 100}% attendance
            </span>
          }
          icon={<Clock size={24} />}
          iconBg="rgba(16, 185, 129, 0.15)"
          iconColor="var(--success)"
          accentColor="var(--success)"
        />

        <ThreeDMetricCard
          label="Pending Leaves"
          value={summary.pending_leave_requests}
          badge={summary.pending_leave_requests > 0 ? "Requires Action" : "Clear"}
          badgeVariant="warning"
          subtext={<span style={{ color: 'var(--warning)' }}>Awaiting your decision</span>}
          icon={<Calendar size={24} />}
          iconBg="rgba(245, 158, 11, 0.15)"
          iconColor="var(--warning)"
          accentColor="var(--warning)"
        />

        <ThreeDMetricCard
          label="Productivity Score"
          value={`${summary.avg_productivity_score} / 5.0`}
          badge="Monthly Rating"
          badgeVariant="purple"
          subtext={<span>Team performance rating</span>}
          icon={<Award size={24} />}
          iconBg="rgba(168, 85, 247, 0.15)"
          iconColor="var(--purple)"
          accentColor="var(--purple)"
        />
      </div>

      {/* 3D Team Topology Network */}
      {team.length > 0 && (
        <WorkforceScene employees={team} />
      )}

      {/* Pending Leave Approvals Section */}
      <Card
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Calendar size={18} style={{ color: 'var(--warning)' }} />
            <span>Pending Team Leave Applications</span>
          </div>
        }
        subtitle={`${pendingLeaves.length} applications requiring immediate review`}
      >
        {pendingLeaves.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)' }}>
            <CheckCircle size={32} style={{ color: 'var(--success)', marginBottom: '0.5rem' }} />
            <div>All clear! No pending leave requests from your team.</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
            {pendingLeaves.map((leave) => (
              <div
                key={leave.leave_id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '1rem',
                  backgroundColor: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  flexWrap: 'wrap',
                  gap: '1rem',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <span style={{ fontWeight: 600, color: '#FFF' }}>{leave.employee_id}</span>
                    <Badge variant="purple">{leave.leave_type}</Badge>
                    <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>
                      {leave.days_count} day(s) • {leave.start_date} to {leave.end_date}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                    Reason: <em>"{leave.reason}"</em>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <Button
                    variant="success"
                    size="sm"
                    icon={<CheckCircle size={14} />}
                    onClick={() => handleApproveLeave(leave.leave_id)}
                  >
                    Approve
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    icon={<XCircle size={14} />}
                    onClick={() => handleRejectLeave(leave.leave_id)}
                  >
                    Reject
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Team AI Intelligence Card */}
      <Card
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BrainCircuit size={18} style={{ color: 'var(--primary)' }} />
            <span>Team AI Workforce Insights</span>
          </div>
        }
        subtitle="Predictive insights, shift optimization, and absenteeism early warnings for your team"
        action={
          <Link to="/ai-intelligence">
            <Button variant="ghost" size="sm" icon={<ArrowRight size={14} />}>
              Open AI Center
            </Button>
          </Link>
        }
      >
        <div style={{ padding: '0.5rem 0', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '200px', padding: '1rem', backgroundColor: 'rgba(255, 255, 255, 0.02)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Absenteeism Early Warning</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--success)', marginTop: '0.2rem' }}>Normal Stability</div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.3rem' }}>No immediate flight or attendance risk flags on reporting members.</p>
          </div>
          <div style={{ flex: 1, minWidth: '200px', padding: '1rem', backgroundColor: 'rgba(255, 255, 255, 0.02)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Shift Optimization</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--primary)', marginTop: '0.2rem' }}>Balanced Coverage</div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.3rem' }}>Overtime distribution within standard compliance thresholds.</p>
          </div>
        </div>
      </Card>

      {/* Direct Reports Table */}
      <Card
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Users size={18} style={{ color: 'var(--primary)' }} />
            <span>Direct Reports Roster</span>
          </div>
        }
        subtitle="Employees reporting directly to your managerial oversight"
        action={
          <Link to="/manager/team">
            <Button variant="ghost" size="sm" icon={<ArrowRight size={14} />}>
              Full Team View
            </Button>
          </Link>
        }
      >
        <div className="desktop-table-view">
          <Table columns={teamColumns} data={team.slice(0, 5)} />
        </div>
        <div className="mobile-card-grid">
          {team.slice(0, 5).map((emp) => (
            <div
              key={emp.employee_id}
              style={{
                padding: '0.85rem 1rem',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ fontWeight: 600, color: '#FFF' }}>{emp.name}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                  {emp.employee_id} • {emp.designation}
                </div>
              </div>
              <Badge variant={emp.employment_status === 'Active' ? 'success' : 'neutral'}>
                {emp.employment_status}
              </Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
