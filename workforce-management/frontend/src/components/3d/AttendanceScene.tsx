import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html, Float } from '@react-three/drei';
import * as THREE from 'three';
import { SceneCanvas } from './SceneCanvas';
import { AttendanceSummary } from '../../types';
import { useTheme } from '../../context/ThemeContext';
import { Clock, CheckCircle2, AlertCircle, AlertTriangle, Moon, Zap } from 'lucide-react';

interface AttendanceSceneProps {
  summary: AttendanceSummary | null;
  dateStr?: string;
  onFilterChange?: (status: string) => void;
}

const ActivityPillar: React.FC<{
  label: string;
  count: number;
  color: string;
  position: [number, number, number];
  heightScale: number;
  isSelected: boolean;
  onSelect: () => void;
}> = ({ label, count, color, position, heightScale, isSelected, onSelect }) => {
  const [hovered, setHovered] = useState(false);
  const meshRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const { reducedMotion } = useTheme();

  const height = Math.max(0.6, heightScale * 2.2);

  useFrame((_, delta) => {
    if (reducedMotion) return;
    if (ringRef.current) {
      ringRef.current.rotation.z += delta * 0.4;
    }
  });

  return (
    <group position={position}>
      {/* 3D Pillar */}
      <mesh
        ref={meshRef}
        position={[0, height / 2, 0]}
        onClick={(e) => {
          e.stopPropagation();
          onSelect();
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
          document.body.style.cursor = 'pointer';
        }}
        onPointerOut={() => {
          setHovered(false);
          document.body.style.cursor = 'auto';
        }}
        scale={isSelected ? [1.2, 1.05, 1.2] : hovered ? [1.15, 1.0, 1.15] : [1, 1, 1]}
      >
        <cylinderGeometry args={[0.35, 0.4, height, 24]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isSelected || hovered ? 0.7 : 0.25}
          roughness={0.2}
          metalness={0.8}
        />
      </mesh>

      {/* Orbiting ground ring */}
      <mesh ref={ringRef} position={[0, 0.05, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.5, 0.58, 32]} />
        <meshBasicMaterial color={color} side={THREE.DoubleSide} transparent opacity={hovered || isSelected ? 0.8 : 0.3} />
      </mesh>

      {/* Floating 3D Metric Tag */}
      <Html distanceFactor={7} position={[0, height + 0.4, 0]} center>
        <div
          style={{
            padding: '0.2rem 0.55rem',
            borderRadius: '6px',
            background: 'rgba(14, 19, 34, 0.9)',
            border: `1px solid ${hovered || isSelected ? color : 'rgba(255, 255, 255, 0.15)'}`,
            color: '#FFFFFF',
            fontSize: '11px',
            fontWeight: 700,
            whiteSpace: 'nowrap',
            boxShadow: `0 0 12px ${color}50`,
            backdropFilter: 'blur(8px)',
            pointerEvents: 'none',
          }}
        >
          {label}: {count}
        </div>
      </Html>
    </group>
  );
};

export const AttendanceScene: React.FC<AttendanceSceneProps> = ({
  summary,
  dateStr = 'Today',
  onFilterChange,
}) => {
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null);

  const presentCount = summary?.present_count ?? 184;
  const lateCount = summary?.late_count ?? 6;
  const leaveCount = summary?.on_leave_count ?? 5;
  const absentCount = summary?.absent_count ?? 3;
  const halfDayCount = summary?.half_day_count ?? 2;
  const total = Math.max(1, presentCount + lateCount + leaveCount + absentCount + halfDayCount);

  const handleSelect = (status: string) => {
    const next = selectedStatus === status ? null : status;
    setSelectedStatus(next);
    if (onFilterChange) onFilterChange(next || 'ALL');
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        background: 'var(--bg-card)',
        border: '1px solid var(--border-glass)',
        borderRadius: 'var(--radius-xl)',
        padding: '1.5rem',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h3 style={{ margin: 0, color: '#FFFFFF', fontSize: '1.2rem', fontWeight: 700 }}>
            3D Attendance Radar & Workforce Activity Model
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '0.2rem' }}>
            Spatial circular activity distribution for {dateStr}. Click pillars to inspect status cohorts.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <span
            style={{
              padding: '0.25rem 0.75rem',
              borderRadius: 'var(--radius-full)',
              background: 'rgba(16, 185, 129, 0.15)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              color: 'var(--success)',
              fontSize: '0.8rem',
              fontWeight: 700,
            }}
          >
            {((presentCount / total) * 100).toFixed(1)}% Present
          </span>
        </div>
      </div>

      <div style={{ position: 'relative', width: '100%', height: '340px', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        <SceneCanvas
          height="100%"
          camera={{ position: [0, 3.5, 5.5], fov: 42 }}
          fallbackTitle="Attendance Activity Radar"
          fallbackSubtitle="Live attendance status metrics."
        >
          <ambientLight intensity={0.7} />
          <directionalLight position={[5, 10, 5]} intensity={1.2} />
          <pointLight position={[0, 2, 0]} intensity={1} color="#6366F1" />

          {/* Concentric Ground Radar Rings */}
          <group position={[0, -0.05, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <ringGeometry args={[1.2, 1.25, 48]} />
            <meshBasicMaterial color="#6366F1" side={THREE.DoubleSide} transparent opacity={0.2} />
          </group>
          <group position={[0, -0.05, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <ringGeometry args={[2.2, 2.25, 48]} />
            <meshBasicMaterial color="#3B82F6" side={THREE.DoubleSide} transparent opacity={0.25} />
          </group>
          <group position={[0, -0.05, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <ringGeometry args={[3.2, 3.25, 48]} />
            <meshBasicMaterial color="#10B981" side={THREE.DoubleSide} transparent opacity={0.15} />
          </group>

          {/* Center Hub */}
          <mesh position={[0, 0.2, 0]}>
            <sphereGeometry args={[0.4, 24, 24]} />
            <meshStandardMaterial color="#6366F1" emissive="#4F46E5" emissiveIntensity={0.6} />
          </mesh>

          {/* North: PRESENT */}
          <ActivityPillar
            label="Present"
            count={presentCount}
            color="#10B981"
            position={[0, 0, -1.8]}
            heightScale={presentCount / total}
            isSelected={selectedStatus === 'Present'}
            onSelect={() => handleSelect('Present')}
          />

          {/* West: LATE */}
          <ActivityPillar
            label="Late"
            count={lateCount}
            color="#F59E0B"
            position={[-2.0, 0, 0]}
            heightScale={lateCount / total}
            isSelected={selectedStatus === 'Late'}
            onSelect={() => handleSelect('Late')}
          />

          {/* East: ABSENT */}
          <ActivityPillar
            label="Absent"
            count={absentCount}
            color="#EF4444"
            position={[2.0, 0, 0]}
            heightScale={absentCount / total}
            isSelected={selectedStatus === 'Absent'}
            onSelect={() => handleSelect('Absent')}
          />

          {/* South-West: ON LEAVE */}
          <ActivityPillar
            label="On Leave"
            count={leaveCount}
            color="#A855F7"
            position={[-1.3, 0, 1.5]}
            heightScale={leaveCount / total}
            isSelected={selectedStatus === 'On Leave'}
            onSelect={() => handleSelect('On Leave')}
          />

          {/* South-East: HALF DAY */}
          <ActivityPillar
            label="Half Day"
            count={halfDayCount}
            color="#0EA5E9"
            position={[1.3, 0, 1.5]}
            heightScale={halfDayCount / total}
            isSelected={selectedStatus === 'Half Day'}
            onSelect={() => handleSelect('Half Day')}
          />
        </SceneCanvas>
      </div>

      {/* Summary KPI Strip */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
          gap: '0.75rem',
          marginTop: '0.5rem',
        }}
      >
        <div style={{ padding: '0.6rem 0.8rem', borderRadius: 'var(--radius-md)', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)' }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Present</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--success)' }}>{presentCount}</div>
        </div>

        <div style={{ padding: '0.6rem 0.8rem', borderRadius: 'var(--radius-md)', background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.25)' }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Late Arrival</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--warning)' }}>{lateCount}</div>
        </div>

        <div style={{ padding: '0.6rem 0.8rem', borderRadius: 'var(--radius-md)', background: 'rgba(168, 85, 247, 0.08)', border: '1px solid rgba(168, 85, 247, 0.25)' }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>On Leave</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--purple)' }}>{leaveCount}</div>
        </div>

        <div style={{ padding: '0.6rem 0.8rem', borderRadius: 'var(--radius-md)', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)' }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Absent</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--danger)' }}>{absentCount}</div>
        </div>

        <div style={{ padding: '0.6rem 0.8rem', borderRadius: 'var(--radius-md)', background: 'rgba(99, 102, 241, 0.08)', border: '1px solid rgba(99, 102, 241, 0.25)' }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Total Overtime</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--primary)' }}>{summary?.total_overtime_hours || 420} hrs</div>
        </div>
      </div>
    </div>
  );
};
