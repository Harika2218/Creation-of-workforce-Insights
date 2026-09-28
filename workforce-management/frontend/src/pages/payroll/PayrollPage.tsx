import React, { useState, useEffect, useCallback } from 'react';
import { Banknote, Download, Eye, FileText, CheckCircle, Printer } from 'lucide-react';
import { Card } from '../../components/common/Card';
import { StatCard } from '../../components/common/StatCard';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Table, Column } from '../../components/common/Table';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { payrollService } from '../../services/payrollService';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { PayrollRecord, PayrollSummary } from '../../types';

export const PayrollPage: React.FC = () => {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [summary, setSummary] = useState<PayrollSummary | null>(null);
  const [records, setRecords] = useState<PayrollRecord[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [page, setPage] = useState<number>(1);
  const [selectedMonth, setSelectedMonth] = useState<string>('2026-03');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Payslip Modal
  const [selectedPayslip, setSelectedPayslip] = useState<PayrollRecord | null>(null);

  const fetchPayroll = useCallback(async () => {
    try {
      setIsLoading(true);
      if (user?.role === 'EMPLOYEE') {
        const empRecords = await payrollService.getEmployeePayroll(user.employee_id);
        setRecords(empRecords);
        setTotal(empRecords.length);
        setTotalPages(1);
      } else {
        const [sum, recs] = await Promise.all([
          payrollService.getPayrollSummary(selectedMonth || undefined),
          payrollService.getPayrollRecords({
            page,
            page_size: 10,
            month: selectedMonth || undefined,
          }),
        ]);
        setSummary(sum);
        setRecords(recs.items);
        setTotal(recs.total);
        setTotalPages(recs.total_pages);
      }
    } catch (err) {
      console.error('Error fetching payroll:', err);
    } finally {
      setIsLoading(false);
    }
  }, [user?.role, user?.employee_id, selectedMonth, page]);

  useEffect(() => {
    fetchPayroll();
  }, [fetchPayroll]);

  const formatINR = (val: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2,
    }).format(val);
  };

  const isHR = user?.role === 'ADMIN' || user?.role === 'HR';

  const columns: Column<PayrollRecord>[] = [
    { key: 'payroll_id', header: 'Payslip Ref', width: '130px' },
    ...(isHR
      ? [
          {
            key: 'employee_id',
            header: 'Employee ID',
            render: (p: PayrollRecord) => <strong style={{ color: 'var(--primary)' }}>{p.employee_id}</strong>,
          },
        ]
      : []),
    { key: 'payroll_month', header: 'Month Period' },
    { key: 'base_salary', header: 'Base Pay', render: (p) => formatINR(p.base_salary) },
    { key: 'gross_salary', header: 'Gross Salary', render: (p) => formatINR(p.gross_salary) },
    { key: 'net_salary', header: 'Net Salary', render: (p) => <strong style={{ color: 'var(--success)' }}>{formatINR(p.net_salary)}</strong> },
    { key: 'payment_status', header: 'Status', render: (p) => <Badge variant={p.payment_status}>{p.payment_status}</Badge> },
    {
      key: 'actions',
      header: 'Payslip',
      align: 'right',
      render: (p) => (
        <Button variant="ghost" size="sm" icon={<Eye size={14} />} onClick={() => setSelectedPayslip(p)}>
          View Statement
        </Button>
      ),
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Title */}
      <div>
        <h1 style={{ margin: 0 }}>Payroll & Compensation</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
          {isHR
            ? 'Enterprise payroll cycle management and company disbursement totals.'
            : 'Your authorized salary statements, earnings breakdown, and payslips.'}
        </p>
      </div>

      {/* HR Summary Cards */}
      {isHR && summary && (
        <div className="grid-4">
          <StatCard
            label="Total Net Disbursement"
            value={formatINR(summary.total_net_disbursement)}
            subtext={<span>Net salaries paid</span>}
            icon={<Banknote size={24} />}
            iconBg="rgba(16, 185, 129, 0.15)"
            iconColor="var(--success)"
          />

          <StatCard
            label="Total Gross Compensation"
            value={formatINR(summary.total_gross_disbursement)}
            subtext={<span>Pre-deduction run</span>}
            icon={<Banknote size={24} />}
            iconBg="rgba(99, 102, 241, 0.15)"
            iconColor="var(--primary)"
          />

          <StatCard
            label="Statutory Deductions"
            value={formatINR(summary.total_deductions)}
            subtext={<span>PF & income tax withheld</span>}
            icon={<Banknote size={24} />}
            iconBg="rgba(245, 158, 11, 0.15)"
            iconColor="var(--warning)"
          />

          <StatCard
            label="Eligible Employees"
            value={summary.total_employees}
            subtext={<span>Avg: {formatINR(summary.avg_net_salary)}</span>}
            icon={<Banknote size={24} />}
            iconBg="rgba(168, 85, 247, 0.15)"
            iconColor="var(--purple)"
          />
        </div>
      )}

      {/* Filter toolbar (HR) */}
      {isHR && (
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', maxWidth: '300px' }}>
            <Input
              type="month"
              value={selectedMonth}
              onChange={(e) => {
                setSelectedMonth(e.target.value);
                setPage(1);
              }}
            />
          </div>
        </Card>
      )}

      {/* Records Table */}
      <Card title={isHR ? `Payroll Register (${total.toLocaleString()})` : 'My Salary Statements'}>
        <Table
          columns={columns}
          data={records}
          isLoading={isLoading}
          page={isHR ? page : undefined}
          totalPages={isHR ? totalPages : undefined}
          totalRecords={isHR ? total : undefined}
          pageSize={10}
          onPageChange={(p) => setPage(p)}
          emptyTitle="No payroll records found"
        />
      </Card>

      {/* Detailed Payslip Statement Modal */}
      {selectedPayslip && (
        <Modal
          isOpen={!!selectedPayslip}
          onClose={() => setSelectedPayslip(null)}
          title={`Official Payslip Statement - ${selectedPayslip.payroll_month}`}
          maxWidth="640px"
          footer={
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                * PDF download service is pending backend integration. You can print this statement.
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <Button variant="secondary" icon={<Printer size={16} />} onClick={() => window.print()}>
                  Print
                </Button>
                <Button variant="ghost" onClick={() => setSelectedPayslip(null)}>
                  Close
                </Button>
              </div>
            </div>
          }
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Header info */}
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
              <div>
                <h3 style={{ margin: 0 }}>HRvantage Technologies Ltd</h3>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Corporate Payroll Division</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: 700, color: 'var(--primary)' }}>{selectedPayslip.payroll_id}</div>
                <Badge variant={selectedPayslip.payment_status}>{selectedPayslip.payment_status}</Badge>
              </div>
            </div>

            {/* Employee metadata */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.85rem' }}>
              <div>
                <span style={{ color: 'var(--text-dim)' }}>Employee ID:</span>{' '}
                <strong style={{ color: '#FFF' }}>{selectedPayslip.employee_id}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)' }}>Pay Period:</span>{' '}
                <strong style={{ color: '#FFF' }}>{selectedPayslip.payroll_month}</strong>
              </div>
            </div>

            {/* Earnings & Deductions Breakdown */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              {/* Earnings column */}
              <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                <h4 style={{ color: 'var(--success)', marginBottom: '0.75rem', fontSize: '0.9rem' }}>Earnings</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.82rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Basic Salary</span>
                    <span>{formatINR(selectedPayslip.base_salary)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>House Rent (HRA)</span>
                    <span>{formatINR(selectedPayslip.hra)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Special Allowances</span>
                    <span>{formatINR(selectedPayslip.special_allowances)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Overtime Pay</span>
                    <span>{formatINR(selectedPayslip.overtime_pay)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Bonuses / Incentives</span>
                    <span>{formatINR(selectedPayslip.bonuses)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.5rem', fontWeight: 700, color: '#FFF' }}>
                    <span>Gross Earnings</span>
                    <span>{formatINR(selectedPayslip.gross_salary)}</span>
                  </div>
                </div>
              </div>

              {/* Deductions column */}
              <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                <h4 style={{ color: 'var(--danger)', marginBottom: '0.75rem', fontSize: '0.9rem' }}>Deductions</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.82rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Provident Fund (PF)</span>
                    <span>{formatINR(selectedPayslip.pf_deduction)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Income Tax (TDS)</span>
                    <span>{formatINR(selectedPayslip.tax_deduction)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Other Deductions</span>
                    <span>{formatINR(selectedPayslip.other_deductions)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.5rem', fontWeight: 700, color: '#FFF' }}>
                    <span>Total Deductions</span>
                    <span>{formatINR(selectedPayslip.pf_deduction + selectedPayslip.tax_deduction + selectedPayslip.other_deductions)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Net Pay Banner */}
            <div
              style={{
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                borderRadius: 'var(--radius-md)',
                padding: '1rem 1.25rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Net Take-Home Pay</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--success)' }}>
                  {formatINR(selectedPayslip.net_salary)}
                </div>
              </div>
              <Badge variant="success">Disbursed to Bank Account</Badge>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
