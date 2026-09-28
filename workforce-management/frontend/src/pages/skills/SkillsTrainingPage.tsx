import React, { useState, useEffect } from 'react';
import { BookOpen, Award, CheckCircle, Clock } from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { Table, Column } from '../../components/common/Table';
import { skillService } from '../../services/skillService';
import { SkillItem, TrainingProgram, TrainingRecord } from '../../types';

export const SkillsTrainingPage: React.FC = () => {
  const [skills, setSkills] = useState<SkillItem[]>([]);
  const [programs, setPrograms] = useState<TrainingProgram[]>([]);
  const [records, setRecords] = useState<TrainingRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [sk, prg, rec] = await Promise.all([
          skillService.getSkills(),
          skillService.getTrainingPrograms(),
          skillService.getTrainingRecords(),
        ]);
        setSkills(sk);
        setPrograms(prg);
        setRecords(rec);
      } catch (err) {
        console.error('Error fetching skills/training:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const trainingColumns: Column<TrainingRecord>[] = [
    { key: 'enrollment_id', header: 'Enrollment ID', width: '130px' },
    { key: 'employee_id', header: 'Employee', render: (t) => <strong style={{ color: 'var(--primary)' }}>{t.employee_id}</strong> },
    { key: 'program_title', header: 'Course Title' },
    { key: 'score', header: 'Score', render: (t) => (t.score ? `${t.score}%` : 'In Progress') },
    { key: 'status', header: 'Status', render: (t) => <Badge variant={t.status}>{t.status}</Badge> },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Title */}
      <div>
        <h1 style={{ margin: 0 }}>Skills Taxonomy & Training Programs</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.2rem' }}>
          Workforce technical capabilities, certifications, and upskilling pathways.
        </p>
      </div>

      {/* Skills Catalog Grid */}
      <Card title={`Enterprise Skills Catalog (${skills.length})`}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '1rem', marginTop: '0.5rem' }}>
          {skills.map((s) => (
            <div
              key={s.skill_id}
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '1rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 600, color: '#FFF' }}>{s.name}</span>
                <Badge variant="purple">{s.category}</Badge>
              </div>
              <p style={{ color: 'var(--text-dim)', fontSize: '0.78rem', marginTop: '0.4rem', lineHeight: 1.4 }}>
                {s.description}
              </p>
            </div>
          ))}
        </div>
      </Card>

      {/* Training Programs Catalog */}
      <Card title={`Active Upskilling Programs (${programs.length})`}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem', marginTop: '0.5rem' }}>
          {programs.map((p) => (
            <div
              key={p.program_id}
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Badge variant="info">{p.category}</Badge>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <Clock size={12} /> {p.duration_hours} hrs
                  </span>
                </div>
                <h4 style={{ margin: '0.6rem 0 0.2rem 0' }}>{p.title}</h4>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Provider: {p.provider}</div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '0.5rem' }}>
                  {p.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Workforce Training Records Table */}
      <Card title={`Employee Enrollment Records (${records.length})`}>
        <Table columns={trainingColumns} data={records} isLoading={isLoading} emptyTitle="No enrollments recorded" />
      </Card>
    </div>
  );
};
