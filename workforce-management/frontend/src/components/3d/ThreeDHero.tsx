import React, { useRef, useState, useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Float, Html, Line } from '@react-three/drei';
import * as THREE from 'three';
import { SceneCanvas } from './SceneCanvas';
import { Sparkles, Building2, Users, Cpu, ShieldCheck } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

interface DepartmentNodeData {
  id: string;
  name: string;
  color: string;
  position: [number, number, number];
  headcount: number;
}

const DEPARTMENTS: DepartmentNodeData[] = [
  { id: 'eng', name: 'Engineering', color: '#6366F1', position: [-2.2, 1.0, 0.4], headcount: 72 },
  { id: 'ops', name: 'Operations', color: '#3B82F6', position: [2.2, 1.1, -0.2], headcount: 48 },
  { id: 'sales', name: 'Sales & Mktg', color: '#10B981', position: [-1.8, -1.2, 0.2], headcount: 36 },
  { id: 'hr', name: 'Human Resources', color: '#A855F7', position: [1.9, -1.1, 0.5], headcount: 18 },
  { id: 'fin', name: 'Finance', color: '#F59E0B', position: [0.0, 1.8, -0.6], headcount: 16 },
  { id: 'legal', name: 'Compliance', color: '#0EA5E9', position: [0.0, -1.8, -0.4], headcount: 10 },
];

const CentralCore: React.FC<{ activeDept: string | null }> = ({ activeDept }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const { reducedMotion } = useTheme();

  useFrame((_, delta) => {
    if (reducedMotion) return;
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.4;
      meshRef.current.rotation.x += delta * 0.2;
    }
    if (ringRef.current) {
      ringRef.current.rotation.z -= delta * 0.3;
      ringRef.current.rotation.x += delta * 0.15;
    }
  });

  return (
    <group position={[0, 0, 0]}>
      {/* Central Workforce AI Nucleus */}
      <mesh ref={meshRef}>
        <octahedronGeometry args={[0.7, 2]} />
        <meshStandardMaterial
          color={activeDept ? '#818CF8' : '#6366F1'}
          emissive="#4338CA"
          emissiveIntensity={0.6}
          roughness={0.2}
          metalness={0.8}
          wireframe={false}
        />
      </mesh>

      {/* Orbiting Orbital Ring */}
      <mesh ref={ringRef}>
        <torusGeometry args={[1.2, 0.03, 16, 64]} />
        <meshStandardMaterial
          color="#A5B4FC"
          emissive="#6366F1"
          emissiveIntensity={0.5}
          roughness={0.1}
          metalness={0.9}
        />
      </mesh>

      {/* Outer Pulse Shell */}
      <mesh>
        <sphereGeometry args={[0.9, 16, 16]} />
        <meshBasicMaterial color="#6366F1" wireframe transparent opacity={0.15} />
      </mesh>
    </group>
  );
};

const DepartmentNode: React.FC<{
  node: DepartmentNodeData;
  isSelected: boolean;
  onSelect: (id: string) => void;
}> = ({ node, isSelected, onSelect }) => {
  const [hovered, setHovered] = useState(false);
  const meshRef = useRef<THREE.Mesh>(null);
  const { reducedMotion } = useTheme();

  useFrame((_, delta) => {
    if (reducedMotion || !meshRef.current) return;
    meshRef.current.rotation.y += delta * 0.5;
  });

  return (
    <group position={node.position}>
      <Float speed={reducedMotion ? 0 : 2} rotationIntensity={0.2} floatIntensity={0.3}>
        <mesh
          ref={meshRef}
          onClick={(e) => {
            e.stopPropagation();
            onSelect(node.id);
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
          scale={isSelected ? 1.3 : hovered ? 1.2 : 1.0}
        >
          <sphereGeometry args={[0.35, 24, 24]} />
          <meshStandardMaterial
            color={node.color}
            emissive={node.color}
            emissiveIntensity={isSelected || hovered ? 0.8 : 0.3}
            roughness={0.2}
            metalness={0.7}
          />
        </mesh>

        {/* Orbit Ring around Node */}
        <mesh rotation={[Math.PI / 4, 0, 0]}>
          <ringGeometry args={[0.45, 0.49, 32]} />
          <meshBasicMaterial
            color={node.color}
            side={THREE.DoubleSide}
            transparent
            opacity={hovered || isSelected ? 0.8 : 0.3}
          />
        </mesh>

        {/* HTML 3D Floating Tag */}
        <Html distanceFactor={10} position={[0, -0.65, 0]} center>
          <div
            style={{
              padding: '0.2rem 0.5rem',
              borderRadius: '6px',
              background: 'rgba(14, 19, 34, 0.85)',
              border: `1px solid ${hovered || isSelected ? node.color : 'rgba(255, 255, 255, 0.15)'}`,
              color: '#FFFFFF',
              fontSize: '11px',
              fontWeight: 600,
              whiteSpace: 'nowrap',
              pointerEvents: 'none',
              backdropFilter: 'blur(8px)',
              boxShadow: hovered ? `0 0 12px ${node.color}60` : '0 2px 8px rgba(0,0,0,0.5)',
              transform: 'scale(1)',
              transition: 'all 0.2s ease',
            }}
          >
            {node.name} • {node.headcount}
          </div>
        </Html>
      </Float>
    </group>
  );
};

const ConstellationScene: React.FC<{
  activeDept: string | null;
  onSelectDept: (id: string | null) => void;
}> = ({ activeDept, onSelectDept }) => {
  const groupRef = useRef<THREE.Group>(null);
  const { mouse } = useThree();
  const { reducedMotion } = useTheme();

  useFrame(() => {
    if (reducedMotion || !groupRef.current) return;
    // Parallax mouse follow
    groupRef.current.rotation.y = THREE.MathUtils.lerp(groupRef.current.rotation.y, mouse.x * 0.25, 0.05);
    groupRef.current.rotation.x = THREE.MathUtils.lerp(groupRef.current.rotation.x, -mouse.y * 0.2, 0.05);
  });

  return (
    <group ref={groupRef} onClick={() => onSelectDept(null)}>
      {/* Lighting */}
      <ambientLight intensity={0.7} />
      <directionalLight position={[5, 8, 5]} intensity={1.2} />
      <pointLight position={[0, 0, 0]} intensity={1.5} color="#818CF8" distance={6} />
      <pointLight position={[-4, 3, 2]} intensity={0.8} color="#3B82F6" />
      <pointLight position={[4, -3, 2]} intensity={0.8} color="#10B981" />

      {/* Central Core */}
      <CentralCore activeDept={activeDept} />

      {/* Department Clusters */}
      {DEPARTMENTS.map((dept) => (
        <React.Fragment key={dept.id}>
          <DepartmentNode
            node={dept}
            isSelected={activeDept === dept.id}
            onSelect={(id) => onSelectDept(activeDept === id ? null : id)}
          />
          {/* Animated Connecting Filament */}
          <Line
            points={[[0, 0, 0], dept.position]}
            color={activeDept === dept.id ? dept.color : 'rgba(99, 102, 241, 0.25)'}
            lineWidth={activeDept === dept.id ? 2 : 1}
            transparent
            opacity={activeDept === dept.id ? 0.9 : 0.35}
          />
        </React.Fragment>
      ))}
    </group>
  );
};

interface ThreeDHeroProps {
  totalEmployees?: number;
  activeEmployees?: number;
  departmentCount?: number;
  locationCount?: number;
}

export const ThreeDHero: React.FC<ThreeDHeroProps> = ({
  totalEmployees = 200,
  activeEmployees = 192,
  departmentCount = 6,
  locationCount = 4,
}) => {
  const [selectedDept, setSelectedDept] = useState<string | null>(null);

  const activeDeptInfo = useMemo(() => {
    return DEPARTMENTS.find((d) => d.id === selectedDept);
  }, [selectedDept]);

  return (
    <div
      style={{
        position: 'relative',
        borderRadius: 'var(--radius-xl)',
        overflow: 'hidden',
        background: 'radial-gradient(ellipse at 70% 30%, rgba(99, 102, 241, 0.2) 0%, rgba(14, 19, 34, 0.85) 75%)',
        border: '1px solid var(--border-glass)',
        boxShadow: 'var(--shadow-lg), 0 0 35px rgba(99, 102, 241, 0.15)',
        minHeight: '340px',
        display: 'flex',
        alignItems: 'stretch',
      }}
    >
      {/* Left Text & Metrics Overlay */}
      <div
        style={{
          flex: '1 1 50%',
          padding: '2.2rem 2.4rem',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          zIndex: 10,
          background: 'linear-gradient(90deg, rgba(11, 15, 25, 0.85) 0%, rgba(11, 15, 25, 0.4) 100%)',
          backdropFilter: 'blur(8px)',
        }}
      >
        <div>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.45rem',
              padding: '0.25rem 0.75rem',
              borderRadius: 'var(--radius-full)',
              background: 'rgba(99, 102, 241, 0.15)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              fontSize: '0.75rem',
              fontWeight: 700,
              color: 'var(--primary)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: '0.8rem',
            }}
          >
            <Sparkles size={14} />
            <span>Workforce Intelligence Mesh • Live 3D</span>
          </div>

          <h2
            style={{
              fontSize: '1.9rem',
              fontWeight: 800,
              color: '#FFFFFF',
              letterSpacing: '-0.02em',
              lineHeight: 1.2,
              marginBottom: '0.6rem',
            }}
          >
            Real-Time Enterprise Workforce Orchestration
          </h2>

          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '480px', lineHeight: 1.5 }}>
            Interactive 3D representation of organizational nodes, predictive workforce capacity, and automated HR pipelines across active departments.
          </p>
        </div>

        {/* Dynamic Interactive Selection Drawer or Stats */}
        {activeDeptInfo ? (
          <div
            style={{
              marginTop: '1.25rem',
              padding: '0.9rem 1.1rem',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(255, 255, 255, 0.04)',
              border: `1px solid ${activeDeptInfo.color}50`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Selected Department</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#FFF' }}>{activeDeptInfo.name}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: activeDeptInfo.color }}>{activeDeptInfo.headcount}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Active Personnel</div>
            </div>
          </div>
        ) : (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: '1rem',
              marginTop: '1.5rem',
            }}
          >
            <div style={{ padding: '0.6rem 0.8rem', borderRadius: 'var(--radius-md)', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                <Users size={14} /> Total Staff
              </div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#FFF', marginTop: '0.2rem' }}>{totalEmployees}</div>
            </div>

            <div style={{ padding: '0.6rem 0.8rem', borderRadius: 'var(--radius-md)', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                <Building2 size={14} /> Units
              </div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#FFF', marginTop: '0.2rem' }}>{departmentCount}</div>
            </div>

            <div style={{ padding: '0.6rem 0.8rem', borderRadius: 'var(--radius-md)', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                <ShieldCheck size={14} /> Active
              </div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--success)', marginTop: '0.2rem' }}>{activeEmployees}</div>
            </div>
          </div>
        )}
      </div>

      {/* Right 3D Canvas Area */}
      <div style={{ flex: '1 1 50%', minHeight: '340px', position: 'relative' }}>
        <SceneCanvas
          height="100%"
          camera={{ position: [0, 0, 6.5], fov: 45 }}
          fallbackTitle="Enterprise Workforce Constellation"
          fallbackSubtitle="Real-time department nodes and organizational data pipelines."
        >
          <ConstellationScene activeDept={selectedDept} onSelectDept={setSelectedDept} />
        </SceneCanvas>
      </div>
    </div>
  );
};
