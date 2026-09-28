import React, { useRef, useState, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';
import { SceneCanvas } from './SceneCanvas';
import { Employee, Department } from '../../types';
import { useTheme } from '../../context/ThemeContext';
import { Badge } from '../common/Badge';

interface WorkforceSceneProps {
  employees: Employee[];
  departments?: Department[];
  onSelectEmployee?: (emp: Employee) => void;
}

// Department color mapping
const DEPT_COLORS: Record<string, string> = {
  Engineering: '#6366F1',
  'Sales & Marketing': '#10B981',
  Sales: '#10B981',
  'Human Resources': '#A855F7',
  HR: '#A855F7',
  Finance: '#F59E0B',
  Operations: '#3B82F6',
  Compliance: '#0EA5E9',
  Legal: '#0EA5E9',
};

// Department spatial centroids in 3D
const DEPT_CENTROIDS: Record<string, [number, number, number]> = {
  Engineering: [-2.5, 1.2, 0],
  'Sales & Marketing': [2.5, 1.2, 0],
  Sales: [2.5, 1.2, 0],
  'Human Resources': [-2.5, -1.2, 0],
  HR: [-2.5, -1.2, 0],
  Finance: [2.5, -1.2, 0],
  Operations: [0, 2.0, -1],
  Compliance: [0, -2.0, 1],
  Legal: [0, -2.0, 1],
};

const EmployeeNode: React.FC<{
  employee: Employee;
  position: [number, number, number];
  color: string;
  isSelected: boolean;
  onSelect: (emp: Employee) => void;
}> = ({ employee, position, color, isSelected, onSelect }) => {
  const [hovered, setHovered] = useState(false);
  const meshRef = useRef<THREE.Mesh>(null);
  const { reducedMotion } = useTheme();

  useFrame((_, delta) => {
    if (reducedMotion || !meshRef.current) return;
    meshRef.current.rotation.y += delta * 0.4;
  });

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={(e) => {
          e.stopPropagation();
          onSelect(employee);
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
        scale={isSelected ? 1.4 : hovered ? 1.25 : 1.0}
      >
        <sphereGeometry args={[0.22, 16, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isSelected || hovered ? 0.9 : 0.3}
          roughness={0.25}
          metalness={0.8}
        />
      </mesh>

      {/* Floating Mini Tag on Hover/Selected */}
      {(hovered || isSelected) && (
        <Html distanceFactor={8} position={[0, 0.4, 0]} center>
          <div
            style={{
              padding: '0.25rem 0.6rem',
              borderRadius: '6px',
              background: 'rgba(14, 19, 34, 0.92)',
              border: `1px solid ${color}`,
              color: '#FFFFFF',
              fontSize: '11px',
              fontWeight: 600,
              whiteSpace: 'nowrap',
              pointerEvents: 'none',
              boxShadow: `0 0 14px ${color}60`,
              backdropFilter: 'blur(8px)',
            }}
          >
            {employee.name} ({employee.employee_id})
          </div>
        </Html>
      )}
    </group>
  );
};

export const WorkforceScene: React.FC<WorkforceSceneProps> = ({
  employees,
  onSelectEmployee,
}) => {
  const [selectedDeptFilter, setSelectedDeptFilter] = useState<string>('ALL');
  const [inspectEmployee, setInspectEmployee] = useState<Employee | null>(null);

  // Group and sample employees to display in the 3D network
  const { filteredEmployees, departmentList } = useMemo(() => {
    const depts = Array.from(new Set(employees.map((e) => e.department_name || e.department_id || 'Operations')));
    const filtered =
      selectedDeptFilter === 'ALL'
        ? employees.slice(0, 45) // limit for high FPS and crisp spatial clarity
        : employees.filter((e) => (e.department_name || e.department_id) === selectedDeptFilter).slice(0, 30);
    return { filteredEmployees: filtered, departmentList: depts };
  }, [employees, selectedDeptFilter]);

  // Calculate 3D node positions around department centroids
  const nodes = useMemo(() => {
    return filteredEmployees.map((emp, index) => {
      const dept = emp.department_name || emp.department_id || 'Operations';
      const centroid = DEPT_CENTROIDS[dept] || [0, 0, 0];
      const angle = (index * 1.618 * 2 * Math.PI) % (2 * Math.PI);
      const radius = 0.5 + (index % 4) * 0.28;
      const x = centroid[0] + Math.cos(angle) * radius;
      const y = centroid[1] + Math.sin(angle) * radius * 0.7;
      const z = centroid[2] + ((index % 3) - 1) * 0.35;
      const color = DEPT_COLORS[dept] || '#6366F1';
      return { emp, position: [x, y, z] as [number, number, number], color };
    });
  }, [filteredEmployees]);

  const handleNodeSelect = (emp: Employee) => {
    setInspectEmployee(emp);
    if (onSelectEmployee) onSelectEmployee(emp);
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
      {/* Top Header & Filter Controls */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', zIndex: 10 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <h3 style={{ margin: 0, color: '#FFFFFF', fontSize: '1.2rem', fontWeight: 700 }}>
              Interactive 3D Workforce Topology
            </h3>
            <Badge variant="primary">{filteredEmployees.length} Nodes Displayed</Badge>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '0.2rem' }}>
            Spatial clustering by department. Drag to orbit, scroll to zoom, click node to inspect.
          </p>
        </div>

        {/* Department Filter Chips */}
        <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => setSelectedDeptFilter('ALL')}
            style={{
              padding: '0.3rem 0.75rem',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.78rem',
              fontWeight: 600,
              cursor: 'pointer',
              border: '1px solid var(--border-subtle)',
              background: selectedDeptFilter === 'ALL' ? 'var(--primary)' : 'rgba(255, 255, 255, 0.05)',
              color: '#FFFFFF',
              transition: 'all 0.2s',
            }}
          >
            All Clusters
          </button>
          {departmentList.slice(0, 5).map((dept) => {
            const isSelected = selectedDeptFilter === dept;
            const color = DEPT_COLORS[dept] || '#6366F1';
            return (
              <button
                key={dept}
                onClick={() => setSelectedDeptFilter(dept)}
                style={{
                  padding: '0.3rem 0.75rem',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: `1px solid ${isSelected ? color : 'var(--border-subtle)'}`,
                  background: isSelected ? `${color}25` : 'rgba(255, 255, 255, 0.03)',
                  color: isSelected ? '#FFFFFF' : 'var(--text-muted)',
                  transition: 'all 0.2s',
                }}
              >
                {dept}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main 3D Canvas with Side HUD Inspector */}
      <div style={{ position: 'relative', width: '100%', height: '420px', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        <SceneCanvas
          height="100%"
          camera={{ position: [0, 0, 7.5], fov: 48 }}
          fallbackTitle="3D Workforce Topology Scene"
          fallbackSubtitle="Select clusters to explore employee distribution."
        >
          <ambientLight intensity={0.7} />
          <directionalLight position={[10, 10, 5]} intensity={1.2} />
          <pointLight position={[0, 0, 4]} intensity={1} color="#6366F1" />

          {/* Department Label Anchor Markers */}
          {Object.entries(DEPT_CENTROIDS).map(([dept, pos]) => (
            <Html key={dept} position={[pos[0], pos[1] + 1.1, pos[2]]} center>
              <div
                style={{
                  padding: '0.2rem 0.5rem',
                  borderRadius: '4px',
                  background: 'rgba(11, 15, 25, 0.75)',
                  border: `1px solid ${DEPT_COLORS[dept] || '#6366F1'}40`,
                  color: DEPT_COLORS[dept] || '#6366F1',
                  fontSize: '10px',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  pointerEvents: 'none',
                }}
              >
                {dept}
              </div>
            </Html>
          ))}

          {/* Interactive Employee Nodes */}
          {nodes.map(({ emp, position, color }) => (
            <EmployeeNode
              key={emp.employee_id}
              employee={emp}
              position={position}
              color={color}
              isSelected={inspectEmployee?.employee_id === emp.employee_id}
              onSelect={handleNodeSelect}
            />
          ))}

          <OrbitControls
            enableDamping
            dampingFactor={0.05}
            maxDistance={12}
            minDistance={3.5}
            maxPolarAngle={Math.PI / 1.8}
            minPolarAngle={Math.PI / 6}
          />
        </SceneCanvas>

        {/* Selected Employee HUD Inspector Drawer */}
        {inspectEmployee && (
          <div
            style={{
              position: 'absolute',
              top: '1rem',
              right: '1rem',
              width: '300px',
              background: 'rgba(14, 19, 34, 0.92)',
              backdropFilter: 'blur(16px)',
              border: '1px solid var(--border-hover)',
              borderRadius: 'var(--radius-lg)',
              padding: '1.25rem',
              boxShadow: 'var(--shadow-lg)',
              zIndex: 30,
              animation: 'fadeIn 0.2s ease-out',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>
                Selected Personnel Node
              </span>
              <button
                onClick={() => setInspectEmployee(null)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-dim)',
                  cursor: 'pointer',
                  fontSize: '1rem',
                  lineHeight: 1,
                }}
              >
                ×
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <div
                style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: '50%',
                  background: 'var(--gradient-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  fontSize: '1rem',
                  color: '#FFFFFF',
                }}
              >
                {inspectEmployee.name?.charAt(0)}
              </div>
              <div>
                <div style={{ fontWeight: 700, color: '#FFF', fontSize: '0.95rem' }}>
                  {inspectEmployee.name}
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                  {inspectEmployee.employee_id} • {inspectEmployee.designation || 'Staff'}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Department:</span>
                <span style={{ color: '#FFF', fontWeight: 600 }}>{inspectEmployee.department_name || inspectEmployee.department_id}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Status:</span>
                <Badge variant={inspectEmployee.employment_status === 'Active' ? 'success' : 'warning'}>
                  {inspectEmployee.employment_status || 'Active'}
                </Badge>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Location:</span>
                <span style={{ color: '#FFF' }}>{inspectEmployee.location_name || inspectEmployee.location_id || 'Headquarters'}</span>
              </div>
              {inspectEmployee.email && (
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Corporate:</span>
                  <span style={{ color: 'var(--primary)', fontSize: '0.75rem' }}>{inspectEmployee.email}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
