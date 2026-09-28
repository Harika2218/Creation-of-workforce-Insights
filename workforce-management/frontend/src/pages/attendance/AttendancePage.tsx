import React, { useState, useEffect, useCallback } from 'react';
import { Clock, Search, Filter, AlertTriangle, CheckCircle, MapPin } from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { PunchClockCard } from '../../components/attendance/PunchClockCard';
import { AttendanceScene, ThreeDMetricCard } from '../../components/3d';
import { attendanceService } from '../../services/attendanceService';
import { useAuth } from '../../context/AuthContext';
import { AttendanceRecord, AttendanceSummary } from '../../types';

export const AttendancePage: React.FC = () => {
  const { user } = useAuth();
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [summary, setSummary] = useState<AttendanceSummary | null>(null);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Filters
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(10);
  const [dateFilter, setDateFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [methodFilter, setMethodFilter] = useState<string>('');
  const [empFilter, setEmpFilter] = useState<string>(
    user?.role === 'EMPLOYEE' ? user.employee_id : ''
  );

  const fetchAttendance = useCallback(async () => {
    try {
      setIsLoading(true);
      const [res, sum] = await Promise.all([
        attendanceService.getAttendance({
          page,
          page_size: pageSize,
          date: dateFilter || undefined,
          status: statusFilter || undefined,
          attendance_method: methodFilter || undefined,
          employee_id: empFilter || undefined,
        }),
        attendanceService.getAttendanceSummary(dateFilter || undefined),
      ]);
      setRecords(res.items);
      setTotal(res.total);
      setTotalPages(res.total_pages);
      setSummary(sum);
    } catch (err) {
      console.error('Error fetching attendance:', err);
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, dateFilter, statusFilter, methodFilter, empFilter]);

  useEffect(() => {
    fetchAttendance();
  }, [fetchAttendance]);

  const columns: Column<AttendanceRecord>[] = [
    {
      key: 'employee_id',
      header: 'Employee ID',
      width: '120px',
      render: (r) => <strong style={{ color: 'var(--primary)' }}>{r.employee_id}</strong>,
    },
    { key: 'date', header: 'Date', width: '110px' },
    { key: 'check_in_time', header: 'Check In', render: (r) => r.check_in_time || '—' },
    { key: 'check_out_time', header: 'Check Out', render: (r) => r.check_out_time || '—' },
    { key: 'work_hours', header: 'Work Hours', render: (r) => `${r.work_hours} hrs` },
    {
      key: 'late_minutes',
      header: 'Late Mins',
      render: (r) => (
        r.late_minutes > 0 ? (
          <span style={{ color: 'var(--warning)', fontWeight: 600 }}>{r.late_minutes}m</span>
        ) : (
          <span style={{ color: 'var(--text-dim)' }}>0m</span>
        )
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (r) => <Badge variant={r.status}>{r.status}</Badge>,
    },
    {
      key: 'attendance_method',
      header: 'Method',
      render: (r) => <Badge variant="neutral">{r.attendance_method}</Badge>,
    },
    {
      key: 'anomaly_flag',
      header: 'Anomaly',
      align: 'center',
      render: (r) => (
        r.anomaly_flag ? (
          <Badge variant="danger" icon={<AlertTriangle size={12} />}>
            Flagged
          </Badge>
        ) : (
          <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>None</span>
        )
      ),
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Title */}
      <div>
        <h1 style={{ margin: 0 }}>Attendance & Time Tracking</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
          GPS geofenced clock-in validation and enterprise attendance logs.
        </p>
      </div>

      {/* Real-time Punch Clock Card */}
      <PunchClockCard onAttendanceChanged={() => fetchAttendance()} />

      {/* 3D Attendance Radar Scene */}
      <AttendanceScene
        summary={summary}
        dateStr={dateFilter || 'Today'}
        onFilterChange={(status) => {
          setStatusFilter(status === 'ALL' ? '' : status);
          setPage(1);
        }}
      />

      {/* Filter Toolbar */}
      <Card>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
          {user?.role !== 'EMPLOYEE' && (
            <Input
              placeholder="Search Employee ID..."
              value={empFilter}
              onChange={(e) => {
                setEmpFilter(e.target.value);
                setPage(1);
              }}
            />
          )}

          <Input
            type="date"
            value={dateFilter}
            onChange={(e) => {
              setDateFilter(e.target.value);
              setPage(1);
            }}
          />

          <Input
            as="select"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All Statuses</option>
            <option value="Present">Present</option>
            <option value="Late">Late</option>
            <option value="On Leave">On Leave</option>
            <option value="Half-day">Half-day</option>
            <option value="Absent">Absent</option>
          </Input>

          <Input
            as="select"
            value={methodFilter}
            onChange={(e) => {
              setMethodFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All Methods</option>
            <option value="GPS">GPS Geofenced</option>
            <option value="Biometric">Biometric</option>
            <option value="Web">Web Portal</option>
          </Input>
        </div>
      </Card>

      {/* Attendance Table with Mobile Card Grid Fallback */}
      <Card title={`Attendance Records (${total.toLocaleString()})`}>
        <div className="desktop-table-view">
          <Table
            columns={columns}
            data={records}
            isLoading={isLoading}
            page={page}
            totalPages={totalPages}
            totalRecords={total}
            pageSize={pageSize}
            onPageChange={(p) => setPage(p)}
            emptyTitle="No attendance logs found"
            emptyDescription="Try selecting another date or adjusting your filters."
          />
        </div>

        <div className="mobile-card-grid">
          {isLoading ? (
            <div style={{ padding: '1rem', color: 'var(--text-muted)', textAlign: 'center' }}>
              Loading attendance logs...
            </div>
          ) : records.length === 0 ? (
            <div style={{ padding: '2rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              No attendance records found.
            </div>
          ) : (
            records.map((r) => (
              <div
                key={r.attendance_id || `${r.employee_id}-${r.date}`}
                style={{
                  padding: '0.85rem 1rem',
                  backgroundColor: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, color: '#FFF' }}>{r.employee_id} • {r.date}</span>
                  <Badge variant={r.status}>{r.status}</Badge>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                  <span>In: <strong style={{ color: '#FFF' }}>{r.check_in_time || '—'}</strong></span>
                  <span>Out: <strong style={{ color: '#FFF' }}>{r.check_out_time || '—'}</strong></span>
                  <span>Hours: <strong style={{ color: 'var(--primary)' }}>{r.work_hours}h</strong></span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                  <span>Method: {r.attendance_method}</span>
                  {r.anomaly_flag ? (
                    <Badge variant="danger" icon={<AlertTriangle size={11} />}>
                      Anomaly
                    </Badge>
                  ) : (
                    <span style={{ color: 'var(--success)' }}>✓ Normal</span>
                  )}
                </div>
              </div>
            ))
          )}

          {/* Simple Mobile Pagination */}
          {totalPages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0' }}>
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
              >
                Previous
              </Button>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Page {page} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
              >
                Next
              </Button>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};
