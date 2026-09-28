import React, { Component, ReactNode, Suspense, useEffect, useState } from 'react';
import { Canvas, CanvasProps } from '@react-three/fiber';
import { WebGLFallback } from './WebGLFallback';
import { useTheme } from '../../context/ThemeContext';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

class CanvasErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.warn('3D Scene Canvas encountered an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

interface SceneCanvasProps extends Omit<CanvasProps, 'children'> {
  children: ReactNode;
  height?: string | number;
  fallbackTitle?: string;
  fallbackSubtitle?: string;
  customFallback?: ReactNode;
  interactive?: boolean;
}

export const SceneCanvas: React.FC<SceneCanvasProps> = ({
  children,
  height = '350px',
  fallbackTitle,
  fallbackSubtitle,
  customFallback,
  interactive = true,
  camera = { position: [0, 0, 8], fov: 45 },
  gl = { antialias: true, alpha: true, powerPreference: 'high-performance' },
  dpr,
  ...rest
}) => {
  const { reducedMotion } = useTheme();
  const [hasWebGL, setHasWebGL] = useState<boolean>(true);
  const [isMobile, setIsMobile] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth < 768;
    }
    return false;
  });

  useEffect(() => {
    try {
      const canvas = document.createElement('canvas');
      const supported = !!(
        window.WebGLRenderingContext &&
        (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
      );
      setHasWebGL(supported);
    } catch {
      setHasWebGL(false);
    }

    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Compute mobile-adapted height: compress large desktop scenes on mobile
  const effectiveHeight = isMobile && height === '350px' ? '240px' : height;

  // On mobile screens, clamp DPR to 1 to reduce thermal throttling and battery drain
  const effectiveDpr = dpr || (isMobile ? [1, 1] : [1, 1.5]);

  const defaultFallback = (
    <WebGLFallback
      height={effectiveHeight}
      title={fallbackTitle}
      subtitle={fallbackSubtitle}
    >
      {customFallback}
    </WebGLFallback>
  );

  // If WebGL is not available or reduced-motion is requested, gracefully render the 2D fallback
  if (!hasWebGL || reducedMotion) {
    return defaultFallback;
  }

  return (
    <div
      style={{
        width: '100%',
        height: typeof effectiveHeight === 'number' ? `${effectiveHeight}px` : effectiveHeight,
        position: 'relative',
        borderRadius: 'var(--radius-lg)',
        overflow: 'hidden',
        pointerEvents: interactive ? 'auto' : 'none',
      }}
    >
      <CanvasErrorBoundary fallback={defaultFallback}>
        <Canvas
          camera={camera}
          gl={{
            ...gl,
            powerPreference: isMobile ? 'default' : 'high-performance',
          }}
          dpr={effectiveDpr}
          style={{ width: '100%', height: '100%', display: 'block' }}
          {...rest}
        >
          <Suspense fallback={null}>
            {children}
          </Suspense>
        </Canvas>
      </CanvasErrorBoundary>
    </div>
  );
};

export default SceneCanvas;
