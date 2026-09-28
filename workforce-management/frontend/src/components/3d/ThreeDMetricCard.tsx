import React, { useRef, useState } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { useTheme } from '../../context/ThemeContext';

interface ThreeDMetricCardProps {
  label: string;
  value: string | number;
  subtext?: React.ReactNode;
  icon?: React.ReactNode;
  iconBg?: string;
  iconColor?: string;
  accentColor?: string;
  badge?: string;
  badgeVariant?: 'success' | 'warning' | 'danger' | 'info' | 'purple';
  onClick?: () => void;
}

export const ThreeDMetricCard: React.FC<ThreeDMetricCardProps> = ({
  label,
  value,
  subtext,
  icon,
  iconBg = 'rgba(99, 102, 241, 0.15)',
  iconColor = 'var(--primary)',
  accentColor = 'var(--primary)',
  badge,
  badgeVariant = 'info',
  onClick,
}) => {
  const { reducedMotion } = useTheme();
  const cardRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  // Mouse tilt tracking
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const springConfig = { damping: 20, stiffness: 200 };
  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [6, -6]), springConfig);
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-6, 6]), springConfig);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (reducedMotion || !cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const xPct = (e.clientX - rect.left) / rect.width - 0.5;
    const yPct = (e.clientY - rect.top) / rect.height - 0.5;
    mouseX.set(xPct);
    mouseY.set(yPct);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    mouseX.set(0);
    mouseY.set(0);
  };

  const getBadgeStyle = () => {
    switch (badgeVariant) {
      case 'success':
        return { bg: 'var(--success-bg)', color: 'var(--success)', border: 'var(--success-border)' };
      case 'warning':
        return { bg: 'var(--warning-bg)', color: 'var(--warning)', border: 'var(--warning-border)' };
      case 'danger':
        return { bg: 'var(--danger-bg)', color: 'var(--danger)', border: 'var(--danger-border)' };
      case 'purple':
        return { bg: 'var(--purple-bg)', color: 'var(--purple)', border: 'var(--purple-border)' };
      default:
        return { bg: 'var(--info-bg)', color: 'var(--info)', border: 'var(--info-border)' };
    }
  };

  const badgeStyle = getBadgeStyle();

  return (
    <motion.div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      style={{
        perspective: '1000px',
        cursor: onClick ? 'pointer' : 'default',
      }}
      animate={reducedMotion ? {} : { scale: isHovered ? 1.02 : 1 }}
      transition={{ duration: 0.2 }}
    >
      <motion.div
        style={{
          rotateX: reducedMotion ? 0 : rotateX,
          rotateY: reducedMotion ? 0 : rotateY,
          transformStyle: 'preserve-3d',
          background: 'var(--bg-card)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: 'var(--border-glass)',
          borderRadius: 'var(--radius-lg)',
          padding: '1.4rem',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: isHovered ? 'var(--card-3d-shadow)' : 'var(--shadow-md)',
          transition: 'border-color 0.25s, box-shadow 0.25s',
          borderColor: isHovered ? accentColor : 'var(--border-subtle)',
        }}
      >
        {/* Subtle accent 3D top bar */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '3px',
            background: accentColor,
            opacity: isHovered ? 1 : 0.7,
            transition: 'opacity 0.2s',
          }}
        />

        {/* Dynamic 3D depth sheen overlay */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: isHovered
              ? 'radial-gradient(circle at 50% 0%, rgba(255, 255, 255, 0.08) 0%, transparent 70%)'
              : 'none',
            pointerEvents: 'none',
            transition: 'background 0.3s ease',
          }}
        />

        {/* Content with 3D z-depth */}
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            gap: '1rem',
            transform: reducedMotion ? 'none' : 'translateZ(15px)',
          }}
        >
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <span className="stat-label" style={{ margin: 0 }}>{label}</span>
              {badge && (
                <span
                  style={{
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    padding: '0.15rem 0.5rem',
                    borderRadius: 'var(--radius-full)',
                    background: badgeStyle.bg,
                    color: badgeStyle.color,
                    border: `1px solid ${badgeStyle.border}`,
                  }}
                >
                  {badge}
                </span>
              )}
            </div>

            <div className="stat-value" style={{ lineHeight: 1.1, marginBottom: '0.4rem' }}>
              {value}
            </div>

            {subtext && (
              <div className="stat-subtext" style={{ fontSize: '0.78rem' }}>
                {subtext}
              </div>
            )}
          </div>

          {icon && (
            <div
              className="stat-icon-wrapper"
              style={{
                background: iconBg,
                color: iconColor,
                border: `1px solid ${iconColor}40`,
                transform: reducedMotion ? 'none' : 'translateZ(25px)',
                boxShadow: isHovered ? `0 0 15px ${iconColor}40` : 'none',
                transition: 'box-shadow 0.25s, transform 0.25s',
              }}
            >
              {icon}
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};
