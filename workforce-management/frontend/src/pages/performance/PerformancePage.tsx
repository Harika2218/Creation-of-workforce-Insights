import React, { useState, useEffect } from 'react';
import { Award, Plus, Star, TrendingUp, CheckCircle } from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Table, Column } from '../../components/common/Table';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { performanceService } from '../../services/performanceService';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { PerformanceReview } from '../../types';

export const PerformancePage: React.FC = () => {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [reviews, setReviews] = useState<PerformanceReview[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Appraisal Modal
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [form, setForm] = useState({
    employee_id: '',
    review_cycle: '2025-Annual',
    rating_score: 4.5,
    feedback: '',
  });

  const fetchReviews = async () => {
    try {
      setIsLoading(true);
      const data = await performanceService.getPerformanceReviews();
      setReviews(data);
    } catch (err) {
      console.error('Error fetching performance:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
  }, []);

  const handleSubmitAppraisal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      await performanceService.createPerformanceReview({
        employee_id: form.employee_id,
        review_cycle: form.review_cycle,
        rating_score: Number(form.rating_score),
        feedback: form.feedback,
      });
      showToast('Appraisal review submitted successfully!', 'success');
      setIsModalOpen(false);
      fetchReviews();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to submit appraisal.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const canReview = user?.role === 'ADMIN' || user?.role === 'HR' || user?.role === 'MANAGER';

  const columns: Column<PerformanceReview>[] = [
    { key: 'review_id', header: 'Review ID', width: '130px' },
    { key: 'employee_id', header: 'Employee ID', render: (r) => <strong style={{ color: 'var(--primary)' }}>{r.employee_id}</strong> },
    { key: 'review_cycle', header: 'Cycle' },
    {
      key: 'rating_score',
      header: 'Score',
      render: (r) => (
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontWeight: 700, color: 'var(--warning)' }}>
          <Star size={14} fill="var(--warning)" /> {r.rating_score} / 5.0
        </span>
      ),
    },
    { key: 'feedback', header: 'Executive Feedback' },
    { key: 'submission_date', header: 'Submitted' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ margin: 0 }}>Performance Appraisals & KPIs</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
            Workforce appraisal cycles, merit ratings, and continuous feedback records.
          </p>
        </div>

        {canReview && (
          <Button variant="primary" icon={<Plus size={16} />} onClick={() => setIsModalOpen(true)}>
            Submit Appraisal Review
          </Button>
        )}
      </div>

      {/* Reviews Table */}
      <Card title={`Appraisal Register (${reviews.length})`}>
        <Table columns={columns} data={reviews} isLoading={isLoading} emptyTitle="No performance reviews found" />
      </Card>

      {/* Appraisal Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Conduct Employee Appraisal Review"
        footer={
          <>
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSubmitAppraisal} isLoading={isSubmitting}>
              Submit Evaluation
            </Button>
          </>
        }
      >
        <form onSubmit={handleSubmitAppraisal} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Input
            label="Target Employee ID *"
            placeholder="EMP045"
            value={form.employee_id}
            onChange={(e) => setForm({ ...form, employee_id: e.target.value })}
            required
          />

          <Input
            label="Appraisal Cycle *"
            value={form.review_cycle}
            onChange={(e) => setForm({ ...form, review_cycle: e.target.value })}
            required
          />

          <Input
            type="number"
            step="0.1"
            min="1.0"
            max="5.0"
            label="Rating Score (1.0 to 5.0) *"
            value={form.rating_score}
            onChange={(e) => setForm({ ...form, rating_score: Number(e.target.value) })}
            required
          />

          <Input
            as="textarea"
            label="Qualitative Performance Feedback *"
            placeholder="Evaluate technical delivery, team collaboration, and goal attainment..."
            value={form.feedback}
            onChange={(e) => setForm({ ...form, feedback: e.target.value })}
            rows={4}
            required
          />
        </form>
      </Modal>
    </div>
  );
};
