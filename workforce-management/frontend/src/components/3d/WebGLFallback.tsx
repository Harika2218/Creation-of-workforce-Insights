import React from 'react';

interface WebGLFallbackProps {
  title?: string;
  subtitle?: string;
  height?: string | number;
  icon?: React.ReactNode;
  children?: React.ReactNode;
}

export const WebGLFallback: React.FC<WebGLFallbackProps> = ({
  title = 'Interactive Visualization',
  subtitle = 'Hardware-accelerated 3D view is in standard rendering mode.',
  height = '320px',
  icon,
  children,
}) => {
  return (
    <div
      style={{
        width: '100%',
        height: typeof height === 'number' ? `${height}px` : height,
        borderRadius: 'var(--radius-lg)',
        background: 'radial-gradient(ellipse at 50% 50%, rgba(99, 102, 241, 0.12) 0%, rgba(14, 19, 34, 0.6) 80%)',
        border: '1px solid var(--border-glass)',
        position: 'relative',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem',
        boxShadow: 'inset 0 0 40px rgba(0, 0, 0, 0.3)',
      }}
    >
      {/* Decorative CSS grid lines */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage:
            'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)',
          backgroundSize: '24px 24px',
          pointerEvents: 'none',
        }}
      />

      {children ? (
        <div style={{ position: 'relative', zIndex: 2, width: '100%' }}>{children}</div>
      ) : (
        <div style={{ position: 'relative', zIndex: 2, textAlign: 'center' }}>
          {icon && (
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                background: 'rgba(99, 102, 241, 0.2)',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--primary)',
                marginBottom: '0.75rem',
              }}
            >
              {icon}
            </div>
          )}
          <h4 style={{ color: '#FFFFFF', marginBottom: '0.35rem', fontWeight: 600 }}>{title}</h4>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', maxWidth: '360px', margin: '0 auto' }}>
            {subtitle}
          </p>
        </div>
      )}
    </div>
  );
};
