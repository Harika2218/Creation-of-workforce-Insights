import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html, Float, Line } from '@react-three/drei';
import * as THREE from 'three';
import { SceneCanvas } from './SceneCanvas';
import { useTheme } from '../../context/ThemeContext';
import { BrainCircuit, Sparkles, TrendingUp, AlertTriangle, Users, BookOpen, Clock, ShieldCheck } from 'lucide-react';
import { Badge } from '../common/Badge';

interface AIModuleNode {
  id: string;
  title: string;
  category: string;
  position: [number, number, number];
  color: string;
  metric: string;
  desc: string;
}

const AI_MODULES: AIModuleNode[] = [
  {
    id: 'absenteeism',
    title: 'Absenteeism Prediction',
    category: 'Risk Modeling',
    position: [-2.4, 1.2, 0.2],
    color: '#F59E0B',
    metric: '92% Accuracy',
    desc: 'RandomForest predictive risk scoring for early intervention.',
  },
  {
    id: 'attrition',
    title: 'Attrition Flight Risk',
    category: 'Retention Intelligence',
    position: [2.4, 1.2, -0.2],
    color: '#EF4444',
    metric: '18 High-Risk Flagged',
    desc: 'Logistic Regression & tenure analysis for workforce stability.',
  },
  {
    id: 'anomaly',
    title: 'Attendance Anomaly',
    category: 'Outlier Detection',
    position: [-2.0, -1.2, 0.4],
    color: '#0EA5E9',
    metric: 'Isolation Forest Active',
    desc: 'Multivariate anomaly detection on clock-in, duration & GPS.',
  },
  {
    id: 'forecast',
    title: 'Workforce Forecaster',
    category: 'Demand & Capacity',
    position: [2.0, -1.2, 0.3],
    color: '#10B981',
    metric: '3-Month Horizon',
    desc: 'Polynomial trend projection against department growth targets.',
  },
  {
    id: 'skills',
    title: 'Skill Gap & Training',
    category: 'Talent Optimization',
    position: [0.0, 1.8, -0.5],
    color: '#A855F7',
    metric: '14 Critical Gaps',
    desc: 'Competency matching against target role benchmarks.',
  },
  {
    id: 'productivity',
    title: 'Productivity Engine',
    category: 'Performance Insights',
    position: [0.0, -1.8, -0.3],
    color: '#6366F1',
    metric: '8.4 hrs/day Normal',
    desc: 'Timesheet, delivery rate & goal completion metrics.',
  },
];

const CentralAICore: React.FC<{ activeModule: string | null }> = ({ activeModule }) => {
  const coreRef = useRef<THREE.Mesh>(null);
  const ring1Ref = useRef<THREE.Mesh>(null);
  const ring2Ref = useRef<THREE.Mesh>(null);
  const { reducedMotion } = useTheme();

  useFrame((_, delta) => {
    if (reducedMotion) return;
    if (coreRef.current) {
      coreRef.current.rotation.y += delta * 0.4;
      coreRef.current.rotation.z += delta * 0.2;
    }
    if (ring1Ref.current) {
      ring1Ref.current.rotation.x += delta * 0.3;
      ring1Ref.current.rotation.y += delta * 0.2;
    }
    if (ring2Ref.current) {
      ring2Ref.current.rotation.z -= delta * 0.25;
      ring2Ref.current.rotation.x -= delta * 0.15;
    }
  });

  return (
    <group position={[0, 0, 0]}>
      {/* Central AI Nucleus */}
      <mesh ref={coreRef}>
        <icosahedronGeometry args={[0.75, 1]} />
        <meshStandardMaterial
          color={activeModule ? '#A5B4FC' : '#6366F1'}
          emissive="#4338CA"
          emissiveIntensity={0.8}
          roughness={0.15}
          metalness={0.85}
          wireframe={false}
        />
      </mesh>

      {/* Orbiting Gyro Ring 1 */}
      <mesh ref={ring1Ref}>
        <torusGeometry args={[1.3, 0.03, 16, 64]} />
        <meshStandardMaterial color="#818CF8" emissive="#6366F1" emissiveIntensity={0.6} />
      </mesh>

      {/* Orbiting Gyro Ring 2 */}
      <mesh ref={ring2Ref} rotation={[Math.PI / 3, 0, 0]}>
        <torusGeometry args={[1.6, 0.025, 16, 64]} />
        <meshStandardMaterial color="#C7D2FE" emissive="#4F46E5" emissiveIntensity={0.4} />
      </mesh>
    </group>
  );
};

const ModuleNode: React.FC<{
  node: AIModuleNode;
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
      <Float speed={reducedMotion ? 0 : 2} rotationIntensity={0.1} floatIntensity={0.25}>
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
          scale={isSelected ? 1.35 : hovered ? 1.2 : 1.0}
        >
          <sphereGeometry args={[0.34, 24, 24]} />
          <meshStandardMaterial
            color={node.color}
            emissive={node.color}
            emissiveIntensity={isSelected || hovered ? 0.9 : 0.3}
            roughness={0.2}
            metalness={0.8}
          />
        </mesh>

        {/* Floating Tag */}
        <Html distanceFactor={8} position={[0, -0.65, 0]} center>
          <div
            style={{
              padding: '0.25rem 0.55rem',
              borderRadius: '6px',
              background: 'rgba(14, 19, 34, 0.92)',
              border: `1px solid ${hovered || isSelected ? node.color : 'rgba(255, 255, 255, 0.15)'}`,
              color: '#FFFFFF',
              fontSize: '11px',
              fontWeight: 700,
              whiteSpace: 'nowrap',
              pointerEvents: 'none',
              backdropFilter: 'blur(8px)',
              boxShadow: `0 0 14px ${node.color}50`,
            }}
          >
            {node.title}
          </div>
        </Html>
      </Float>
    </group>
  );
};

export const AIIntelligenceCore: React.FC = () => {
  const [selectedModule, setSelectedModule] = useState<string | null>('absenteeism');

  const activeModuleData = AI_MODULES.find((m) => m.id === selectedModule);

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
      {/* Header Pipeline Banner */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <h3 style={{ margin: 0, color: '#FFFFFF', fontSize: '1.2rem', fontWeight: 700 }}>
              AI Workforce Intelligence Core
            </h3>
            <Badge variant="purple">Neural Pipeline Active</Badge>
          </div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              color: 'var(--text-dim)',
              fontSize: '0.78rem',
              marginTop: '0.35rem',
            }}
          >
            <span>HR Data Streams</span>
            <span>→</span>
            <span style={{ color: 'var(--primary)', fontWeight: 600 }}>AI Analysis</span>
            <span>→</span>
            <span style={{ color: 'var(--info)', fontWeight: 600 }}>Workforce Intelligence</span>
            <span>→</span>
            <span style={{ color: 'var(--success)', fontWeight: 600 }}>Automated Workflows</span>
          </div>
        </div>

        {activeModuleData && (
          <div
            style={{
              padding: '0.4rem 0.85rem',
              borderRadius: 'var(--radius-md)',
              background: `${activeModuleData.color}15`,
              border: `1px solid ${activeModuleData.color}40`,
              color: activeModuleData.color,
              fontSize: '0.8rem',
              fontWeight: 700,
            }}
          >
            {activeModuleData.metric}
          </div>
        )}
      </div>

      {/* 3D Scene View */}
      <div style={{ position: 'relative', width: '100%', height: '360px', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        <SceneCanvas
          height="100%"
          camera={{ position: [0, 0, 6.8], fov: 45 }}
          fallbackTitle="AI Intelligence Core"
          fallbackSubtitle="Neural workforce intelligence modules."
        >
          <ambientLight intensity={0.7} />
          <directionalLight position={[10, 10, 5]} intensity={1.2} />
          <pointLight position={[0, 0, 3]} intensity={1.2} color="#818CF8" />

          {/* Central AI Core */}
          <CentralAICore activeModule={selectedModule} />

          {/* AI Satellite Nodes & Data Conduits */}
          {AI_MODULES.map((node) => (
            <React.Fragment key={node.id}>
              <ModuleNode
                node={node}
                isSelected={selectedModule === node.id}
                onSelect={(id) => setSelectedModule(selectedModule === id ? null : id)}
              />
              <Line
                points={[[0, 0, 0], node.position]}
                color={selectedModule === node.id ? node.color : 'rgba(99, 102, 241, 0.25)'}
                lineWidth={selectedModule === node.id ? 2 : 1}
                transparent
                opacity={selectedModule === node.id ? 0.9 : 0.35}
              />
            </React.Fragment>
          ))}
        </SceneCanvas>

        {/* Selected Module Detail HUD Card */}
        {activeModuleData && (
          <div
            style={{
              position: 'absolute',
              bottom: '1rem',
              left: '1rem',
              maxWidth: '380px',
              padding: '0.85rem 1.1rem',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(14, 19, 34, 0.92)',
              backdropFilter: 'blur(12px)',
              border: `1px solid ${activeModuleData.color}50`,
              boxShadow: 'var(--shadow-lg)',
              pointerEvents: 'none',
              zIndex: 20,
            }}
          >
            <div style={{ fontSize: '0.72rem', color: activeModuleData.color, textTransform: 'uppercase', fontWeight: 700 }}>
              {activeModuleData.category}
            </div>
            <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#FFF', margin: '0.2rem 0' }}>
              {activeModuleData.title}
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
              {activeModuleData.desc}
            </div>
          </div>
        )}
      </div>

      {/* Module Selector Chips Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
          gap: '0.6rem',
        }}
      >
        {AI_MODULES.map((m) => (
          <button
            key={m.id}
            onClick={() => setSelectedModule(m.id)}
            style={{
              padding: '0.65rem 0.85rem',
              borderRadius: 'var(--radius-md)',
              background: selectedModule === m.id ? `${m.color}20` : 'rgba(255, 255, 255, 0.02)',
              border: `1px solid ${selectedModule === m.id ? m.color : 'var(--border-subtle)'}`,
              color: selectedModule === m.id ? '#FFFFFF' : 'var(--text-muted)',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              transition: 'all 0.2s',
            }}
          >
            <span>{m.title}</span>
            <span
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: m.color,
                boxShadow: selectedModule === m.id ? `0 0 8px ${m.color}` : 'none',
              }}
            />
          </button>
        ))}
      </div>
    </div>
  );
};
