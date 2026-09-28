import React, { ReactNode } from 'react';

interface StatCardProps {
  label: string;
  value: string | number;
  subtext?: ReactNode;
  icon: ReactNode;
  iconBg?: string;
  iconColor?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  subtext,
  icon,
  iconBg,
  iconColor,
}) => {
  return (
    <div className="stat-card">
      <div className="stat-info">
        <span className="stat-label">{label}</span>
        <span className="stat-value">{value}</span>
        {subtext && <div className="stat-subtext">{subtext}</div>}
      </div>
      <div
        className="stat-icon-wrapper"
        style={{
          background: iconBg,
          color: iconColor,
        }}
      >
        {icon}
      </div>
    </div>
  );
};
