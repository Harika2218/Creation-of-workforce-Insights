import React from 'react';

interface LoadingSkeletonProps {
  lines?: number;
  height?: string;
  style?: React.CSSProperties;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  lines = 4,
  height = '24px',
  style,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem', width: '100%', ...style }}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton"
          style={{
            height,
            width: i === lines - 1 && lines > 1 ? '70%' : '100%',
          }}
        />
      ))}
    </div>
  );
};
