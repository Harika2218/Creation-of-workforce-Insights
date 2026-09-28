import React, { useState, useEffect } from 'react';
import { CalendarDays, Clock, ArrowRightLeft, Plus, CheckCircle, XCircle } from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Table, Column } from '../../components/common/Table';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { ShiftCapacityScene } from '../../components/3d';
import { shiftService } from '../../services/shiftService';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { ShiftTemplate, ShiftSwapRequest } from '../../types';

export const ShiftsPage: React.FC = () => {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [shifts, setShifts] = useState<ShiftTemplate[]>([]);
  const [swaps, setSwaps] = useState<ShiftSwapRequest[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Swap Modal
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [swapForm, setSwapForm] = useState({
    target_employee_id: '',
    requestor_shift_date: new Date().toISOString().split('T')[0],
    target_shift_date: new Date().toISOString().split('T')[0],
    reason: '',
  });

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [sList, swList] = await Promise.all([
        shiftService.getShifts(),
        shiftService.getSwapRequests(),
      ]);
      setShifts(sList);
      setSwaps(swList);
    } catch (err) {
      console.error('Error fetching shift data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSwapAction = async (swapId: string, status: 'Approved' | 'Rejected') => {
    try {
      await shiftService.updateSwapRequest(swapId, status);
      showToast(`Shift swap request ${status.toLowerCase()}!`, 'success');
      fetchData();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to update swap request.', 'error');
    }
  };

  const handleSubmitSwap = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      await shiftService.submitSwapRequest(swapForm);
      showToast('Shift swap request submitted!', 'success');
      setIsModalOpen(false);
      fetchData();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to submit shift swap.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isManager = user?.role === 'ADMIN' || user?.role === 'HR' || user?.role === 'MANAGER';

  const swapColumns: Column<ShiftSwapRequest>[] = [
    { key: 'swap_id', header: 'Swap ID', width: '100px' },
    { key: 'requestor_employee_id', header: 'Requestor', render: (s) => <strong style={{ color: 'var(--primary)' }}>{s.requestor_employee_id}</strong> },
    { key: 'target_employee_id', header: 'Swap With' },
    { key: 'requestor_shift_date', header: 'Requestor Date' },
    { key: 'target_shift_date', header: 'Target Date' },
    { key: 'reason', header: 'Reason' },
    { key: 'status', header: 'Status', render: (s) => <Badge variant={s.status}>{s.status}</Badge> },
    ...(isManager
      ? [
          {
            key: 'actions',
            header: 'Action',
            render: (s: ShiftSwapRequest) => (
              s.status === 'Pending' ? (
                <div style={{ display: 'flex', gap: '0.4rem' }}>
                  <Button variant="success" size="sm" onClick={() => handleSwapAction(s.swap_id, 'Approved')}>
                    Approve
                  </Button>
                  <Button variant="danger" size="sm" onClick={() => handleSwapAction(s.swap_id, 'Rejected')}>
                    Reject
                  </Button>
                </div>
              ) : (
                <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>Closed</span>
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
          <h1 style={{ margin: 0 }}>Shift Rostering & Swaps</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
            Enterprise shift definitions, scheduling policies, and peer swap workflows.
          </p>
        </div>

        <Button variant="primary" icon={<ArrowRightLeft size={16} />} onClick={() => setIsModalOpen(true)}>
          Request Shift Swap
        </Button>
      </div>

      {/* 3D Shift Allocation Podiums */}
      <ShiftCapacityScene />

      {/* Shift Templates Grid */}
      <div className="grid-4">
        {shifts.map((s) => (
          <Card key={s.shift_id} title={s.shift_name} subtitle={`Code: ${s.shift_id}`}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#FFF' }}>
                <Clock size={16} style={{ color: 'var(--primary)' }} />
                <span style={{ fontWeight: 600 }}>{s.start_time} - {s.end_time}</span>
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Grace Period: {s.grace_period_mins} mins
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Break Duration: {s.break_duration_mins} mins
              </div>
              <Badge variant="active">Active Schedule</Badge>
            </div>
          </Card>
        ))}
      </div>

      {/* Shift Swap Requests Table */}
      <Card
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ArrowRightLeft size={18} style={{ color: 'var(--primary)' }} />
            <span>Shift Swap Requests Queue</span>
          </div>
        }
      >
        <Table columns={swapColumns} data={swaps} isLoading={isLoading} emptyTitle="No shift swap requests" />
      </Card>

      {/* Swap Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Submit Peer Shift Swap Request"
        footer={
          <>
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSubmitSwap} isLoading={isSubmitting}>
              Submit Request
            </Button>
          </>
        }
      >
        <form onSubmit={handleSubmitSwap} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Input
            label="Swap Partner Employee ID *"
            placeholder="EMP025"
            value={swapForm.target_employee_id}
            onChange={(e) => setSwapForm({ ...swapForm, target_employee_id: e.target.value })}
            required
          />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Input
              type="date"
              label="My Shift Date *"
              value={swapForm.requestor_shift_date}
              onChange={(e) => setSwapForm({ ...swapForm, requestor_shift_date: e.target.value })}
              required
            />
            <Input
              type="date"
              label="Target Shift Date *"
              value={swapForm.target_shift_date}
              onChange={(e) => setSwapForm({ ...swapForm, target_shift_date: e.target.value })}
              required
            />
          </div>

          <Input
            as="textarea"
            label="Reason for Swap *"
            placeholder="Explain the operational reason or personal requirement..."
            value={swapForm.reason}
            onChange={(e) => setSwapForm({ ...swapForm, reason: e.target.value })}
            rows={3}
            required
          />
        </form>
      </Modal>
    </div>
  );
};
