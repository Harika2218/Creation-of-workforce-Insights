import React, { useState, useEffect, useCallback } from 'react';
import { FileSpreadsheet, Plus, CheckCircle, XCircle } from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Table, Column } from '../../components/common/Table';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { timesheetService } from '../../services/timesheetService';
import { projectService } from '../../services/projectService';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { TimesheetRecord, Project } from '../../types';

export const TimesheetsPage: React.FC = () => {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [timesheets, setTimesheets] = useState<TimesheetRecord[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [page, setPage] = useState<number>(1);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Submit Modal
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [tsForm, setTsForm] = useState({
    project_id: 'PRJ001',
    date: new Date().toISOString().split('T')[0],
    hours_worked: 8,
    billable_hours: 8,
    non_billable_hours: 0,
    task_description: '',
  });

  const fetchTimesheets = useCallback(async () => {
    try {
      setIsLoading(true);
      const res = await timesheetService.getTimesheets({
        page,
        page_size: 10,
        status: statusFilter || undefined,
        employee_id: user?.role === 'EMPLOYEE' ? user.employee_id : undefined,
      });
      setTimesheets(res.items);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (err) {
      console.error('Error fetching timesheets:', err);
    } finally {
      setIsLoading(false);
    }
  }, [user?.employee_id, user?.role, page, statusFilter]);

  useEffect(() => {
    fetchTimesheets();
    projectService.getProjects().then(setProjects).catch(() => {});
  }, [fetchTimesheets]);

  const handleSubmitTimesheet = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user?.employee_id) return;

    const totalHours = Number(tsForm.hours_worked);
    const billable = Number(tsForm.billable_hours);
    const nonBillable = Number(tsForm.non_billable_hours);

    if (totalHours <= 0 || totalHours > 24) {
      showToast('Hours worked must be between 0.5 and 24.', 'error');
      return;
    }

    if (billable + nonBillable !== totalHours) {
      showToast('Billable hours + Non-billable hours must equal Total Hours Worked.', 'error');
      return;
    }

    try {
      setIsSubmitting(true);
      await timesheetService.createTimesheet({
        employee_id: user.employee_id,
        project_id: tsForm.project_id,
        date: tsForm.date,
        hours_worked: totalHours,
        billable_hours: billable,
        non_billable_hours: nonBillable,
        task_description: tsForm.task_description,
      });
      showToast('Timesheet submitted successfully!', 'success');
      setIsModalOpen(false);
      fetchTimesheets();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to submit timesheet.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await timesheetService.approveTimesheet(id);
      showToast('Timesheet approved!', 'success');
      fetchTimesheets();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Approval failed.', 'error');
    }
  };

  const handleReject = async (id: string) => {
    const reason = prompt('Please enter rejection reason:');
    if (!reason) return;
    try {
      await timesheetService.rejectTimesheet(id, reason);
      showToast('Timesheet rejected.', 'info');
      fetchTimesheets();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Rejection failed.', 'error');
    }
  };

  const isManager = user?.role === 'ADMIN' || user?.role === 'HR' || user?.role === 'MANAGER';

  const columns: Column<TimesheetRecord>[] = [
    { key: 'timesheet_id', header: 'Timesheet ID', width: '130px' },
    { key: 'employee_id', header: 'Employee', render: (t) => <strong style={{ color: 'var(--primary)' }}>{t.employee_id}</strong> },
    { key: 'project_id', header: 'Project' },
    { key: 'date', header: 'Date' },
    { key: 'hours_worked', header: 'Total (hrs)', render: (t) => `${t.hours_worked}h` },
    { key: 'billable_hours', header: 'Billable', render: (t) => <span style={{ color: 'var(--success)' }}>{t.billable_hours}h</span> },
    { key: 'task_description', header: 'Task Summary' },
    { key: 'status', header: 'Status', render: (t) => <Badge variant={t.status}>{t.status}</Badge> },
    ...(isManager
      ? [
          {
            key: 'actions',
            header: 'Manager Action',
            render: (t: TimesheetRecord) => (
              t.status === 'Submitted' ? (
                <div style={{ display: 'flex', gap: '0.4rem' }}>
                  <Button variant="success" size="sm" onClick={() => handleApprove(t.timesheet_id)}>
                    Approve
                  </Button>
                  <Button variant="danger" size="sm" onClick={() => handleReject(t.timesheet_id)}>
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
          <h1 style={{ margin: 0 }}>Timesheet Management</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
            Daily activity tracking, billable project allocation, and manager sign-offs.
          </p>
        </div>

        <Button variant="primary" icon={<Plus size={16} />} onClick={() => setIsModalOpen(true)}>
          Log Work Hours
        </Button>
      </div>

      {/* Filter toolbar */}
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
            <option value="">All Timesheets</option>
            <option value="Submitted">Pending Review</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
          </Input>
        </div>
      </Card>

      {/* Timesheets Table */}
      <Card title={`Timesheet Entries (${total.toLocaleString()})`}>
        <Table
          columns={columns}
          data={timesheets}
          isLoading={isLoading}
          page={page}
          totalPages={totalPages}
          totalRecords={total}
          pageSize={10}
          onPageChange={(p) => setPage(p)}
          emptyTitle="No timesheets found"
        />
      </Card>

      {/* Log Hours Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Submit Timesheet Entry"
        footer={
          <>
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSubmitTimesheet} isLoading={isSubmitting}>
              Submit Timesheet
            </Button>
          </>
        }
      >
        <form onSubmit={handleSubmitTimesheet} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Input
            as="select"
            label="Assigned Project *"
            value={tsForm.project_id}
            onChange={(e) => setTsForm({ ...tsForm, project_id: e.target.value })}
          >
            {projects.map((p) => (
              <option key={p.project_id} value={p.project_id}>
                {p.project_name} ({p.project_id})
              </option>
            ))}
          </Input>

          <Input
            type="date"
            label="Work Date *"
            value={tsForm.date}
            onChange={(e) => setTsForm({ ...tsForm, date: e.target.value })}
            required
          />

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
            <Input
              type="number"
              label="Total Hours *"
              step="0.5"
              value={tsForm.hours_worked}
              onChange={(e) => setTsForm({ ...tsForm, hours_worked: Number(e.target.value) })}
              required
            />
            <Input
              type="number"
              label="Billable Hours *"
              step="0.5"
              value={tsForm.billable_hours}
              onChange={(e) => setTsForm({ ...tsForm, billable_hours: Number(e.target.value) })}
              required
            />
            <Input
              type="number"
              label="Non-Billable *"
              step="0.5"
              value={tsForm.non_billable_hours}
              onChange={(e) => setTsForm({ ...tsForm, non_billable_hours: Number(e.target.value) })}
              required
            />
          </div>

          <Input
            as="textarea"
            label="Task Description *"
            placeholder="Describe completed deliverables, bugfixes, or features worked on..."
            value={tsForm.task_description}
            onChange={(e) => setTsForm({ ...tsForm, task_description: e.target.value })}
            rows={3}
            required
          />
        </form>
      </Modal>
    </div>
  );
};
