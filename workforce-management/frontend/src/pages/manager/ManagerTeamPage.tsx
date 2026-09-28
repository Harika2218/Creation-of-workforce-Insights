import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Users, Clock, CalendarDays, Eye, Mail, Phone, MapPin } from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Table, Column } from '../../components/common/Table';
import { LoadingSkeleton } from '../../components/common/LoadingSkeleton';
import { managerService } from '../../services/managerService';
import { Employee, AttendanceRecord, ShiftSchedule } from '../../types';

export const ManagerTeamPage: React.FC = () => {
  const [team, setTeam] = useState<Employee[]>([]);
  const [attendance, setAttendance] = useState<AttendanceRecord[]>([]);
  const [shifts, setShifts] = useState<ShiftSchedule[]>([]);
  const [activeTab, setActiveTab] = useState<'members' | 'attendance' | 'shifts'>('members');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchTeamData = async () => {
      try {
        setIsLoading(true);
        const [teamList, attList, shiftList] = await Promise.all([
          managerService.getTeam(),
          managerService.getTeamAttendance(),
          managerService.getTeamShifts(),
        ]);
        setTeam(teamList);
        setAttendance(attList);
        setShifts(shiftList);
      } catch (err) {
        console.error('Error fetching manager team data:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchTeamData();
  }, []);

  const memberColumns: Column<Employee>[] = [
    {
      key: 'employee_id',
      header: 'EMP ID',
      width: '120px',
      render: (emp) => <strong style={{ color: 'var(--primary)' }}>{emp.employee_id}</strong>,
    },
    {
      key: 'name',
      header: 'Team Member',
      render: (emp) => (
        <div>
          <div style={{ fontWeight: 600, color: '#FFF' }}>{emp.name}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>{emp.email}</div>
        </div>
      ),
    },
    { key: 'designation', header: 'Designation' },
    { key: 'location_name', header: 'Office Location', render: (emp) => emp.location_name || emp.location_id },
    { key: 'employment_status', header: 'Status', render: (emp) => <Badge variant={emp.employment_status}>{emp.employment_status}</Badge> },
    {
      key: 'actions',
      header: 'Action',
      align: 'right',
      render: (emp) => (
        <Link to={`/employees/${emp.employee_id}`}>
          <Button variant="ghost" size="sm" icon={<Eye size={14} />}>
            View Profile
          </Button>
        </Link>
      ),
    },
  ];

  const attendanceColumns: Column<AttendanceRecord>[] = [
    { key: 'employee_id', header: 'Employee ID' },
    { key: 'date', header: 'Date' },
    { key: 'check_in_time', header: 'Check In', render: (r) => r.check_in_time || '—' },
    { key: 'check_out_time', header: 'Check Out', render: (r) => r.check_out_time || '—' },
    { key: 'work_hours', header: 'Hours', render: (r) => `${r.work_hours}h` },
    { key: 'status', header: 'Status', render: (r) => <Badge variant={r.status}>{r.status}</Badge> },
  ];

  const shiftColumns: Column<ShiftSchedule>[] = [
    { key: 'employee_id', header: 'Employee ID' },
    { key: 'shift_id', header: 'Shift ID' },
    { key: 'start_time', header: 'Hours', render: (s) => `${s.start_time || '09:00'} - ${s.end_time || '18:00'}` },
    { key: 'date', header: 'Assigned Date' },
    { key: 'status', header: 'Status', render: (s) => <Badge variant="active">{s.status}</Badge> },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Title */}
      <div>
        <h1 style={{ margin: 0 }}>My Team Roster</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
          Direct reports oversight, operational scheduling, and daily attendance logs.
        </p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
        {[
          { key: 'members', label: `Team Members (${team.length})`, icon: <Users size={16} /> },
          { key: 'attendance', label: `Team Attendance (${attendance.length})`, icon: <Clock size={16} /> },
          { key: 'shifts', label: `Shift Allocations (${shifts.length})`, icon: <CalendarDays size={16} /> },
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
            }}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      <Card>
        {activeTab === 'members' && (
          <Table columns={memberColumns} data={team} isLoading={isLoading} emptyTitle="No team members found" />
        )}
        {activeTab === 'attendance' && (
          <Table columns={attendanceColumns} data={attendance} isLoading={isLoading} emptyTitle="No attendance logs found" />
        )}
        {activeTab === 'shifts' && (
          <Table columns={shiftColumns} data={shifts} isLoading={isLoading} emptyTitle="No shift assignments found" />
        )}
      </Card>
    </div>
  );
};
