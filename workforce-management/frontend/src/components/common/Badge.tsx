import React, { ReactNode } from 'react';

export type BadgeVariant =
  | 'success' | 'warning' | 'danger' | 'info' | 'purple' | 'neutral'
  | 'present' | 'absent' | 'late' | 'half-day' | 'on-leave'
  | 'active' | 'notice' | 'deactivated'
  | 'pending' | 'approved' | 'rejected'
  | 'high' | 'medium' | 'low';

interface BadgeProps {
  variant?: BadgeVariant | string;
  children: ReactNode;
  icon?: ReactNode;
  ariaLabel?: string;
}

export const Badge: React.FC<BadgeProps> = ({ variant = 'neutral', children, icon, ariaLabel }) => {
  // Normalize string to match CSS class
  const normalized = String(variant).toLowerCase().replace(/\s+/g, '-');
  const badgeClass = `badge badge-${normalized}`;

  return (
    <span
      className={badgeClass}
      role="status"
      aria-label={ariaLabel || (typeof children === 'string' ? `Status: ${children}` : undefined)}
    >
      {icon && (
        <span aria-hidden="true" style={{ display: 'inline-flex', alignItems: 'center', marginRight: '4px' }}>
          {icon}
        </span>
      )}
      <span>{children}</span>
    </span>
  );
};

export default Badge;
