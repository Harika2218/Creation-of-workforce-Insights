import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { SceneCanvas } from './SceneCanvas';
import { useTheme } from '../../context/ThemeContext';
import { Sun, Sunset, Moon, RefreshCw } from 'lucide-react';

interface ShiftCapacityData {
  id: string;
  name: string;
  assigned: number;
  capacity: number;
  timing: string;
  color: string;
  icon: string;
}

const DEFAULT_SHIFTS: ShiftCapacityData[] = [
  { id: 'morning', name: 'Morning Shift', assigned: 94, capacity: 100, timing: '08:00 - 17:00', color: '#10B981', icon: 'sun' },
  { id: 'afternoon', name: 'Afternoon Shift', assigned: 52, capacity: 60, timing: '14:00 - 23:00', color: '#3B82F6', icon: 'sunset' },
  { id: 'night', name: 'Night Shift', assigned: 32, capacity: 40, timing: '22:00 - 07:00', color: '#A855F7', icon: 'moon' },
  { id: 'rotational', name: 'Rotational Shift', assigned: 22, capacity: 30, timing: 'Flex Rotation', color: '#F59E0B', icon: 'refresh' },
];

const ShiftPodium: React.FC<{
  data: ShiftCapacityData;
  position: [number, number, number];
  isSelected: boolean;
  onSelect: () => void;
}> = ({ data, position, isSelected, onSelect }) => {
  const [hovered, setHovered] = useState(false);
  const meshRef = useRef<THREE.Mesh>(null);
  const fillRef = useRef<THREE.Mesh>(null);
  const { reducedMotion } = useTheme();

  const utilization = data.assigned / data.capacity;
  const cylinderHeight = 2.4;
  const fillHeight = Math.max(0.2, utilization * cylinderHeight);

  useFrame((_, delta) => {
    if (reducedMotion) return;
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.2;
    }
  });

  return (
    <group position={position}>
      {/* Outer Glass Container */}
      <mesh
        ref={meshRef}
        position={[0, cylinderHeight / 2, 0]}
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
      >
        <cylinderGeometry args={[0.55, 0.55, cylinderHeight, 32]} />
        <meshPhysicalMaterial
          color="#FFFFFF"
          transparent
          opacity={0.15}
          roughness={0.1}
          metalness={0.1}
          transmission={0.8}
          ior={1.4}
        />
      </mesh>

      {/* Inner Fluid Fill Cylinder */}
      <mesh ref={fillRef} position={[0, fillHeight / 2, 0]}>
        <cylinderGeometry args={[0.48, 0.48, fillHeight, 32]} />
        <meshStandardMaterial
          color={data.color}
          emissive={data.color}
          emissiveIntensity={isSelected || hovered ? 0.7 : 0.3}
          roughness={0.3}
          metalness={0.6}
        />
      </mesh>

      {/* Floating 3D Label */}
      <Html distanceFactor={8} position={[0, cylinderHeight + 0.5, 0]} center>
        <div
          style={{
            padding: '0.3rem 0.65rem',
            borderRadius: '6px',
            background: 'rgba(14, 19, 34, 0.9)',
            border: `1px solid ${hovered || isSelected ? data.color : 'rgba(255, 255, 255, 0.15)'}`,
            color: '#FFFFFF',
            fontSize: '11px',
            fontWeight: 700,
            whiteSpace: 'nowrap',
            backdropFilter: 'blur(8px)',
            boxShadow: `0 0 12px ${data.color}40`,
            pointerEvents: 'none',
            textAlign: 'center',
          }}
        >
          <div>{data.name}</div>
          <div style={{ color: data.color, fontSize: '10px' }}>
            {data.assigned} / {data.capacity} ({((utilization) * 100).toFixed(0)}%)
          </div>
        </div>
      </Html>
    </group>
  );
};

export const ShiftCapacityScene: React.FC<{ shifts?: ShiftCapacityData[] }> = ({
  shifts = DEFAULT_SHIFTS,
}) => {
  const [selectedShift, setSelectedShift] = useState<string | null>(null);

  const totalAssigned = shifts.reduce((acc, s) => acc + s.assigned, 0);
  const totalCapacity = shifts.reduce((acc, s) => acc + s.capacity, 0);

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
            3D Shift Allocation & Capacity Podiums
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '0.2rem' }}>
            Visual capacity utilization across Morning, Afternoon, Night, and Rotational operational rosters.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span
            style={{
              padding: '0.25rem 0.75rem',
              borderRadius: 'var(--radius-full)',
              background: 'rgba(59, 130, 246, 0.15)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              color: 'var(--info)',
              fontSize: '0.8rem',
              fontWeight: 700,
            }}
          >
            {totalAssigned} / {totalCapacity} Capacity ({((totalAssigned / totalCapacity) * 100).toFixed(0)}%)
          </span>
        </div>
      </div>

      <div style={{ position: 'relative', width: '100%', height: '320px', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        <SceneCanvas
          height="100%"
          camera={{ position: [0, 2.8, 6.2], fov: 42 }}
          fallbackTitle="Shift Capacity Scene"
          fallbackSubtitle="Roster distribution and staffing capacity."
        >
          <ambientLight intensity={0.7} />
          <directionalLight position={[10, 10, 5]} intensity={1.2} />
          <pointLight position={[0, 3, 0]} intensity={1.2} color="#6366F1" />

          {/* 4 Shift Spatial Podiums arranged linearly */}
          <ShiftPodium
            data={shifts[0]}
            position={[-3.0, -0.6, 0]}
            isSelected={selectedShift === shifts[0].id}
            onSelect={() => setSelectedShift(selectedShift === shifts[0].id ? null : shifts[0].id)}
          />
          <ShiftPodium
            data={shifts[1]}
            position={[-1.0, -0.6, 0]}
            isSelected={selectedShift === shifts[1].id}
            onSelect={() => setSelectedShift(selectedShift === shifts[1].id ? null : shifts[1].id)}
          />
          <ShiftPodium
            data={shifts[2]}
            position={[1.0, -0.6, 0]}
            isSelected={selectedShift === shifts[2].id}
            onSelect={() => setSelectedShift(selectedShift === shifts[2].id ? null : shifts[2].id)}
          />
          <ShiftPodium
            data={shifts[3]}
            position={[3.0, -0.6, 0]}
            isSelected={selectedShift === shifts[3].id}
            onSelect={() => setSelectedShift(selectedShift === shifts[3].id ? null : shifts[3].id)}
          />
        </SceneCanvas>
      </div>

      {/* Shift Details Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '0.75rem',
        }}
      >
        {shifts.map((s) => (
          <div
            key={s.id}
            style={{
              padding: '0.8rem',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(255, 255, 255, 0.02)',
              border: `1px solid ${selectedShift === s.id ? s.color : 'var(--border-subtle)'}`,
              transition: 'all 0.2s',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
              <span style={{ fontWeight: 600, color: '#FFF', fontSize: '0.85rem' }}>{s.name}</span>
              <span style={{ fontSize: '0.75rem', color: s.color, fontWeight: 700 }}>
                {((s.assigned / s.capacity) * 100).toFixed(0)}%
              </span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{s.timing}</div>
            <div style={{ width: '100%', height: '4px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '2px', marginTop: '0.5rem', overflow: 'hidden' }}>
              <div style={{ width: `${(s.assigned / s.capacity) * 100}%`, height: '100%', background: s.color }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
