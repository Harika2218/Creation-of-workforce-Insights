import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Users, Search, Plus, Filter, UserX, Eye, Edit } from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { employeeService, EmployeeFilters } from '../../services/employeeService';
import { departmentService } from '../../services/departmentService';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Employee, Department } from '../../types';

export const EmployeeListPage: React.FC = () => {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [employees, setEmployees] = useState<Employee[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Filters
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(10);
  const [search, setSearch] = useState<string>('');
  const [deptFilter, setDeptFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [roleFilter, setRoleFilter] = useState<string>('');

  // Add Employee Modal
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [formData, setFormData] = useState({
    employee_id: '',
    name: '',
    email: '',
    phone: '+91 98765 43210',
    department_id: 'DEP001',
    designation: 'Software Engineer',
    role: 'EMPLOYEE',
    manager_id: 'EMP002',
    location_id: 'LOC001',
    date_of_joining: new Date().toISOString().split('T')[0],
    employment_type: 'Full-Time',
    employment_status: 'Active',
    base_salary: 850000,
  });

  const fetchEmployees = useCallback(async () => {
    try {
      setIsLoading(true);
      const params: EmployeeFilters = {
        page,
        page_size: pageSize,
        search: search || undefined,
        department_id: deptFilter || undefined,
        employment_status: statusFilter || undefined,
        role: roleFilter || undefined,
      };
      const res = await employeeService.getEmployees(params);
      setEmployees(res.items);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (err) {
      console.error('Error fetching employees:', err);
      showToast('Failed to load employees list.', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, search, deptFilter, statusFilter, roleFilter, showToast]);

  useEffect(() => {
    fetchEmployees();
  }, [fetchEmployees]);

  useEffect(() => {
    const fetchDepts = async () => {
      try {
        const d = await departmentService.getDepartments();
        setDepartments(d);
      } catch {
        // Silently handled
      }
    };
    fetchDepts();
  }, []);

  const handleDeactivate = async (employeeId: string) => {
    if (!window.confirm(`Are you sure you want to deactivate employee ${employeeId}?`)) return;
    try {
      await employeeService.deactivateEmployee(employeeId);
      showToast(`Employee ${employeeId} deactivated.`, 'success');
      fetchEmployees();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Deactivation failed.', 'error');
    }
  };

  const handleCreateEmployee = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      await employeeService.createEmployee(formData as any);
      showToast(`Employee ${formData.employee_id} created successfully!`, 'success');
      setIsModalOpen(false);
      fetchEmployees();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to create employee.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const canManage = user?.role === 'ADMIN' || user?.role === 'HR';

  const columns: Column<Employee>[] = [
    {
      key: 'employee_id',
      header: 'ID',
      width: '100px',
      render: (emp) => (
        <Link to={`/employees/${emp.employee_id}`} style={{ fontWeight: 700, color: 'var(--primary)' }}>
          {emp.employee_id}
        </Link>
      ),
    },
    {
      key: 'name',
      header: 'Employee Name & Email',
      render: (emp) => (
        <div>
          <div style={{ fontWeight: 600, color: '#FFFFFF' }}>{emp.name}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>{emp.email}</div>
        </div>
      ),
    },
    {
      key: 'department_name',
      header: 'Department',
      render: (emp) => <span>{emp.department_name || emp.department_id}</span>,
    },
    {
      key: 'designation',
      header: 'Designation',
    },
    {
      key: 'role',
      header: 'Role',
      render: (emp) => (
        <Badge variant={emp.role === 'ADMIN' ? 'danger' : emp.role === 'HR' ? 'purple' : emp.role === 'MANAGER' ? 'info' : 'neutral'}>
          {emp.role}
        </Badge>
      ),
    },
    {
      key: 'location_name',
      header: 'Location',
      render: (emp) => <span>{emp.location_name || emp.location_id}</span>,
    },
    {
      key: 'employment_status',
      header: 'Status',
      render: (emp) => <Badge variant={emp.employment_status}>{emp.employment_status}</Badge>,
    },
    {
      key: 'actions',
      header: 'Actions',
      align: 'right',
      render: (emp) => (
        <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'flex-end' }}>
          <Link to={`/employees/${emp.employee_id}`}>
            <Button variant="ghost" size="sm" icon={<Eye size={14} />}>
              Profile
            </Button>
          </Link>
          {canManage && emp.employment_status !== 'Deactivated' && (
            <Button
              variant="danger"
              size="sm"
              icon={<UserX size={14} />}
              onClick={() => handleDeactivate(emp.employee_id)}
            >
              Deactivate
            </Button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ margin: 0 }}>Employee Directory</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
            Comprehensive management of {total} enterprise employees.
          </p>
        </div>

        {canManage && (
          <Button variant="primary" icon={<Plus size={16} />} onClick={() => setIsModalOpen(true)}>
            Onboard Employee
          </Button>
        )}
      </div>

      {/* Filter Toolbar */}
      <Card>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div className="search-wrapper">
            <Search size={16} className="search-icon" />
            <input
              type="text"
              className="form-control search-input"
              placeholder="Search by name, ID, or email..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <Input
            as="select"
            value={deptFilter}
            onChange={(e) => {
              setDeptFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All Departments</option>
            {departments.map((d) => (
              <option key={d.department_id} value={d.department_id}>
                {d.department_name}
              </option>
            ))}
          </Input>

          <Input
            as="select"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All Statuses</option>
            <option value="Active">Active</option>
            <option value="Notice Period">Notice Period</option>
            <option value="Deactivated">Deactivated</option>
          </Input>

          <Input
            as="select"
            value={roleFilter}
            onChange={(e) => {
              setRoleFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All Roles</option>
            <option value="ADMIN">ADMIN</option>
            <option value="HR">HR</option>
            <option value="MANAGER">MANAGER</option>
            <option value="EMPLOYEE">EMPLOYEE</option>
          </Input>
        </div>
      </Card>

      {/* Employee Data Table with Mobile Responsive Card Grid */}
      <Card>
        <div className="desktop-table-view">
          <Table
            columns={columns}
            data={employees}
            isLoading={isLoading}
            page={page}
            totalPages={totalPages}
            totalRecords={total}
            pageSize={pageSize}
            onPageChange={(p) => setPage(p)}
            emptyTitle="No employees matched"
            emptyDescription="Try adjusting your search criteria or filters."
          />
        </div>

        <div className="mobile-card-grid">
          {isLoading ? (
            <div style={{ padding: '1rem', color: 'var(--text-muted)', textAlign: 'center' }}>
              Loading workforce directory...
            </div>
          ) : employees.length === 0 ? (
            <div style={{ padding: '2rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              No employees matched current filter.
            </div>
          ) : (
            employees.map((emp) => (
              <div
                key={emp.employee_id}
                style={{
                  padding: '1rem',
                  backgroundColor: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.6rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <strong style={{ color: '#FFFFFF', fontSize: '0.95rem' }}>{emp.name}</strong>
                    <div style={{ fontSize: '0.75rem', color: 'var(--primary)', fontWeight: 600 }}>
                      {emp.employee_id} • {emp.designation}
                    </div>
                  </div>
                  <Badge variant={emp.employment_status === 'Active' ? 'success' : 'neutral'}>
                    {emp.employment_status}
                  </Badge>
                </div>

                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', display: 'flex', gap: '1rem' }}>
                  <span>Dept: {emp.department_name || emp.department_id}</span>
                  <span>Role: {emp.role}</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '0.4rem', borderTop: '1px solid var(--border-subtle)' }}>
                  <Link to={`/employees/${emp.employee_id}`}>
                    <Button variant="ghost" size="sm" icon={<Eye size={14} />}>
                      Profile
                    </Button>
                  </Link>
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

      {/* Add Employee Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Onboard New Employee"
        maxWidth="620px"
        footer={
          <>
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleCreateEmployee}
              isLoading={isSubmitting}
            >
              Submit Onboarding
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreateEmployee} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <Input
            label="Employee ID *"
            placeholder="EMP201"
            value={formData.employee_id}
            onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
            required
          />

          <Input
            label="Full Name *"
            placeholder="Jane Doe"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />

          <Input
            label="Corporate Email *"
            type="email"
            placeholder="jane.doe@company.com"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />

          <Input
            label="Contact Phone *"
            placeholder="+91 98765 43210"
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            required
          />

          <Input
            as="select"
            label="Department *"
            value={formData.department_id}
            onChange={(e) => setFormData({ ...formData, department_id: e.target.value })}
          >
            {departments.map((d) => (
              <option key={d.department_id} value={d.department_id}>
                {d.department_name}
              </option>
            ))}
          </Input>

          <Input
            label="Designation *"
            value={formData.designation}
            onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
            required
          />

          <Input
            as="select"
            label="System Role *"
            value={formData.role}
            onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
          >
            <option value="EMPLOYEE">EMPLOYEE</option>
            <option value="MANAGER">MANAGER</option>
            <option value="HR">HR</option>
            <option value="ADMIN">ADMIN</option>
          </Input>

          <Input
            label="Base Annual Salary (INR) *"
            type="number"
            value={formData.base_salary}
            onChange={(e) => setFormData({ ...formData, base_salary: Number(e.target.value) })}
            required
          />
        </form>
      </Modal>
    </div>
  );
};
