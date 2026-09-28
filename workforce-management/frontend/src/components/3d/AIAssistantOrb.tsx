import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { SceneCanvas } from './SceneCanvas';
import { useTheme } from '../../context/ThemeContext';

interface AIAssistantOrbProps {
  size?: number | string;
  isThinking?: boolean;
  onClick?: () => void;
}

const HologramOrb: React.FC<{ isThinking: boolean }> = ({ isThinking }) => {
  const coreRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const outerRingRef = useRef<THREE.Mesh>(null);
  const { reducedMotion } = useTheme();

  useFrame((state, delta) => {
    if (reducedMotion) return;
    const t = state.clock.getElapsedTime();
    const speedMultiplier = isThinking ? 2.5 : 1.0;

    if (coreRef.current) {
      coreRef.current.rotation.y += delta * 0.6 * speedMultiplier;
      coreRef.current.rotation.x = Math.sin(t * 1.2) * 0.2;
      const scale = 1 + Math.sin(t * (isThinking ? 4 : 2)) * 0.06;
      coreRef.current.scale.set(scale, scale, scale);
    }

    if (ringRef.current) {
      ringRef.current.rotation.z += delta * 0.8 * speedMultiplier;
      ringRef.current.rotation.x = Math.PI / 3 + Math.cos(t * 1.5) * 0.15;
    }

    if (outerRingRef.current) {
      outerRingRef.current.rotation.y -= delta * 0.5 * speedMultiplier;
      outerRingRef.current.rotation.z = Math.sin(t * 1.0) * 0.2;
    }
  });

  return (
    <group position={[0, 0, 0]}>
      {/* Central Holographic Sphere */}
      <mesh ref={coreRef}>
        <sphereGeometry args={[0.9, 32, 32]} />
        <meshStandardMaterial
          color={isThinking ? '#818CF8' : '#6366F1'}
          emissive={isThinking ? '#4F46E5' : '#3730A3'}
          emissiveIntensity={isThinking ? 0.9 : 0.6}
          roughness={0.1}
          metalness={0.9}
          wireframe={isThinking}
        />
      </mesh>

      {/* Inner Holographic Ring */}
      <mesh ref={ringRef}>
        <torusGeometry args={[1.3, 0.035, 16, 64]} />
        <meshStandardMaterial
          color="#38BDF8"
          emissive="#0EA5E9"
          emissiveIntensity={0.8}
          roughness={0.1}
          metalness={0.8}
        />
      </mesh>

      {/* Outer Holographic Ring */}
      <mesh ref={outerRingRef} rotation={[Math.PI / 4, 0, 0]}>
        <torusGeometry args={[1.65, 0.025, 16, 64]} />
        <meshStandardMaterial
          color="#A855F7"
          emissive="#9333EA"
          emissiveIntensity={0.7}
          roughness={0.1}
          metalness={0.9}
        />
      </mesh>

      {/* Ambient Particle Dust */}
      <mesh>
        <sphereGeometry args={[1.1, 16, 16]} />
        <meshBasicMaterial color="#818CF8" wireframe transparent opacity={0.12} />
      </mesh>
    </group>
  );
};

export const AIAssistantOrb: React.FC<AIAssistantOrbProps> = ({
  size = 180,
  isThinking = false,
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      style={{
        width: typeof size === 'number' ? `${size}px` : size,
        height: typeof size === 'number' ? `${size}px` : size,
        position: 'relative',
        cursor: onClick ? 'pointer' : 'default',
        borderRadius: '50%',
        overflow: 'hidden',
        background: 'radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%)',
      }}
    >
      <SceneCanvas
        height="100%"
        camera={{ position: [0, 0, 4.5], fov: 45 }}
        fallbackTitle="AI Assistant Orb"
        fallbackSubtitle="Interactive AI HR Assistant."
      >
        <ambientLight intensity={0.8} />
        <pointLight position={[2, 3, 4]} intensity={1.5} color="#818CF8" />
        <pointLight position={[-2, -3, -2]} intensity={0.8} color="#38BDF8" />
        <HologramOrb isThinking={isThinking} />
      </SceneCanvas>
    </div>
  );
};
