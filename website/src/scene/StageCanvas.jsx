import { Canvas } from '@react-three/fiber';
import { Suspense } from 'react';

export default function StageCanvas({ children, dpr = [1, 2], shadows = true, className = 'fixed inset-0 -z-0' }) {
  return (
    <div className={className}>
      <Canvas
        shadows={shadows}
        dpr={dpr}
        camera={{ position: [0, 1.5, 5], fov: 38 }}
        gl={{ antialias: true, powerPreference: 'high-performance' }}
      >
        <Suspense fallback={null}>
          {children}
        </Suspense>
      </Canvas>
    </div>
  );
}
