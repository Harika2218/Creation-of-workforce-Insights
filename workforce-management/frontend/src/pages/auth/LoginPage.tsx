import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Lock, Mail, AlertCircle, ArrowRight, UserCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { showToast } = useToast();

  const [email, setEmail] = useState<string>('hr@demo.com');
  const [password, setPassword] = useState<string>('Demo@2026');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const demoAccounts = [
    { label: 'Admin', email: 'admin@demo.com', role: 'ADMIN', color: 'var(--danger)' },
    { label: 'HR Lead', email: 'hr@demo.com', role: 'HR', color: 'var(--purple)' },
    { label: 'Manager', email: 'manager@demo.com', role: 'MANAGER', color: 'var(--info)' },
    { label: 'Employee', email: 'employee@demo.com', role: 'EMPLOYEE', color: 'var(--success)' },
  ];

  const handleSelectDemo = (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword('Demo@2026');
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please provide both email and password.');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      const user = await login(email, password);
      showToast(`Welcome back, ${user.name}!`, 'success');

      // Smart role-based redirect
      if (user.role === 'ADMIN' || user.role === 'HR') {
        navigate('/dashboard');
      } else if (user.role === 'MANAGER') {
        navigate('/manager/dashboard');
      } else {
        navigate('/employee/dashboard');
      }
    } catch (err: any) {
      let msg = err.response?.data?.detail;
      if (!msg) {
        if (!err.response || err.code === 'ERR_NETWORK') {
          const targetUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
          msg = `Cannot connect to backend API server (${targetUrl}). The backend is offline or unreachable.`;
        } else {
          msg = 'Invalid email or password. Please verify your credentials.';
        }
      }
      setError(msg);
      showToast(msg, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        width: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'radial-gradient(ellipse at 50% 20%, rgba(99, 102, 241, 0.15) 0%, #0B0F19 75%)',
        padding: '1.5rem',
      }}
    >
      <div
        className="glass-card"
        style={{
          width: '100%',
          maxWidth: '460px',
          padding: '2.5rem 2rem',
          borderRadius: 'var(--radius-xl)',
          boxShadow: 'var(--shadow-lg), 0 0 40px rgba(99, 102, 241, 0.15)',
        }}
      >
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div
            style={{
              width: '56px',
              height: '56px',
              borderRadius: 'var(--radius-lg)',
              background: 'var(--gradient-primary)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF',
              boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)',
              marginBottom: '1rem',
            }}
          >
            <ShieldCheck size={32} />
          </div>
          <h1 style={{ fontSize: '1.85rem', marginBottom: '0.35rem' }}>HRvantage</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            AI-Powered Workforce Management Automation System
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div
            style={{
              backgroundColor: 'var(--danger-bg)',
              border: '1px solid var(--danger-border)',
              borderRadius: 'var(--radius-md)',
              padding: '0.75rem 1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              color: 'var(--danger)',
              fontSize: '0.85rem',
              marginBottom: '1.25rem',
            }}
          >
            <AlertCircle size={18} style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          <Input
            label="Corporate Email"
            type="email"
            placeholder="user@demo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            icon={<Mail size={16} />}
            required
          />

          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            icon={<Lock size={16} />}
            required
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={isLoading}
            style={{ width: '100%', marginTop: '0.5rem' }}
            icon={<ArrowRight size={18} />}
          >
            Sign In to Enterprise Portal
          </Button>
        </form>

        {/* 1-Click Demo Accounts Switcher */}
        <div style={{ marginTop: '2rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '1.5rem' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '0.75rem',
              fontSize: '0.78rem',
              color: 'var(--text-dim)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              fontWeight: 700,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <UserCheck size={14} />
              <span>1-Click Demo Accounts</span>
            </div>
            <span style={{ textTransform: 'none', letterSpacing: 'normal' }}>
              Pass: <strong style={{ color: 'var(--primary-light, #818cf8)' }}>Demo@2026</strong>
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' }}>
            {demoAccounts.map((d) => (
              <button
                key={d.role}
                type="button"
                onClick={() => handleSelectDemo(d.email)}
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: email === d.email ? '1px solid var(--primary)' : 'var(--border-glass)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '0.5rem 0.6rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.45rem',
                  color: email === d.email ? '#FFFFFF' : 'var(--text-muted)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all var(--transition-fast)',
                }}
              >
                <span
                  style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: d.color,
                  }}
                />
                <div style={{ fontSize: '0.78rem', lineHeight: 1.2 }}>
                  <div style={{ fontWeight: 600 }}>{d.label}</div>
                  <div style={{ color: 'var(--text-dim)', fontSize: '0.7rem' }}>{d.role}</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
