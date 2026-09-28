import React, { useState, useEffect } from 'react';
import { CalendarDays, Plus, Trash2, MapPin } from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Table, Column } from '../../components/common/Table';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { holidayService } from '../../services/holidayService';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Holiday } from '../../types';

export const HolidaysPage: React.FC = () => {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [form, setForm] = useState({
    holiday_id: '',
    holiday_name: '',
    date: new Date().toISOString().split('T')[0],
    type: 'National Holiday',
  });

  const fetchHolidays = async () => {
    try {
      setIsLoading(true);
      const data = await holidayService.getHolidays();
      setHolidays(data);
    } catch (err) {
      console.error('Error fetching holidays:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHolidays();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      await holidayService.createHoliday(form);
      showToast('Holiday added to corporate calendar!', 'success');
      setIsModalOpen(false);
      fetchHolidays();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to add holiday.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Delete this holiday entry?')) return;
    try {
      await holidayService.deleteHoliday(id);
      showToast('Holiday removed.', 'info');
      fetchHolidays();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to delete holiday.', 'error');
    }
  };

  const canManage = user?.role === 'ADMIN' || user?.role === 'HR';

  const columns: Column<Holiday>[] = [
    { key: 'date', header: 'Observance Date', width: '150px', render: (h) => <strong style={{ color: '#FFF' }}>{h.date}</strong> },
    { key: 'holiday_name', header: 'Holiday Name' },
    { key: 'type', header: 'Classification', render: (h) => <Badge variant="purple">{h.type}</Badge> },
    { key: 'location_id', header: 'Applicable Hubs', render: (h) => h.location_id || 'All Locations' },
    ...(canManage
      ? [
          {
            key: 'actions',
            header: 'Action',
            align: 'right' as const,
            render: (h: Holiday) => (
              <Button variant="danger" size="sm" icon={<Trash2 size={14} />} onClick={() => handleDelete(h.holiday_id)}>
                Remove
              </Button>
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
          <h1 style={{ margin: 0 }}>Official Holiday Calendar</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
            Recognized national, regional, and company holidays for calendar year 2026.
          </p>
        </div>

        {canManage && (
          <Button variant="primary" icon={<Plus size={16} />} onClick={() => setIsModalOpen(true)}>
            Add Holiday
          </Button>
        )}
      </div>

      <Card title={`Corporate Holidays (${holidays.length})`}>
        <Table columns={columns} data={holidays} isLoading={isLoading} emptyTitle="No holidays registered" />
      </Card>

      {/* Add Holiday Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Schedule Corporate Holiday"
        footer={
          <>
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleCreate} isLoading={isSubmitting}>
              Add to Calendar
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Input
            label="Holiday ID *"
            placeholder="HOL020"
            value={form.holiday_id}
            onChange={(e) => setForm({ ...form, holiday_id: e.target.value })}
            required
          />

          <Input
            label="Holiday Name *"
            placeholder="Diwali Festive Holiday"
            value={form.holiday_name}
            onChange={(e) => setForm({ ...form, holiday_name: e.target.value })}
            required
          />

          <Input
            type="date"
            label="Observance Date *"
            value={form.date}
            onChange={(e) => setForm({ ...form, date: e.target.value })}
            required
          />

          <Input
            as="select"
            label="Holiday Type *"
            value={form.type}
            onChange={(e) => setForm({ ...form, type: e.target.value })}
          >
            <option value="National Holiday">National Holiday</option>
            <option value="Festival Holiday">Festival Holiday</option>
            <option value="Corporate Holiday">Corporate Holiday</option>
          </Input>
        </form>
      </Modal>
    </div>
  );
};
