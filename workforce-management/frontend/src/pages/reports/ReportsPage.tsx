import React, { useState, useEffect } from 'react';
import { BarChart3, Download, FileSpreadsheet, Clock, Calendar, Banknote, Award } from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Table, Column } from '../../components/common/Table';
import { LoadingSkeleton } from '../../components/common/LoadingSkeleton';
import { reportService } from '../../services/reportService';
import { useToast } from '../../context/ToastContext';

export const ReportsPage: React.FC = () => {
  const { showToast } = useToast();
  const [activeReport, setActiveReport] = useState<'attendance' | 'overtime' | 'leave' | 'payroll' | 'performance'>('attendance');
  const [reportData, setReportData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        setIsLoading(true);
        let res: any = null;
        if (activeReport === 'attendance') {
          res = await reportService.getAttendanceReport();
        } else if (activeReport === 'overtime') {
          res = await reportService.getOvertimeReport();
        } else if (activeReport === 'leave') {
          res = await reportService.getLeaveReport();
        } else if (activeReport === 'payroll') {
          res = await reportService.getPayrollReport();
        } else if (activeReport === 'performance') {
          res = await reportService.getDepartmentPerformanceReport();
        }
        setReportData(res);
      } catch (err) {
        console.error('Error fetching report:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchReport();
  }, [activeReport]);

  // Real client-side CSV generator and downloader
  const handleExportCSV = () => {
    if (!reportData) return;

    let rows: any[] = [];
    let filename = `hrvantage_${activeReport}_report_${new Date().toISOString().split('T')[0]}.csv`;

    if (Array.isArray(reportData)) {
      rows = reportData;
    } else if (reportData.items && Array.isArray(reportData.items)) {
      rows = reportData.items;
    } else if (typeof reportData === 'object') {
      // Convert key-value entries to rows
      rows = Object.entries(reportData).map(([k, v]) => ({
        metric: k,
        value: typeof v === 'object' ? JSON.stringify(v) : v,
      }));
    }

    if (rows.length === 0) {
      showToast('No data available to export.', 'warning');
      return;
    }

    const headers = Object.keys(rows[0]);
    const csvContent = [
      headers.join(','),
      ...rows.map((row) =>
        headers.map((h) => `"${String(row[h] ?? '').replace(/"/g, '""')}"`).join(',')
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    showToast(`Exported ${filename} successfully!`, 'success');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ margin: 0 }}>Workforce Intelligence & Reports</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
            Comprehensive analytics summaries with instant CSV data export.
          </p>
        </div>

        <Button variant="primary" icon={<Download size={16} />} onClick={handleExportCSV}>
          Export CSV
        </Button>
      </div>

      {/* Report Categories Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem', overflowX: 'auto' }}>
        {[
          { key: 'attendance', label: 'Attendance Breakdown', icon: <Clock size={16} /> },
          { key: 'overtime', label: 'Top Overtime Leaders', icon: <BarChart3 size={16} /> },
          { key: 'leave', label: 'Leave Utilization', icon: <Calendar size={16} /> },
          { key: 'payroll', label: 'Compensation Trends', icon: <Banknote size={16} /> },
          { key: 'performance', label: 'Department Scorecards', icon: <Award size={16} /> },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveReport(tab.key as any)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.65rem 1.2rem',
              borderRadius: 'var(--radius-md)',
              background: activeReport === tab.key ? 'rgba(99, 102, 241, 0.18)' : 'transparent',
              border: activeReport === tab.key ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid transparent',
              color: activeReport === tab.key ? '#FFFFFF' : 'var(--text-muted)',
              fontWeight: 600,
              fontSize: '0.88rem',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
            }}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Report Data Viewer */}
      <Card title={`${activeReport.toUpperCase()} Analytic Report`}>
        {isLoading ? (
          <LoadingSkeleton lines={6} height="36px" />
        ) : reportData ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div
              style={{
                backgroundColor: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '1.25rem',
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                color: '#FFF',
                maxHeight: '450px',
                overflowY: 'auto',
                whiteSpace: 'pre-wrap',
              }}
            >
              {JSON.stringify(reportData, null, 2)}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button variant="secondary" icon={<Download size={16} />} onClick={handleExportCSV}>
                Download Raw CSV
              </Button>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem 0', color: 'var(--text-dim)' }}>
            No report data available
          </div>
        )}
      </Card>
    </div>
  );
};
