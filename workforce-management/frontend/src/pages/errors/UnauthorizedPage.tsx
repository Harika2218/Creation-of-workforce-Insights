import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { useAuth } from '../../context/AuthContext';

export const UnauthorizedPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '70vh',
        textAlign: 'center',
        padding: '2rem',
      }}
    >
      <div
        style={{
          width: '80px',
          height: '80px',
          borderRadius: '50%',
          background: 'rgba(245, 158, 11, 0.12)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--warning)',
          marginBottom: '1.5rem',
        }}
      >
        <ShieldAlert size={40} />
      </div>
      <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>403 - Access Denied</h1>
      <p style={{ color: 'var(--text-muted)', maxWidth: '460px', marginBottom: '1.5rem' }}>
        Your role (<strong>{user?.role || 'Guest'}</strong>) does not have sufficient permission to view this resource.
      </p>
      <Link to="/">
        <Button variant="primary" icon={<ArrowLeft size={18} />}>
          Return to Dashboard
        </Button>
      </Link>
    </div>
  );
};
