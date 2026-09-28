import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, Plus, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Table, Column } from '../../components/common/Table';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { leaveService } from '../../services/leaveService';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { LeaveBalance, LeaveRequest } from '../../types';

export const LeavePage: React.FC = () => {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [balances, setBalances] = useState<LeaveBalance | null>(null);
  const [requests, setRequests] = useState<LeaveRequest[]>([]);
  const [leaveTypes, setLeaveTypes] = useState<string[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [page, setPage] = useState<number>(1);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Application Modal
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [leaveForm, setLeaveForm] = useState({
    leave_type: 'Annual Leave',
    start_date: new Date().toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    reason: '',
  });

  const fetchLeaveData = useCallback(async () => {
    try {
      setIsLoading(true);
      const [bal, reqs, types] = await Promise.all([
        user?.employee_id ? leaveService.getLeaveBalances(user.employee_id) : Promise.resolve(null),
        leaveService.getLeaveRequests({
          page,
          page_size: 10,
          status: statusFilter || undefined,
          employee_id: user?.role === 'EMPLOYEE' ? user.employee_id : undefined,
        }),
        leaveService.getLeaveTypes(),
      ]);
      setBalances(bal);
      setRequests(reqs.items);
      setTotal(reqs.total);
      setTotalPages(reqs.total_pages);
      setLeaveTypes(types);
    } catch (err) {
      console.error('Error fetching leave data:', err);
    } finally {
      setIsLoading(false);
    }
  }, [user?.employee_id, user?.role, page, statusFilter]);

  useEffect(() => {
    fetchLeaveData();
  }, [fetchLeaveData]);

  const handleApplyLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user?.employee_id) return;

    if (leaveForm.start_date > leaveForm.end_date) {
      showToast('Start date must be on or before end date.', 'error');
      return;
    }

    try {
      setIsSubmitting(true);
      await leaveService.applyLeave({
        employee_id: user.employee_id,
        leave_type: leaveForm.leave_type,
        start_date: leaveForm.start_date,
        end_date: leaveForm.end_date,
        reason: leaveForm.reason,
      });
      showToast('Leave request submitted successfully!', 'success');
      setIsModalOpen(false);
      fetchLeaveData();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to apply for leave.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleApprove = async (leaveId: string) => {
    try {
      await leaveService.approveLeave(leaveId);
      showToast('Leave request approved!', 'success');
      fetchLeaveData();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to approve leave.', 'error');
    }
  };

  const handleReject = async (leaveId: string) => {
    const reason = prompt('Please enter rejection reason:');
    if (!reason) return;
    try {
      await leaveService.rejectLeave(leaveId, reason);
      showToast('Leave request rejected.', 'info');
      fetchLeaveData();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to reject leave.', 'error');
    }
  };

  const isApprover = user?.role === 'ADMIN' || user?.role === 'HR' || user?.role === 'MANAGER';

  const columns: Column<LeaveRequest>[] = [
    { key: 'leave_id', header: 'Application ID', width: '130px' },
    {
      key: 'employee_id',
      header: 'Employee ID',
      render: (l) => <strong style={{ color: 'var(--primary)' }}>{l.employee_id}</strong>,
    },
    {
      key: 'leave_type',
      header: 'Leave Type',
      render: (l) => <Badge variant="purple">{l.leave_type}</Badge>,
    },
    { key: 'start_date', header: 'Start Date' },
    { key: 'end_date', header: 'End Date' },
    { key: 'days_count', header: 'Days', render: (l) => `${l.days_count} d` },
    { key: 'reason', header: 'Reason' },
    {
      key: 'status',
      header: 'Status',
      render: (l) => <Badge variant={l.status}>{l.status}</Badge>,
    },
    ...(isApprover
      ? [
          {
            key: 'actions',
            header: 'Review Action',
            render: (l: LeaveRequest) => (
              l.status === 'Pending' ? (
                <div style={{ display: 'flex', gap: '0.4rem' }}>
                  <Button variant="success" size="sm" onClick={() => handleApprove(l.leave_id)}>
                    Approve
                  </Button>
                  <Button variant="danger" size="sm" onClick={() => handleReject(l.leave_id)}>
                    Reject
                  </Button>
                </div>
              ) : (
                <span style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>Processed</span>
              )
            ),
          },
        ]
      : []),
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ margin: 0 }}>Leave & PTO Management</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
            Available balances, PTO applications, and multi-tier manager approvals.
          </p>
        </div>

        <Button variant="primary" icon={<Plus size={16} />} onClick={() => setIsModalOpen(true)}>
          Apply for Leave
        </Button>
      </div>

      {/* Leave Balances Strip */}
      {balances && (
        <div className="grid-4">
          <div className="glass-card" style={{ textAlign: 'center', padding: '1.25rem' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Annual Leave</span>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--success)', marginTop: '0.2rem' }}>
              {balances.annual_leave}
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Days Available</span>
          </div>

          <div className="glass-card" style={{ textAlign: 'center', padding: '1.25rem' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Sick Leave</span>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--warning)', marginTop: '0.2rem' }}>
              {balances.sick_leave}
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Days Available</span>
          </div>

          <div className="glass-card" style={{ textAlign: 'center', padding: '1.25rem' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Casual Leave</span>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--info)', marginTop: '0.2rem' }}>
              {balances.casual_leave}
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Days Available</span>
          </div>

          <div className="glass-card" style={{ textAlign: 'center', padding: '1.25rem' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Emergency Leave</span>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--purple)', marginTop: '0.2rem' }}>
              {balances.emergency_leave}
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Days Available</span>
          </div>
        </div>
      )}

      {/* Filter Bar */}
      <Card>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', maxWidth: '300px' }}>
          <Input
            as="select"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All Applications</option>
            <option value="Pending">Pending Review</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
          </Input>
        </div>
      </Card>

      {/* Requests Table */}
      <Card title={`Leave Applications (${total})`}>
        <Table
          columns={columns}
          data={requests}
          isLoading={isLoading}
          page={page}
          totalPages={totalPages}
          totalRecords={total}
          pageSize={10}
          onPageChange={(p) => setPage(p)}
          emptyTitle="No leave applications found"
        />
      </Card>

      {/* Apply Leave Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Submit Leave Application"
        footer={
          <>
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleApplyLeave} isLoading={isSubmitting}>
              Submit Application
            </Button>
          </>
        }
      >
        <form onSubmit={handleApplyLeave} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Input
            as="select"
            label="Leave Type *"
            value={leaveForm.leave_type}
            onChange={(e) => setLeaveForm({ ...leaveForm, leave_type: e.target.value })}
          >
            {leaveTypes.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </Input>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Input
              type="date"
              label="Start Date *"
              value={leaveForm.start_date}
              onChange={(e) => setLeaveForm({ ...leaveForm, start_date: e.target.value })}
              required
            />
            <Input
              type="date"
              label="End Date *"
              value={leaveForm.end_date}
              onChange={(e) => setLeaveForm({ ...leaveForm, end_date: e.target.value })}
              required
            />
          </div>

          <Input
            as="textarea"
            label="Reason for Leave *"
            placeholder="Please detail your reason for taking time off..."
            value={leaveForm.reason}
            onChange={(e) => setLeaveForm({ ...leaveForm, reason: e.target.value })}
            rows={3}
            required
          />
        </form>
      </Modal>
    </div>
  );
};
