import React, { useState, useEffect } from 'react';
import { Briefcase, Plus, Calendar, DollarSign } from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Table, Column } from '../../components/common/Table';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { projectService } from '../../services/projectService';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Project } from '../../types';

export const ProjectsPage: React.FC = () => {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [form, setForm] = useState({
    project_id: '',
    project_name: '',
    client_name: '',
    start_date: new Date().toISOString().split('T')[0],
    manager_id: 'EMP002',
    budget_inr: 5000000,
    status: 'Active',
  });

  const fetchProjects = async () => {
    try {
      setIsLoading(true);
      const data = await projectService.getProjects();
      setProjects(data);
    } catch (err) {
      console.error('Error fetching projects:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      await projectService.createProject(form as any);
      showToast('Project registered successfully!', 'success');
      setIsModalOpen(false);
      fetchProjects();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to create project.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const canManage = user?.role === 'ADMIN' || user?.role === 'HR';

  const formatINR = (val: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(val);
  };

  const columns: Column<Project>[] = [
    { key: 'project_id', header: 'Project ID', width: '120px', render: (p) => <strong style={{ color: 'var(--primary)' }}>{p.project_id}</strong> },
    { key: 'project_name', header: 'Project Title', render: (p) => <strong style={{ color: '#FFF' }}>{p.project_name}</strong> },
    { key: 'client_name', header: 'Client' },
    { key: 'manager_id', header: 'Project Manager' },
    { key: 'budget_inr', header: 'Total Budget', render: (p) => formatINR(p.budget_inr) },
    { key: 'start_date', header: 'Kickoff Date' },
    { key: 'status', header: 'Status', render: (p) => <Badge variant={p.status}>{p.status}</Badge> },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ margin: 0 }}>Enterprise Projects</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
            Client project portfolio, delivery milestones, and allocation budgets.
          </p>
        </div>

        {canManage && (
          <Button variant="primary" icon={<Plus size={16} />} onClick={() => setIsModalOpen(true)}>
            Register Project
          </Button>
        )}
      </div>

      <Card title={`Active Projects Portfolio (${projects.length})`}>
        <Table columns={columns} data={projects} isLoading={isLoading} emptyTitle="No projects registered" />
      </Card>

      {/* Register Project Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Register New Client Project"
        footer={
          <>
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleCreateProject} isLoading={isSubmitting}>
              Save Project
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreateProject} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <Input
            label="Project ID *"
            placeholder="PRJ010"
            value={form.project_id}
            onChange={(e) => setForm({ ...form, project_id: e.target.value })}
            required
          />

          <Input
            label="Project Name *"
            placeholder="Cloud Modernization Initiative"
            value={form.project_name}
            onChange={(e) => setForm({ ...form, project_name: e.target.value })}
            required
          />

          <Input
            label="Client Name *"
            placeholder="Global Financial Corp"
            value={form.client_name}
            onChange={(e) => setForm({ ...form, client_name: e.target.value })}
            required
          />

          <Input
            label="Lead Project Manager ID *"
            placeholder="EMP002"
            value={form.manager_id}
            onChange={(e) => setForm({ ...form, manager_id: e.target.value })}
            required
          />

          <Input
            type="date"
            label="Kickoff Date *"
            value={form.start_date}
            onChange={(e) => setForm({ ...form, start_date: e.target.value })}
            required
          />

          <Input
            type="number"
            label="Total Budget (INR) *"
            value={form.budget_inr}
            onChange={(e) => setForm({ ...form, budget_inr: Number(e.target.value) })}
            required
          />
        </form>
      </Modal>
    </div>
  );
};
